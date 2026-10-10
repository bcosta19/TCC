"""Atualiza as colunas de evidência das tabelas de revisão sem tocar nas decisões.

Depois de uma nova coleta (``run_pipeline_2026.py --refresh-web``), a pipeline
recusa as tabelas de revisão porque as fontes mudaram. Regenerá-las com
``--refresh-review-templates`` apagaria todas as decisões. Este script:

1. gera tabelas novas numa cópia temporária de ``dados/processados``, com o
   mesmo gerador (``build_review_tables_2026.py``);
2. em cada tabela real, atualiza só as colunas de evidência das linhas que
   continuam existindo (casadas por chave) e preserva as colunas de decisão;
3. acrescenta, com decisão vazia, as linhas novas, e remove as que sumiram
   das fontes (listadas na saída);
4. atualiza o manifesto de hashes das fontes.

Depois, reaplique as regras: ``prefill_fixed_schedules_2026.py``,
``prefill_external_references_2026.py --sobrescrever`` e
``prefill_inferences_2026.py``.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scripts.build_review_tables_2026 as generator  # noqa: E402

DATA = ROOT / "dados" / "processados"

# tabela → (chave, colunas de decisão preservadas)
TABLES: dict[str, tuple[list[str], list[str]]] = {
    "revisao_classificacao_curricular_2026.csv": (["turma_id"], ["decisao"]),
    "universo_h12_2026.csv": (["nome_normalizado"], ["incluido_h12", "observacao", "criterio_h12"]),
    "politica_cotutoria_2026.csv": (["turma_id"], ["politica_h12", "professor_responsavel", "observacao"]),
    "cadastro_salas_2026.csv": (["sala"], ["capacidade_fisica", "recursos_oficiais", "validado", "criterio_capacidade"]),
    "revisao_recursos_disciplinas_2026.csv": (
        ["codigo", "disciplina"], ["requer_laboratorio", "recursos_requeridos", "validado", "criterio_laboratorio"],
    ),
    "revisao_horarios_fixos_2026.csv": (["turma_id"], ["horario_fixo", "validado", "cursos_externos", "criterio_horario"]),
    "revisao_setores_2026.csv": (["codigo", "disciplina"], ["setor_oficial", "dias_oficiais", "validado", "criterio_setor"]),
    "revisao_habilitacao_docente_2026.csv": (
        ["codigo", "disciplina", "docente"], ["habilitado", "validado", "criterio_habilitacao"],
    ),
    "revisao_prioridades_docentes_2026.csv": (["nome_normalizado"], ["prioridade", "validado", "criterio_prioridade"]),
    "revisao_turmas_externas_2026.csv": (
        ["semestre", "codigo", "turma"],
        ["tratamento_no_modelo", "criterio_referencia", "inscritos_curso_pct", "periodo_curricular"],
    ),
}
BUILDERS = (
    "build_curricular_review",
    "build_h12_universe",
    "build_cotutoria_policy",
    "build_rooms_registry",
    "build_resources_review",
    "build_fixed_schedules_review",
    "build_sectors_review",
    "build_teacher_qualification_review",
    "build_teacher_priorities_review",
    "build_external_classes_review",
)


def merge(current: pd.DataFrame, fresh: pd.DataFrame, key: list[str], decisions: list[str]) -> tuple[pd.DataFrame, dict]:
    """Evidência de ``fresh`` + decisões de ``current``; linhas casadas pela chave."""
    current = current.drop_duplicates(subset=key, keep="first")
    kept = [column for column in decisions if column in current.columns]
    merged = fresh.drop(columns=[c for c in kept if c in fresh.columns]).merge(
        current[key + kept], on=key, how="left",
    )
    for column in kept:
        merged[column] = merged[column].fillna("")
    columns = list(current.columns) + [c for c in merged.columns if c not in current.columns]
    merged = merged[[c for c in columns if c in merged.columns]]
    old_keys = set(map(tuple, current[key].values.tolist()))
    new_keys = set(map(tuple, fresh[key].values.tolist()))
    report = {"novas": sorted(new_keys - old_keys), "removidas": sorted(old_keys - new_keys)}
    return merged, report


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp)
        for path in DATA.iterdir():
            if path.is_file() and path.suffix in {".csv", ".json"}:
                shutil.copy2(path, scratch / path.name)
        original = generator.DATA
        generator.DATA = scratch
        try:
            for name in BUILDERS:
                getattr(generator, name)()
        finally:
            generator.DATA = original
        for name, (key, decisions) in TABLES.items():
            current = pd.read_csv(DATA / name, dtype=str).fillna("")
            fresh = pd.read_csv(scratch / name, dtype=str).fillna("")
            merged, report = merge(current, fresh, key, decisions)
            merged.to_csv(DATA / name, index=False)
            changes = f"{len(report['novas'])} novas, {len(report['removidas'])} removidas"
            print(f"{name}: {len(merged)} linhas ({changes})")
            for label in ("novas", "removidas"):
                for row in report[label]:
                    print(f"  {'+' if label == 'novas' else '-'} {' | '.join(row)}")
    generator.write_review_manifest()
    print(f"{generator.REVIEW_MANIFEST.relative_to(ROOT)} atualizado")


if __name__ == "__main__":
    main()
