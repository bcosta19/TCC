"""Pré-preenche as tabelas de revisão de 2026 por inferência (HP3–HP7) e decisões de 10/10/2026.

Hipóteses provisórias propostas pelo aluno em 10/10/2026
(``anotacoes/hipoteses_provisorias_2026_10_10.md``), pendentes de validação do
orientador:

- HP3 — capacidade da sala: ``capacidade_fisica`` recebe o maior número de
  vagas entre as turmas alocadas na sala em 2026
  (``capacidade_minima_observada``). É um limite inferior: a alocação
  observada respeita H10 por construção.
- HP4 — laboratório: a disciplina requer laboratório quando alguma turma dela
  teve encontro em sala de laboratório (identificador iniciado por "L"). Se a
  disciplina também usou sala comum, o builder só exige laboratório nos
  encontros observados em laboratório.
- HP5 — setor: o setor da planilha QH 2025 (``setor_historico_2025``) quando
  existe; senão, o setor das disciplinas de mesmo assunto
  (``SETOR_POR_AFINIDADE``), com a confiança registrada no critério.
- HP6 — habilitação: o docente é habilitado nas disciplinas que deu em 2025
  ou 2026 (cada linha da tabela é um desses pares). Nomes fora do cadastro
  docente (artefatos da planilha 2025, como "FECHADA") ficam ``nao``.

- HP7 — universo de H12: docente na página de docentes do IC/UFF
  (``dados/brutos/docentes_ic_2026.csv``) com cargo de carreira permanente
  (auxiliar, assistente, adjunto, associado, titular) entra em H12; quem não
  está na página fica fora. A página não é um cadastro completo, então
  exceções conhecidas são registradas como decisão manual.

Decisões do aluno em 10/10/2026, aplicadas pelo mesmo script:

- prioridade uniforme: todos os docentes com ``prioridade=1`` (a lista
  ordenada de prioridade sai do escopo);
- optativas de outros departamentos sem tratamento em
  ``revisao_turmas_externas_2026.csv`` ficam ``ignorar_fora_do_ic``; turmas do
  IC ausentes do PDF do QH ficam ``ignorar_fora_do_pdf``.

As tabelas têm uma linha por par (código, nome da disciplina), mas o builder
indexa por código; por isso laboratório e setor são decididos por código e
repetidos em todas as linhas dele.

As linhas recebem ``validado=sim`` e a evidência fica em ``criterio_*``,
começando por ``HP`` ou ``decisão 10/10/2026``. Linhas validadas manualmente
(``validado=sim`` e critério sem esses prefixos) não são alteradas, salvo com
``--sobrescrever``.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.eval.preferences import normalize_name  # noqa: E402

DATA = ROOT / "dados" / "processados"
ROOMS = DATA / "cadastro_salas_2026.csv"
RESOURCES = DATA / "revisao_recursos_disciplinas_2026.csv"
SECTORS = DATA / "revisao_setores_2026.csv"
QUALIFICATIONS = DATA / "revisao_habilitacao_docente_2026.csv"
H12_UNIVERSE = DATA / "universo_h12_2026.csv"
IC_FACULTY = ROOT / "dados" / "brutos" / "docentes_ic_2026.csv"
PERMANENT_RE = re.compile(r"^Prof(?:a|essor|essora)?\.?\s+(Auxiliar|Assistente|Adjunt[oa]|Associad[oa]|Titular)\b", re.IGNORECASE)
NAME_STOPWORDS = {"DE", "DA", "DO", "DOS", "DAS", "E"}
PRIORITIES = DATA / "revisao_prioridades_docentes_2026.csv"
EXTERNAL = DATA / "revisao_turmas_externas_2026.csv"
RULE_DATE = "10/10/2026"
DECISION = f"decisão {RULE_DATE}"

# Disciplinas sem setor na planilha QH 2025: setor de disciplinas de mesmo
# assunto, só entre os setores que existem em 2025 (os padrões de dias do
# domínio de horários vêm deles). Confiança "baixa" marca escolhas que o
# orientador deve conferir primeiro.
SETOR_POR_AFINIDADE: dict[str, tuple[str, str, str]] = {
    "CGI00004": ("GER.SIST.TI", "media", "seminários de SI; turma externa de horário fixo"),
    "TCC00194": ("ALG.CPX.", "baixa", "algoritmos aplicados à biologia; também caberia em IA ou COMP.NUM."),
    "TCC00195": ("ALG.CPX.", "alta", "otimização, mesmo setor de Pesquisa Operacional (TCC00318)"),
    "TCC00196": ("ALG.CPX.", "alta", "otimização combinatória, mesmo setor de Pesquisa Operacional (TCC00318)"),
    "TCC00200": ("B.D.", "media", "dados; também caberia em IA"),
    "TCC00203": ("COMP.VIS.JOGOS", "alta", "imagens, mesmo setor de Computação Gráfica (TCC00291)"),
    "TCC00205": ("LING.TEOR.", "alta", "linguagens de programação, mesmo setor de TCC00304"),
    "TCC00230": ("REDES", "alta", "segurança, mesmo setor de Segurança da Informação (TCC00341)"),
    "TCC00234": ("ARQ.SO.", "alta", "arquitetura, mesmo setor de Arquiteturas de Computadores (TCC00286)"),
    "TCC00237": ("ARQ.SO.", "baixa", "robótica e sistemas embarcados; também caberia em IA ou COMP.VIS.JOGOS"),
    "TCC00241": ("ALG.CPX.", "baixa", "tópicos de tema variável: Grafos (ALG.CPX.) em uma oferta, Visão Computacional (COMP.VIS.JOGOS) em outra"),
    "TCC00242": ("COMP.NUM.", "baixa", "tópicos de tema variável: Álgebra Linear Computacional em uma oferta, outra sem tema"),
    "TCC00243": ("ALG.CPX.", "alta", "algoritmos e complexidade"),
    "TCC00244": ("B.D.", "alta", "tópicos em banco de dados"),
    "TCC00245": ("B.D.", "alta", "tópicos em banco de dados"),
    "TCC00250": ("ENG.SOFT.", "media", "tópicos em engenharia de software; o tema Game Analytics é próximo de COMP.VIS.JOGOS"),
    "TCC00251": ("ENG.SOFT.", "alta", "tópicos em engenharia de software"),
    "TCC00252": ("ENG.SOFT.", "alta", "tópicos em engenharia de software"),
    "TCC00253": ("LING.TEOR.", "baixa", "sistemas de programação; também caberia em ESTR.PROG."),
    "TCC00259": ("IA", "alta", "tópicos em inteligência artificial"),
    "TCC00260": ("IA", "alta", "tópicos em inteligência artificial"),
    "TCC00265": ("IHC", "alta", "tópicos em interface homem-máquina"),
    "TCC00271": ("LING.TEOR.", "media", "tópicos em linguagens de programação; o tema Lógica Nebulosa é próximo de IA"),
    "TCC00280": ("GER.SIST.TI", "media", "mesmo perfil de Computação e Sociedade (TCC00290)"),
    "TCC00371": ("IA", "baixa", "assunto de IA; perfil próximo de Computação e Sociedade (GER.SIST.TI)"),
    "TCC00357": ("ENG.SOFT.", "alta", "POO, mesmo setor de TCC00328; na planilha 2025 aparece 2× em ENG.SOFT. e 1× em ALG.CPX. (turma X1)"),
}


def is_true(value: object) -> bool:
    return str(value or "").strip().lower() in {"sim", "true", "1"}


def manual(row: pd.Series, column: str) -> bool:
    return is_true(row.get("validado")) and not str(row.get(column, "")).startswith(("HP", DECISION))


def ensure_column(table: pd.DataFrame, column: str) -> pd.DataFrame:
    table = table.copy()
    if column not in table.columns:
        table[column] = ""
    return table


def prefill_rooms(table: pd.DataFrame, overwrite: bool = False) -> pd.DataFrame:
    column = "criterio_capacidade"
    table = ensure_column(table, column)
    for index, row in table.iterrows():
        if manual(row, column) and not overwrite:
            continue
        try:
            observed = int(float(row.get("capacidade_minima_observada", "")))
        except ValueError:
            continue
        if observed <= 0:
            continue
        table.at[index, "capacidade_fisica"] = str(observed)
        table.at[index, column] = f"HP3 {RULE_DATE}: maior número de vagas entre as turmas alocadas na sala em 2026"
        table.at[index, "validado"] = "sim"
    return table


def prefill_resources(table: pd.DataFrame, overwrite: bool = False) -> pd.DataFrame:
    column = "criterio_laboratorio"
    table = ensure_column(table, column)
    kinds: dict[str, set[str]] = defaultdict(set)
    for _, row in table.iterrows():
        if is_true(row.get("usou_laboratorio")):
            kinds[row["codigo"]].add("laboratorio")
        if is_true(row.get("usou_sala_comum")):
            kinds[row["codigo"]].add("comum")
    for index, row in table.iterrows():
        if manual(row, column) and not overwrite:
            continue
        used = kinds.get(row["codigo"], set())
        if not used:
            continue
        if used == {"laboratorio"}:
            needs, reason = "sim", "todos os encontros observados em laboratório"
        elif "laboratorio" in used:
            needs, reason = "sim", "alternou laboratório e sala comum: laboratório só nos encontros observados em laboratório"
        else:
            needs, reason = "nao", "nenhum encontro observado em laboratório"
        table.at[index, "requer_laboratorio"] = needs
        table.at[index, column] = f"HP4 {RULE_DATE}: {reason}"
        table.at[index, "validado"] = "sim"
    return table


def prefill_sectors(table: pd.DataFrame, overwrite: bool = False) -> pd.DataFrame:
    column = "criterio_setor"
    table = ensure_column(table, column)
    historical: dict[str, str] = {}
    for _, row in table.iterrows():
        sector = str(row.get("setor_historico_2025", "")).strip()
        if sector:
            historical.setdefault(row["codigo"], sector)
    for index, row in table.iterrows():
        if manual(row, column) and not overwrite:
            continue
        code = row["codigo"]
        if code in historical:
            sector, reason = historical[code], "setor da planilha QH 2025"
        elif code in SETOR_POR_AFINIDADE:
            sector, confidence, why = SETOR_POR_AFINIDADE[code]
            reason = f"afinidade de assunto (confiança {confidence}): {why}"
        else:
            continue
        table.at[index, "setor_oficial"] = sector
        table.at[index, column] = f"HP5 {RULE_DATE}: {reason}"
        table.at[index, "validado"] = "sim"
    return table


def prefill_qualifications(table: pd.DataFrame, roster: set[str], overwrite: bool = False) -> pd.DataFrame:
    column = "criterio_habilitacao"
    table = ensure_column(table, column)
    for index, row in table.iterrows():
        if manual(row, column) and not overwrite:
            continue
        if row["docente"] not in roster:
            enabled, reason = "nao", "nome fora do cadastro docente (carga 2025 e QH 2026); artefato da planilha 2025"
        elif is_true(row.get("observado_2026")):
            enabled, reason = "sim", "deu a disciplina em 2026"
        else:
            enabled, reason = "sim", "deu a disciplina em 2025"
        table.at[index, "habilitado"] = enabled
        table.at[index, column] = f"HP6 {RULE_DATE}: {reason}"
        table.at[index, "validado"] = "sim"
    return table


def prefill_priorities(table: pd.DataFrame, overwrite: bool = False) -> pd.DataFrame:
    column = "criterio_prioridade"
    table = ensure_column(table, column)
    for index, row in table.iterrows():
        if manual(row, column) and not overwrite:
            continue
        table.at[index, "prioridade"] = "1"
        table.at[index, column] = f"{DECISION}: prioridade uniforme, lista ordenada de prioridade fora do escopo"
        table.at[index, "validado"] = "sim"
    return table


def prefill_external(table: pd.DataFrame, overwrite: bool = False) -> pd.DataFrame:
    """Trata as ofertas da coleta web ainda sem tratamento.

    Outros departamentos → ``ignorar_fora_do_ic``. Turmas do IC que não estão no
    PDF do QH (seções Z1 de 1–3 vagas, seções extras X1, tópicos abertos depois)
    → ``ignorar_fora_do_pdf``: a instância parte do planejamento oficial.
    """
    column = "criterio_referencia"
    table = ensure_column(table, column)
    for index, row in table.iterrows():
        current = str(row.get("tratamento_no_modelo", "")).strip()
        owned = str(row.get(column, "")).startswith(DECISION)
        if current and not (owned or overwrite):
            continue
        if str(row["codigo"]).startswith("TCC"):
            table.at[index, "tratamento_no_modelo"] = "ignorar_fora_do_pdf"
            table.at[index, column] = f"{DECISION}: turma do IC fora do PDF do QH, que é a base do planejamento"
        else:
            table.at[index, "tratamento_no_modelo"] = "ignorar_fora_do_ic"
            table.at[index, column] = f"{DECISION}: optativa de outro departamento, fora de H8 e das salas do IC"
    return table


def name_tokens(name: str) -> set[str]:
    return {token for token in normalize_name(name).split() if len(token) > 1 and token not in NAME_STOPWORDS}


def match_faculty(full_name: str, alias: str, faculty: pd.DataFrame) -> int | None:
    """Índice do docente da página do IC com o mesmo nome; ``None`` se não houver um único candidato.

    Casa primeiro o nome completo normalizado; depois, nomes em que um conjunto
    de palavras contém o outro (ex.: "Raphael Guerra" × "Raphael P. de Oliveira
    Guerra"), desempatando pela maior sobreposição.
    """
    exact = [index for index, name in faculty["nome"].items() if normalize_name(name) == normalize_name(full_name)]
    if len(exact) == 1:
        return exact[0]
    scored = []
    for index, name in faculty["nome"].items():
        site = name_tokens(name)
        for ours in (name_tokens(full_name), name_tokens(alias)):
            if ours and site and (ours <= site or site <= ours):
                scored.append((len(ours & site), index))
                break
    if not scored:
        return None
    best = max(score for score, _ in scored)
    winners = [index for score, index in scored if score == best]
    return winners[0] if len(winners) == 1 else None


def prefill_h12_universe(table: pd.DataFrame, faculty: pd.DataFrame, overwrite: bool = False) -> pd.DataFrame:
    column = "criterio_h12"
    table = ensure_column(table, column)
    for index, row in table.iterrows():
        filled = str(row.get("incluido_h12", "")).strip() != ""
        if filled and not str(row.get(column, "")).startswith("HP") and not overwrite:
            continue
        match = match_faculty(row["docente"], row["nome_normalizado"], faculty)
        if match is None:
            included, reason = "nao", "ausente da página de docentes do IC/UFF (substituto, outro departamento ou cadastro incompleto)"
        else:
            cargo = str(faculty.at[match, "cargo"]).strip()
            if PERMANENT_RE.match(cargo):
                included, reason = "sim", f"página de docentes do IC/UFF: {cargo}"
            else:
                included, reason = "sim", "listado na página de docentes do IC/UFF, cargo não informado"
        table.at[index, "incluido_h12"] = included
        table.at[index, column] = f"HP7 {RULE_DATE}: {reason}"
    return table


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sobrescrever", action="store_true", help="Reaplica as inferências também em linhas validadas manualmente")
    args = parser.parse_args()
    roster = set(pd.read_csv(PRIORITIES, dtype=str).fillna("")["nome_normalizado"])
    faculty = pd.read_csv(IC_FACULTY, dtype=str).fillna("")
    for path, prefill, column in (
        (ROOMS, prefill_rooms, "criterio_capacidade"),
        (RESOURCES, prefill_resources, "criterio_laboratorio"),
        (SECTORS, prefill_sectors, "criterio_setor"),
        (QUALIFICATIONS, lambda table, overwrite: prefill_qualifications(table, roster, overwrite), "criterio_habilitacao"),
        (PRIORITIES, prefill_priorities, "criterio_prioridade"),
        (EXTERNAL, prefill_external, "tratamento_no_modelo"),
        (H12_UNIVERSE, lambda table, overwrite: prefill_h12_universe(table, faculty, overwrite), "criterio_h12"),
    ):
        table = pd.read_csv(path, dtype=str).fillna("")
        result = prefill(table, overwrite=args.sobrescrever)
        result.to_csv(path, index=False)
        print(f"{path.relative_to(ROOT)}:")
        for value, count in result[column].value_counts().items():
            print(f"  - {count:3d} × {value or '(sem inferência)'}")


if __name__ == "__main__":
    main()
