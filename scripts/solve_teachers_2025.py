"""Executa o SA experimental de professores."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.solve.teacher_sa import solve_file  # noqa: E402


parser = argparse.ArgumentParser(description="Executa o SA para professores")
parser.add_argument("--input", default=str(ROOT / "dados" / "processados" / "instancia_2025_cc_si.json"))
parser.add_argument("--output", default=str(ROOT / "dados" / "processados" / "solucao_professores_sa_2025.json"))
parser.add_argument("--iterations", type=int, default=5000)
parser.add_argument("--seed", type=int, default=2025)
parser.add_argument(
    "--allow-unrestricted",
    action="store_true",
    help="teste de estresse: ignora professores_habilitados e usa todos os professores IC",
)
parser.add_argument(
    "--allow-incomplete",
    action="store_true",
    help="Permite rodar sobre instâncias com pronta_para_experimento=false",
)
args = parser.parse_args()
metadata = solve_file(
    args.input,
    args.output,
    iterations=args.iterations,
    seed=args.seed,
    allow_unrestricted=args.allow_unrestricted,
    allow_incomplete=args.allow_incomplete,
)
print(json.dumps(metadata, ensure_ascii=False, indent=2))
