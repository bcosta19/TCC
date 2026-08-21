# Auditoria dos quadros de horários de 2026

> Esta é uma auditoria de extração e qualidade dos dados. Os candidatos a
> conflito abaixo não são resultados experimentais nem conflitos confirmados.

## Escopo

- Turmas/ofertas extraídas: **262**.
- Encontros semanais extraídos: **482**.
- Salas observadas: **22**.
- Registros sem código: **18**.
- Registros com múltiplos professores: **4**.
- Registros incompletos: **3**.
- Registros cancelados: **1**.

Os dados abrangem ofertas regulares, pós-graduação, graduação/pós e
disciplinas de serviço. Os PDFs não fornecem uma classificação completa de
pertinência às grades de CC e SI.

## Integridade estrutural

- IDs duplicados: **0**.
- Turmas sem encontro: **3**.
- Encontros órfãos: **0**.
- Horários inválidos: **0**.
- Horários com fim não posterior ao início: **0**.
- Encontros sem sala: **2**.

### Registros incompletos ou cancelados

- `2026-1-TCC00311-A1` — PROJETO FINAL II: **incompleta** (horario_ausente).
- `2026-1-TCC00326-J1` — PROGRAMAÇÃO DE COMPUTADORES: **incompleta** (professor_ausente).
- `2026-2-TCC00326-H2` — PROGRAMAÇÃO DE COMPUTADORES (CANCELADA): **cancelada** (horario_ausente;professor_ausente).
- `2026-2-TCC00311-B1` — PROJETO FINAL II: **incompleta** (horario_ausente;professor_ausente).

## Normalização de docentes

- Grafias distintas encontradas: **138**.
- Correspondências não verificadas: **3**: `Julio Stacchini`, `Miguel`, `Thiago`.
- A normalização usa nomes e aliases de `carga_docente_2025.csv`; casos sem
  correspondência única são preservados para revisão manual.

## Candidatos a sobreposição

- Pares com sobreposição de sala: **6**.
- Pares com sobreposição de professor: **4**.

- **2026-1, quinta, 319**: `2026-1-SEM-CODIGO-007-SEM-TURMA` (14:00–16:00) × `2026-1-TCC00359-Z1` (14:00–16:00); classificação: `choque_sala_candidato`.
- **2026-1, terca, 306**: `2026-1-TCC00326-G2` (11:00–13:00) × `2026-1-TIC10005-SEM-TURMA` (11:00–13:00); classificação: `choque_sala_candidato`.
- **2026-1, terca, 319**: `2026-1-SEM-CODIGO-007-SEM-TURMA` (14:00–16:00) × `2026-1-TCC00359-Z1` (14:00–16:00); classificação: `choque_sala_candidato`.
- **2026-2, quarta, 217**: `2026-2-TCC00305-A1` (09:00–11:00) × `2026-2-TCC00305-X1` (09:00–11:00); classificação: `possivel_turma_agrupada`.
- **2026-2, quarta, 302**: `2026-2-TCC00252-SEM-TURMA` (16:00–18:00) × `2026-2-TCC00308-A1` (16:00–18:00); classificação: `choque_sala_candidato`.
- **2026-2, segunda, 217**: `2026-2-TCC00305-A1` (09:00–11:00) × `2026-2-TCC00305-X1` (09:00–11:00); classificação: `possivel_turma_agrupada`.
- **2026-1, quinta, Igor Moraes**: `2026-1-SEM-CODIGO-007-SEM-TURMA` (14:00–16:00) × `2026-1-TCC00359-Z1` (14:00–16:00); classificação: `choque_professor_candidato`.
- **2026-1, terca, Igor Moraes**: `2026-1-SEM-CODIGO-007-SEM-TURMA` (14:00–16:00) × `2026-1-TCC00359-Z1` (14:00–16:00); classificação: `choque_professor_candidato`.
- **2026-2, quinta, Celio**: `2026-2-SEM-CODIGO-002-SEM-TURMA` (09:00–11:00) × `2026-2-TCC00313-A1` (09:00–11:00); classificação: `choque_professor_candidato`.
- **2026-2, terca, Celio**: `2026-2-SEM-CODIGO-002-SEM-TURMA` (09:00–11:00) × `2026-2-TCC00313-A1` (09:00–11:00); classificação: `choque_professor_candidato`.

Os detalhes estruturados estão em `conflitos_candidatos_2026.csv`. Casos da
mesma disciplina podem representar turmas agrupadas em vez de choque real.

## Comparação entre os semestres

- Chaves código+turma presentes nos dois semestres: **89**.
- Mesmo padrão de dias e horários: **56**.
- Padrão de dias ou horários diferente: **33**.
- Mesmo padrão incluindo salas: **18**.

Essa comparação descreve as alocações observadas; não transforma horários ou
salas históricas em parâmetros fixos do solver.

## Cobertura curricular CC/SI

- Linhas dos PDFs classificadas por código nas grades: **179**.
- Vínculos confirmados com turmas retornadas pelas buscas públicas de CC/SI: **180**.
- O recorte consolidado, incluindo vagas e turmas compartilhadas, está em
  `auditoria_2026_cc_si.md`.

`classificacao_curricular_proxy_2026.csv` permanece apenas como comparação
histórica com 2025; as grades versionadas são a fonte curricular principal.

## Itens ainda não calculáveis no recorte CC/SI

- H12: faltam o universo de docentes e a regra para alocações múltiplas.
- Capacidade e desperdício: as vagas estão disponíveis, mas faltam capacidades físicas das salas.
- Quatro turmas ainda não possuem grupo de período nas grades Markdown.
- Setores, prioridade e habilitação docente não constam nos PDFs nem nas grades.

## Arquivos de revisão

- `revisao_turmas_2026.csv` — registros incompletos, sem código, com múltiplos
  professores ou com normalização pendente.
- `normalizacao_docentes_2026.csv` — vínculo de cada grafia com o alias usado
  nos dados processados.
- `salas_2026.csv` — salas observadas, sem capacidades inventadas.
