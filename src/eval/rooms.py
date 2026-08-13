"""Metadados e compatibilidade de recursos das salas."""

from __future__ import annotations

import re


LAB_RESOURCE = "laboratorio"


def is_lab_room(room: str) -> bool:
    return str(room or "").strip().upper().startswith("L")


def room_metadata(room: str) -> dict:
    room = str(room or "").strip().upper()
    is_lab = is_lab_room(room)
    digits = re.search(r"(\d+)", room)
    if not digits:
        return {
            "id": room,
            "laboratorio": is_lab,
            "predio": "laboratorio" if is_lab else "principal",
            "andar": None,
            "numero": None,
            "lado": None,
            "recursos": [LAB_RESOURCE] if is_lab else [],
        }
    number = int(digits.group(1))
    return {
        "id": room,
        "laboratorio": is_lab,
        "predio": "laboratorio" if is_lab else "principal",
        "andar": int(str(number)[0]),
        "numero": number,
        "lado": number % 2,
        "recursos": [LAB_RESOURCE] if is_lab else [],
    }


def room_matches_resources(room: str, required_resources: list[str] | None) -> bool:
    """Verifica a compatibilidade de sala para os recursos conhecidos.

    Nesta primeira versão o único recurso modelado é laboratório. A política é
    estrita: uma aula marcada como laboratório só pode ir para uma sala `L...`,
    e uma aula sem essa exigência não consome uma sala de laboratório.
    """
    required_resources = required_resources or []
    requires_lab = LAB_RESOURCE in required_resources
    return is_lab_room(room) == requires_lab
