"""Adaptador pyoptframe para o solver integrado do TCC.

Embrulha o payload JSON e as funcoes de ``src.solve.integrated`` nos
protocolos XSolution/XProblem/XConstructive/XMinimize/XMove/XNS do OptFrame,
permitindo executar o BasicSA nativo sobre a
mesma representacao e o mesmo avaliador das implementacoes de referencia.

Notas de projeto:
- A funcao objetivo e o ``search_energy`` de referencia (escalar
  lexicografico: hard * 1e9 + deficit H12 * 1e6 + soft). Como a escala e
  grande, a temperatura inicial (T0) precisa ser calibrada nessa escala.
- O criterio de parada do OptFrame e TEMPO (segundos), nao orcamento de
  avaliacoes. O contador ``ProblemTimetable.evaluations`` registra quantas
  avaliacoes ocorreram, para reporte no protocolo experimental.
- A semente controla a vizinhanca Python; o RNG interno do motor nativo
  nao e configurado por este adaptador. Nao prometer determinismo completo.
- A solucao inicial e gerada pelo construtivo registrado no engine; por
  padrao, ``generateSolution`` executa a passagem gulosa integrada
  (``greedy_improve``), mantendo o fluxo do benchmark de referencia.
- Nao usar `from __future__ import annotations` neste modulo: o engine
  inspeciona ``inspect.signature(NS.randomMove).return_annotation`` e exige a
  CLASSE do movimento (nao uma string) para registrar a vizinhanca.
"""

import copy
import math
import random
from typing import Optional

from optframe import Engine
from optframe.components import Move
from optframe.core import LogLevel
from optframe.heuristics import BasicSimulatedAnnealing

from src.solve.direct_objective import evaluate
from src.solve.validation import validate_solution
from src.solve.integrated import (
    apply_move,
    greedy_improve,
    propose_move,
    search_energy,
)


# ---------------------------------------------------------------------------
# Solucao e problema
# ---------------------------------------------------------------------------


class SolutionTimetable:
    """XSolution: embrulha o payload JSON do TCC."""

    def __init__(self, payload: dict):
        self.payload = payload

    def __str__(self) -> str:
        return f"SolutionTimetable(classes={len(self.payload.get('classes', []))})"


class ProblemTimetable:
    """XProblem + XConstructive + XMinimize sobre o payload do TCC."""

    def __init__(self, payload: dict, greedy_start: bool = True, max_candidates: int = 6):
        self.engine = Engine()
        self.base = copy.deepcopy(payload)
        self.greedy_start = greedy_start
        self.max_candidates = max_candidates
        self.evaluations = 0
        self.rng = random.Random()  # semeado por solve_sa_optframe

    @staticmethod
    def minimize(p: "ProblemTimetable", s: SolutionTimetable) -> float:
        p.evaluations += 1
        return search_energy(evaluate(s.payload))

    @staticmethod
    def generateSolution(p: "ProblemTimetable") -> SolutionTimetable:
        if p.greedy_start:
            solution, _meta = greedy_improve(copy.deepcopy(p.base), p.max_candidates)
        else:
            solution = copy.deepcopy(p.base)
        return SolutionTimetable(solution)


# ---------------------------------------------------------------------------
# Movimentos (uma unica classe Move: o engine inspeciona a anotacao de
# retorno de randomMove e exige um tipo concreto de XMove por NS)
# ---------------------------------------------------------------------------


class MoveTCC(Move):
    """Move unificado (teacher/schedule/room) com undo reversivel."""

    def __init__(self, move: Optional[dict] = None, undo: Optional[dict] = None):
        self.move = dict(move) if move else None  #None = no-op identidade
        self.undo = undo  # preenchido quando este Move e o reverso

    def __str__(self) -> str:
        if self.move is None:
            return "MoveTCC(noop)"
        return f"MoveTCC({self.move})"

    def apply(self, problemCtx: ProblemTimetable, sol: SolutionTimetable) -> "MoveTCC":
        if self.move is None:
            return MoveTCC(None, None)
        if self.undo is not None:
            # Este Move carrega um undo pendente: aplica o undo e devolve
            # o reverso que refaz o movimento original.
            reverse_undo = apply_move(sol.payload, self.undo)
            return MoveTCC(self.move, reverse_undo)
        reverse_undo = apply_move(sol.payload, self.move)
        return MoveTCC(self.move, reverse_undo)

    def canBeApplied(self, problemCtx: ProblemTimetable, sol: SolutionTimetable) -> bool:
        return True

    def eq(self, problemCtx: ProblemTimetable, m2: "MoveTCC") -> bool:
        return self.move == m2.move and self.undo == m2.undo


class NSIntegrated:
    @staticmethod
    def randomMove(p: ProblemTimetable, sol: SolutionTimetable) -> MoveTCC:
        move = propose_move(sol.payload, p.rng)
        if move is None:
            # Nenhum movimento disponivel: no-op identidade.
            return MoveTCC(None, None)
        return MoveTCC(move, None)


# ---------------------------------------------------------------------------
# Montagem do engine e busca
# ---------------------------------------------------------------------------


def build_engine(payload: dict, greedy_start: bool = True, max_candidates: int = 6):
    """Registra problema (avaliador + construtivo) e vizinhanca no engine."""
    p = ProblemTimetable(payload, greedy_start=greedy_start, max_candidates=max_candidates)
    # setup() registra evaluator, constructive e InitialSearch — necessario
    # para o BasicSA (str_args referencia GeneralEvaluator e InitialSearch).
    p.engine.setup(p)
    p.engine.add_ns_class(p, NSIntegrated)
    return p


def solve_sa_optframe(
    payload: dict,
    seed: int,
    seconds: float,
    alpha: float = 0.98,
    iter_max: int = 100,
    t0: float = 1e8,
    greedy_start: bool = True,
    max_candidates: int = 6,
) -> tuple[dict, dict, dict]:
    """Executa o BasicSA nativo do OptFrame sobre o payload do TCC.

    Retorna (solucao, avaliacao_de_referencia, metadados), no mesmo espírito
    de ``integrated.SearchResult``.
    """
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("O limite de tempo deve ser positivo e finito")
    if not 0 < alpha < 1 or iter_max < 1 or not math.isfinite(t0) or t0 <= 0:
        raise ValueError("Parametros invalidos: 0 < alpha < 1, iter_max >= 1 e t0 > 0")
    # Erros Python dentro de callbacks ctypes nao se propagam com seguranca.
    search_energy(evaluate(payload))
    validate_solution(payload, payload)
    p = build_engine(payload, greedy_start=greedy_start, max_candidates=max_candidates)
    p.rng.seed(seed)

    list_idx = p.engine.create_component_list("[ OptFrame:NS 0 ]", "OptFrame:NS[]")

    sa = BasicSimulatedAnnealing(p.engine, 0, 0, list_idx, alpha, iter_max, t0)
    sout = sa.search(seconds)

    best_s = getattr(sout, "best_s", None)
    if best_s is None:
        raise RuntimeError("BasicSA nao retornou solucao; aumente o limite de tempo")
    best_payload = best_s.payload
    evaluation = evaluate(best_payload)

    metadata = {
        "algorithm": "sa_optframe",
        "seed": seed,
        "seed_scope": "vizinhanca Python; RNG interno do OptFrame nao configurado",
        "seconds": seconds,
        "alpha": alpha,
        "iter_max": iter_max,
        "t0": t0,
        "engine_evaluations": p.evaluations,
        "engine_best_energy": getattr(sout, "best_e", None),
    }
    return best_payload, evaluation, metadata
