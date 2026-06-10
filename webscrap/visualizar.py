"""
Visualização dos dados de preferência de professores.
Uso: python3 visualizar.py
"""

import sys
import pandas as pd
import plotext as plt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.columns import Columns
from rich import box

console = Console()


def carregar() -> pd.DataFrame:
    try:
        return pd.read_csv('turmas_raw.csv')
    except FileNotFoundError:
        console.print('[red]Arquivo turmas_raw.csv não encontrado.[/red]')
        console.print('Rode primeiro: [bold]python3 scraper.py[/bold] e [bold]python3 fix_names.py[/bold]')
        sys.exit(1)


def separador(titulo: str = ''):
    console.rule(f'[bold cyan]{titulo}[/bold cyan]' if titulo else '')


# ── SEÇÕES ────────────────────────────────────────────────────────────────────

def sec_visao_geral(df: pd.DataFrame):
    separador('VISÃO GERAL')
    cards = [
        Panel(f'[bold yellow]{len(df)}[/bold yellow]\nregistros',          title='Total'),
        Panel(f'[bold yellow]{df["docente"].nunique()}[/bold yellow]\nprofessores', title='Docentes'),
        Panel(f'[bold yellow]{df["codigo"].nunique()}[/bold yellow]\ndisciplinas',  title='Disciplinas'),
        Panel(f'[bold yellow]{df["semestre"].nunique()}[/bold yellow]\nsemestres',  title='Semestres'),
    ]
    console.print(Columns(cards))

    por_sem = df.groupby('semestre')['turma'].count().reset_index().sort_values('semestre')
    plt.clear_figure()
    plt.bar(por_sem['semestre'].tolist(), por_sem['turma'].tolist(), color='cyan')
    plt.title('Turmas por semestre')
    plt.plotsize(60, 12)
    plt.theme('dark')
    plt.show()


def sec_ranking(df: pd.DataFrame):
    separador('RANKING DE PROFESSORES')
    por_prof = (
        df.groupby('docente')
        .agg(total_turmas=('turma', 'count'), disciplinas=('codigo', 'nunique'))
        .reset_index()
        .sort_values('total_turmas', ascending=False)
    )

    top15 = por_prof.head(15)
    plt.clear_figure()
    plt.bar(
        top15['docente'].str.split().str[0].tolist(),
        top15['total_turmas'].tolist(),
        color='green',
        orientation='h',
    )
    plt.title('Top 15 professores — total de turmas')
    plt.plotsize(70, 20)
    plt.theme('dark')
    plt.show()

    tabela = Table(title='Top 20 Professores', box=box.ROUNDED, highlight=True)
    tabela.add_column('#', style='dim', width=3)
    tabela.add_column('Professor', style='bold')
    tabela.add_column('Turmas', justify='right', style='yellow')
    tabela.add_column('Disciplinas distintas', justify='right')
    for i, row in enumerate(por_prof.head(20).itertuples(), 1):
        tabela.add_row(str(i), row.docente, str(row.total_turmas), str(row.disciplinas))
    console.print(tabela)


def sec_professor(df: pd.DataFrame):
    separador('BUSCA POR PROFESSOR')
    busca = Prompt.ask('Nome (parte)').strip().lower()

    matches = df[df['docente'].str.lower().str.contains(busca)]['docente'].unique()
    if not len(matches):
        console.print('[red]Nenhum professor encontrado.[/red]')
        return

    if len(matches) > 1:
        for i, m in enumerate(sorted(matches), 1):
            console.print(f'  [cyan]{i}[/cyan]. {m}')
        escolha = Prompt.ask('Número', default='1')
        try:
            nome = sorted(matches)[int(escolha) - 1]
        except (ValueError, IndexError):
            return
    else:
        nome = matches[0]

    sub = df[df['docente'] == nome]
    sems = ', '.join(sorted(sub['semestre'].unique()))

    console.print(Panel(f'[bold cyan]{nome}[/bold cyan]', expand=False))
    console.print(f'  Turmas: [yellow]{len(sub)}[/yellow]   '
                  f'Disciplinas: [yellow]{sub["codigo"].nunique()}[/yellow]   '
                  f'Semestres: {sems}\n')

    por_disc = (
        sub.groupby(['codigo', 'disciplina'])
        .agg(turmas=('turma', 'count'), semestres=('semestre', lambda s: ', '.join(sorted(s.unique()))))
        .reset_index()
        .sort_values('turmas', ascending=False)
    )
    tabela = Table(box=box.SIMPLE_HEAVY)
    tabela.add_column('Código', style='dim')
    tabela.add_column('Disciplina')
    tabela.add_column('Turmas', justify='right', style='yellow')
    tabela.add_column('Semestres')
    for row in por_disc.itertuples():
        tabela.add_row(row.codigo, row.disciplina, str(row.turmas), row.semestres)
    console.print(tabela)

    evo = sub.groupby('semestre')['turma'].count()
    sems_ord = sorted(df['semestre'].unique())
    vals = [int(evo.get(s, 0)) for s in sems_ord]
    plt.clear_figure()
    plt.bar(sems_ord, vals, color='cyan')
    plt.title(f'Turmas por semestre — {nome.split()[0]}')
    plt.plotsize(50, 10)
    plt.theme('dark')
    plt.show()


