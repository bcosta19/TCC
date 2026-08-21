"""Gera tabelas de revisão com evidências e campos vazios para validação humana.

Cria os seguintes arquivos de auditoria e revisão para 2026:
- revisao_classificacao_curricular_2026.csv (TCC00368 e TCC00371)
- universo_h12_2026.csv (Docentes candidatos para H12)
- politica_cotutoria_2026.csv (Tratamento das duas cotutorias)
- cadastro_salas_2026.csv (22 salas com capacidade mínima observada)
- revisao_recursos_disciplinas_2026.csv (Uso observado de salas/labs)
- revisao_horarios_fixos_2026.csv (Horários observados vs parâmetros fixos)
- revisao_setores_2026.csv (Setores históricos vs oficiais)
- revisao_habilitacao_docente_2026.csv (Habilitação docente por disciplina)
- revisao_prioridades_docentes_2026.csv (Prioridade de atendimento docente)
- revisao_turmas_externas_2026.csv (Disciplinas externas e seções alternativas)
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "processados"
WEBSCRAP = ROOT / "webscrap"


def build_curricular_review() -> None:
    rows = [
        {
            "turma_id": "2026-1-TCC00368-A1",
            "codigo": "TCC00368",
            "nome_pdf": "PESQUISA OPERACIONAL PARA SISTEMAS DE INFORMAÇÃO",
            "nome_sistema": "PESQUISA OPERACIONAL PARA SISTEMAS DE INFORMAÇÃO",
            "curriculos_retornados_pela_busca": "SI",
            "periodo_grade_markdown": "",
            "tipo_grade_markdown": "",
            "historico_2025": "SI-P7 (WEB AVANC. / PESQUISA OPERACIONAL PARA SI)",
            "evidencias": (
                "Código TCC00368 retornado na busca do currículo de SI com vagas para SI (59) e CC (2); "
                "ausente das grades Markdown versionadas; no QH 2025 aparecia vinculado a SI-P7"
            ),
            "fontes": "webscrap/turmas_2026_raw.csv; dados/brutos/QH-2026-1.pdf; dados/grade_si.md; dados/processados/turmas_2025.csv",
            "decisao": "",
        },
        {
            "turma_id": "2026-2-TCC00368-A1",
            "codigo": "TCC00368",
            "nome_pdf": "P.O. PARA S.I. (WEB AVANC.)",
            "nome_sistema": "PESQUISA OPERACIONAL PARA SISTEMAS DE INFORMAÇÃO",
            "curriculos_retornados_pela_busca": "SI",
            "periodo_grade_markdown": "",
            "tipo_grade_markdown": "",
            "historico_2025": "SI-P7 (P.O. PARA S.I. (WEB AVANC.))",
            "evidencias": (
                "Código TCC00368 retornado na busca do currículo de SI com vagas para SI (61); "
                "ausente das grades Markdown versionadas; no QH 2025 aparecia vinculado a SI-P7"
            ),
            "fontes": "webscrap/turmas_2026_raw.csv; dados/brutos/QH-2026-2.pdf; dados/grade_si.md; dados/processados/turmas_2025.csv",
            "decisao": "",
        },
        {
            "turma_id": "2026-1-TCC00371-A1",
            "codigo": "TCC00371",
            "nome_pdf": "ÉTICA EM INT. ARTIFICIAL E CIÊNCIA DE DADOS",
            "nome_sistema": "ÉTICA EM INTELIGÊNCIA ARTIFICIAL E CIÊNCIA DE DADOS",
            "curriculos_retornados_pela_busca": "CC",
            "periodo_grade_markdown": "",
            "tipo_grade_markdown": "",
            "historico_2025": "não ofertada em 2025",
            "evidencias": (
                "Código TCC00371 retornado na busca do currículo de CC com vagas para CC (10) e IA/CD (20); "
                "ausente das grades Markdown versionadas"
            ),
            "fontes": "webscrap/turmas_2026_raw.csv; dados/brutos/QH-2026-1.pdf; dados/grade_cc.md",
            "decisao": "",
        },
        {
            "turma_id": "2026-2-TCC00371-A1",
            "codigo": "TCC00371",
            "nome_pdf": "ÉTICA EM INT. ARTIFICIAL E CIÊNCIA DE DADOS",
            "nome_sistema": "ÉTICA EM INTELIGÊNCIA ARTIFICIAL E CIÊNCIA DE DADOS",
            "curriculos_retornados_pela_busca": "CC",
            "periodo_grade_markdown": "",
            "tipo_grade_markdown": "",
            "historico_2025": "não ofertada em 2025",
            "evidencias": (
                "Código TCC00371 retornado na busca do currículo de CC com vagas para CC (10), SI (15) e IA/CD (25); "
                "ausente das grades Markdown versionadas"
            ),
            "fontes": "webscrap/turmas_2026_raw.csv; dados/brutos/QH-2026-2.pdf; dados/grade_cc.md",
            "decisao": "",
        },
    ]
    pd.DataFrame(rows).to_csv(DATA / "revisao_classificacao_curricular_2026.csv", index=False)


def build_h12_universe() -> None:
    classes = pd.read_csv(DATA / "turmas_2026_cc_si.csv", dtype=str).fillna("")
    carga25 = pd.read_csv(DATA / "carga_docente_2025.csv", dtype=str).fillna("")
    norm26 = pd.read_csv(DATA / "normalizacao_docentes_2026.csv", dtype=str).fillna("")

    # Map normalizations
    norm_map = dict(zip(norm26["nome_original"], norm26["nome_normalizado"]))

    # Count obligatory classes in 2026
    obligatory = classes[classes["obrigatoria"].str.lower().eq("true")]
    ob_counts: dict[str, int] = defaultdict(int)
    for row in obligatory.itertuples():
        profs = [p.strip() for p in str(row.professores).split(";") if p.strip()]
        for p in profs:
            ob_counts[p] += 1

    all_observed_2026 = set()
    for row in classes.itertuples():
        profs = [p.strip() for p in str(row.professores).split(";") if p.strip()]
        all_observed_2026.update(profs)

    carga_lookup = {}
    for _, row in carga25.iterrows():
        alias = str(row.get("Nome Planilha", "")).strip()
        docente = str(row.get("Docente", "")).strip()
        if not alias or alias in {"SOMA", "CHECK", "CH AVG", "~ Turmas 4h"}:
            continue
        cargo = str(row.get("Cargo / Afastamento", "")).strip()
        observacao_carga = str(row.get("Observação", "")).strip()
        afastamento = cargo or observacao_carga
        carga_lookup[alias] = {
            "docente_completo": docente,
            "afastamento": afastamento,
        }


    all_names = sorted(all_observed_2026 | set(carga_lookup.keys()))
    rows = []
    for name in all_names:
        in_2026 = name in all_observed_2026
        in_2025 = name in carga_lookup
        docente_completo = carga_lookup.get(name, {}).get("docente_completo", "") or name
        afastamento = carga_lookup.get(name, {}).get("afastamento", "")
        ob_count = ob_counts.get(name, 0)
        obs = []
        if not in_2025:
            obs.append("docente observado em 2026, mas ausente da aba CH Docente de 2025")
        if not in_2026:
            obs.append("presente em 2025, mas sem turmas no recorte CC/SI de 2026")
        if afastamento:
            obs.append(f"afastamento/cargo registrado em 2025: {afastamento}")

        rows.append({
            "docente": docente_completo,
            "nome_normalizado": name,
            "observado_2026": in_2026,
            "presente_carga_2025": in_2025,
            "obrigatorias_2026": ob_count,
            "afastamento_evidenciado": afastamento,
            "incluido_h12": "",
            "observacao": "; ".join(obs) or "sem pendências de cadastro",
            "fonte": "carga_docente_2025.csv; turmas_2026_cc_si.csv",
        })

    pd.DataFrame(rows).sort_values(["observado_2026", "nome_normalizado"], ascending=[False, True]).to_csv(
        DATA / "universo_h12_2026.csv", index=False
    )


def build_cotutoria_policy() -> None:
    rows = [
        {
            "turma_id": "2026-2-TCC00285-A1",
            "professores": "Martinhon;Raquel",
            "politica_h12": "",
            "professor_responsavel": "",
            "observacao": (
                "Alocação dupla observada no PDF; valores permitidos: "
                "integral_para_cada_docente, fracionada, contar_para_um_responsavel, nao_contabilizar_em_h12"
            ),
            "fonte": "dados/brutos/QH-2026-2.pdf; dados/processados/turmas_2026_cc_si.csv",
        },
        {
            "turma_id": "2026-2-TCC00354-A1",
            "professores": "Martinhon;Raquel",
            "politica_h12": "",
            "professor_responsavel": "",
            "observacao": (
                "Alocação dupla observada no PDF; valores permitidos: "
                "integral_para_cada_docente, fracionada, contar_para_um_responsavel, nao_contabilizar_em_h12"
            ),
            "fonte": "dados/brutos/QH-2026-2.pdf; dados/processados/turmas_2026_cc_si.csv",
        },
    ]
    pd.DataFrame(rows).to_csv(DATA / "politica_cotutoria_2026.csv", index=False)


def build_rooms_registry() -> None:
    rooms_df = pd.read_csv(DATA / "salas_2026_cc_si.csv", dtype=str).fillna("")
    rows = []
    for row in rooms_df.itertuples():
        sala = str(row.id)
        is_lab = str(row.laboratorio).lower() == "true"
        min_cap = str(row.capacidade_minima_observada)
        rows.append({
            "sala": sala,
            "laboratorio_observado": is_lab,
            "capacidade_minima_observada": min_cap,
            "capacidade_fisica": "",
            "recursos_oficiais": "",
            "fonte": "salas_2026_cc_si.csv; capacidade mínima observada calculada pelo maior número de vagas das turmas alocadas",
            "validado": "",
        })
    pd.DataFrame(rows).sort_values("sala").to_csv(DATA / "cadastro_salas_2026.csv", index=False)


def build_resources_review() -> None:
    classes = pd.read_csv(DATA / "turmas_2026_cc_si.csv", dtype=str).fillna("")
    meetings = pd.read_csv(DATA / "horarios_2026_cc_si.csv", dtype=str).fillna("")

    h = meetings.merge(classes[["id", "disciplina"]], left_on="turma_id", right_on="id", how="left")
    rows = []
    for (code, disc), group in h.groupby(["codigo", "disciplina"]):
        rooms_used = sorted({r for r in group["sala"] if r})
        used_common = any(not r.startswith("L") for r in rooms_used)
        used_lab = any(r.startswith("L") for r in rooms_used)
        alternated = used_common and used_lab
        rows.append({
            "codigo": code,
            "disciplina": disc,
            "usou_sala_comum": used_common,
            "usou_laboratorio": used_lab,
            "alternou_tipo_de_sala": alternated,
            "salas_observadas": ";".join(rooms_used),
            "requer_laboratorio": "",
            "recursos_requeridos": "",
            "fonte": "horarios_2026_cc_si.csv",
            "validado": "",
        })
    pd.DataFrame(rows).sort_values("codigo").to_csv(
        DATA / "revisao_recursos_disciplinas_2026.csv", index=False
    )


def build_fixed_schedules_review() -> None:
    classes = pd.read_csv(DATA / "turmas_2026_cc_si.csv", dtype=str).fillna("")
    meetings = pd.read_csv(DATA / "horarios_2026_cc_si.csv", dtype=str).fillna("")

    summary = {
        class_id: "; ".join(f"{row.dia} {row.inicio}-{row.fim}" for row in group.itertuples())
        for class_id, group in meetings.groupby("turma_id")
    }
    days_summary = {
        class_id: ";".join(sorted(set(group["dia"])))
        for class_id, group in meetings.groupby("turma_id")
    }

    rows = []
    for row in classes.itertuples():
        origem = str(row.origem)
        is_fixed_candidate = origem == "externa"
        rows.append({
            "turma_id": row.id,
            "semestre": row.semestre,
            "codigo": row.codigo,
            "disciplina": row.disciplina,
            "turma": row.turma,
            "origem": origem,
            "horario_observado": summary.get(row.id, ""),
            "dias_observados": days_summary.get(row.id, ""),
            "horario_fixo": "",
            "fonte": f"{origem.lower()}; turmas_2026_cc_si.csv",
            "validado": "",
        })
    pd.DataFrame(rows).sort_values(["semestre", "codigo", "turma"]).to_csv(
        DATA / "revisao_horarios_fixos_2026.csv", index=False
    )


def build_sectors_review() -> None:
    classes = pd.read_csv(DATA / "turmas_2026_cc_si.csv", dtype=str).fillna("")
    meetings = pd.read_csv(DATA / "horarios_2026_cc_si.csv", dtype=str).fillna("")
    turmas25 = pd.read_csv(DATA / "turmas_2025.csv", dtype=str).fillna("") if (DATA / "turmas_2025.csv").exists() else pd.DataFrame()
    dias25 = pd.read_csv(DATA / "dias_por_setor_2025.csv", dtype=str).fillna("") if (DATA / "dias_por_setor_2025.csv").exists() else pd.DataFrame()

    setor_hist_map = {}
    if not turmas25.empty and "codigo" in turmas25 and "setor" in turmas25:
        for _, r in turmas25.iterrows():
            if r["codigo"] and r["setor"]:
                setor_hist_map[r["codigo"]] = r["setor"]

    days_hist_map = {}
    if not dias25.empty and "setor" in dias25 and "dias_observados" in dias25:
        for _, r in dias25.iterrows():
            if r["setor"] and r["dias_observados"]:
                days_hist_map.setdefault(r["setor"], set()).update(r["dias_observados"].split(";"))

    h = meetings.merge(classes[["id", "disciplina", "origem"]], left_on="turma_id", right_on="id", how="left")
    rows = []
    for (code, disc, origem), group in h.groupby(["codigo", "disciplina", "origem"]):
        dias_obs = sorted(set(group["dia"]))
        setor_hist = setor_hist_map.get(code, "")
        dias_setor_hist = sorted(days_hist_map.get(setor_hist, set()))
        rows.append({
            "codigo": code,
            "disciplina": disc,
            "origem": origem,
            "setor_historico_2025": setor_hist,
            "dias_observados_2026": ";".join(dias_obs),
            "dias_setor_historico": ";".join(dias_setor_hist),
            "setor_oficial": "",
            "fonte": "turmas_2025.csv; dias_por_setor_2025.csv; horarios_2026_cc_si.csv",
            "validado": "",
        })
    pd.DataFrame(rows).sort_values("codigo").to_csv(
        DATA / "revisao_setores_2026.csv", index=False
    )


def build_teacher_qualification_review() -> None:
    classes = pd.read_csv(DATA / "turmas_2026_cc_si.csv", dtype=str).fillna("")
    turmas25 = pd.read_csv(DATA / "turmas_2025.csv", dtype=str).fillna("") if (DATA / "turmas_2025.csv").exists() else pd.DataFrame()
    pref25 = pd.read_csv(DATA / "preferencias_2025.csv", dtype=str).fillna("") if (DATA / "preferencias_2025.csv").exists() else pd.DataFrame()

    freq_map: dict[tuple[str, str], str] = {}
    if not pref25.empty:
        for _, r in pref25.iterrows():
            freq_map[(r.get("codigo", ""), r.get("docente", ""))] = str(r.get("total_alocacoes", ""))

    setor_hist_map = {}
    if not turmas25.empty and "codigo" in turmas25 and "setor" in turmas25:
        for _, r in turmas25.iterrows():
            if r["codigo"] and r["setor"]:
                setor_hist_map[r["codigo"]] = r["setor"]

    pairs = set()
    for row in classes.itertuples():
        code = row.codigo
        disc = row.disciplina
        profs = [p.strip() for p in str(row.professores).split(";") if p.strip()]
        for p in profs:
            pairs.add((code, disc, p, True))

    if not turmas25.empty:
        for _, row in turmas25.iterrows():
            code = row.get("codigo", "")
            disc = row.get("disciplina", "")
            prof = row.get("alocacao", "")
            if code and prof:
                # check if already in pairs
                existing = [item for item in pairs if item[0] == code and item[2] == prof]
                if not existing:
                    pairs.add((code, disc, prof, False))

    rows = []
    for code, disc, prof, obs26 in sorted(pairs):
        setor = setor_hist_map.get(code, "")
        freq = freq_map.get((code, prof), "")
        rows.append({
            "codigo": code,
            "disciplina": disc,
            "docente": prof,
            "setor_historico": setor,
            "frequencia_historica_2023_2025": freq,
            "observado_2026": obs26,
            "habilitado": "",
            "fonte": "turmas_2026_cc_si.csv; turmas_2025.csv; preferencias_2025.csv",
            "validado": "",
        })
    pd.DataFrame(rows).sort_values(["codigo", "docente"]).to_csv(
        DATA / "revisao_habilitacao_docente_2026.csv", index=False
    )


def build_teacher_priorities_review() -> None:
    classes = pd.read_csv(DATA / "turmas_2026_cc_si.csv", dtype=str).fillna("")
    carga25 = pd.read_csv(DATA / "carga_docente_2025.csv", dtype=str).fillna("") if (DATA / "carga_docente_2025.csv").exists() else pd.DataFrame()
    pref25 = pd.read_csv(DATA / "preferencias_2025.csv", dtype=str).fillna("") if (DATA / "preferencias_2025.csv").exists() else pd.DataFrame()

    total_allocations: dict[str, int] = defaultdict(int)
    if not pref25.empty:
        for _, r in pref25.iterrows():
            doc = str(r.get("docente", ""))
            count = int(float(r.get("total_alocacoes", 0) or 0))
            total_allocations[doc] += count

    obs26_teachers = set()
    for row in classes.itertuples():
        profs = [p.strip() for p in str(row.professores).split(";") if p.strip()]
        obs26_teachers.update(profs)

    docente_full = {}
    if not carga25.empty:
        for _, r in carga25.iterrows():
            alias = str(r.get("Nome Planilha", "")).strip()
            full = str(r.get("Docente", "")).strip()
            if alias and alias not in {"SOMA", "CHECK", "CH AVG", "~ Turmas 4h"}:
                docente_full[alias] = full

    all_teachers = sorted(obs26_teachers | set(docente_full.keys()))
    rows = []
    for t in all_teachers:
        full = docente_full.get(t, t)
        allocs = total_allocations.get(t, "")
        rows.append({
            "docente": full,
            "nome_normalizado": t,
            "ocorrencias_2023_2025": allocs,
            "observado_2026": t in obs26_teachers,
            "prioridade": "",
            "fonte": "turmas_2026_cc_si.csv; carga_docente_2025.csv; preferencias_2025.csv",
            "validado": "",
        })
    pd.DataFrame(rows).sort_values("nome_normalizado").to_csv(
        DATA / "revisao_prioridades_docentes_2026.csv", index=False
    )


def build_external_classes_review() -> None:
    web = pd.read_csv(WEBSCRAP / "turmas_2026_raw.csv", dtype=str).fillna("")
    links = pd.read_csv(DATA / "vagas_turmas_2026.csv", dtype=str).fillna("") if (DATA / "vagas_turmas_2026.csv").exists() else pd.DataFrame()
    linked_urls = set(links["turma_url"]) if not links.empty else set()

    # Group by (semestre, codigo) to find alternative sections count
    section_counts = web.groupby(["semestre", "codigo"]).size().to_dict()

    rows = []
    for row in web.itertuples():
        code = str(row.codigo)
        is_external = not code.startswith("TCC")
        is_linked = row.turma_url in linked_urls
        # Include all non-linked or external offerings
        if is_external or not is_linked:
            rows.append({
                "semestre": row.semestre,
                "codigo": code,
                "disciplina": row.disciplina,
                "curso": row.cursos_busca,
                "periodo_curricular": "",
                "turma": row.turma,
                "turma_url": row.turma_url,
                "horarios": row.horario,
                "vagas_por_curso": row.vagas_por_curso_json,
                "quantidade_secoes_alternativas": section_counts.get((row.semestre, code), 1),
                "vinculada_ao_pdf": is_linked,
                "tratamento_no_modelo": "",
            })
    pd.DataFrame(rows).sort_values(["semestre", "codigo", "turma"]).to_csv(
        DATA / "revisao_turmas_externas_2026.csv", index=False
    )


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    build_curricular_review()
    build_h12_universe()
    build_cotutoria_policy()
    build_rooms_registry()
    build_resources_review()
    build_fixed_schedules_review()
    build_sectors_review()
    build_teacher_qualification_review()
    build_teacher_priorities_review()
    build_external_classes_review()
    print("Tabelas de revisão geradas em dados/processados/")


if __name__ == "__main__":
    main()
