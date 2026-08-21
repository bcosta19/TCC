# Dados — pendências e organização

## Convenção

- `dados/brutos/` — dados como chegaram (planilhas do orientador, exports, etc.).
- `dados/processados/` — instâncias limpas no formato de entrada do solver.
- Os dados do webscrap permanecem em `webscrap/` (pipeline autocontido); versões limpas vão para `dados/processados/`.

## Checklist de dados a obter (Validação Humana 2026)

Consulte o relatório operacional detalhado em:
`dados/processados/PENDENCIAS_VALIDACAO_2026.md`

- [ ] **Tabela oficial de setores/áreas** do departamento — setor → professores habilitados → matérias → dias oficiais (`revisao_setores_2026.csv` e `revisao_habilitacao_docente_2026.csv`).
- [ ] **Lista de matérias externas com horários fixos** — `revisao_horarios_fixos_2026.csv` e `revisao_turmas_externas_2026.csv`.
- [x] **Baseline anual observado de horários, professores e salas em 2026** — extraído de `QH-2026-1.pdf` e `QH-2026-2.pdf`; ver `dados/processados/auditoria_2026.md`.
- [ ] **Grade de horários fixos permitidos** por semestre par e ímpar — `revisao_horarios_fixos_2026.csv`.
- [ ] **Salas do IC**: identificação, capacidade física oficial, recursos (laboratório, projetor etc.) — `cadastro_salas_2026.csv` e `revisao_recursos_disciplinas_2026.csv`.
- [ ] **Optativas pretendidas** por professor (horário livre).
- [ ] **Lista de prioridade dos professores** (idade/antiguidade) — `revisao_prioridades_docentes_2026.csv`.
- [x] **Vagas/tamanho das turmas de 2026** — extraídas das páginas públicas de detalhe e preservadas por curso em `webscrap/turmas_2026_raw.csv`; as 180 turmas vinculadas ao recorte CC/SI têm vagas e inscritos conhecidos.
- [x] **Grade curricular por período de CC e SI** — fontes em `dados/grade_cc.md` e `dados/grade_si.md`, normalizadas em `curriculos_cc_si.csv`.
- [x] **Identificadores de SI no Quadro de Horários** — filtro interno `idcurso=263`, `idcurriculo=3473`, currículo acadêmico `83.01.003`.
- [x] **Mapa de disciplinas compartilhadas CC∩SI** — interseção por código em `intersecao_curriculos_cc_si.csv`: 64 códigos; a oferta física não é duplicada na instância.

## Limpezas e auditorias executadas

- [x] Extrair e auditar os dois QHs de 2026 em CSVs normalizados, preservando alocações observadas e campos ausentes.
- [x] Classificar por código as ofertas de 2026 usando as grades versionadas; resultado em `classificacao_curricular_2026.csv`.
- [x] Vincular PDFs e páginas públicas de turma: 180 vínculos para 178 linhas dos PDFs; duas linhas compactadas foram corretamente expandidas em turmas AA/BA.
- [x] Auditar vínculos não triviais e divergências de horário: gerado `revisao_vinculos_2026.csv` (19 linhas) com divergência de `CGI00004` documentada.
- [x] Preparar tabela de revisão curricular para `TCC00368` e `TCC00371`: `revisao_classificacao_curricular_2026.csv` (4 linhas com campo `decisao` para preenchimento).
- [x] Preparar tabela do universo H12: `universo_h12_2026.csv` (73 docentes candidatos cruzados com carga 2025; campo `incluido_h12` para validação humana).
- [x] Preparar política de cotutoria: `politica_cotutoria_2026.csv` para as duas turmas com alocação dupla (`TCC00285-A1` e `TCC00354-A1`).
- [x] Preparar cadastro de salas sem capacidades inventadas: `cadastro_salas_2026.csv` (22 salas com `capacidade_minima_observada`).
- [x] Preparar tabelas de revisão de recursos, setores, horários fixos, habilitação e prioridades.
- [x] Criar verificador de prontidão (`scripts/check_readiness_2026.py`) e orquestrador reproduzível (`scripts/run_pipeline_2026.py`).

## Nota sobre a pipeline reproduzível de 2026

Execute a pipeline completa com:
```bash
python scripts/run_pipeline_2026.py --offline
```
Ela executa a cadeia completa de extração, auditoria, construção da instância e geração das tabelas de revisão. A instância `instancia_2026_cc_si.json` permanece marcada com `pronta_para_experimento=false` até que as decisões humanas pendentes sejam validadas via `check_readiness_2026.py`.
