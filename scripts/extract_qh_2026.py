"""Extrai os quadros de horários de 2026, em PDF, para CSVs auditáveis.

Os dois PDFs foram exportados de planilhas diferentes e têm layouts distintos.
A extração usa as coordenadas geradas por ``pdftotext -bbox-layout``; não faz
OCR e não infere curso, período curricular, obrigatoriedade, setor ou capacidade.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "dados" / "brutos"
OUTPUT = ROOT / "dados" / "processados"
TEACHER_REFERENCE = OUTPUT / "carga_docente_2025.csv"

CODE_RE = re.compile(r"^[A-Z]{2,4}\d{4,6}$")
QH1_TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})$")
QH2_TIME_RE = re.compile(r"^(\d{1,2})/(\d{1,2})$")
MISSING_TEACHER = {"", "-", "--", "----"}
DAYS = ("segunda", "terca", "quarta", "quinta", "sexta")


@dataclass(frozen=True)
class Layout:
    semester: str
    filename: str
    discipline_range: tuple[float, float]
    class_range: tuple[float, float]
    teacher_range: tuple[float, float]
    day_centers: tuple[float, ...]
    vertical_tolerance: float
    no_code_mode: str


LAYOUTS = (
    Layout(
        semester="2026-1",
        filename="QH-2026-1.pdf",
        discipline_range=(82.0, 390.0),
        class_range=(390.0, 430.0),
        teacher_range=(430.0, 545.0),
        day_centers=(578.0, 629.0, 680.0, 731.0, 782.0),
        vertical_tolerance=8.0,
        no_code_mode="pos_label",
    ),
    Layout(
        semester="2026-2",
        filename="QH-2026-2.pdf",
        discipline_range=(80.0, 500.0),
        class_range=(500.0, 540.0),
        teacher_range=(710.0, 842.0),
        day_centers=(558.5, 591.7, 625.0, 658.2, 691.4),
        vertical_tolerance=8.0,
        no_code_mode="dash",
    ),
)


@dataclass(frozen=True)
class Word:
    text: str
    x0: float
    x1: float
    y0: float
    y1: float
    page: int

    @property
    def center_x(self) -> float:
        return (self.x0 + self.x1) / 2


@dataclass(frozen=True)
class TeacherMatch:
    original: str
    normalized: str
    method: str
    verified: bool


def normalize_text(value: object) -> str:
    """Normaliza texto apenas para comparação, preservando o valor de saída."""
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.upper().replace(", 20H", "")
    return re.sub(r"[^A-Z0-9]+", " ", text).strip()


def clean_text(words: list[Word]) -> str:
    return " ".join(word.text for word in sorted(words, key=lambda item: item.x0)).strip()


def split_teachers(value: str) -> list[str]:
    value = str(value or "").strip()
    if value in MISSING_TEACHER:
        return []
    return [part.strip() for part in re.split(r"\s*/\s*", value) if part.strip() not in MISSING_TEACHER]


class TeacherNormalizer:
    """Vincula abreviações do QH à coluna ``Nome Planilha`` de 2025.

    Casos sem correspondência única são preservados e marcados como não
    verificados. Assim, a extração não inventa equivalências entre docentes.
    """

    def __init__(self, reference_path: Path = TEACHER_REFERENCE):
        self.records: list[dict] = []
        if not reference_path.exists():
            return
        frame = pd.read_csv(reference_path, dtype=str).fillna("")
        for _, row in frame.iterrows():
            alias = str(row.get("Nome Planilha", "")).strip()
            full_name = str(row.get("Docente", "")).strip()
            if not alias or alias in {"SOMA", "CHECK", "CH AVG", "~ Turmas 4h"}:
                continue
            self.records.append(
                {
                    "alias": alias,
                    "full_name": full_name,
                    "alias_norm": normalize_text(alias),
                    "full_norm": normalize_text(full_name),
                }
            )

    @staticmethod
    def _tokens_match(raw_tokens: list[str], candidate_tokens: set[str]) -> bool:
        if not raw_tokens:
            return False
        for token in raw_tokens:
            if len(token) == 1:
                if not any(value.startswith(token) for value in candidate_tokens):
                    return False
            elif token not in candidate_tokens:
                return False
        return True

    def match(self, value: str) -> TeacherMatch:
        original = str(value or "").strip()
        normalized = normalize_text(original)
        if not normalized:
            return TeacherMatch(original, "", "ausente", False)

        aliases = [record for record in self.records if normalized == record["alias_norm"]]
        if len(aliases) == 1:
            return TeacherMatch(original, aliases[0]["alias"], "alias_exato", True)

        full_names = [record for record in self.records if normalized == record["full_norm"]]
        if len(full_names) == 1:
            return TeacherMatch(original, full_names[0]["alias"], "nome_completo_exato", True)

        raw_tokens = normalized.split()
        candidates = []
        raw_token_set = set(raw_tokens)
        for record in self.records:
            full_tokens = set(record["full_norm"].split())
            alias_tokens = set(record["alias_norm"].split())
            raw_identifies_candidate = self._tokens_match(raw_tokens, full_tokens | alias_tokens)
            alias_is_expanded_by_raw = (
                bool(alias_tokens)
                and alias_tokens.issubset(raw_token_set)
                and all(len(token) >= 5 for token in alias_tokens)
            )
            if raw_identifies_candidate or alias_is_expanded_by_raw:
                # Um único sobrenome só é aceito quando identifica uma pessoa.
                candidates.append(record)
        unique = {record["alias"]: record for record in candidates}
        if len(unique) == 1 and (len(raw_tokens) >= 2 or len(normalized) >= 5):
            record = next(iter(unique.values()))
            return TeacherMatch(original, record["alias"], "tokens_univocos", True)

        return TeacherMatch(original, original, "sem_correspondencia_univoca", False)


def require_pdftotext() -> str:
    executable = shutil.which("pdftotext")
    if not executable:
        raise RuntimeError("pdftotext não encontrado; instale o pacote poppler")
    return executable


def pdf_words(pdf_path: Path, pdftotext: str, temporary_directory: Path) -> list[list[Word]]:
    xml_path = temporary_directory / f"{pdf_path.stem}.html"
    subprocess.run(
        [pdftotext, "-bbox-layout", str(pdf_path), str(xml_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    root = ET.parse(xml_path).getroot()
    pages: list[list[Word]] = []
    page_elements = [element for element in root.iter() if element.tag.endswith("page")]
    for page_number, page in enumerate(page_elements, start=1):
        words = []
        for element in page.iter():
            if not element.tag.endswith("word"):
                continue
            words.append(
                Word(
                    text="".join(element.itertext()),
                    x0=float(element.attrib["xMin"]),
                    x1=float(element.attrib["xMax"]),
                    y0=float(element.attrib["yMin"]),
                    y1=float(element.attrib["yMax"]),
                    page=page_number,
                )
            )
        pages.append(words)
    return pages


def same_baseline(words: list[Word], y0: float, tolerance: float = 0.7) -> list[Word]:
    return [word for word in words if abs(word.y0 - y0) < tolerance]


def field_at(words: list[Word], bounds: tuple[float, float]) -> str:
    lower, upper = bounds
    return clean_text([word for word in words if lower <= word.center_x < upper])


def row_anchors(words: list[Word], layout: Layout) -> list[tuple[Word, str]]:
    anchors: dict[float, tuple[Word, str]] = {}
    for word in words:
        if CODE_RE.match(word.text):
            anchors[word.y0] = (word, word.text)

    if layout.no_code_mode == "dash":
        for word in words:
            if word.text == "--" and word.center_x < 80:
                anchors.setdefault(word.y0, (word, ""))
    elif layout.no_code_mode == "pos_label":
        for word in words:
            if word.text.casefold() != "pós:":
                continue
            if not (layout.discipline_range[0] <= word.center_x < layout.discipline_range[1]):
                continue
            line = same_baseline(words, word.y0)
            if not any(CODE_RE.match(item.text) for item in line):
                anchors.setdefault(word.y0, (word, ""))
    return [anchors[key] for key in sorted(anchors)]


def normalize_room(value: str) -> str:
    value = normalize_text(value)
    value = re.sub(r"^SALA\s*", "", value)
    value = re.sub(r"^(?:LAB|L)\s*", "L", value)
    return value.replace(" ", "").strip("-;,.")


def parse_time(value: str, semester: str) -> tuple[str, str] | None:
    value = str(value or "").strip()
    if semester.endswith("-1"):
        match = QH1_TIME_RE.match(value)
        if not match:
            return None
        start_hour, start_minute, end_hour, end_minute = map(int, match.groups())
    else:
        match = QH2_TIME_RE.match(value)
        if not match:
            return None
        start_hour, end_hour = map(int, match.groups())
        start_minute = end_minute = 0
    return f"{start_hour:02d}:{start_minute:02d}", f"{end_hour:02d}:{end_minute:02d}"


def parse_meetings(words: list[Word], anchor: Word, layout: Layout) -> list[dict]:
    nearby = [word for word in words if abs(word.y0 - anchor.y0) <= layout.vertical_tolerance]
    meetings = []
    for center, day in zip(layout.day_centers, DAYS):
        cell = [word for word in nearby if abs(word.center_x - center) < 25]
        parsed_time = None
        original_time = ""
        for word in sorted(cell, key=lambda item: (item.y0, item.x0)):
            parsed_time = parse_time(word.text, layout.semester)
            if parsed_time is not None:
                original_time = word.text
                break
        if parsed_time is None:
            continue
        room_words = [word for word in cell if word.y0 > anchor.y0 + 1]
        room_original = clean_text(room_words)
        room = normalize_room(room_original)
        if room in MISSING_TEACHER:
            room = ""
        start, end = parsed_time
        meetings.append(
            {
                "dia": day,
                "inicio": start,
                "fim": end,
                "sala": room,
                "horario_original": original_time,
                "sala_original": room_original,
                "valor_original": " ".join(value for value in (original_time, room_original) if value),
            }
        )
    return meetings


def section_markers(pages: list[list[Word]]) -> list[tuple[int, float, str]]:
    markers = []
    for page_number, words in enumerate(pages, start=1):
        for word in words:
            if normalize_text(word.text) != "SECAO":
                continue
            line = clean_text(same_baseline(words, word.y0))
            normalized = normalize_text(line)
            if "OBRIGATORIAS DA POS" in normalized:
                category = "obrigatoria_pos"
            elif "OBRIGATORIAS DE OUTROS INSTITUTOS" in normalized:
                category = "obrigatoria_outros_institutos"
            elif "DISCIPLINAS DE SERVICO" in normalized:
                category = "servico"
            elif "DISCIPLINAS OPTATIVAS" in normalized:
                category = "optativa"
            else:
                category = "secao_nao_identificada"
            markers.append((page_number, word.y0, category))
    return sorted(markers)


def observed_category(
    layout: Layout,
    page: int,
    y0: float,
    discipline: str,
    markers: list[tuple[int, float, str]],
) -> str:
    if layout.semester.endswith("-1"):
        previous = [marker for marker in markers if (marker[0], marker[1]) < (page, y0)]
        return previous[-1][2] if previous else "nao_informada"
    normalized = normalize_text(discipline)
    if "OPTATIVA" in normalized:
        return "optativa_explicita_no_nome"
    if "GRAD E POS" in normalized:
        return "graduacao_pos_explicita_no_nome"
    return "nao_informada"


def parse_pdf(
    pdf_path: Path,
    layout: Layout,
    pdftotext: str,
    temporary_directory: Path,
    teacher_normalizer: TeacherNormalizer,
) -> tuple[list[dict], list[dict], list[TeacherMatch]]:
    pages = pdf_words(pdf_path, pdftotext, temporary_directory)
    markers = section_markers(pages)
    classes: list[dict] = []
    meetings: list[dict] = []
    matches: list[TeacherMatch] = []
    no_code_counter = 0

    for page_number, words in enumerate(pages, start=1):
        for anchor, code in row_anchors(words, layout):
            line = same_baseline(words, anchor.y0)
            discipline = field_at(line, layout.discipline_range)
            class_code_original = field_at(line, layout.class_range)
            class_code = "" if class_code_original in MISSING_TEACHER else class_code_original
            teacher_original = field_at(line, layout.teacher_range)
            if not discipline:
                continue

            if not code:
                no_code_counter += 1
                internal_code = f"SEM-CODIGO-{no_code_counter:03d}"
            else:
                internal_code = code
            normalized_class = class_code or "SEM-TURMA"
            class_id = f"{layout.semester}-{internal_code}-{normalized_class}"

            teacher_parts = split_teachers(teacher_original)
            teacher_matches = [teacher_normalizer.match(value) for value in teacher_parts]
            matches.extend(teacher_matches)
            normalized_teachers = [match.normalized for match in teacher_matches if match.normalized]
            class_meetings = parse_meetings(words, anchor, layout)
            cancelled = "CANCELADA" in normalize_text(discipline)
            pending = []
            if not code:
                pending.append("codigo_ausente")
            if not class_meetings:
                pending.append("horario_ausente")
            if not normalized_teachers:
                pending.append("professor_ausente")
            if len(normalized_teachers) > 1:
                pending.append("multiplos_professores")
            if any(not match.verified for match in teacher_matches):
                pending.append("normalizacao_docente_nao_verificada")
            status = "cancelada" if cancelled else ("incompleta" if {"horario_ausente", "professor_ausente"} & set(pending) else "ativa")

            category = observed_category(layout, page_number, anchor.y0, discipline, markers)
            record = {
                "id": class_id,
                "semestre": layout.semester,
                "codigo": code,
                "codigo_original": code or ("--" if layout.no_code_mode == "dash" else ""),
                "codigo_interno": internal_code,
                "disciplina": discipline,
                "turma": class_code,
                "turma_original": class_code_original,
                "origem_codigo": (
                    "IC" if code.startswith(("TCC", "TIC"))
                    else ("externa" if code else "nao_identificada")
                ),
                "categoria_observada": category,
                "alocacao": normalized_teachers[0] if len(normalized_teachers) == 1 else "",
                "professores": ";".join(normalized_teachers),
                "professores_qtd": len(normalized_teachers),
                "alocacao_original": teacher_original,
                "normalizacao_docente_verificada": bool(teacher_matches) and all(match.verified for match in teacher_matches),
                "status": status,
                "pendencias": ";".join(pending),
                "pagina_pdf": page_number,
                "posicao_y": round(anchor.y0, 3),
                "arquivo_origem": str(pdf_path.relative_to(ROOT)),
            }
            classes.append(record)
            for meeting_number, meeting in enumerate(class_meetings, start=1):
                meetings.append(
                    {
                        "turma_id": class_id,
                        "semestre": layout.semester,
                        "codigo": code,
                        "turma": class_code,
                        "encontro": meeting_number,
                        **meeting,
                        "pagina_pdf": page_number,
                        "arquivo_origem": str(pdf_path.relative_to(ROOT)),
                    }
                )
    return classes, meetings, matches


def teacher_review_rows(classes: list[dict], matches: list[TeacherMatch]) -> list[dict]:
    semesters_by_original: dict[str, set[str]] = defaultdict(set)
    for record in classes:
        for teacher in split_teachers(record["alocacao_original"]):
            semesters_by_original[teacher].add(record["semestre"])
    counts = Counter(match.original for match in matches)
    unique_matches = {match.original: match for match in matches}
    return [
        {
            "nome_original": original,
            "nome_normalizado": match.normalized,
            "metodo": match.method,
            "verificada": match.verified,
            "ocorrencias": counts[original],
            "semestres": ";".join(sorted(semesters_by_original[original])),
        }
        for original, match in sorted(unique_matches.items(), key=lambda item: normalize_text(item[0]))
    ]


def main() -> None:
    pdftotext = require_pdftotext()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    teacher_normalizer = TeacherNormalizer()
    all_classes: list[dict] = []
    all_meetings: list[dict] = []
    all_matches: list[TeacherMatch] = []

    with tempfile.TemporaryDirectory(prefix="qh-2026-") as temporary:
        temporary_directory = Path(temporary)
        for layout in LAYOUTS:
            pdf_path = RAW / layout.filename
            if not pdf_path.exists():
                raise FileNotFoundError(pdf_path)
            classes, meetings, matches = parse_pdf(
                pdf_path,
                layout,
                pdftotext,
                temporary_directory,
                teacher_normalizer,
            )
            all_classes.extend(classes)
            all_meetings.extend(meetings)
            all_matches.extend(matches)

    class_frame = pd.DataFrame(all_classes)
    meeting_frame = pd.DataFrame(all_meetings)
    teacher_frame = pd.DataFrame(teacher_review_rows(all_classes, all_matches))
    class_frame.to_csv(OUTPUT / "turmas_2026.csv", index=False)
    meeting_frame.to_csv(OUTPUT / "horarios_2026.csv", index=False)
    teacher_frame.to_csv(OUTPUT / "normalizacao_docentes_2026.csv", index=False)

    summary = {
        "arquivos_origem": [str((RAW / layout.filename).relative_to(ROOT)) for layout in LAYOUTS],
        "metodo_extracao": "pdftotext -bbox-layout",
        "turmas": int(len(class_frame)),
        "turmas_com_codigo": int(class_frame["codigo"].ne("").sum()),
        "turmas_sem_codigo": int(class_frame["codigo"].eq("").sum()),
        "encontros": int(len(meeting_frame)),
        "codigos_distintos": int(class_frame.loc[class_frame["codigo"].ne(""), "codigo"].nunique()),
        "salas": sorted(meeting_frame.loc[meeting_frame["sala"].ne(""), "sala"].unique()),
        "por_semestre": {
            semester: {
                "turmas": int(len(group)),
                "turmas_com_codigo": int(group["codigo"].ne("").sum()),
                "turmas_sem_codigo": int(group["codigo"].eq("").sum()),
                "encontros": int(meeting_frame["semestre"].eq(semester).sum()),
                "ativas": int(group["status"].eq("ativa").sum()),
                "incompletas": int(group["status"].eq("incompleta").sum()),
                "canceladas": int(group["status"].eq("cancelada").sum()),
            }
            for semester, group in class_frame.groupby("semestre")
        },
        "normalizacoes_docentes_nao_verificadas": int((~teacher_frame["verificada"]).sum()),
        "observacoes": [
            "As contagens incluem graduação, pós-graduação, disciplinas de serviço e registros sem código.",
            "Curso, período curricular, obrigatoriedade, setor, vagas e capacidades não constam nos PDFs.",
            "Horários, salas e professores são alocações observadas, não parâmetros fixos do solver.",
        ],
    }
    (OUTPUT / "resumo_2026.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
