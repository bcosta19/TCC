"""Verificador de prontidão da instância de 2026 para experimentos.

Valida os arquivos de revisão e garante que 'pronta_para_experimento' permaneça
falsa no JSON enquanto houver decisões humanas pendentes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "processados"
INSTANCE_PATH = DATA / "instancia_2026_cc_si.json"

VALID_POLITICA_COTUTORIA = {
    "integral_para_cada_docente",
    "fracionada",
    "contar_para_um_responsavel",
    "nao_contabilizar_em_h12",
}
VALID_BOOLEAN_CHOICES = {"sim", "nao", "não", "true", "false", "1", "0"}


def check_curricular_classification() -> list[str]:
    path = DATA / "revisao_classificacao_curricular_2026.csv"
    if not path.exists():
        return [f"Arquivo ausente: {path}"]
    df = pd.read_csv(path, dtype=str).fillna("")
    pendencias = []
    for _, row in df.iterrows():
        if not row.get("decisao", "").strip():
            pendencias.append(
                f"revisao_classificacao_curricular_2026.csv: turma {row.get('turma_id')} "
                f"({row.get('codigo')}) sem campo 'decisao' preenchido"
            )
    return pendencias


def check_cotutoria_policy() -> list[str]:
    path = DATA / "politica_cotutoria_2026.csv"
    if not path.exists():
        return [f"Arquivo ausente: {path}"]
    df = pd.read_csv(path, dtype=str).fillna("")
    pendencias = []
    for _, row in df.iterrows():
        pol = str(row.get("politica_h12", "")).strip().lower()
        if not pol:
            pendencias.append(
                f"politica_cotutoria_2026.csv: turma {row.get('turma_id')} sem campo 'politica_h12' preenchido"
            )
        elif pol not in VALID_POLITICA_COTUTORIA:
            pendencias.append(
                f"politica_cotutoria_2026.csv: turma {row.get('turma_id')} com política inválida '{pol}'. "
                f"Valores permitidos: {', '.join(sorted(VALID_POLITICA_COTUTORIA))}"
            )
        elif pol == "contar_para_um_responsavel":
            resp = str(row.get("professor_responsavel", "")).strip()
            profs = [p.strip() for p in str(row.get("professores", "")).split(";") if p.strip()]
            if not resp or resp not in profs:
                pendencias.append(
                    f"politica_cotutoria_2026.csv: turma {row.get('turma_id')} requer 'professor_responsavel' "
                    f"pertencente a ({', '.join(profs)})"
                )
    return pendencias


def check_h12_universe() -> list[str]:
    path = DATA / "universo_h12_2026.csv"
    if not path.exists():
        return [f"Arquivo ausente: {path}"]
    df = pd.read_csv(path, dtype=str).fillna("")
    pendencias = []
    included_count = 0
    empty_count = 0
    for _, row in df.iterrows():
        val = str(row.get("incluido_h12", "")).strip().lower()
        if not val:
            empty_count += 1
        elif val in {"sim", "true", "1"}:
            included_count += 1
        elif val in {"nao", "não", "false", "0"}:
            pass
        else:
            pendencias.append(
                f"universo_h12_2026.csv: docente {row.get('nome_normalizado')} com valor inválido '{val}'. "
                "Aceita apenas 'sim' ou 'nao'"
            )
    if empty_count > 0:
        pendencias.append(f"universo_h12_2026.csv: {empty_count} docentes com campo 'incluido_h12' vazio")

    # Condição estrutural: máximo 49 docentes com 3 obrigatórias
    if included_count > 49:
        pendencias.append(
            f"universo_h12_2026.csv: {included_count} docentes marcados como 'sim', mas 149 obrigatórias "
            "comportam no máximo 49 docentes recebendo três obrigatórias"
        )
    return pendencias


def check_rooms_registry() -> list[str]:
    path = DATA / "cadastro_salas_2026.csv"
    if not path.exists():
        return [f"Arquivo ausente: {path}"]
    df = pd.read_csv(path, dtype=str).fillna("")
    pendencias = []
    for _, row in df.iterrows():
        cap = str(row.get("capacidade_fisica", "")).strip()
        val = str(row.get("validado", "")).strip().lower()
        if not cap:
            pendencias.append(f"cadastro_salas_2026.csv: sala {row.get('sala')} sem 'capacidade_fisica'")
        else:
            try:
                num = int(cap)
                if num <= 0:
                    pendencias.append(f"cadastro_salas_2026.csv: sala {row.get('sala')} com capacidade física não positiva: {cap}")
            except ValueError:
                pendencias.append(f"cadastro_salas_2026.csv: sala {row.get('sala')} com capacidade física inválida: {cap}")
        if val not in {"sim", "true", "1"}:
            pendencias.append(f"cadastro_salas_2026.csv: sala {row.get('sala')} não validada")
    return pendencias


def check_resources_review() -> list[str]:
    path = DATA / "revisao_recursos_disciplinas_2026.csv"
    if not path.exists():
        return [f"Arquivo ausente: {path}"]
    df = pd.read_csv(path, dtype=str).fillna("")
    pendencias = []
    for _, row in df.iterrows():
        req = str(row.get("requer_laboratorio", "")).strip().lower()
        val = str(row.get("validado", "")).strip().lower()
        if not req:
            pendencias.append(f"revisao_recursos_disciplinas_2026.csv: disciplina {row.get('codigo')} sem 'requer_laboratorio'")
        elif req not in VALID_BOOLEAN_CHOICES:
            pendencias.append(f"revisao_recursos_disciplinas_2026.csv: disciplina {row.get('codigo')} com 'requer_laboratorio' inválido: {req}")
        if val not in {"sim", "true", "1"}:
            pendencias.append(f"revisao_recursos_disciplinas_2026.csv: disciplina {row.get('codigo')} não validada")
    return pendencias


def check_fixed_schedules() -> list[str]:
    path = DATA / "revisao_horarios_fixos_2026.csv"
    if not path.exists():
        return [f"Arquivo ausente: {path}"]
    df = pd.read_csv(path, dtype=str).fillna("")
    pendencias = []
    for _, row in df.iterrows():
        fixo = str(row.get("horario_fixo", "")).strip().lower()
        val = str(row.get("validado", "")).strip().lower()
        if not fixo:
            pendencias.append(f"revisao_horarios_fixos_2026.csv: turma {row.get('turma_id')} sem 'horario_fixo'")
        elif fixo not in VALID_BOOLEAN_CHOICES:
            pendencias.append(f"revisao_horarios_fixos_2026.csv: turma {row.get('turma_id')} com 'horario_fixo' inválido: {fixo}")
        if val not in {"sim", "true", "1"}:
            pendencias.append(f"revisao_horarios_fixos_2026.csv: turma {row.get('turma_id')} não validada")
    return pendencias


def check_sectors_review() -> list[str]:
    path = DATA / "revisao_setores_2026.csv"
    if not path.exists():
        return [f"Arquivo ausente: {path}"]
    df = pd.read_csv(path, dtype=str).fillna("")
    pendencias = []
    for _, row in df.iterrows():
        setor = str(row.get("setor_oficial", "")).strip()
        val = str(row.get("validado", "")).strip().lower()
        if not setor:
            pendencias.append(f"revisao_setores_2026.csv: disciplina {row.get('codigo')} sem 'setor_oficial'")
        if val not in {"sim", "true", "1"}:
            pendencias.append(f"revisao_setores_2026.csv: disciplina {row.get('codigo')} não validada")
    return pendencias


def check_teacher_qualifications() -> list[str]:
    path = DATA / "revisao_habilitacao_docente_2026.csv"
    if not path.exists():
        return [f"Arquivo ausente: {path}"]
    df = pd.read_csv(path, dtype=str).fillna("")
    pendencias = []
    for _, row in df.iterrows():
        hab = str(row.get("habilitado", "")).strip().lower()
        val = str(row.get("validado", "")).strip().lower()
        if not hab:
            pendencias.append(f"revisao_habilitacao_docente_2026.csv: par ({row.get('codigo')}, {row.get('docente')}) sem 'habilitado'")
        elif hab not in VALID_BOOLEAN_CHOICES:
            pendencias.append(f"revisao_habilitacao_docente_2026.csv: par ({row.get('codigo')}, {row.get('docente')}) com 'habilitado' inválido: {hab}")
        if val not in {"sim", "true", "1"}:
            pendencias.append(f"revisao_habilitacao_docente_2026.csv: par ({row.get('codigo')}, {row.get('docente')}) não validado")
    return pendencias


def check_teacher_priorities() -> list[str]:
    path = DATA / "revisao_prioridades_docentes_2026.csv"
    if not path.exists():
        return [f"Arquivo ausente: {path}"]
    df = pd.read_csv(path, dtype=str).fillna("")
    pendencias = []
    for _, row in df.iterrows():
        prio = str(row.get("prioridade", "")).strip()
        val = str(row.get("validado", "")).strip().lower()
        if not prio:
            pendencias.append(f"revisao_prioridades_docentes_2026.csv: docente {row.get('nome_normalizado')} sem 'prioridade'")
        else:
            try:
                num = float(prio)
                if num < 0:
                    pendencias.append(f"revisao_prioridades_docentes_2026.csv: docente {row.get('nome_normalizado')} com prioridade negativa: {prio}")
            except ValueError:
                pendencias.append(f"revisao_prioridades_docentes_2026.csv: docente {row.get('nome_normalizado')} com prioridade inválida: {prio}")
        if val not in {"sim", "true", "1"}:
            pendencias.append(f"revisao_prioridades_docentes_2026.csv: docente {row.get('nome_normalizado')} não validado")
    return pendencias


def check_external_classes() -> list[str]:
    path = DATA / "revisao_turmas_externas_2026.csv"
    if not path.exists():
        return [f"Arquivo ausente: {path}"]
    df = pd.read_csv(path, dtype=str).fillna("")
    pendencias = []
    for _, row in df.iterrows():
        trat = str(row.get("tratamento_no_modelo", "")).strip()
        if not trat:
            pendencias.append(f"revisao_turmas_externas_2026.csv: oferta {row.get('codigo')} turma {row.get('turma')} sem 'tratamento_no_modelo'")
    return pendencias


def update_instance_readiness(is_ready: bool) -> None:
    if not INSTANCE_PATH.exists():
        return
    payload = json.loads(INSTANCE_PATH.read_text(encoding="utf-8"))
    payload["pronta_para_experimento"] = bool(is_ready)
    INSTANCE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def check_profile(profile: str) -> tuple[bool, list[str]]:
    pendencias = []
    if profile in {"baseline", "professores", "salas", "completo"}:
        pendencias.extend(check_curricular_classification())
        pendencias.extend(check_cotutoria_policy())
        pendencias.extend(check_fixed_schedules())

    if profile in {"professores", "completo"}:
        pendencias.extend(check_h12_universe())
        pendencias.extend(check_sectors_review())
        pendencias.extend(check_teacher_qualifications())
        pendencias.extend(check_teacher_priorities())

    if profile in {"salas", "completo"}:
        pendencias.extend(check_rooms_registry())
        pendencias.extend(check_resources_review())

    if profile in {"completo"}:
        pendencias.extend(check_external_classes())

    is_ready = len(pendencias) == 0
    update_instance_readiness(is_ready)
    return is_ready, pendencias


def main() -> None:
    parser = argparse.ArgumentParser(description="Verificador de prontidão dos dados de 2026")
    parser.add_argument(
        "--profile",
        choices=["baseline", "professores", "salas", "completo"],
        default="completo",
        help="Perfil de validação da instância (default: completo)",
    )
    args = parser.parse_args()

    is_ready, pendencias = check_profile(args.profile)

    print(f"=== Verificação de Prontidão 2026 (perfil: {args.profile}) ===")
    if is_ready:
        print("Status: PRONTA PARA EXPERIMENTO (todas as validações do perfil foram concluídas)")
        sys.exit(0)
    else:
        print(f"Status: NÃO PRONTA PARA EXPERIMENTO ({len(pendencias)} pendência(s) encontrada(s))")
        print("\nPrincipais pendências:")
        for p in pendencias[:20]:
            print(f"  - {p}")
        if len(pendencias) > 20:
            print(f"  ... e mais {len(pendencias) - 20} pendências.")
        print(f"\nConsulte dados/processados/PENDENCIAS_VALIDACAO_2026.md para instruções de preenchimento.")
        sys.exit(1)


if __name__ == "__main__":
    main()
