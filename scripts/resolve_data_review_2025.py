"""Registra decisões de qualidade para a instância CC/SI de 2025."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "processados"


def target_data():
    t = pd.read_csv(DATA / "turmas_2025.csv", dtype=str).fillna("")
    h = pd.read_csv(DATA / "horarios_2025.csv", dtype=str).fillna("")
    keep = t["curso"].isin({"31", "83"}) | (
        t["curso"].eq("") & t["periodo"].str.startswith(("CC-", "SI-"))
    )
    t = t[keep].copy()
    h = h[h["turma_id"].isin(set(t["id"]))].copy()
    return t, h


def review_rooms(t: pd.DataFrame, h: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for turma_id, group in h[h["sala"].eq("")].groupby("turma_id"):
        turma = t[t["id"].eq(turma_id)].iloc[0]
        candidates = sorted(
            set(h[(h["codigo"].eq(turma.codigo)) & h["sala"].ne("")]["sala"])
        )
        rows.append({
            "turma_id": turma_id,
            "semestre": turma.semestre,
            "codigo": turma.codigo,
            "disciplina": turma.disciplina,
            "curso": turma.curso or ("SI" if turma.periodo.startswith("SI-") else "CC"),
            "periodo": turma.periodo,
            "professor": turma.alocacao,
            "setor": turma.setor,
            "encontros_sem_sala": "; ".join(f"{r.dia} {r.inicio}-{r.fim}" for _, r in group.iterrows()),
            "candidatos_historicos": ", ".join(candidates),
            "status": "externa_sem_sala" if not turma.codigo.startswith("TCC") else "pendente_confirmacao",
            "decisao": "não preencher automaticamente",
        })
    return pd.DataFrame(rows)


def review_sectors(t: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, turma in t[t["setor"].eq("")].iterrows():
        external = not turma.codigo.startswith("TCC")
        rows.append({
            "turma_id": turma.id,
            "semestre": turma.semestre,
            "codigo": turma.codigo,
            "disciplina": turma.disciplina,
            "curso": turma.curso or ("SI" if turma.periodo.startswith("SI-") else "CC"),
            "periodo": turma.periodo,
            "professor": turma.alocacao,
            "classificacao": "externa" if external else "optativa_ou_ementa_variavel",
            "decisao": "setor não aplicável; não restringir dias por setor",
        })
    return pd.DataFrame(rows)


def validate_curriculum(t: pd.DataFrame, h: pd.DataFrame) -> pd.DataFrame:
    # Disciplinas obrigatórias confirmadas nos arquivos grade_cc.md/grade_si.md.
    official = {
        ("CC", "P5"): {"TCC00226", "TCC00312"},
        ("SI", "P1"): {"TCC00332", "TCC00354"},
    }
    h = h.merge(t[["id", "curso", "periodo", "disciplina"]], left_on="turma_id", right_on="id", how="left")
    h["grupo"] = h.apply(
        lambda r: f"{'CC' if r.curso == '31' else 'SI' if r.curso == '83' else r.curso}|{str(r.periodo).split('-P')[-1].split('-')[0]}",
        axis=1,
    )
    rows = []
    for key, group in h.groupby(["semestre", "grupo", "dia", "inicio", "fim"]):
        codes = set(group["codigo"].drop_duplicates())
        if len(codes) <= 1:
            continue
        course, period = key[1].split("|", 1)
        confirmed = codes.issubset(official.get((course, f"P{period}"), set()))
        rows.append({
            "semestre": key[0],
            "grupo": key[1],
            "dia": key[2],
            "inicio": key[3],
            "fim": key[4],
            "disciplinas": ", ".join(sorted(codes)),
            "confirmado_na_grade": confirmed,
            "decisao": "manter como hard" if confirmed else "revisar manualmente",
        })
    return pd.DataFrame(rows)


def main() -> None:
    t, h = target_data()
    room_review = review_rooms(t, h)
    sector_review = review_sectors(t)
    curriculum_review = validate_curriculum(t, h)
    rooms = pd.read_csv(DATA / "salas_2025.csv", dtype=str).fillna("")
    resources_path = DATA / "recursos_turmas_2025.csv"
    resource_classes = pd.read_csv(resources_path, dtype=str).fillna("") if resources_path.exists() else pd.DataFrame()
    resource_meetings_path = DATA / "recursos_encontros_2025.csv"
    resource_meetings = pd.read_csv(resource_meetings_path, dtype=str).fillna("") if resource_meetings_path.exists() else pd.DataFrame()
    lab_classes = int(resource_classes["exige_laboratorio"].eq("True").sum()) if not resource_classes.empty else 0
    unknown_classes = int(resource_classes["exige_laboratorio"].eq("").sum()) if not resource_classes.empty else 0
    lab_meetings = int(resource_meetings["requer_laboratorio"].eq("True").sum()) if not resource_meetings.empty else 0

    room_review.to_csv(DATA / "revisao_salas_2025.csv", index=False)
    sector_review.to_csv(DATA / "revisao_setores_2025.csv", index=False)
    curriculum_review.to_csv(DATA / "validacao_curricular_2025.csv", index=False)

    decisions = {
        "salas_sem_informacao": {
            "quantidade_turmas": int(room_review["turma_id"].nunique()),
            "decisao": "não preencher automaticamente; manter sala nula e candidatos históricos apenas como apoio",
        },
        "setores_ausentes": {
            "quantidade_turmas": int(len(sector_review)),
            "decisao": "externas e optativas/ementas variáveis não recebem restrição de setor nesta versão",
        },
        "conflitos_curriculares": {
            "quantidade": int(len(curriculum_review)),
            "confirmados_na_grade": int(curriculum_review["confirmado_na_grade"].sum()) if len(curriculum_review) else 0,
            "decisao": "conflitos confirmados permanecem hard",
        },
        "capacidade_salas": {
            "quantidade_salas": int(len(rooms)),
            "laboratorios": rooms[rooms["laboratorio"].astype(str).str.lower().eq("true")]["id"].tolist(),
            "decisao": "aceitar max(CAP) observado como capacidade provisória para testes; substituir por dado oficial depois",
        },
        "recursos_laboratorio": {
            "turmas_com_laboratorio": lab_classes,
            "encontros_com_laboratorio": lab_meetings,
            "turmas_com_recurso_desconhecido": unknown_classes,
            "decisao": "tratar L... como laboratório em prédio separado e aplicar compatibilidade estrita por encontro; confirmar os casos desconhecidos",
        },
    }
    (DATA / "decisoes_qualidade_2025.json").write_text(json.dumps(decisions, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Decisões de qualidade da instância CC/SI 2025",
        "",
        "## 1. Encontros sem sala",
        "",
        f"Foram encontradas **{room_review['turma_id'].nunique()} turmas** com pelo menos um encontro sem sala.",
        "A sala não foi inventada. O CSV de revisão registra candidatos históricos por código, mas a decisão é manter a sala nula até confirmação.",
        "",
        "Arquivo: `revisao_salas_2025.csv`.",
        "",
        "## 2. Turmas sem setor",
        "",
        f"Foram encontradas **{len(sector_review)} turmas** sem setor.",
        "Disciplinas externas não recebem setor do IC. Disciplinas `TCC` de optativa ou ementa variável ficam sem restrição de setor nesta versão.",
        "",
        "Arquivo: `revisao_setores_2025.csv`.",
        "",
        "## 3. Conflitos curriculares",
        "",
        f"Foram encontrados **{len(curriculum_review)} grupos de conflito**; **{int(curriculum_review['confirmado_na_grade'].sum()) if len(curriculum_review) else 0}** foram confirmados nas grades oficiais.",
        "Os conflitos confirmados permanecem restrições hard. As confirmações principais são CC-P5 (`TCC00226`/`TCC00312`) e SI-P1 (`TCC00332`/`TCC00354`).",
        "",
        "Arquivo: `validacao_curricular_2025.csv`.",
        "",
        "## 4. Capacidade das salas",
        "",
        "A capacidade foi estimada por `max(CAP)` das turmas observadas em cada sala.",
        "Essa regra é aceita para testes e permite ativar H10/O4, mas não é uma confirmação física: uma sala pode ter recebido apenas turmas menores.",
        "A capacidade oficial deve substituir `capacidade_estimada` quando for obtida.",
        "",
        "Arquivo: `salas_2025.csv`.",
        "",
        "## 5. Recursos e laboratórios",
        "",
        f"Foram inferidas **{lab_classes} turmas** com pelo menos um encontro de laboratório e **{lab_meetings} encontros** com exigência de laboratório.",
        f"Há **{unknown_classes} turma(s)** com recurso desconhecido; ela(s) não recebe(m) exigência inventada.",
        "O prefixo `L` identifica laboratório e prédio separado. A compatibilidade é estrita no protótipo: encontros de laboratório vão para `L...` e encontros comuns não são enviados para `L...`.",
        "",
        "Arquivos: `recursos_turmas_2025.csv` e `recursos_encontros_2025.csv`.",
        "",
        "## Estado após as decisões",
        "",
        "- Não preencher salas ausentes automaticamente.",
        "- Não impor setor a externas e optativas/ementas variáveis.",
        "- Manter conflitos curriculares confirmados como hard.",
        "- Usar capacidade estimada apenas como parâmetro provisório.",
        "- Confirmar os recursos desconhecidos e substituir a inferência histórica por cadastro oficial quando disponível.",
    ]
    (DATA / "decisoes_qualidade_2025.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(DATA / "decisoes_qualidade_2025.md")


if __name__ == "__main__":
    main()
