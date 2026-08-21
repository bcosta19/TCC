"""Coleta publicamente as turmas de CC e SI em 2026, com vagas por curso.

A mesma ``turma_url`` retornada nas buscas de CC e SI representa uma única
oferta física. O script consolida essas ocorrências em uma linha e preserva a
discriminação das vagas alocadas a cada curso.

Uso, a partir da raiz do repositório:

    python webscrap/scrape_2026.py
"""

from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import requests

from scraper import (
    SEARCH_PARAMS,
    SESSION_EXPIRED_MARKER,
    fetch_semester,
    fetch_turma_details,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(__file__).resolve().parent / "turmas_2026_raw.csv"
WORKERS = 6

SEMESTERS = {
    "20261": "2026-1",
    "20262": "2026-2",
}

# IDs públicos consultados em 15/08/2026. O código acadêmico do curso de SI é
# 83, mas o identificador interno usado pelo filtro do site é 263.
COURSES = {
    "CC": {
        "idcurso": "31",
        "codigo_curso": "31",
        "idcurriculo": "3092",
        "curriculo": "31.02.003",
    },
    "SI": {
        "idcurso": "263",
        "codigo_curso": "83",
        "idcurriculo": "3473",
        "curriculo": "83.01.003",
    },
}

_local = threading.local()


def public_session() -> requests.Session:
    session = getattr(_local, "session", None)
    if session is None:
        session = requests.Session()
        _local.session = session
    return session


def details(url: str) -> tuple[str, dict]:
    result = fetch_turma_details(url, public_session())
    if result == SESSION_EXPIRED_MARKER or not isinstance(result, dict):
        result = {}
    return url, result


def search_params(course: dict) -> dict:
    return {
        **SEARCH_PARAMS,
        "q[vagas_turma_curso_idcurso_eq]": course["idcurso"],
        "q[disciplina_disciplinas_curriculos_idcurriculo_eq]": course["idcurriculo"],
    }


def sum_course(allocations: list[dict], course_code: str, field: str) -> int:
    return sum(
        int(item.get(field, 0) or 0)
        for item in allocations
        if str(item.get("codigo_curso", "")) == course_code
    )


def main() -> None:
    listing_session = requests.Session()
    consolidated: dict[str, dict] = {}

    for semester_code, semester_label in SEMESTERS.items():
        for course_label, course in COURSES.items():
            records = fetch_semester(
                semester_code,
                f"{semester_label}/{course_label}",
                listing_session,
                search_params(course),
            )
            for record in records:
                url = record["turma_url"]
                key = url or "|".join(
                    (semester_label, record["codigo"], record["turma"], course_label)
                )
                item = consolidated.setdefault(
                    key,
                    {
                        **record,
                        "semestre": semester_label,
                        "cursos_busca": set(),
                    },
                )
                item["cursos_busca"].add(course_label)

    urls = sorted({item["turma_url"] for item in consolidated.values() if item["turma_url"]})
    print(f"\nBuscando detalhes públicos de {len(urls)} turmas ({WORKERS} conexões)...")
    cache: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(details, url) for url in urls]
        for index, future in enumerate(as_completed(futures), start=1):
            url, result = future.result()
            cache[url] = result
            if index % 25 == 0 or index == len(futures):
                print(f"  {index}/{len(futures)}")

    rows = []
    for item in consolidated.values():
        detail = cache.get(item["turma_url"], {})
        allocations = detail.get("vagas_por_curso") or []
        tooltip_teachers = [
            name.strip()
            for name in str(item.get("docente_tooltip", "")).split(",")
            if name.strip() and name.strip() != "(não informado)"
        ]
        detail_teachers = detail.get("docentes") or []
        teachers = detail_teachers or tooltip_teachers
        search_courses = sorted(item["cursos_busca"])
        allocated_codes = sorted(
            {str(value.get("codigo_curso", "")) for value in allocations if value.get("codigo_curso")}
        )
        total_vacancies = detail.get("vagas")
        total_enrolled = detail.get("inscritos")
        cc_vacancies = sum_course(allocations, "31", "vagas")
        si_vacancies = sum_course(allocations, "83", "vagas")
        cc_enrolled = sum_course(allocations, "31", "inscritos")
        si_enrolled = sum_course(allocations, "83", "inscritos")
        rows.append(
            {
                "semestre": item["semestre"],
                "codigo": item["codigo"],
                "disciplina": item["disciplina"],
                "turma": item["turma"],
                "turma_url": item["turma_url"],
                "docentes": ";".join(teachers),
                "horario": detail.get("horario", ""),
                "padrao_dias": detail.get("padrao_dias", ""),
                "cursos_busca": ";".join(search_courses),
                "compartilhada_busca_cc_si": set(search_courses) == {"CC", "SI"},
                "codigos_cursos_com_vagas": ";".join(allocated_codes),
                "compartilhada_vagas_cc_si": {"31", "83"}.issubset(allocated_codes),
                "vagas": total_vacancies,
                "inscritos": total_enrolled,
                "vagas_cc": cc_vacancies,
                "inscritos_cc": cc_enrolled,
                "vagas_si": si_vacancies,
                "inscritos_si": si_enrolled,
                "vagas_outros_cursos": (
                    int(total_vacancies or 0) - cc_vacancies - si_vacancies
                    if total_vacancies is not None
                    else None
                ),
                "inscritos_outros_cursos": (
                    int(total_enrolled or 0) - cc_enrolled - si_enrolled
                    if total_enrolled is not None
                    else None
                ),
                "vagas_por_curso_json": json.dumps(
                    allocations, ensure_ascii=False, separators=(",", ":")
                ),
                "fonte": "Quadro de Horários UFF — páginas públicas de listagem e detalhe",
            }
        )

    frame = pd.DataFrame(rows).sort_values(
        ["semestre", "codigo", "turma", "turma_url"]
    )
    frame.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print(
        f"\n{OUTPUT}: {len(frame)} turmas; "
        f"{int(frame['compartilhada_vagas_cc_si'].sum())} com vagas para CC e SI"
    )


if __name__ == "__main__":
    main()
