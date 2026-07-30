"""Inferência provisória de recursos exigidos pelas turmas."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .rooms import LAB_RESOURCE, is_lab_room


def lab_evidence_by_code(rows: Iterable[dict]) -> dict[str, set[str]]:
    """Agrupa salas observadas por código de disciplina.

    Salas vazias não entram na evidência. A função é deliberadamente simples:
    o histórico do mesmo código serve como proxy enquanto não houver cadastro
    oficial de recursos por disciplina.
    """
    evidence: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        code = str(row.get("codigo", ""))
        room = str(row.get("sala", "")).strip().upper()
        if code and room:
            evidence[code].add(room)
    return dict(evidence)


def infer_lab_requirement(
    room: str,
    code: str,
    evidence: dict[str, set[str]],
) -> tuple[bool | None, str]:
    """Retorna (exige laboratório?, fonte da inferência).

    A exigência é por encontro. Para códigos que historicamente usam somente
    laboratórios, a exigência é propagada inclusive a encontros sem sala. Para
    códigos mistos, preserva-se a sala observada; se a sala estiver ausente,
    o requisito fica desconhecido em vez de inventar uma regra.
    """
    rooms = evidence.get(str(code), set())
    normalized_room = str(room or "").strip().upper()
    if rooms and all(is_lab_room(value) for value in rooms):
        return True, "codigo_historico_somente_laboratorio"
    if rooms and any(is_lab_room(value) for value in rooms):
        if normalized_room:
            return is_lab_room(normalized_room), "sala_observada_codigo_misto"
        return None, "codigo_historico_misto_sem_sala"
    if normalized_room:
        return is_lab_room(normalized_room), "sala_observada"
    return False, "sem_evidencia_de_laboratorio"


def resources_from_requirement(required_lab: bool | None) -> list[str] | None:
    if required_lab is None:
        return None
    return [LAB_RESOURCE] if required_lab else []
