# Dados processados

## Quadros de horários de 2026

Fontes:

- `dados/brutos/QH-2026-1.pdf` e `dados/brutos/QH-2026-2.pdf` — professor,
  horário e sala observados;
- `dados/grade_cc.md` e `dados/grade_si.md` — vínculo curricular, período e
  obrigatoriedade;
- páginas públicas do Quadro de Horários — `turma_url`, vagas e inscritos por
  curso, coletadas em `webscrap/turmas_2026_raw.csv`.

Pipeline reproduzível:

```bash
# Execução completa da cadeia 2026 (offline):
python3 scripts/run_pipeline_2026.py --offline

# Ou passo a passo:
python3 scripts/extract_qh_2026.py
python3 scripts/build_curriculum_mapping_2026.py
python3 scripts/match_qh_web_2026.py
python3 scripts/audit_instance_2026.py
python3 scripts/build_instance_2026.py
python3 scripts/build_instance_2026_cc_si.py
python3 scripts/audit_instance_2026_cc_si.py
python3 scripts/build_review_tables_2026.py
python3 scripts/check_readiness_2026.py --profile baseline
```

### Tabelas de Revisão e Validação Humana

Consulte o relatório operacional em `PENDENCIAS_VALIDACAO_2026.md`.

- `revisao_vinculos_2026.csv` — auditoria dos 19 vínculos PDF × Web não triviais ou divergentes;
- `revisao_classificacao_curricular_2026.csv` — revisão de classificação de `TCC00368` e `TCC00371`;
- `universo_h12_2026.csv` — mapeamento dos docentes para a restrição de carga anual mínima H12;
- `politica_cotutoria_2026.csv` — tratamento de cotutorias (`TCC00285` e `TCC00354`);
- `cadastro_salas_2026.csv` — cadastro das 22 salas observadas com capacidade mínima observada;
- `revisao_recursos_disciplinas_2026.csv` — exigência de laboratório e recursos especiais;
- `revisao_horarios_fixos_2026.csv` — turmas externas e flexibilidade de horários;
- `revisao_setores_2026.csv` — setores departamentais e dias da semana oficiais;
- `revisao_habilitacao_docente_2026.csv` — habilitação docente por disciplina;
- `revisao_prioridades_docentes_2026.csv` — prioridades docentes;
- `revisao_turmas_externas_2026.csv` — mapeamento de ofertas públicas não vinculadas ao PDF do IC.


### Extração integral dos PDFs

- `turmas_2026.csv` e `horarios_2026.csv` — 262 linhas de oferta e 482
  encontros, incluindo pós-graduação e serviço;
- `normalizacao_docentes_2026.csv` e `revisao_turmas_2026.csv` — auditoria de
  nomes e registros incompletos;
- `auditoria_2026.md` — qualidade do quadro integral;
- `salas_2026.csv`, `recursos_turmas_2026.csv` e
  `recursos_encontros_2026.csv` — uso observado de salas/laboratórios, sem
  convertê-lo automaticamente em requisito.

### Currículos e turmas compartilhadas

- `curriculos_cc_si.csv` — normalização das duas grades;
- `intersecao_curriculos_cc_si.csv` — 64 códigos presentes nas duas grades;
- `classificacao_curricular_2026.csv` — classificação das linhas dos PDFs por
  código, período e obrigatoriedade;
- `vagas_turmas_2026.csv` — vínculo PDF × página pública, com vagas e inscritos
  discriminados por curso;
- `classificacao_curricular_proxy_2026.csv` — comparação histórica com 2025,
  mantida separada e não usada como fonte curricular principal.

A interseção por código não duplica a oferta: uma turma compartilhada mantém
um único professor, horário e sala, com vínculos para os dois currículos. A
alocação observada de vagas para CC e SI é preservada em indicador separado.

### Recorte CC/SI resultante

- 180 turmas com vagas conhecidas;
- 329 encontros semanais;
- 61 docentes observados;
- 22 salas observadas;
- 149 turmas classificadas como obrigatórias;
- 25 turmas compartilhadas pela interseção curricular;
- 55 turmas com vagas simultaneamente alocadas a CC e SI;
- duas linhas compactadas nos PDFs expandidas em suas seções AA/BA.

Arquivos: `turmas_2026_cc_si.csv`, `horarios_2026_cc_si.csv`,
`salas_2026_cc_si.csv` e `auditoria_2026_cc_si.md`.

`instancia_2026_cc_si.json` é recriável e ignorada pelo Git. Ela continua com
`pronta_para_experimento=false`, pois ainda faltam capacidades físicas das
salas, universo H12 e tratamento explícito das duas alocações docentes
múltiplas. Quatro turmas (`TCC00368` e `TCC00371`, nos dois semestres) são
retornadas pelos filtros curriculares atuais, mas não aparecem nas grades
Markdown e permanecem sem grupo de período.

Horários, salas e professores observados constituem o baseline de 2026; não
são automaticamente domínios fixos do solver.

## Planilha QH 2025

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
