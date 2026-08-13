# Dados processados da planilha QH 2025

Fonte: `dados/brutos/QH-2025-1-2.xlsx`.

A extração é reproduzível com:

```bash
python3 scripts/extract_qh_2025.py
```

## Arquivos

- `turmas_2025.csv` — uma linha por turma, com semestre, curso, período,
  capacidade, código, disciplina, setor e alocação registrada na planilha.
- `horarios_2025.csv` — uma linha por encontro semanal, com dia, início, fim e
  sala normalizados.
- `carga_docente_2025.csv` — aba `CH Docente` exportada para CSV.
- `salas_2025.csv` — salas usadas, indicação provisória de laboratório e
  capacidade estimada a partir do maior `CAP` observado; salas `L...` são
  marcadas como laboratório.
- `recursos_turmas_2025.csv` — exigência de laboratório inferida por turma.
- `recursos_encontros_2025.csv` — exigência de laboratório inferida por
  encontro semanal, preservando disciplinas que alternam sala comum e lab.
- `preferencias_2025.csv` — frequência histórica professor×disciplina
  normalizada por código, usada como proxy de preferência nos testes.
- `professores_por_setor_2025.csv` — professores observados em cada setor no
  QH 2025, usado como proxy não oficial de habilitação por setor.
- `dominios_professores_turmas_2025.csv` — domínio de candidatos por turma,
  derivado do setor da disciplina e das alocações observadas em 2025.
- `dias_por_setor_2025.csv` — padrões de dias observados por setor, semestre e
  assinatura de encontros, usado para domínios provisórios de horários.
- `auditoria_h12_professores_2025.csv` — comparação entre o universo H12 atual
  da instância e a aba `CH Docente`.
- `relatorio_experimento_nao_oficial_2025.md` — resultados e validações da
  rodada não oficial da instância CC/SI.
- `resumo_2025.json` — contagens e valores observados na extração.

## Resultado atual

- 235 turmas;
- 429 encontros semanais;
- 124 turmas em 2025/1;
- 111 turmas em 2025/2;
- 223 registros classificados como IC pelo código `TCC`;
- 12 registros classificados como externos;
- 85 disciplinas distintas;
- salas identificadas: 21.

## Observações

- A coluna `Setor` já existe na planilha e foi preservada; não foi inferida.
- Os domínios de professor e de dias por setor são inferidos a partir do
  histórico observado em 2025. Eles servem para testes não oficiais e precisam
  ser substituídos ou validados pela tabela oficial do orientador.
- A coluna `ALOCAÇÃO` foi preservada como o nome abreviado usado na planilha.
- A origem foi classificada inicialmente como `IC` para códigos `TCC` e
  `externa` para os demais códigos. Essa regra deverá ser revisada para cursos
  de SI e outras disciplinas administradas pelo IC.
- Há 20 encontros sem sala preenchida ou com sala não identificada. Eles devem
  ser revisados antes da instância final.
- A capacidade da sala é uma estimativa: `max(CAP)` das turmas observadas nela.
  Ela é útil para testes, mas deve ser substituída pela capacidade física oficial
  quando disponível.
- A classificação provisória de obrigatória usa `CH_OB`; H12 exige três
  obrigatórias por professor no horizonte anual.
- A prioridade dos professores é neutra (`1.0`) apenas nas instâncias de teste;
  a lista validada pelo orientador ainda está pendente.
- O prefixo `L` é tratado como indicação provisória de laboratório.
- A exigência de laboratório é inferida primeiro pela sala observada e, para
  códigos que só aparecem em laboratórios, propagada aos encontros sem sala.
  Códigos que alternam sala comum e laboratório permanecem com requisito por
  encontro; casos sem evidência suficiente ficam marcados como desconhecidos.
- A planilha contém registros de pós-graduação (`TIC...`) que precisam ser
  excluídos caso a instância seja apenas de graduação.
- O arquivo é uma extração dos dados concretos de 2025, não ainda uma instância
  JSON do solver.

## Instância e solver

Para o primeiro experimento CC/SI, a instância filtrada está em
`instancia_2025_cc_si.json`. A variante com domínios provisórios de horários
está em `instancia_2025_cc_si_flex.json`.

Comandos principais:

```bash
python3 scripts/evaluate_json.py dados/processados/instancia_2025_cc_si.json
python3 scripts/solve_schedule_2025.py --iterations 1000 --seed 2025
python3 scripts/evaluate_json.py dados/processados/solucao_horarios_sa_2025.json
python3 scripts/report_schedule_solver_run.py
python3 scripts/run_experimento_nao_oficial_2025.py
```

O solver atual mantém externas e projetos finais fixos, e permite movimentos
de horário e sala nas turmas internas. Há também um SA experimental de
professores; por padrão ele usa o domínio histórico por setor e só deve usar
domínio irrestrito em teste de estresse explícito. Os domínios e capacidades
ainda são provisórios e devem ser substituídos por dados oficiais.
