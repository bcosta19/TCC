"""Avalia a solução real registrada na planilha QH de 2025."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import argparse

parser = argparse.ArgumentParser(description="Avalia a solução real registrada nos CSVs processados")
parser.add_argument("--year", default="2025", help="Ano a ser avaliado (padrão: 2025)")
parser.add_argument("--dir", default=str(ROOT / "dados" / "processados"), help="Diretório dos CSVs")
parser.add_argument("--profile", default="cc_si", choices=["cc_si", "completo"], help="Perfil a ser avaliado")
args = parser.parse_args()

result = evaluate_directory(args.dir, profile=args.profile, year=args.year)
print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
