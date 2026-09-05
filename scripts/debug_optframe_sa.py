"""Diagnóstico mínimo da avaliação e da busca BasicSA nativa em instância toy."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.test_optframe_adapter import toy_payload
from src.solve.optframe_adapter import build_engine, ProblemTimetable, SolutionTimetable

def main():
    payload = toy_payload()
    p = build_engine(payload, greedy_start=False)
    p.rng.seed(101)

    print("A: evaluate manual")
    sol = SolutionTimetable(payload)
    e = ProblemTimetable.minimize(p, sol)
    print("energia manual:", e)

    print("B: create_component_list")
    list_idx = p.engine.create_component_list("[ OptFrame:NS 0 ]", "OptFrame:NS[]")
    print("list_idx:", list_idx)

    print("C: build SA com T0 pequeno (1e5)")
    from optframe.heuristics import BasicSimulatedAnnealing
    sa = BasicSimulatedAnnealing(p.engine, 0, 0, list_idx, 0.98, 100, 1e5)
    print("D: search 0.5s")
    sout = sa.search(0.5)
    print("sout:", sout.status, sout.has_best, sout.best_e)
    print("avaliacoes:", p.evaluations)


if __name__ == "__main__":
    main()
