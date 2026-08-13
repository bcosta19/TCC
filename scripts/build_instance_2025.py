"""Gera uma instância JSON inicial para CC/SI a partir dos CSVs processados."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.eval.rooms import room_metadata
from src.eval.resources import infer_lab_requirement, lab_evidence_by_code, resources_from_requirement
from src.eval.preferences import load_preference_lookup


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "processados"
OUT = DATA / "instancia_2025_cc_si.json"
PREFERENCE_WORKBOOK = ROOT / "webscrap" / "preferencias_professores.xlsx"
TEACHER_SECTOR_CSV = DATA / "professores_por_setor_2025.csv"
TEACHER_DOMAIN_CSV = DATA / "dominios_professores_turmas_2025.csv"
H12_AUDIT_CSV = DATA / "auditoria_h12_professores_2025.csv"


def write_teacher_sector_domains(classes: list[dict]) -> None:
    """Gera domínios provisórios professor-turma a partir do histórico por setor."""
    stats: dict[str, dict[str, dict]] = defaultdict(
        lambda: defaultdict(lambda: {
            "turmas": 0,
            "obrigatorias": 0,
            "semestres": set(),
            "codigos": set(),
            "disciplinas": set(),
        })
    )
    for item in classes:
        if item.get("origem") != "IC" or not item.get("setor") or not item.get("professor"):
            continue
        record = stats[item["setor"]][item["professor"]]
        record["turmas"] += 1
        record["obrigatorias"] += int(bool(item.get("obrigatoria")))
        record["semestres"].add(str(item.get("semestre", "")))
        record["codigos"].add(str(item.get("codigo", "")))
        record["disciplinas"].add(str(item.get("disciplina", "")))

    domains = {
        sector: sorted(professors)
        for sector, professors in stats.items()
    }

    sector_rows = []
    for sector, professors in sorted(stats.items()):
        for professor, record in sorted(professors.items()):
            sector_rows.append({
                "setor": sector,
                "professor": professor,
                "turmas_2025": record["turmas"],
                "obrigatorias_2025": record["obrigatorias"],
                "semestres": ";".join(sorted(record["semestres"])),
                "codigos": ";".join(sorted(record["codigos"])),
                "disciplinas": ";".join(sorted(record["disciplinas"])),
                "fonte": "alocacoes observadas na planilha QH 2025; proxy nao oficial",
            })
    pd.DataFrame(sector_rows).to_csv(TEACHER_SECTOR_CSV, index=False)

    domain_rows = []
    for item in classes:
        if item.get("origem") != "IC":
            continue
        sector = item.get("setor")
        current = item.get("professor")
        domain = list(domains.get(sector, [])) if sector else []
        if current and current not in domain:
            domain.append(current)
        domain = sorted({value for value in domain if value})
        if domain:
            item["professores_habilitados"] = domain
            item["professores_habilitados_fonte"] = (
                "proxy historico: professores alocados no mesmo setor na planilha QH 2025"
            )
        elif current:
            item["professores_habilitados"] = [current]
            item["professores_habilitados_fonte"] = (
                "sem setor historico disponivel; mantido professor observado"
            )

        domain_rows.append({
            "turma_id": item.get("id", ""),
            "semestre": item.get("semestre", ""),
            "codigo": item.get("codigo", ""),
            "disciplina": item.get("disciplina", ""),
            "setor": sector or "",
            "professor_atual": current or "",
            "candidatos": ";".join(domain),
            "qtd_candidatos": len(domain),
            "obrigatoria": bool(item.get("obrigatoria")),
            "movel_professor": len(domain) > 1,
            "fonte": item.get("professores_habilitados_fonte", ""),
        })
    pd.DataFrame(domain_rows).to_csv(TEACHER_DOMAIN_CSV, index=False)


def write_h12_teacher_audit(classes: list[dict], teachers: list[str], min_obligatory: int) -> None:
    """Compara o universo H12 atual com a aba CH Docente."""
    counts: dict[str, int] = defaultdict(int)
    for item in classes:
        if item.get("origem") == "IC" and item.get("professor") and item.get("obrigatoria"):
            counts[str(item["professor"])] += 1

    rows = []
    carga_path = DATA / "carga_docente_2025.csv"
    seen_aliases = set()
    if carga_path.exists():
        carga = pd.read_csv(carga_path, dtype=str).fillna("")
        for _, row in carga.iterrows():
            alias = str(row.get("Nome Planilha", "")).strip()
            if alias:
                seen_aliases.add(alias)
            assigned = counts.get(alias, 0)
            rows.append({
                "docente": row.get("Docente", ""),
                "nome_planilha": alias,
                "incluido_universo_h12_atual": alias in teachers,
                "obrigatorias_instancia_atual": assigned,
                "minimo_h12_provisorio": min_obligatory,
                "abaixo_minimo_se_incluido": assigned < min_obligatory,
                "ch_ob_2025_1": row.get("CH_OB", ""),
                "ch_ob_2025_2": row.get("CH_OB.1", ""),
                "ch_anual": row.get("CH Anual", ""),
                "ch_ref_min": row.get("CH REF MIN", ""),
                "cargo_afastamento": row.get("a. Cargo / Afast.", ""),
                "cred_pos": row.get("b. Cred. Pós", ""),
                "outros_abatimentos": row.get("z. Saúde / 20H / Subst. / Outros", ""),
                "observacao": "universo H12 a validar com orientador",
            })

    for teacher in sorted(set(teachers) - seen_aliases):
        assigned = counts.get(teacher, 0)
        rows.append({
            "docente": "",
            "nome_planilha": teacher,
            "incluido_universo_h12_atual": True,
            "obrigatorias_instancia_atual": assigned,
            "minimo_h12_provisorio": min_obligatory,
            "abaixo_minimo_se_incluido": assigned < min_obligatory,
            "ch_ob_2025_1": "",
            "ch_ob_2025_2": "",
            "ch_anual": "",
            "ch_ref_min": "",
            "cargo_afastamento": "",
            "cred_pos": "",
            "outros_abatimentos": "",
            "observacao": "professor aparece na instancia, mas nao foi pareado na aba CH Docente",
        })
    pd.DataFrame(rows).to_csv(H12_AUDIT_CSV, index=False)


def main() -> None:
    turmas = pd.read_csv(DATA / "turmas_2025.csv", dtype=str).fillna("")
    horarios = pd.read_csv(DATA / "horarios_2025.csv", dtype=str).fillna("")
    keep = turmas["curso"].isin({"31", "83"}) | (
        turmas["curso"].eq("") & turmas["periodo"].str.startswith(("CC-", "SI-"))
    )
    turmas = turmas[keep].copy()
    horarios = horarios[horarios["turma_id"].isin(set(turmas["id"]))].copy()

    evidence = lab_evidence_by_code(horarios.to_dict("records"))
    encontros = {}
    for turma_id, group in horarios.groupby("turma_id"):
        code = str(group["codigo"].iloc[0])
        values = []
        for _, meeting in group.iterrows():
            required_lab, source = infer_lab_requirement(meeting["sala"], code, evidence)
            values.append({
                "dia": meeting["dia"],
                "inicio": meeting["inicio"],
                "fim": meeting["fim"],
                "sala": meeting["sala"],
                "requer_laboratorio": required_lab,
                "recursos_requeridos": resources_from_requirement(required_lab),
                "recurso_fonte": source,
            })
        encontros[turma_id] = values

    def class_resource_summary(meetings: list[dict]) -> tuple[bool | None, list[str], list[str]]:
        requirements = [meeting.get("requer_laboratorio") for meeting in meetings]
        sources = sorted({str(meeting.get("recurso_fonte", "")) for meeting in meetings if meeting.get("recurso_fonte")})
        if any(value is True for value in requirements):
            return True, ["laboratorio"], sources
        if requirements and all(value is False for value in requirements):
            return False, [], sources
        return None, [], sources

    def is_obligatory(row: pd.Series) -> bool:
        value = pd.to_numeric(pd.Series([row.get("ch_ob", "")]), errors="coerce").iloc[0]
        return bool(pd.notna(value) and value > 0)

    classes = []
    for _, row in turmas.iterrows():
        class_meetings = encontros.get(row["id"], [])
        requires_lab, class_resources, resource_sources = class_resource_summary(class_meetings)
        classes.append({
            "id": row["id"],
            "semestre": row["semestre"],
            "curso": row["curso"] or ("SI" if row["periodo"].startswith("SI-") else "CC"),
            "periodo": row["periodo"],
            "codigo": row["codigo"],
            "disciplina": row["disciplina"],
            "turma": row["turma"],
            "origem": "IC" if row["codigo"].startswith("TCC") else "externa",
            "setor": row["setor"] or None,
            "professor": row["alocacao"] or None,
            "capacidade_turma": int(float(row["capacidade"])) if row["capacidade"] else None,
            "obrigatoria": is_obligatory(row),
            "exige_laboratorio": requires_lab,
            "recursos_requeridos": class_resources,
            "recurso_fontes": resource_sources,
            "horario_fixo": True,
            "sala_fixa": False,
            "encontros": class_meetings,
        })

    rooms = sorted({e["sala"] for values in encontros.values() for e in values if e["sala"]})
    capacity_by_room = {}
    linked = horarios.merge(turmas[["id", "capacidade"]], left_on="turma_id", right_on="id", how="left")
    linked["capacidade_num"] = pd.to_numeric(linked["capacidade"], errors="coerce")
    for room, group in linked[linked["sala"].ne("")].groupby("sala"):
        values = group["capacidade_num"].dropna()
        if not values.empty:
            capacity_by_room[room] = int(values.max())
    teachers = sorted({
        c["professor"] for c in classes
        if c["professor"] and c["origem"] == "IC"
    })
    min_obligatory = 3
    write_teacher_sector_domains(classes)
    write_h12_teacher_audit(classes, teachers, min_obligatory)
    sectors = sorted({c["setor"] for c in classes if c["setor"]})
    preferences, preference_table = load_preference_lookup(
        PREFERENCE_WORKBOOK, DATA / "carga_docente_2025.csv", teachers
    )
    for item in classes:
        item["preferencias_professores"] = {
            teacher: float(preferences.get(item["codigo"], {}).get(teacher, 0.0))
            for teacher in teachers
        }
    groups: dict[str, dict] = {}
    for c in classes:
        if not c["periodo"]:
            continue
        key = f"{c['semestre']}|{c['curso']}|{c['periodo']}"
        groups.setdefault(key, {"semestre": c["semestre"], "curso": c["curso"], "periodo": c["periodo"], "disciplinas": []})
        if c["codigo"] not in groups[key]["disciplinas"]:
            groups[key]["disciplinas"].append(c["codigo"])

    instance = {
        "schema_version": "0.1",
        "source": "dados/brutos/QH-2025-1-2.xlsx",
        "profile": "cc_si",
        "min_obrigatorias_ano": min_obligatory,
        "prioridades_professores": {teacher: 1.0 for teacher in teachers},
        "prioridade_fonte": "neutra para experimento não oficial; substituir pela lista do orientador",
        "preferencia_fonte": "frequência histórica normalizada de webscrap/preferencias_professores.xlsx",
        "dominio_professores_fonte": (
            "professores alocados no mesmo setor na planilha QH 2025; proxy não oficial"
        ),
        "universo_h12_fonte": (
            "professores com alocação IC no recorte CC/SI; conferir auditoria_h12_professores_2025.csv"
        ),
        "notes": [
            "Instância inicial baseada na solução real da planilha.",
            "Horários são fixos nesta versão.",
            "O prefixo L identifica laboratório.",
            "A exigência de laboratório é inferida por encontro a partir do histórico do código e da sala observada.",
            "A capacidade ainda é estimada; recursos de laboratório são uma inferência provisória.",
            "Professores são nomes abreviados conforme a coluna ALOCAÇÃO da planilha.",
            "Domínios de professor por turma usam alocações observadas em 2025 no mesmo setor; isso é proxy não oficial.",
            "A classificação obrigatória/optativa usa CH_OB; deve ser revisada com a grade curricular.",
        ],
        "rooms": [
            {
                **room_metadata(room),
                "capacity": None,
                "capacidade_estimada": capacity_by_room.get(room),
                "capacidade_fonte": "max(CAP) das turmas observadas na sala",
                "resources": ["laboratorio"] if room_metadata(room)["laboratorio"] else [],
            }
            for room in rooms
        ],
        "teachers": [{"name": teacher} for teacher in teachers],
        "sectors": sectors,
        "curriculum_groups": list(groups.values()),
        "classes": classes,
    }
    OUT.write_text(json.dumps(instance, ensure_ascii=False, indent=2), encoding="utf-8")
    resource_class_rows = []
    resource_meeting_rows = []
    for item in classes:
        resource_class_rows.append({
            "turma_id": item["id"],
            "semestre": item["semestre"],
            "codigo": item["codigo"],
            "disciplina": item["disciplina"],
            "periodo": item["periodo"],
            "exige_laboratorio": item["exige_laboratorio"],
            "recursos_requeridos": ",".join(item["recursos_requeridos"]),
            "fontes": ";".join(item["recurso_fontes"]),
        })
        for meeting in item["encontros"]:
            resource_meeting_rows.append({
                "turma_id": item["id"],
                "semestre": item["semestre"],
                "codigo": item["codigo"],
                "disciplina": item["disciplina"],
                "dia": meeting["dia"],
                "inicio": meeting["inicio"],
                "fim": meeting["fim"],
                "sala_observada": meeting["sala"],
                "requer_laboratorio": meeting["requer_laboratorio"],
                "recursos_requeridos": ",".join(meeting["recursos_requeridos"] or []),
                "fonte": meeting["recurso_fonte"],
            })
    pd.DataFrame(resource_class_rows).to_csv(DATA / "recursos_turmas_2025.csv", index=False)
    pd.DataFrame(resource_meeting_rows).to_csv(DATA / "recursos_encontros_2025.csv", index=False)
    room_table = pd.DataFrame([room_metadata(room) for room in rooms])
    room_table["capacidade_estimada"] = room_table["id"].map(capacity_by_room)
    room_table["capacidade_fonte"] = "max(CAP) das turmas observadas na sala"
    room_table["recursos"] = room_table["laboratorio"].map(lambda x: "laboratorio" if x else "")
    room_table.to_csv(DATA / "salas_2025.csv", index=False)
    preference_table.to_csv(DATA / "preferencias_2025.csv", index=False)
    print(f"{OUT}: {len(classes)} turmas, {len(rooms)} salas, {len(teachers)} professores")


if __name__ == "__main__":
    main()
