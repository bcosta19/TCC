"""Executa o solver experimental de salas e horários."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.solve.schedule_sa import solve_file


parser = argparse.ArgumentParser(description="Executa o solver de salas e horários flexíveis")
parser.add_argument("--input", default=str(ROOT / "dados" / "processados" / "instancia_2025_cc_si_flex.json"))
parser.add_argument("--output", default=str(ROOT / "dados" / "processados" / "solucao_horarios_sa_2025.json"))
parser.add_argument("--iterations", type=int, default=1000)
parser.add_argument("--seed", type=int, default=2025)
parser.add_argument("--allow-incomplete", action="store_true", help="Permite rodar sobre instâncias com pronta_para_experimento=false")
args = parser.parse_args()
metadata = solve_file(args.input, args.output, args.iterations, args.seed, allow_incomplete=args.allow_incomplete)
print(json.dumps(metadata, ensure_ascii=False, indent=2))
