"""Executa e relata os experimentos não oficiais da instância CC/SI 2025.

Os resultados servem para validação técnica da pipeline. A prioridade dos
professores é neutra (1.0) e os dados de capacidade/recurso são estimados;
portanto, o relatório não representa resultado experimental final do TCC.
"""

from __future__ import annotations

import csv
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "processados"
BASE = DATA / "instancia_2025_cc_si.json"
FLEX = DATA / "instancia_2025_cc_si_flex.json"
PROVISIONAL = DATA / "provisoria_2025" / "instancia_2025_cc_si.json"
ROOM_SOLUTION = DATA / "solucao_salas_sa_2025.json"
SCHEDULE_SOLUTION = DATA / "solucao_horarios_sa_2025.json"
TEACHER_SOLUTION = DATA / "solucao_professores_sa_2025.json"
REPORT = DATA / "relatorio_experimento_nao_oficial_2025.md"

sys.path.insert(0, str(ROOT))

from src.eval.evaluator import evaluate_json  # noqa: E402
from src.solve.direct_objective import evaluate as fast_evaluate  # noqa: E402
from src.solve.room_sa import frames_from_payload  # noqa: E402
from src.solve.room_sa import solve_file as solve_rooms  # noqa: E402
from src.solve.schedule_sa import solve_file as solve_schedule  # noqa: E402
from src.solve.teacher_sa import solve_file as solve_teachers  # noqa: E402


def ensure_instances() -> None:
    """Reconstrói as instâncias geradas para refletir o código atual."""
    for script in (
        "build_instance_2025.py",
        "build_provisional_2025.py",
        "enrich_schedule_domains_2025.py",
    ):
        subprocess.run([sys.executable, str(ROOT / "scripts" / script)], check=True)


def check_evaluation(result: dict) -> list[str]:
    checks = []
    assert "distancia" not in result["soft"], "critério de distância ainda presente"
    assert result["hard_violations"] == sum(result["hard"].values()), "hard inconsistente"
    expected_score = result["hard_violations"] * 1_000_000 + sum(result["soft"].values())
    assert abs(result["score"] - expected_score) < 1e-8, "score inconsistente"
    assert "carga_anual_insuficiente" in result["hard"], "H12 ausente"
    checks.extend([
        "distância ausente do avaliador",
        "contagem de violações hard consistente",
        "score consistente com hard + soft",
        "H12 presente como restrição hard",
    ])
    return checks


def exact_payload(path: Path) -> dict:
    return evaluate_json(path).as_dict()


def compare_fast_exact(path: Path) -> tuple[bool, float]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    fast = fast_evaluate(payload)
    classes, meetings, rooms = frames_from_payload(payload)
    exact = evaluate_json(path).as_dict()
    delta = abs(float(fast["score"]) - float(exact["score"]))
    assert delta < 1e-8, f"avaliadores divergentes em {path.name}: {delta}"
    return True, delta


