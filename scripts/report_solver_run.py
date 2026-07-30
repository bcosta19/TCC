"""Gera relatório comparativo da execução do solver de salas."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "processados"
INITIAL = DATA / "instancia_2025_cc_si.json"
BEST = DATA / "solucao_salas_sa_2025.json"
OUT = DATA / "relatorio_solver_salas_2025.md"


def room_pattern(item: dict) -> dict[tuple[str, str, str], str]:
    return {
        (str(m.get("dia", "")), str(m.get("inicio", "")), str(m.get("fim", ""))): str(m.get("sala", ""))
        for m in item.get("encontros", [])
    }


def main() -> None:
    initial = json.loads(INITIAL.read_text(encoding="utf-8"))
    best = json.loads(BEST.read_text(encoding="utf-8"))
    initial_map = {item["id"]: item for item in initial["classes"]}
    changes = []
    for item in best["classes"]:
        before = room_pattern(initial_map[item["id"]])
        after = room_pattern(item)
        for meeting_key in sorted(set(before) | set(after)):
            if before.get(meeting_key, "") == after.get(meeting_key, ""):
                continue
            day, start, end = meeting_key
            changes.append({
                "id": item["id"],
                "codigo": item.get("codigo", ""),
                "disciplina": item.get("disciplina", ""),
                "encontro": f"{day} {start}–{end}",
                "antes": before.get(meeting_key, "") or "sem sala",
                "depois": after.get(meeting_key, "") or "sem sala",
            })

    initial_eval = best["solution"]["initial"]
    best_eval = best["solution"]["best"]
    lines = [
        "# Execução do solver de salas — 2025",
        "",
        "Algoritmo: **Simulated Annealing**, com horários e professores fixos.",
        "",
        "## Configuração",
        "",
        f"- Seed: `{best['solution']['seed']}`",
        f"- Iterações: `{best['solution']['iterations']}`",
        f"- Movimentos tentados: `{best['solution']['attempted_moves']}`",
        f"- Movimentos aceitos: `{best['solution']['accepted_moves']}`",
        f"- Turmas mutáveis: `{best['solution']['mutable_classes']}`",
        "",
        "## Comparação",
        "",
        "| Métrica | Inicial | Melhor solução |",
        "|---|---:|---:|",
        f"| Score | {initial_eval['score']} | {best_eval['score']} |",
        f"| Violações hard | {initial_eval['hard_violations']} | {best_eval['hard_violations']} |",
        f"| Conflitos de sala | {initial_eval['hard']['conflitos_sala']} | {best_eval['hard']['conflitos_sala']} |",
        f"| Conflitos curriculares | {initial_eval['hard']['conflitos_curriculares']} | {best_eval['hard']['conflitos_curriculares']} |",
        f"| Recursos incompatíveis | {initial_eval['hard']['recursos_incompativeis']} | {best_eval['hard']['recursos_incompativeis']} |",
        f"| Desperdício estimado | {initial_eval['soft']['desperdicio_capacidade']} | {best_eval['soft']['desperdicio_capacidade']} |",
        f"| Distância estimada | {initial_eval['soft']['distancia']} | {best_eval['soft']['distancia']} |",
        "",
        f"Foram alterados **{len(changes)} encontros** na melhor solução encontrada; a comparação é feita por dia e horário para preservar turmas que usam sala comum e laboratório na mesma semana.",
        "",
        "## Alterações de sala",
        "",
        "| ID | Código | Disciplina | Encontro | Antes | Depois |",
        "|---|---|---|---|---|---|",
    ]
    for change in changes:
        lines.append(f"| {change['id']} | {change['codigo']} | {change['disciplina']} | {change['encontro']} | {change['antes']} | {change['depois']} |")
    lines += [
        "",
        "## Interpretação",
        "",
        "A busca conseguiu reduzir os conflitos de sala sem alterar professores ou horários, mantendo a compatibilidade entre aulas de laboratório e salas `L...`.",
        "Os conflitos curriculares permaneceram porque esta versão do solver não libera horários.",
        "As capacidades são estimadas; a distância diferencia prédios e laboratórios, mas ainda não é uma medição física.",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
