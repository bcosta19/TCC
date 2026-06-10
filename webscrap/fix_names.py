"""
Corrige nomes abreviados (tooltip) para nomes completos confirmados manualmente.
Roda após scraper.py quando há entradas com nome apenas em MAIÚSCULAS.

Uso: python3 fix_names.py
"""

import pandas as pd

# Mapeamento confirmado manualmente (abreviado → nome completo)
MAPEAMENTO = {
    'ANTONIO':   'Antonio Augusto de Aragao Rocha',
    'IGOR':      'Igor Machado Coelho',
    'MARIO':     'Mario Roberto Folhadela Benevides',
    'ISABEL':    'Isabel Cristina Mello Rosseti',
    'ALINE':     'Aline Marins Paes Carvalho',
    'FLAVIA':    'Flavia Coimbra Delicato',
    'LUIS':      'Luis Felipe Ignacio Cunha',
    'LUIZ':      'Luiz Fernando Bez',
    'RODRIGO':   'Rodrigo Ferreira Sobreiro',
    'ALEXANDRE': 'Alexandre Santos de La Vega',
    'RICARDO':   'Ricardo Leiderman',
    'DANIELE':   'Daniele Pereira dos Santos Magon',
    'LUCIANA':   'Luciana Cardoso de Castro Salgado',
    'AMERICO':   'Americo da Costa Ramos Filho',
    'LOANA':     'Loana Tito Nogueira',
    'TATHIANNA': 'Tathianna Prado Dawes',
    'AURA':      'Aura Conci',
    'DJALMA':    'Djalma Rosa Mendes Junior',
    'SHANGJIE':  'Shangjie Yang',
}


def analyze(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    por_disc = (
        df.groupby(['docente', 'codigo', 'disciplina'])
        .agg(
            total_turmas=('turma', 'count'),
            semestres=('semestre', lambda s: ', '.join(sorted(s.unique()))),
        )
        .reset_index()
        .sort_values(['docente', 'total_turmas'], ascending=[True, False])
    )
    por_prof = (
        df.groupby('docente')
        .agg(
            total_turmas=('turma', 'count'),
            disciplinas_distintas=('codigo', 'nunique'),
            semestres=('semestre', lambda s: ', '.join(sorted(s.unique()))),
        )
        .reset_index()
        .sort_values('total_turmas', ascending=False)
    )
    return por_disc, por_prof


def main():
    df = pd.read_csv('turmas_raw.csv')

    # Detecta nomes ainda em maiúsculas
    pendentes = df[df['docente'].apply(str.isupper)]
    novos = pendentes[~pendentes['docente'].isin(MAPEAMENTO)]['docente'].unique()
    if len(novos):
        print(f'[AVISO] {len(novos)} nome(s) em maiúsculas sem mapeamento definido:')
        for n in sorted(novos):
            print(f'  {n}')
        print('Adicione-os ao dicionário MAPEAMENTO antes de continuar.\n')

    antes = df['docente'].nunique()
    df['docente'] = df['docente'].replace(MAPEAMENTO)
    depois = df['docente'].nunique()

    restantes = df[df['docente'].apply(str.isupper)]
    print(f'Docentes únicos: {antes} → {depois}')
    print(f'Ainda em maiúsculas: {len(restantes)}')

    df.to_csv('turmas_raw.csv', index=False, encoding='utf-8-sig')

    por_disc, por_prof = analyze(df)
    with pd.ExcelWriter('preferencias_professores.xlsx', engine='openpyxl') as w:
        df.to_excel(w, sheet_name='Dados Brutos', index=False)
        por_disc.to_excel(w, sheet_name='Por Disciplina', index=False)
        por_prof.to_excel(w, sheet_name='Totais por Professor', index=False)

    print('CSV e Excel atualizados.')
    print('\n=== TOP 15 professores por nº de turmas ===')
    print(por_prof.head(15).to_string(index=False))


if __name__ == '__main__':
    main()
