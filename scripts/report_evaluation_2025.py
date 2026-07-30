"""Gera um relatório legível dos conflitos da instância CC/SI de 2025."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.eval.evaluator import QHEvaluator  # noqa: E402


DATA = ROOT / "dados" / "processados"
OUT = DATA / "avaliacao_2025_cc_si.md"


def details(frame: pd.DataFrame, keys: list[str], distinct_code: bool = False):
    frame = frame[frame["sala"].fillna("").ne("")].copy() if "sala" in frame else frame.copy()
    if distinct_code:
        frame = frame.drop_duplicates(["semestre", "grupo", "codigo", "dia", "inicio", "fim"])
    groups = []
    for key, group in frame.groupby(keys, dropna=False):
        if len(group) > 1:
            groups.append((key, group.copy()))
    return groups


def main() -> None:
    turmas = pd.read_csv(DATA / "turmas_2025.csv", dtype=str).fillna("")
    horarios = pd.read_csv(DATA / "horarios_2025.csv", dtype=str).fillna("")
    rooms = pd.read_csv(DATA / "salas_2025.csv", dtype=str).fillna("")
    keep = turmas["curso"].isin({"31", "83"}) | (
        turmas["curso"].eq("") & turmas["periodo"].str.startswith(("CC-", "SI-"))
    )
    turmas = turmas[keep].copy()
    horarios = horarios[horarios["turma_id"].isin(set(turmas["id"]))].copy()
    h = horarios.merge(
        turmas[["id", "curso", "periodo", "alocacao", "disciplina", "setor", "capacidade"]],
        left_on="turma_id", right_on="id", how="left"
    )
    h["grupo"] = h["curso"] + "|" + h["periodo"].str.extract(r"(^[^-]+-P\d+)")[0].fillna("")
    evaluator = QHEvaluator(turmas, horarios, rooms).evaluate()

    room_groups = details(h, ["semestre", "dia", "inicio", "fim", "sala"])
    curricular = h[h["grupo"].str.endswith(tuple(f"-P{i}" for i in range(1, 9)))].copy()
    curricular_groups = details(
        curricular,
        ["semestre", "grupo", "dia", "inicio", "fim"],
        distinct_code=True,
    )

    lines = [
        "# Avaliação da solução real — CC/SI 2025",
        "",
        "Perfil avaliado: cursos CC (`31`) e SI (`83`), mais disciplinas com período curricular explícito `CC-P*`/`SI-P*`.",
        "",
        "## Resultado agregado",
        "",
        f"- Turmas: **{len(turmas)}**",
        f"- Encontros semanais: **{len(horarios)}**",
        f"- Violações hard: **{evaluator.hard_violations}**",
        f"- Conflitos de sala: **{evaluator.hard['conflitos_sala']} ocorrências excedentes em {len(room_groups)} grupos**",
        f"- Conflitos de professor: **{evaluator.hard['conflitos_professor']}**",
        f"- Conflitos curriculares: **{evaluator.hard['conflitos_curriculares']}**",
        f"- Recursos incompatíveis (laboratório/sala comum): **{evaluator.hard['recursos_incompativeis']}**",
        f"- Dias-professor: **{evaluator.soft['dias_trabalhados']}**",
        f"- Janelas: **{evaluator.soft['janelas']}**",
        f"- Desperdício de capacidade estimado: **{evaluator.soft['desperdicio_capacidade']} vagas**",
        f"- Distância estimada: **{evaluator.soft['distancia']} unidades**",
        f"- Repetições de professor entre semestres: **{evaluator.soft['rodizio_semestre']}**",
        "",
        "## Conflitos de sala",
        "",
        "Cada bloco abaixo representa uma sala ocupada por mais de uma turma no mesmo semestre, dia e horário.",
        "",
    ]
    for number, (key, group) in enumerate(room_groups, 1):
        codes = sorted(group["codigo"].drop_duplicates().tolist())
        kind = "turmas paralelas da mesma disciplina" if len(codes) == 1 else "disciplinas diferentes — candidato a conflito real"
        lines.append(f"### Sala conflictante {number}: `{key[-1]}` — {key[0]}, {key[1]} {key[2]}–{key[3]}")
        lines.append("")
        lines.append(f"Classificação preliminar: **{kind}**.")
        lines.append("")
        lines.append("| Código | Turma | Disciplina | Curso/período | Professor | Setor | Capacidade |")
        lines.append("|---|---|---|---|---|---|---:|")
        for _, row in group.iterrows():
            lines.append(f"| {row.codigo} | {row.turma} | {row.disciplina} | {row.curso}/{row.periodo} | {row.alocacao} | {row.setor} | {row.capacidade or '—'} |")
        lines.append("")

    lines += [
        "## Conflitos curriculares",
        "",
        "A classificação considera disciplinas de um mesmo curso e período ocupando o mesmo dia e horário. Turmas paralelas da mesma disciplina foram deduplicadas.",
        "",
    ]
    for number, (key, group) in enumerate(curricular_groups, 1):
        lines.append(f"### Conflito curricular {number}: `{key[1]}` — {key[0]}, {key[2]} {key[3]}–{key[4]}")
        lines.append("")
        lines.append("| Código | Turma | Disciplina | Professor | Sala | Setor |")
        lines.append("|---|---|---|---|---|---|")
        for _, row in group.iterrows():
            lines.append(f"| {row.codigo} | {row.turma} | {row.disciplina} | {row.alocacao} | {row.sala or '—'} | {row.setor} |")
        lines.append("")

    lines += [
        "## Interpretação e próximas verificações",
        "",
        "1. Confirmar se a mesma sala pode aparecer para turmas paralelas no quadro original; se não puder, esses casos são violações reais do baseline.",
        "2. Confirmar na regra curricular se todos os componentes de um período precisam ser cursáveis pelo mesmo aluno; isso define se os conflitos curriculares são hard.",
        "3. Excluir definitivamente pós-graduação e outros cursos da instância CC/SI antes dos experimentos.",
        "4. Adicionar capacidades das salas para ativar H10/O4.",
        "5. Substituir a capacidade estimada por capacidades físicas oficiais quando disponíveis.",
        "6. Substituir a matriz de distância estimada por medições ou coordenadas se forem obtidas.",
        "7. Confirmar as exigências de laboratório inferidas por encontro; o prefixo `L` é tratado como laboratório e prédio separado.",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
