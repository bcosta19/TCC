"""Metadados, recursos e distância aproximada entre salas."""

from __future__ import annotations

import re


LAB_RESOURCE = "laboratorio"
# Peso provisório da troca de prédio. Ele torna 308 -> L307 mais caro que uma
# troca intra-prédio no mesmo andar. Deve ser calibrado se forem obtidas
# distâncias físicas ou tempos reais de deslocamento.
BUILDING_CHANGE_DISTANCE = 3


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


def estimated_room_distance(room_a: str, room_b: str) -> int | None:
    """Calcula a distância discreta adotada para a instância de 2025.

    A distância horizontal e a distância vertical física não são modeladas.
    Em prédios diferentes, soma-se o custo fixo da troca de prédio à diferença
    entre os andares. No mesmo prédio, em andares diferentes, usa-se a
    diferença de andar; no mesmo andar, salas do mesmo lado/paridade ficam a
    uma unidade e lados/paridades diferentes ficam a duas unidades.
    """
    a = room_metadata(room_a)
    b = room_metadata(room_b)
    if a["andar"] is None or b["andar"] is None:
        return None
    if a["id"] == b["id"]:
        return 0
    floor_gap = abs(a["andar"] - b["andar"])
    if a["predio"] != b["predio"]:
        return BUILDING_CHANGE_DISTANCE + floor_gap
    if floor_gap:
        return floor_gap
    return 1 if a["lado"] == b["lado"] else 2
