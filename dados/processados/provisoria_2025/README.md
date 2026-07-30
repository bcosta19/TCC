# Instância provisória CC/SI 2025

Esta pasta contém uma cópia da instância CC/SI com salas ausentes parcialmente
reparadas para permitir um primeiro teste algorítmico.

## Regra de reparo

- disciplinas internas `TCC` com período curricular receberam uma sala que não
  gerava conflito imediato;
- foram priorizadas salas já observadas para o mesmo código em outro semestre;
- a capacidade estimada da sala precisava ser suficiente para o `CAP` da turma;
- Projeto Final e disciplinas externas sem sala permaneceram sem sala;
- todas as atribuições provisórias estão registradas em `reparos_salas.csv`.

## Resultado do reparo

- 8 turmas receberam sala provisória;
- 2 turmas de Projeto Final permaneceram sem sala;
- 2 disciplinas externas permaneceram sem sala.

Essa instância é adequada para testar a pipeline e movimentos de sala, mas não
deve ser interpretada como o quadro oficial da UFF.

Para avaliá-la:

```bash
python3 scripts/evaluate_provisional_2025.py
python3 scripts/evaluate_json.py dados/processados/provisoria_2025/instancia_2025_cc_si.json
```
