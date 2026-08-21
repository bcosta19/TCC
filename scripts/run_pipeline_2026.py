"""Orquestrador reproduzível da pipeline de dados de 2026.

Suporta modos --offline (padrão) e --refresh-web.
Executa a cadeia completa de extração, auditoria, construção de instâncias e tabelas de revisão.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "dados" / "brutos"
WEBSCRAP = ROOT / "webscrap"


def run_step(step_name: str, command: list[str], ignore_exit: bool = False) -> int:
    print(f"\n>>> [Pipeline 2026] Executando: {step_name} ...")
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0 and not ignore_exit:
        print(f"ERRO: Etapa '{step_name}' falhou com código de retorno {result.returncode}.", file=sys.stderr)
        sys.exit(result.returncode)
    return result.returncode


def validate_inputs(offline: bool) -> None:
    pdf1 = DATA_RAW / "QH-2026-1.pdf"
    pdf2 = DATA_RAW / "QH-2026-2.pdf"
    if not pdf1.exists() or not pdf2.exists():
        print(f"ERRO: PDFs de entrada não encontrados em {DATA_RAW} ({pdf1.name}, {pdf2.name}).", file=sys.stderr)
        sys.exit(1)

    if offline:
        web_raw = WEBSCRAP / "turmas_2026_raw.csv"
        if not web_raw.exists():
            print(f"ERRO: Modo offline requer {web_raw}.", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Orquestrador reproduzível da pipeline de 2026")
    parser.add_argument(
        "--offline",
        action="store_true",
        default=True,
        help="Executa usando apenas artefatos locais já coletados (padrão: True)",
    )
    parser.add_argument(
        "--refresh-web",
        action="store_true",
        help="Executa coleta web pública para 2026 antes de processar os dados",
    )
    args = parser.parse_args()

    is_offline = not args.refresh_web

    validate_inputs(is_offline)

    python_bin = sys.executable

    if args.refresh_web:
        scraper_script = WEBSCRAP / "scraper.py"
        if scraper_script.exists():
            run_step(
                "Coleta Web Pública 2026",
                [python_bin, str(scraper_script), "--year", "2026", "--public-only"],
            )
        else:
            print("AVISO: scraper.py não encontrado; continuando com dados locais.")

    steps = [
        ("Extração dos PDFs de 2026", [python_bin, str(ROOT / "scripts" / "extract_qh_2026.py")]),
        ("Mapeamento Curricular CC/SI", [python_bin, str(ROOT / "scripts" / "build_curriculum_mapping_2026.py")]),
        ("Vínculo PDF × Sistema Web", [python_bin, str(ROOT / "scripts" / "match_qh_web_2026.py")]),
        ("Auditoria da Instância Geral", [python_bin, str(ROOT / "scripts" / "audit_instance_2026.py")]),
        ("Construção da Instância Geral", [python_bin, str(ROOT / "scripts" / "build_instance_2026.py")]),
        ("Construção da Instância CC/SI", [python_bin, str(ROOT / "scripts" / "build_instance_2026_cc_si.py")]),
        ("Auditoria da Instância CC/SI", [python_bin, str(ROOT / "scripts" / "audit_instance_2026_cc_si.py")]),
        ("Construção das Tabelas de Revisão", [python_bin, str(ROOT / "scripts" / "build_review_tables_2026.py")]),
        ("Verificação de Prontidão", [python_bin, str(ROOT / "scripts" / "check_readiness_2026.py"), "--profile", "baseline"]),
    ]

    for step_name, cmd in steps:
        if step_name == "Verificação de Prontidão":
            # O verificador de prontidão retorna código 1 enquanto houver decisões humanas pendentes
            ret = run_step(step_name, cmd, ignore_exit=True)
            if ret != 0:
                print(
                    "\n[Pipeline 2026] Pipeline concluída com sucesso técnico. "
                    "A instância permanece marcada como 'pronta_para_experimento=false' até a conclusão das revisões humanas."
                )
        else:
            run_step(step_name, cmd)

    print("\n[Pipeline 2026] Processamento finalizado.")


if __name__ == "__main__":
    main()
