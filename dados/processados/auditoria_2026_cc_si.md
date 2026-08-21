# Auditoria da instância CC/SI observada em 2026

> Auditoria de dados; as sobreposições não são resultados experimentais.

## Cobertura obtida

- Turmas físicas após consolidar/expandir os registros: **180**.
- Encontros semanais: **329**.
- Docentes observados: **61**.
- Salas observadas: **22**.
- Turmas com vagas e inscritos disponíveis: **180**.
- Turmas classificadas como obrigatórias: **149**.
- Turmas com obrigatoriedade ainda desconhecida: **4**.

## Turmas compartilhadas

- Códigos na interseção das grades completas: **64**.
- Turmas de 2026 compartilhadas pela interseção curricular: **25**.
- Turmas com vagas simultaneamente alocadas a CC e SI: **55**.

Os dois indicadores são diferentes: a interseção descreve a grade; as vagas
descrevem a alocação observada da turma no semestre.

## Pendências remanescentes

- Sem grupo curricular nas grades Markdown: **4** — `2026-1-TCC00368-A1`, `2026-1-TCC00371-A1`, `2026-2-TCC00368-A1`, `2026-2-TCC00371-A1`.
- Turmas com múltiplos professores: **2**.
- Encontros sem sala: **0**.
- Capacidades físicas das salas: ausentes; `capacidade_minima_observada`
  é somente um limite inferior derivado das vagas.
- Universo oficial de docentes submetidos a H12: ausente.

## Verificações da alocação observada

- Sobreposições candidatas de sala: **3**.
- Sobreposições candidatas de professor: **0**.
- Conflitos curriculares observados: **10**.
- Divergências de horário PDF × página pública: **1**.

Os pares de sala/professor estão em `conflitos_candidatos_2026_cc_si.csv`.

## Condição estrutural de H12

Há **149** turmas obrigatórias classificadas. Sem contar
alocações múltiplas, esse total comporta no máximo **49**
docentes recebendo três obrigatórias. A violação de H12 só pode ser calculada
após definir quais docentes compõem seu universo.
