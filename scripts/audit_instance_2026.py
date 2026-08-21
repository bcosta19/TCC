"""Audita a extração dos quadros de horários de 2026.

O relatório descreve dados e candidatos a inconsistência. Ele não transforma
essas verificações em resultados experimentais nem decide quais turmas
pertencem às grades de CC e SI.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "processados"
OUT_JSON = DATA / "auditoria_2026.json"
OUT_MD = DATA / "auditoria_2026.md"
CONFLICTS_CSV = DATA / "conflitos_candidatos_2026.csv"
REVIEW_CSV = DATA / "revisao_turmas_2026.csv"
ROOMS_CSV = DATA / "salas_2026.csv"


def minute(value: str) -> int:
    hour, minutes = str(value).split(":")
    return int(hour) * 60 + int(minutes)


def intervals_overlap(start_a: str, end_a: str, start_b: str, end_b: str) -> bool:
    return max(minute(start_a), minute(start_b)) < min(minute(end_a), minute(end_b))


def meeting_pattern(frame: pd.DataFrame) -> tuple[tuple[str, str, str], ...]:
    return tuple(sorted(zip(frame["dia"], frame["inicio"], frame["fim"])))


def room_pattern(frame: pd.DataFrame) -> tuple[tuple[str, str, str, str], ...]:
    return tuple(sorted(zip(frame["dia"], frame["inicio"], frame["fim"], frame["sala"])))


def candidate_conflicts(classes: pd.DataFrame, meetings: pd.DataFrame) -> pd.DataFrame:
    class_lookup = classes.set_index("id")
    valid_ids = set(classes.loc[classes["status"].ne("cancelada"), "id"])
    joined = meetings[meetings["turma_id"].isin(valid_ids)].copy()
    joined["professores"] = joined["turma_id"].map(class_lookup["professores"]).fillna("")
    joined["disciplina"] = joined["turma_id"].map(class_lookup["disciplina"]).fillna("")
    joined["status"] = joined["turma_id"].map(class_lookup["status"]).fillna("")

    rows = []

    def append_pairs(frame: pd.DataFrame, group_keys: list[str], kind: str, resource: str) -> None:
        for key, group in frame.groupby(group_keys, dropna=False):
            records = list(group.sort_values(["inicio", "fim", "turma_id"]).to_dict("records"))
            for index, first in enumerate(records):
                for second in records[index + 1 :]:
                    if first["turma_id"] == second["turma_id"]:
                        continue
                    if not intervals_overlap(first["inicio"], first["fim"], second["inicio"], second["fim"]):
                        continue
                    same_code = bool(first["codigo"] and first["codigo"] == second["codigo"])
                    rows.append(
                        {
                            "tipo": kind,
                            "classificacao": "possivel_turma_agrupada" if kind == "sala" and same_code else f"choque_{kind}_candidato",
                            "semestre": first["semestre"],
                            "dia": first["dia"],
                            resource: key[-1] if isinstance(key, tuple) else key,
                            "turma_id_a": first["turma_id"],
                            "codigo_a": first["codigo"],
                            "disciplina_a": first["disciplina"],
                            "inicio_a": first["inicio"],
                            "fim_a": first["fim"],
                            "turma_id_b": second["turma_id"],
                            "codigo_b": second["codigo"],
                            "disciplina_b": second["disciplina"],
                            "inicio_b": second["inicio"],
                            "fim_b": second["fim"],
                        }
                    )

    occupied_rooms = joined[joined["sala"].ne("")]
    append_pairs(occupied_rooms, ["semestre", "dia", "sala"], "sala", "sala")

    exploded = joined.assign(professor=joined["professores"].str.split(";")).explode("professor")
    exploded["professor"] = exploded["professor"].fillna("").str.strip()
    exploded = exploded[exploded["professor"].ne("")]
    append_pairs(exploded, ["semestre", "dia", "professor"], "professor", "professor")

    columns = [
        "tipo", "classificacao", "semestre", "dia", "sala", "professor",
        "turma_id_a", "codigo_a", "disciplina_a", "inicio_a", "fim_a",
        "turma_id_b", "codigo_b", "disciplina_b", "inicio_b", "fim_b",
    ]
    result = pd.DataFrame(rows)
    for column in columns:
        if column not in result:
            result[column] = ""
    return result[columns].fillna("")


def curricular_proxy(classes: pd.DataFrame) -> dict:
    path = DATA / "turmas_2025.csv"
    if not path.exists():
        return {
            "fonte_disponivel": False,
            "observacao": "turmas_2025.csv não encontrado",
        }
    historical = pd.read_csv(path, dtype=str).fillna("")
    target = historical[historical["curso"].isin({"31", "83"}) | (
        historical["curso"].eq("") & historical["periodo"].str.startswith(("CC-", "SI-"))
    )]
    mapped_codes = set(target["codigo"])
    coded = classes[classes["codigo"].ne("")]
    unmapped = sorted(set(coded["codigo"]) - mapped_codes)
    return {
        "fonte_disponivel": True,
        "fonte": "dados/processados/turmas_2025.csv",
        "natureza": "proxy histórico; não substitui a classificação curricular de 2026",
        "codigos_2026_com_correspondencia": len(set(coded["codigo"]) & mapped_codes),
        "codigos_2026_sem_correspondencia": unmapped,
        "turmas_2026_com_codigo_correspondente": int(coded["codigo"].isin(mapped_codes).sum()),
        "turmas_2026_sem_codigo_correspondente": int((~coded["codigo"].isin(mapped_codes)).sum()),
    }


def annual_patterns(classes: pd.DataFrame, meetings: pd.DataFrame) -> dict:
    coded = classes[classes["codigo"].ne("")].copy()
    per_semester = {
        semester: {(row.codigo, row.turma): row.id for row in group.itertuples()}
        for semester, group in coded.groupby("semestre")
    }
    first = per_semester.get("2026-1", {})
    second = per_semester.get("2026-2", {})
    common = sorted(set(first) & set(second))
    by_class = {class_id: group for class_id, group in meetings.groupby("turma_id")}
    same_time = 0
    same_time_room = 0
    for key in common:
        first_meetings = by_class.get(first[key], pd.DataFrame(columns=meetings.columns))
        second_meetings = by_class.get(second[key], pd.DataFrame(columns=meetings.columns))
        if meeting_pattern(first_meetings) == meeting_pattern(second_meetings):
            same_time += 1
        if room_pattern(first_meetings) == room_pattern(second_meetings):
            same_time_room += 1
    return {
        "chaves_codigo_turma_comuns": len(common),
        "mesmo_padrao_dias_horarios": same_time,
        "padrao_dias_horarios_diferente": len(common) - same_time,
        "mesmo_padrao_dias_horarios_salas": same_time_room,
        "observacao": "comparação descritiva das alocações observadas; não define horários fixos",
    }


def format_list(values: list[str], empty: str = "nenhum") -> str:
    return ", ".join(f"`{value}`" for value in values) if values else empty


def main() -> None:
    classes = pd.read_csv(DATA / "turmas_2026.csv", dtype=str).fillna("")
    meetings = pd.read_csv(DATA / "horarios_2026.csv", dtype=str).fillna("")
    teachers = pd.read_csv(DATA / "normalizacao_docentes_2026.csv", dtype=str).fillna("")

    duplicate_ids = sorted(classes.loc[classes["id"].duplicated(keep=False), "id"].unique())
    missing_meetings = sorted(set(classes["id"]) - set(meetings["turma_id"]))
    orphan_meetings = sorted(set(meetings["turma_id"]) - set(classes["id"]))
    invalid_time = meetings[
        ~meetings["inicio"].str.match(r"^\d{2}:\d{2}$")
        | ~meetings["fim"].str.match(r"^\d{2}:\d{2}$")
    ]
    reversed_time = meetings[
        meetings.apply(lambda row: minute(row["inicio"]) >= minute(row["fim"]), axis=1)
    ] if invalid_time.empty else pd.DataFrame()
    no_room = meetings[meetings["sala"].eq("")]
    no_code = classes[classes["codigo"].eq("")]
    multiple_teachers = classes[pd.to_numeric(classes["professores_qtd"], errors="coerce").fillna(0).gt(1)]
    incomplete = classes[classes["status"].eq("incompleta")]
    cancelled = classes[classes["status"].eq("cancelada")]
    unverified_teachers = teachers[teachers["verificada"].str.lower().ne("true")]

    conflicts = candidate_conflicts(classes, meetings)
    conflicts.to_csv(CONFLICTS_CSV, index=False)

    review = classes[
        classes["status"].ne("ativa")
        | classes["pendencias"].ne("")
        | classes["codigo"].eq("")
    ].copy()
    review.to_csv(REVIEW_CSV, index=False)

    room_rows = []
    for room in sorted(value for value in meetings["sala"].unique() if value):
        is_lab = room.upper().startswith("L")
        room_rows.append(
            {
                "id": room,
                "laboratorio_inferido": is_lab,
                "recursos_inferidos": "laboratorio" if is_lab else "",
                "capacidade": "",
                "fonte_tipo": "prefixo L no quadro observado" if is_lab else "sem classificação oficial de recurso",
                "capacidade_fonte": "não disponível nos PDFs",
            }
        )
    pd.DataFrame(room_rows).to_csv(ROOMS_CSV, index=False)

    patterns = annual_patterns(classes, meetings)
    proxy = curricular_proxy(classes)
    official_path = DATA / "classificacao_curricular_2026.csv"
    official = pd.read_csv(official_path, dtype=str).fillna("") if official_path.exists() else pd.DataFrame()
    links_path = DATA / "vagas_turmas_2026.csv"
    links = pd.read_csv(links_path, dtype=str).fillna("") if links_path.exists() else pd.DataFrame()
    room_conflicts = conflicts[conflicts["tipo"].eq("sala")]
    teacher_conflicts = conflicts[conflicts["tipo"].eq("professor")]

    result = {
        "escopo": "extração integral dos PDFs de 2026; o recorte CC/SI é auditado separadamente",
        "turmas": int(len(classes)),
        "encontros": int(len(meetings)),
        "salas_observadas": len(room_rows),
        "ids_duplicados": duplicate_ids,
        "turmas_sem_encontro": missing_meetings,
        "encontros_sem_turma": orphan_meetings,
        "horarios_invalidos": int(len(invalid_time)),
        "horarios_com_fim_nao_posterior": int(len(reversed_time)),
        "encontros_sem_sala": int(len(no_room)),
        "turmas_sem_codigo": int(len(no_code)),
        "turmas_com_multiplos_professores": int(len(multiple_teachers)),
        "turmas_incompletas": incomplete["id"].tolist(),
        "turmas_canceladas": cancelled["id"].tolist(),
        "normalizacoes_docentes_nao_verificadas": unverified_teachers["nome_original"].tolist(),
        "candidatos_conflito_sala": int(len(room_conflicts)),
        "candidatos_conflito_professor": int(len(teacher_conflicts)),
        "padroes_anuais": patterns,
        "classificacao_curricular": {
            "fonte_disponivel": not official.empty,
            "ofertas_nos_curriculos": int(official["nos_curriculos"].str.lower().eq("true").sum()) if not official.empty else 0,
            "vinculos_pdf_web": int(len(links)),
            "fonte": "dados/grade_cc.md; dados/grade_si.md; páginas públicas das turmas",
        },
        "classificacao_curricular_proxy": proxy,
        "h12": {
            "calculavel": False,
            "motivos": [
                "o universo oficial de docentes submetidos à regra não está definido",
                "há alocações múltiplas que exigem regra explícita de contagem",
            ],
        },
    }
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Auditoria dos quadros de horários de 2026",
        "",
        "> Esta é uma auditoria de extração e qualidade dos dados. Os candidatos a",
        "> conflito abaixo não são resultados experimentais nem conflitos confirmados.",
        "",
        "## Escopo",
        "",
        "- Turmas/ofertas extraídas: **{}**.".format(len(classes)),
        "- Encontros semanais extraídos: **{}**.".format(len(meetings)),
        "- Salas observadas: **{}**.".format(len(room_rows)),
        "- Registros sem código: **{}**.".format(len(no_code)),
        "- Registros com múltiplos professores: **{}**.".format(len(multiple_teachers)),
        "- Registros incompletos: **{}**.".format(len(incomplete)),
        "- Registros cancelados: **{}**.".format(len(cancelled)),
        "",
        "Os dados abrangem ofertas regulares, pós-graduação, graduação/pós e",
        "disciplinas de serviço. Os PDFs não fornecem uma classificação completa de",
        "pertinência às grades de CC e SI.",
        "",
        "## Integridade estrutural",
        "",
        f"- IDs duplicados: **{len(duplicate_ids)}**.",
        f"- Turmas sem encontro: **{len(missing_meetings)}**.",
        f"- Encontros órfãos: **{len(orphan_meetings)}**.",
        f"- Horários inválidos: **{len(invalid_time)}**.",
        f"- Horários com fim não posterior ao início: **{len(reversed_time)}**.",
        f"- Encontros sem sala: **{len(no_room)}**.",
        "",
        "### Registros incompletos ou cancelados",
        "",
    ]
    for row in classes[classes["status"].ne("ativa")].itertuples():
        lines.append(f"- `{row.id}` — {row.disciplina}: **{row.status}** ({row.pendencias or 'sem pendência registrada'}).")

    lines.extend([
        "",
        "## Normalização de docentes",
        "",
        f"- Grafias distintas encontradas: **{len(teachers)}**.",
        f"- Correspondências não verificadas: **{len(unverified_teachers)}**: "
        + format_list(unverified_teachers["nome_original"].tolist()) + ".",
        "- A normalização usa nomes e aliases de `carga_docente_2025.csv`; casos sem",
        "  correspondência única são preservados para revisão manual.",
        "",
        "## Candidatos a sobreposição",
        "",
        f"- Pares com sobreposição de sala: **{len(room_conflicts)}**.",
        f"- Pares com sobreposição de professor: **{len(teacher_conflicts)}**.",
        "",
    ])
    if conflicts.empty:
        lines.append("Nenhum candidato encontrado.")
    else:
        for row in conflicts.itertuples():
            resource = row.sala if row.tipo == "sala" else row.professor
            lines.append(
                f"- **{row.semestre}, {row.dia}, {resource}**: `{row.turma_id_a}` "
                f"({row.inicio_a}–{row.fim_a}) × `{row.turma_id_b}` "
                f"({row.inicio_b}–{row.fim_b}); classificação: `{row.classificacao}`."
            )

    lines.extend([
        "",
        "Os detalhes estruturados estão em `conflitos_candidatos_2026.csv`. Casos da",
        "mesma disciplina podem representar turmas agrupadas em vez de choque real.",
        "",
        "## Comparação entre os semestres",
        "",
        f"- Chaves código+turma presentes nos dois semestres: **{patterns['chaves_codigo_turma_comuns']}**.",
        f"- Mesmo padrão de dias e horários: **{patterns['mesmo_padrao_dias_horarios']}**.",
        f"- Padrão de dias ou horários diferente: **{patterns['padrao_dias_horarios_diferente']}**.",
        f"- Mesmo padrão incluindo salas: **{patterns['mesmo_padrao_dias_horarios_salas']}**.",
        "",
        "Essa comparação descreve as alocações observadas; não transforma horários ou",
        "salas históricas em parâmetros fixos do solver.",
        "",
        "## Cobertura curricular CC/SI",
        "",
    ])
    if not official.empty and not links.empty:
        lines.extend([
            f"- Linhas dos PDFs classificadas por código nas grades: **{int(official['nos_curriculos'].str.lower().eq('true').sum())}**.",
            f"- Vínculos confirmados com turmas retornadas pelas buscas públicas de CC/SI: **{len(links)}**.",
            "- O recorte consolidado, incluindo vagas e turmas compartilhadas, está em",
            "  `auditoria_2026_cc_si.md`.",
            "",
            "`classificacao_curricular_proxy_2026.csv` permanece apenas como comparação",
            "histórica com 2025; as grades versionadas são a fonte curricular principal.",
        ])
    else:
        lines.append("- Execute os scripts de currículo e vínculo com as páginas públicas.")

    lines.extend([
        "",
        "## Itens ainda não calculáveis no recorte CC/SI",
        "",
        "- H12: faltam o universo de docentes e a regra para alocações múltiplas.",
        "- Capacidade e desperdício: as vagas estão disponíveis, mas faltam capacidades físicas das salas.",
        "- Quatro turmas ainda não possuem grupo de período nas grades Markdown.",
        "- Setores, prioridade e habilitação docente não constam nos PDFs nem nas grades.",
        "",
        "## Arquivos de revisão",
        "",
        "- `revisao_turmas_2026.csv` — registros incompletos, sem código, com múltiplos",
        "  professores ou com normalização pendente.",
        "- `normalizacao_docentes_2026.csv` — vínculo de cada grafia com o alias usado",
        "  nos dados processados.",
        "- `salas_2026.csv` — salas observadas, sem capacidades inventadas.",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT_MD)


if __name__ == "__main__":
    main()
