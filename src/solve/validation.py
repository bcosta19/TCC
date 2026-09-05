"""Conferencia estrutural independente dos movimentos, sem alterar H1--H12."""
from src.solve.direct_objective import DAY_ORDER, minutes, teachers_for_item


def pattern(item):
    return [(m.get('dia'), m.get('inicio'), m.get('fim')) for m in item.get('encontros', [])]


def validate_solution(source: dict, solution: dict) -> None:
    """Rejeita perdas de dados, atribuicoes ausentes e alteracoes fora dos dominios.

    Conflitos hard podem existir em estados intermediarios; sao quantificados
    pelos avaliadores. Esta verificacao nao declara viabilidade institucional.
    """
    def indexed(items):
        ids = [item.get('id') for item in items]
        if not all(ids) or len(set(ids)) != len(ids):
            raise ValueError('Identificadores ausentes ou duplicados')
        return {item['id']: item for item in items}
    before = indexed(source['classes'])
    after = indexed(solution['classes'])
    if before.keys() != after.keys():
        raise ValueError('Conjunto de turmas alterado')
    if {k: v for k, v in source.items() if k != 'classes'} != {k: v for k, v in solution.items() if k != 'classes'}:
        raise ValueError('Metadados da instancia alterados')
    rooms = indexed(source['rooms'])
    mutable = {'professor', 'professores_alocados', 'encontros'}
    slot_keys = {'dia', 'inicio', 'fim', 'sala'}
    for ident, old in before.items():
        new = after[ident]
        if {k:v for k,v in old.items() if k not in mutable} != {k:v for k,v in new.items() if k not in mutable}:
            raise ValueError(f'{ident}: dados estaticos alterados')
        teachers = teachers_for_item(new)
        if not teachers or len(teachers) != len(set(teachers)):
            raise ValueError(f'{ident}: professor ausente ou duplicado')
        if 'professores_alocados' in new and not new['professores_alocados']:
            raise ValueError(f'{ident}: atribuicao explicita vazia')
        if len(teachers) == 1 and old.get('professores_habilitados') is not None:
            if teachers[0] not in old['professores_habilitados']:
                raise ValueError(f'{ident}: professor fora do dominio')
        if len(teachers) == 1 and new.get('professor') and new['professor'] != teachers[0]:
            raise ValueError(f'{ident}: atribuicoes de professor contraditorias')
        if teachers != teachers_for_item(old):
            if old.get('professor_fixo') or old.get('origem') != 'IC' or len(teachers_for_item(old)) != 1:
                raise ValueError(f'{ident}: professor fixo alterado')
            if len(teachers) != 1 or teachers[0] not in (old.get('professores_habilitados') or []):
                raise ValueError(f'{ident}: professor fora do dominio')
        if not new.get('encontros') or len(old['encontros']) != len(new['encontros']):
            raise ValueError(f'{ident}: encontros ausentes ou quantidade alterada')
        if pattern(new) != pattern(old):
            if old.get('horario_fixo', True):
                raise ValueError(f'{ident}: horario fixo alterado')
            allowed = [pattern({'encontros': p}) for p in old.get('dominio_horarios', [])]
            if pattern(new) not in allowed:
                raise ValueError(f'{ident}: horario fora do dominio')
        for a, b in zip(old['encontros'], new['encontros']):
            if {k:v for k,v in a.items() if k not in slot_keys} != {k:v for k,v in b.items() if k not in slot_keys}:
                raise ValueError(f'{ident}: metadados do encontro alterados')
            if b.get('sala') not in rooms:
                raise ValueError(f'{ident}: sala ausente ou desconhecida')
            if b['sala'] != a.get('sala') and (old.get('sala_fixa') or old.get('origem') != 'IC'):
                raise ValueError(f'{ident}: sala fixa alterada')
            if b.get('dia') not in DAY_ORDER or minutes(b.get('inicio', '')) >= minutes(b.get('fim', '')):
                raise ValueError(f'{ident}: intervalo invalido')
