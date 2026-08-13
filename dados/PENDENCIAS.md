# Dados — pendências e organização

## Convenção

- `dados/brutos/` — dados como chegaram (planilhas do orientador, exports, etc.).
- `dados/processados/` — instâncias limpas no formato de entrada do solver.
- Os dados do webscrap permanecem em `webscrap/` (pipeline autocontido); versões limpas vão para `dados/processados/`.

## Checklist de dados a obter

- [ ] **Tabela oficial de setores/áreas** do departamento — setor → professores habilitados → matérias → dias oficiais. A planilha QH 2025 já contém a coluna `Setor` por disciplina e permite gerar um proxy histórico, mas não substitui essa tabela validada.
- [ ] **Lista de matérias externas** com horários fixos (não mudam, alta prioridade).
- [ ] **Grade de horários prevista** das matérias por semestre par e ímpar (a "solução vigente" — também serve de baseline).
- [ ] **Salas do IC**: identificação, capacidade, recursos (laboratório, projetor etc.).
- [ ] **Optativas pretendidas** por professor (horário livre).
- [ ] **Lista de prioridade dos professores** (idade/antiguidade) ou critério para construí-la.
- [ ] **Vagas/tamanho das turmas** (pode ser extraível das páginas de turma do quadro de horários — `turma_url` já está no CSV).
- [ ] **Grade curricular por período** de cada curso — **CC e SI** (quais matérias o aluno do período X cursa juntas) — necessário para evitar choques para o aluno.
- [ ] **Grade de SI**: descobrir **idcurso/idcurriculo de Sistemas de Informação** (Niterói) no quadro de horários — hoje só a grade de CC foi coletada.
- [ ] **Mapa de disciplinas compartilhadas CC∩SI** (disciplina nas duas grades = uma única turma para os dois cursos) — o tamanho da interseção condiciona os experimentos E1/E2 do modelo.

## Limpezas pendentes nos dados já coletados

- [ ] Revisar `professores_por_setor_2025.csv`, `dominios_professores_turmas_2025.csv` e `dias_por_setor_2025.csv`: esses arquivos foram inferidos do histórico QH 2025 e precisam de validação antes dos experimentos oficiais.
- [ ] Revisar `auditoria_h12_professores_2025.csv` para decidir quais docentes da aba `CH Docente` entram no universo H12 do modelo.
- [ ] Filtrar optativas humanísticas que vieram no webscrap (não são do IC).
- [ ] Separar disciplinas do IC (códigos TCC/TIC...) das de outros departamentos (TEP, GMA etc.) que aparecem no currículo.
- [ ] Consolidar `preferencias_professores.xlsx` em CSV processado com nomes corrigidos (`fix_names.py`).

## Nota sobre o webscrap (coleta de SI)

`webscrap/scraper.py` hoje fixa `idcurso=31` e `idcurriculo=3092` (CC, Niterói). Para coletar a grade de SI será preciso **parametrizar curso/currículo** no scraper — tarefa de execução da Fase 2 (`PLANO.md`), fora do escopo da edição de modelagem.
