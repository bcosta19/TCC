"""Orquestrador reproduzível da pipeline de dados de 2026.

Suporta modos --offline (padrão) e --refresh-web.
Executa a cadeia completa de extração, auditoria, construção de instâncias e tabelas de revisão.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "dados" / "brutos"
WEBSCRAP = ROOT / "webscrap"
REVIEW_FILES = (
    "revisao_classificacao_curricular_2026.csv",
    "universo_h12_2026.csv",
    "politica_cotutoria_2026.csv",
    "cadastro_salas_2026.csv",
    "revisao_recursos_disciplinas_2026.csv",
    "revisao_horarios_fixos_2026.csv",
    "revisao_setores_2026.csv",
    "revisao_habilitacao_docente_2026.csv",
    "revisao_prioridades_docentes_2026.csv",
    "revisao_turmas_externas_2026.csv",
    "revisoes_2026_manifest.json",
)


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


def csv_values(path: Path, column: str) -> set[str]:
    with path.open(encoding="utf-8", newline="") as file:
        return {str(row.get(column, "")).strip() for row in csv.DictReader(file) if str(row.get(column, "")).strip()}


def validate_review_coverage() -> None:
    """Impede usar revisoes que nao cobrem mais as turmas e salas da instancia."""
    data = ROOT / "dados" / "processados"
    instance_path = data / "instancia_2026_cc_si.json"
    if not instance_path.exists():
        return
    payload = json.loads(instance_path.read_text(encoding="utf-8"))
    expected_classes = {str(item.get("id", "")) for item in payload.get("classes", [])}
    expected_rooms = {str(item.get("id", "")) for item in payload.get("rooms", [])}
    reviewed_classes = csv_values(data / "revisao_horarios_fixos_2026.csv", "turma_id")
    reviewed_rooms = csv_values(data / "cadastro_salas_2026.csv", "sala")
    manifest_path = data / "revisoes_2026_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = []
    if reviewed_classes != expected_classes:
        errors.append(
            f"revisao_horarios_fixos_2026.csv difere da instancia "
            f"({len(reviewed_classes)} revisadas, {len(expected_classes)} esperadas)"
        )
    if reviewed_rooms != expected_rooms:
        errors.append(
            f"cadastro_salas_2026.csv difere da instancia "
            f"({len(reviewed_rooms)} revisadas, {len(expected_rooms)} esperadas)"
        )
    for relative_path, expected_hash in manifest.get("sources", {}).items():
        source_path = ROOT / relative_path
        if not source_path.exists():
            errors.append(f"fonte ausente desde a revisao: {relative_path}")
            continue
        current_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if current_hash != expected_hash:
            errors.append(f"fonte alterada desde a revisao: {relative_path}")
    if errors:
        print("ERRO: tabelas de revisao obsoletas; nenhuma decisao foi sobrescrita.", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print("Revise as fontes e use --refresh-review-templates somente com confirmacao humana.", file=sys.stderr)
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
    parser.add_argument(
        "--refresh-review-templates",
        action="store_true",
        help="Recria tabelas de revisão e apaga campos decisórios existentes",
    )
    args = parser.parse_args()

    is_offline = not args.refresh_web

    validate_inputs(is_offline)

    python_bin = sys.executable

    if args.refresh_web:
        scraper_script = WEBSCRAP / "scrape_2026.py"
        if scraper_script.exists():
            run_step(
                "Coleta Web Pública 2026",
                [python_bin, str(scraper_script)],
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
        ("Verificação de Prontidão", [python_bin, str(ROOT / "scripts" / "check_readiness_2026.py"), "--profile", "baseline"]),
    ]

    existing_review_files = [
        name for name in REVIEW_FILES
        if (ROOT / "dados" / "processados" / name).exists()
    ]
    if existing_review_files and len(existing_review_files) != len(REVIEW_FILES) and not args.refresh_review_templates:
        missing = sorted(set(REVIEW_FILES) - set(existing_review_files))
        print(
            "ERRO: conjunto parcial de tabelas de revisao; arquivos existentes foram preservados.",
            file=sys.stderr,
        )
        for name in missing:
            print(f"  - ausente: dados/processados/{name}", file=sys.stderr)
        print("Restaure os arquivos ausentes ou use --refresh-review-templates conscientemente.", file=sys.stderr)
        sys.exit(1)
    if args.refresh_review_templates or not existing_review_files:
        steps.insert(
            -1,
            ("Construção das Tabelas de Revisão", [python_bin, str(ROOT / "scripts" / "build_review_tables_2026.py")]),
        )
    else:
        print("[Pipeline 2026] Tabelas de revisão existentes serão preservadas.")

    for step_name, cmd in steps:
        if step_name == "Verificação de Prontidão":
            validate_review_coverage()
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
