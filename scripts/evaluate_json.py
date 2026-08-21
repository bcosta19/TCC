"""Avalia uma instância JSON produzida pela pipeline."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.eval.evaluator import evaluate_json


parser = argparse.ArgumentParser(description="Avalia uma instância JSON produzida pela pipeline")
parser.add_argument(
    "instance",
    nargs="?",
    default=str(ROOT / "dados" / "processados" / "instancia_2025_cc_si.json"),
    help="Caminho para o arquivo JSON da instância",
)
parser.add_argument(
    "--allow-incomplete",
    action="store_true",
    help="Permite avaliar instâncias com pronta_para_experimento=false (apenas para auditoria/baseline)",
)
args = parser.parse_args()
result = evaluate_json(args.instance, allow_incomplete=args.allow_incomplete)
print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
