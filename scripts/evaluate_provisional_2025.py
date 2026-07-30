"""Avalia a variante provisória com salas reparadas."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.eval.evaluator import evaluate_directory

result = evaluate_directory(ROOT / "dados" / "processados" / "provisoria_2025", profile="cc_si")
print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