def check_teacher_domains(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    checked = 0
    violations = []
    for item in payload.get("classes", []):
        domain = [str(value) for value in item.get("professores_habilitados", []) if str(value)]
        teacher = str(item.get("professor", "") or "")
        if not domain or not teacher:
            continue
        checked += 1
        if teacher not in set(domain):
            violations.append(f"{item.get('id')}: {teacher}")
    assert not violations, "professor fora do domínio histórico: " + ", ".join(violations[:10])
    return checked


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(encoding="utf-8", newline="") as file:
        return max(0, sum(1 for _ in csv.reader(file)) - 1)


def result_lines(label: str, result: dict) -> list[str]:
    hard = result["hard"]
    soft = result["soft"]
    return [
        f"| {label} | {result['score']:.2f} | {result['hard_violations']} | "
        f"{hard['conflitos_sala']} | {hard['conflitos_curriculares']} | "
        f"{hard['carga_anual_insuficiente']} | {soft.get('preferencia_priorizada', 0):.2f} | "
        f"{soft['dias_trabalhados']} | {soft['janelas']} | {soft['desperdicio_capacidade']:.2f} | "
        f"{soft['rodizio_semestre']} |",
    ]


def main() -> None:
    ensure_instances()
    checks: list[str] = []
    results: dict[str, dict] = {}
    base_payload = json.loads(BASE.read_text(encoding="utf-8"))
    teacher_count = len(base_payload.get("teachers", []))
    teacher_domain_classes = sum(
        bool(item.get("professores_habilitados"))
        for item in base_payload.get("classes", [])
        if item.get("origem") == "IC"
    )
    movable_teacher_classes = sum(
        len(item.get("professores_habilitados") or []) > 1
        for item in base_payload.get("classes", [])
        if item.get("origem") == "IC"
    )
    obligatory_count = sum(
        bool(item.get("obrigatoria"))
        for item in base_payload.get("classes", [])
        if item.get("origem") == "IC"
    )
    minimum_obligatory = int(base_payload.get("min_obrigatorias_ano", 3))
    required_obligatory = teacher_count * minimum_obligatory
    h12_infeasible = obligatory_count < required_obligatory
    h12_feasibility_note = (
        "é estruturalmente inviável para H12"
        if h12_infeasible
        else "atende ao mínimo estrutural de H12"
    )

    results["baseline"] = exact_payload(BASE)
    results["provisoria"] = exact_payload(PROVISIONAL)
    checks.extend(check_evaluation(results["baseline"]))
    checks.extend(check_evaluation(results["provisoria"]))

    checked_pairs = {
        "instância flexível": FLEX,
        "baseline observado": BASE,
        "baseline provisório": PROVISIONAL,
    }

    room_metadata = solve_rooms(BASE, ROOM_SOLUTION, iterations=3000, seed=2025)
    results["sa_salas"] = room_metadata["best"]
    checks.extend(check_evaluation(results["sa_salas"]))

    schedule_metadata = solve_schedule(FLEX, SCHEDULE_SOLUTION, iterations=1000, seed=2025)
    results["sa_horarios"] = schedule_metadata["best"]
    checks.extend(check_evaluation(results["sa_horarios"]))

    teacher_metadata = solve_teachers(
        BASE,
        TEACHER_SOLUTION,
        iterations=5000,
        seed=2025,
        allow_unrestricted=False,
    )
    results["sa_professores"] = teacher_metadata["best"]
    checks.extend(check_evaluation(results["sa_professores"]))
    assert not teacher_metadata["allow_unrestricted"], "experimento de professores deve usar domínio restrito"
    checks.append("SA de professores usou domínio histórico por setor, sem modo irrestrito")

    checked_pairs.update({
        "solução SA de salas": ROOM_SOLUTION,
        "solução SA de horários": SCHEDULE_SOLUTION,
        "solução SA de professores": TEACHER_SOLUTION,
    })
    for label, path in checked_pairs.items():
        compare_fast_exact(path)
        checks.append(f"avaliador rápido e avaliador exato equivalentes ({label})")
    checked_domain_assignments = check_teacher_domains(TEACHER_SOLUTION)
    checks.append(
        f"professores atribuídos respeitam os domínios históricos ({checked_domain_assignments} turmas verificadas)"
    )

    # O SA de salas não altera atribuição de docentes; H12 deve permanecer igual.
    assert (
        results["sa_salas"]["hard"]["carga_anual_insuficiente"]
        == results["baseline"]["hard"]["carga_anual_insuficiente"]
    )
    checks.append("SA de salas preservou a carga anual enquanto movimentou apenas salas")
    assert (
        results["sa_professores"]["hard"]["carga_anual_insuficiente"]
        <= results["baseline"]["hard"]["carga_anual_insuficiente"]
    )
    checks.append("SA de professores não aumentou violações H12")

    lines = [
        "# Relatório do experimento não oficial — CC/SI 2025",
        "",
        f"Execução: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"Python: `{platform.python_version()}`",
        "",
        "> Este relatório valida a implementação e a pipeline com dados provisórios. "
        "Não é resultado experimental oficial da monografia.",
        "",
        "## Configuração e ressalvas",
        "",
        "- Instância derivada do quadro QH 2025, filtrada para CC/SI.",
        "- Capacidade de sala e requisito de laboratório são estimativas/inferências.",
        "- Preferências usam frequência histórica do webscrap normalizada por disciplina.",
        "- A prioridade de todos os professores foi fixada em `1.0` apenas para este teste.",
        "- Domínios de professor usam professores observados no mesmo setor em QH 2025.",
        "- Domínios de horário usam padrões de dias observados no mesmo setor e semestre.",
        f"- H12 foi ativada com mínimo de {minimum_obligatory} obrigatórias por professor no ano.",
        f"- A instância tem {teacher_count} professores IC e {obligatory_count} obrigatórias; "
        f"H12 requer {required_obligatory} alocações, portanto a configuração provisória "
        f"{h12_feasibility_note}.",
        "- O critério de distância não participa da avaliação nem dos solvers.",
        f"- {teacher_domain_classes} turmas IC receberam domínio de professor; "
        f"{movable_teacher_classes} têm mais de um candidato.",
        f"- Arquivos de revisão gerados: `professores_por_setor_2025.csv` "
        f"({count_csv_rows(DATA / 'professores_por_setor_2025.csv')} linhas), "
        f"`dominios_professores_turmas_2025.csv` "
        f"({count_csv_rows(DATA / 'dominios_professores_turmas_2025.csv')} linhas), "
        f"`dias_por_setor_2025.csv` ({count_csv_rows(DATA / 'dias_por_setor_2025.csv')} linhas) "
        f"e `auditoria_h12_professores_2025.csv` "
        f"({count_csv_rows(DATA / 'auditoria_h12_professores_2025.csv')} linhas).",
        "",
        "## Resultados",
        "",
        "| Configuração | Score | Hard | Sala | Currículo | H12 | Preferência | Dias | Janelas | Capacidade | Rodízio |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key, label in (
        ("baseline", "Baseline observado"),
        ("provisoria", "Baseline com salas provisórias"),
        ("sa_salas", "SA — salas"),
        ("sa_horarios", "SA — salas e horários"),
        ("sa_professores", "SA — professores (setor histórico)"),
    ):
        lines.extend(result_lines(label, results[key]))

    lines += [
        "",
        "## Validações automatizadas",
        "",
    ]
    # Uma validação de estrutura é executada para cada configuração, mas o
    # relatório lista cada tipo uma vez para permanecer legível.
    lines.extend(f"- [x] {check}" for check in dict.fromkeys(checks))
    lines += [
        "",
        "## Interpretação técnica",
        "",
        "Os solvers executaram sem depender de distância. O SA de salas pode melhorar conflitos e desperdício de capacidade, mas não pode alterar H12 porque sua vizinhança só troca salas. O SA de salas e horários também não altera professores; portanto, a carga anual permanece limitada pela atribuição histórica de entrada.",
        "",
        f"O SA de professores alterou H12 de {results['baseline']['hard']['carga_anual_insuficiente']} para {results['sa_professores']['hard']['carga_anual_insuficiente']} usando apenas professores observados no mesmo setor em 2025. Como a instância tem apenas {obligatory_count} obrigatórias para {required_obligatory} exigidas, {('H12 não pode zerar nesse recorte' if h12_infeasible else 'a viabilidade estrutural de H12 não é descartada')}; o resultado valida a vizinhança e o domínio histórico, não substitui a tabela oficial de habilitação.",
        "",
        "## Próxima etapa autorizada",
        "",
        "1. Validar com o orientador se o histórico 2025 pode ser usado como proxy de habilitação por setor.",
        "2. Validar a classificação obrigatória/optativa com as grades CC e SI.",
        "3. Substituir a prioridade neutra por dados validados pelo orientador.",
        "4. Trocar os dias observados por dias oficiais de setor quando a tabela oficial estiver fechada.",
        "5. Repetir o teste com seeds distintas somente depois de revisar esses dados.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT)


if __name__ == "__main__":
    main()
