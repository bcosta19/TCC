"""Avalia a solução real registrada na planilha QH de 2025."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.eval.evaluator import evaluate_directory


result = evaluate_directory(ROOT / "dados" / "processados", profile="cc_si")
print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
