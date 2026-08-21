"""Vincula linhas dos PDFs de 2026 às turmas públicas do Quadro de Horários.

O vínculo usa semestre+código, turma normalizada e encontros. Uma linha
compactada do PDF pode corresponder a mais de uma turma do sistema (por
exemplo, ``A-A/B-A``). Esses vínculos permanecem em linhas separadas.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "processados"
WEB = ROOT / "webscrap" / "turmas_2026_raw.csv"
OUT = DATA / "vagas_turmas_2026.csv"
UNMATCHED_WEB = DATA / "turmas_web_sem_qh_2026.csv"

DAY_MAP = {
    "Seg": "segunda",
    "Ter": "terca",
    "Qua": "quarta",
    "Qui": "quinta",
    "Sex": "sexta",
    "Sab": "sabado",
}
MEETING_RE = re.compile(r"(Seg|Ter|Qua|Qui|Sex|Sab)\s+(\d{2}:\d{2})-(\d{2}:\d{2})")


def normalize_class_code(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", str(value or "").upper())


def web_meetings(value: str) -> set[tuple[str, str, str]]:
    return {
        (DAY_MAP[day], start, end)
        for day, start, end in MEETING_RE.findall(str(value or ""))
    }


def pdf_meetings(frame: pd.DataFrame) -> set[tuple[str, str, str]]:
    return set(zip(frame["dia"], frame["inicio"], frame["fim"]))


def match_score(pdf_row, pdf_slots: set[tuple[str, str, str]], web_row) -> tuple[int, str]:
    pdf_class = normalize_class_code(pdf_row.turma)
    web_class = normalize_class_code(web_row.turma)
    web_slots = web_meetings(web_row.horario)
    slots_equal = bool(web_slots) and web_slots == pdf_slots
    slots_subset = bool(web_slots) and web_slots.issubset(pdf_slots)

    if pdf_class and web_class and pdf_class == web_class and slots_equal:
        return 120, "turma_e_encontros_exatos"
    if pdf_class and web_class and pdf_class == web_class:
        return 110, "turma_exata"
    if pdf_class and web_class and web_class in pdf_class and slots_subset:
        return 100, "turma_contida_e_encontros_contidos"
    if slots_equal:
        return 90, "encontros_exatos"
    if slots_subset:
        return 80, "encontros_contidos"
    return 0, ""


def main() -> None:
    classes = pd.read_csv(DATA / "turmas_2026.csv", dtype=str).fillna("")
    meetings = pd.read_csv(DATA / "horarios_2026.csv", dtype=str).fillna("")
    web = pd.read_csv(WEB, dtype=str).fillna("")
    classification = pd.read_csv(
        DATA / "classificacao_curricular_2026.csv", dtype=str
    ).fillna("")
    classification_by_id = classification.set_index("turma_id")

    meetings_by_class = {
        class_id: pdf_meetings(group)
        for class_id, group in meetings.groupby("turma_id")
    }
    pdf_by_code: dict[tuple[str, str], list] = defaultdict(list)
    for row in classes.itertuples():
        if row.codigo:
            pdf_by_code[(row.semestre, row.codigo)].append(row)

    links = []
    matched_web_urls = set()
    for web_row in web.itertuples():
        candidates = pdf_by_code.get((web_row.semestre, web_row.codigo), [])
        scored = []
        for pdf_row in candidates:
            score, method = match_score(
                pdf_row,
                meetings_by_class.get(pdf_row.id, set()),
                web_row,
            )
            if score:
                scored.append((score, method, pdf_row))
        if not scored:
            continue
        best_score = max(item[0] for item in scored)
        best = [item for item in scored if item[0] == best_score]
        if len(best) != 1:
            continue
        _, method, pdf_row = best[0]
        curriculum = classification_by_id.loc[pdf_row.id]
        links.append(
            {
                "turma_id": pdf_row.id,
                "semestre": pdf_row.semestre,
                "codigo": pdf_row.codigo,
                "disciplina_pdf": pdf_row.disciplina,
                "turma_pdf": pdf_row.turma,
                "turma_web": web_row.turma,
                "turma_url": web_row.turma_url,
                "metodo_vinculo": method,
                "docentes_web": web_row.docentes,
                "horario_web": web_row.horario,
                "cursos_busca": web_row.cursos_busca,
                "codigos_cursos_com_vagas": web_row.codigos_cursos_com_vagas,
                "vagas": web_row.vagas,
                "inscritos": web_row.inscritos,
                "vagas_cc": web_row.vagas_cc,
                "inscritos_cc": web_row.inscritos_cc,
                "vagas_si": web_row.vagas_si,
                "inscritos_si": web_row.inscritos_si,
                "vagas_outros_cursos": web_row.vagas_outros_cursos,
                "inscritos_outros_cursos": web_row.inscritos_outros_cursos,
                "compartilhada_vagas_cc_si": web_row.compartilhada_vagas_cc_si,
                "curriculos": curriculum.curriculos,
                "grupos_curriculares": curriculum.grupos_curriculares,
                "compartilhada_curriculos_cc_si": curriculum.compartilhada_cc_si,
                "obrigatoria": curriculum.obrigatoria,
                "vagas_por_curso_json": web_row.vagas_por_curso_json,
                "fonte": "webscrap/turmas_2026_raw.csv + dados/processados/turmas_2026.csv",
            }
        )
        matched_web_urls.add(web_row.turma_url)

    links_frame = pd.DataFrame(links).sort_values(
        ["semestre", "codigo", "turma_pdf", "turma_web"]
    )
    links_frame.to_csv(OUT, index=False)

    unmatched = web[~web["turma_url"].isin(matched_web_urls)].copy()
    unmatched.to_csv(UNMATCHED_WEB, index=False)

    meetings_summary = {
        class_id: "; ".join(f"{row.dia} {row.inicio}-{row.fim}" for row in group.itertuples())
        for class_id, group in meetings.groupby("turma_id")
    }

    review_rows = []
    for link in links:
        if link["metodo_vinculo"] == "turma_e_encontros_exatos":
            continue
        h_pdf = meetings_summary.get(link["turma_id"], "")
        h_web = link["horario_web"]
        method = link["metodo_vinculo"]
        code = link["codigo"]
        c_count = len(pdf_by_code.get((link["semestre"], code), []))

        if method == "turma_exata":
            status = "divergencia_horario"
            evidence = (
                f"Horário do PDF ({h_pdf}) difere do sistema web ({h_web}); "
                "horário do PDF preservado sem substituição automática"
            )
        elif method == "turma_contida_e_encontros_contidos" and "/" in link["turma_pdf"]:
            status = "expansao_linha_compactada"
            evidence = (
                f"Linha compactada '{link['turma_pdf']}' do PDF expandida na turma "
                f"'{link['turma_web']}' do sistema conforme subconjunto de encontros ({h_web})"
            )
        elif method == "encontros_contidos" and "/" in link["turma_pdf"]:
            status = "expansao_linha_compactada"
            evidence = (
                f"Linha compactada '{link['turma_pdf']}' do PDF expandida na turma "
                f"'{link['turma_web']}' do sistema pelo horário ({h_web})"
            )
        elif method == "encontros_exatos" and not link["turma_pdf"]:
            status = "turma_sem_identificador_no_pdf"
            evidence = (
                f"Oferta do PDF sem identificador de turma vinculada à turma única '{link['turma_web']}' "
                f"do sistema pelo horário exato ({h_web})"
            )
        else:
            status = "turma_normalizada"
            evidence = (
                f"Turma no PDF '{link['turma_pdf']}' vinculada à turma '{link['turma_web']}' "
                f"do sistema pelo método {method} ({h_web})"
            )

        review_rows.append({
            "turma_id": link["turma_id"],
            "turma_url": link["turma_url"],
            "semestre": link["semestre"],
            "codigo": link["codigo"],
            "turma_pdf": link["turma_pdf"],
            "turma_web": link["turma_web"],
            "metodo_vinculo": method,
            "horario_pdf": h_pdf,
            "horario_web": h_web,
            "vagas": link["vagas"],
            "inscritos": link["inscritos"],
            "quantidade_candidatos": c_count,
            "status_vinculo": status,
            "evidencia": evidence,
            "decisao": "",
        })

    review_frame = pd.DataFrame(review_rows).sort_values(["semestre", "codigo", "turma_pdf", "turma_web"])
    review_out = DATA / "revisao_vinculos_2026.csv"
    review_frame.to_csv(review_out, index=False)

    linked_pdf_ids = set(links_frame["turma_id"])
    stats = {
        "turmas_pdf": len(classes),
        "turmas_web_cc_si": len(web),
        "vinculos": len(links_frame),
        "turmas_pdf_vinculadas": len(linked_pdf_ids),
        "turmas_pdf_com_multiplos_vinculos": int(
            links_frame.groupby("turma_id").size().gt(1).sum()
        ),
        "turmas_web_sem_vinculo_pdf": len(unmatched),
        "vinculos_com_vagas_cc_si": int(
            links_frame["compartilhada_vagas_cc_si"].astype(str).str.lower().eq("true").sum()
        ),
        "vagas_conhecidas": int(links_frame["vagas"].ne("").sum()),
        "vinculos_revisao": len(review_frame),
    }
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