def sec_disciplina(df: pd.DataFrame):
    separador('BUSCA POR DISCIPLINA')
    busca = Prompt.ask('Nome ou código (parte)').strip().lower()

    mask = (df['disciplina'].str.lower().str.contains(busca) |
            df['codigo'].str.lower().str.contains(busca))
    discs = df[mask][['codigo', 'disciplina']].drop_duplicates()

    if not len(discs):
        console.print('[red]Nenhuma disciplina encontrada.[/red]')
        return

    if len(discs) > 1:
        for i, row in enumerate(discs.itertuples(), 1):
            console.print(f'  [cyan]{i}[/cyan]. {row.codigo} — {row.disciplina}')
        escolha = Prompt.ask('Número', default='1')
        try:
            codigo = discs.iloc[int(escolha) - 1]['codigo']
        except (ValueError, IndexError):
            return
    else:
        codigo = discs.iloc[0]['codigo']

    sub = df[df['codigo'] == codigo]
    console.print(Panel(f'[bold cyan]{codigo} — {sub["disciplina"].iloc[0]}[/bold cyan]', expand=False))

    por_prof = (
        sub.groupby('docente')
        .agg(turmas=('turma', 'count'), semestres=('semestre', lambda s: ', '.join(sorted(s.unique()))))
        .reset_index()
        .sort_values('turmas', ascending=False)
    )
    tabela = Table(box=box.ROUNDED)
    tabela.add_column('Professor')
    tabela.add_column('Turmas', justify='right', style='yellow')
    tabela.add_column('Semestres')
    for row in por_prof.itertuples():
        tabela.add_row(row.docente, str(row.turmas), row.semestres)
    console.print(tabela)

    top = por_prof.head(10)
    plt.clear_figure()
    plt.bar(top['docente'].str.split().str[0].tolist(), top['turmas'].tolist(),
            color='magenta', orientation='h')
    plt.title(f'Professores em {codigo}')
    plt.plotsize(60, 15)
    plt.theme('dark')
    plt.show()


def sec_semestre(df: pd.DataFrame):
    separador('POR SEMESTRE')
    sems = sorted(df['semestre'].unique())
    for i, s in enumerate(sems, 1):
        console.print(f'  [cyan]{i}[/cyan]. {s}')
    escolha = Prompt.ask('Número')
    try:
        semestre = sems[int(escolha) - 1]
    except (ValueError, IndexError):
        return

    sub = df[df['semestre'] == semestre]
    console.print(Panel(f'[bold cyan]{semestre}[/bold cyan] — {len(sub)} turmas', expand=False))

    por_prof = (
        sub.groupby('docente')
        .agg(turmas=('turma', 'count'), disciplinas=('codigo', 'nunique'))
        .reset_index()
        .sort_values('turmas', ascending=False)
        .head(20)
    )
    tabela = Table(box=box.ROUNDED)
    tabela.add_column('Professor')
    tabela.add_column('Turmas', justify='right', style='yellow')
    tabela.add_column('Disciplinas', justify='right')
    for row in por_prof.itertuples():
        tabela.add_row(row.docente, str(row.turmas), str(row.disciplinas))
    console.print(tabela)


# ── MENU ──────────────────────────────────────────────────────────────────────

MENU = {
    '1': ('Visão geral',           sec_visao_geral),
    '2': ('Ranking de professores', sec_ranking),
    '3': ('Buscar professor',      sec_professor),
    '4': ('Buscar disciplina',     sec_disciplina),
    '5': ('Ver por semestre',      sec_semestre),
    '0': ('Sair',                  None),
}


def main():
    df = carregar()
    console.print(Panel('[bold cyan]UFF — Preferências de Professores[/bold cyan]\n'
                        'Ciência da Computação · Niterói · 2023/1–2025/2', expand=False))

    while True:
        console.print()
        for key, (label, _) in MENU.items():
            console.print(f'  [cyan]{key}[/cyan]. {label}')

        opcao = Prompt.ask('\n[bold]Opção[/bold]', choices=list(MENU.keys()), default='1')
        if opcao == '0':
            break
        _, fn = MENU[opcao]
        if fn:
            console.print()
            fn(df)


if __name__ == '__main__':
    main()
