"""Gera relatório da execução do solver de salas e horários."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "processados"
INITIAL = DATA / "instancia_2025_cc_si_flex.json"
BEST = DATA / "solucao_horarios_sa_2025.json"
OUT = DATA / "relatorio_solver_horarios_2025.md"


def pattern(item: dict) -> str:
    values = []
    for meeting in item.get("encontros", []):
        values.append(
            f"{meeting.get('dia', '')} {meeting.get('inicio', '')}–{meeting.get('fim', '')}"
        )
    return "; ".join(values) or "sem horário"


def rooms(item: dict) -> str:
    values = []
    for meeting in item.get("encontros", []):
        room = str(meeting.get("sala", "")) or "sem sala"
        values.append(
            f"{meeting.get('dia', '')} {meeting.get('inicio', '')}–{meeting.get('fim', '')}: {room}"
        )
    return "; ".join(values) or "sem sala"


def main() -> None:
    initial = json.loads(INITIAL.read_text(encoding="utf-8"))
    best = json.loads(BEST.read_text(encoding="utf-8"))
    initial_map = {item["id"]: item for item in initial["classes"]}
    changed = []
    for item in best["classes"]:
        before = initial_map[item["id"]]
        schedule_changed = pattern(before) != pattern(item)
        room_changed = rooms(before) != rooms(item)
        if schedule_changed or room_changed:
            changed.append({
                "id": item["id"],
                "codigo": item.get("codigo", ""),
                "disciplina": item.get("disciplina", ""),
                "fixo": bool(item.get("horario_fixo", True)),
                "horario_antes": pattern(before),
                "horario_depois": pattern(item),
                "sala_antes": rooms(before),
                "sala_depois": rooms(item),
            })

    solution = best["solution"]
    initial_eval = solution["initial"]
    best_eval = solution["best"]
    schedule_only = sum(1 for item in changed if item["horario_antes"] != item["horario_depois"])
    room_only = sum(1 for item in changed if item["sala_antes"] != item["sala_depois"])
    fixed_changed = sum(1 for item in changed if item["fixo"])

    lines = [
        "# Execução do solver de salas e horários — 2025",
        "",
        "Algoritmo: **Simulated Annealing**, com movimentos de horário e de sala.",
        "",
        "## Configuração",
        "",
        f"- Seed: `{solution['seed']}`",
        f"- Iterações: `{solution['iterations']}`",
        f"- Movimentos tentados: `{solution['attempted_moves']}`",
        f"- Movimentos aceitos: `{solution['accepted_moves']}`",
        f"- Turmas flexíveis: `{solution['flexible_classes']}`",
        "- Turmas fixas: externas e projetos finais, conforme a regra provisória de domínios.",
        "",
        "## Comparação",
        "",
        "| Métrica | Instância inicial | Melhor solução |",
        "|---|---:|---:|",
        f"| Score | {initial_eval['score']} | {best_eval['score']} |",
        f"| Violações hard | {initial_eval['hard_violations']} | {best_eval['hard_violations']} |",
        f"| Conflitos de sala | {initial_eval['hard']['conflitos_sala']} | {best_eval['hard']['conflitos_sala']} |",
        f"| Conflitos de professor | {initial_eval['hard']['conflitos_professor']} | {best_eval['hard']['conflitos_professor']} |",
        f"| Conflitos curriculares | {initial_eval['hard']['conflitos_curriculares']} | {best_eval['hard']['conflitos_curriculares']} |",
        f"| Recursos incompatíveis | {initial_eval['hard']['recursos_incompativeis']} | {best_eval['hard']['recursos_incompativeis']} |",
        f"| Descanso insuficiente | {initial_eval['hard']['descanso_insuficiente']} | {best_eval['hard']['descanso_insuficiente']} |",
        f"| Janelas | {initial_eval['soft']['janelas']} | {best_eval['soft']['janelas']} |",
        f"| Desperdício estimado | {initial_eval['soft']['desperdicio_capacidade']} | {best_eval['soft']['desperdicio_capacidade']} |",
        f"| Distância estimada | {initial_eval['soft']['distancia']} | {best_eval['soft']['distancia']} |",
        "",
        f"Foram alteradas **{len(changed)} turmas**: **{schedule_only}** tiveram horário alterado e **{room_only}** tiveram sala alterada. Alterações em turmas marcadas como fixas: **{fixed_changed}**.",
        "",
        "## Alterações encontradas",
        "",
        "| ID | Código | Disciplina | Horário antes | Horário depois | Sala antes | Sala depois |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in changed:
        lines.append(
            f"| {item['id']} | {item['codigo']} | {item['disciplina']} | "
            f"{item['horario_antes']} | {item['horario_depois']} | "
            f"{item['sala_antes']} | {item['sala_depois']} |"
        )

    lines += [
        "",
        "## Interpretação",
        "",
        "A busca respeita a distinção entre salas comuns e laboratórios e eliminou os conflitos de sala. Os conflitos hard restantes são curriculares; nenhum conflito de professor, capacidade, recurso ou descanso permaneceu.",
        "",
        "O aumento de janelas, desperdício e distância mostra o compromisso entre viabilidade e qualidade: nesta execução o peso das restrições hard dominou a função objetivo. Os domínios de horário ainda são provisórios e foram gerados a partir dos horários históricos observados.",
        "",
        "Capacidades e distâncias continuam estimadas; a distância usa custo 3 para troca de prédio mais diferença de andar. A solução serve como primeiro teste reprodutível da pipeline, não como grade oficial pronta para publicação.",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
