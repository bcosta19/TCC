# Dados — pendências e organização

## Convenção

- `dados/brutos/` — dados como chegaram (planilhas do orientador, exports, etc.).
- `dados/processados/` — instâncias limpas no formato de entrada do solver.
- Os dados do webscrap permanecem em `webscrap/` (pipeline autocontido); versões limpas vão para `dados/processados/`.

## Checklist de dados a obter

- [ ] **Planilha de setores/áreas** do departamento (orientador vai enviar) — setor → professores → matérias.
- [ ] **Lista de matérias externas** com horários fixos (não mudam, alta prioridade).
- [ ] **Grade de horários prevista** das matérias por semestre par e ímpar (a "solução vigente" — também serve de baseline).
- [ ] **Salas do IC**: identificação, capacidade, recursos (laboratório, projetor etc.).
- [ ] **Localização das salas** (prédio/andar) para a matriz de distâncias — necessário para o critério original de minimizar deslocamento dos alunos.
- [ ] **Optativas pretendidas** por professor (horário livre).
- [ ] **Lista de prioridade dos professores** (idade/antiguidade) ou critério para construí-la.
- [ ] **Vagas/tamanho das turmas** (pode ser extraível das páginas de turma do quadro de horários — `turma_url` já está no CSV).
- [ ] **Grade curricular por período** de cada curso — **CC e SI** (quais matérias o aluno do período X cursa juntas) — necessário para evitar choques para o aluno e para o critério de distância.
- [ ] **Grade de SI**: descobrir **idcurso/idcurriculo de Sistemas de Informação** (Niterói) no quadro de horários — hoje só a grade de CC foi coletada.
- [ ] **Mapa de disciplinas compartilhadas CC∩SI** (disciplina nas duas grades = uma única turma para os dois cursos) — o tamanho da interseção condiciona os experimentos E1/E2 do modelo.

## Limpezas pendentes nos dados já coletados

- [ ] Filtrar optativas humanísticas que vieram no webscrap (não são do IC).
- [ ] Separar disciplinas do IC (códigos TCC/TIC...) das de outros departamentos (TEP, GMA etc.) que aparecem no currículo.
- [ ] Consolidar `preferencias_professores.xlsx` em CSV processado com nomes corrigidos (`fix_names.py`).

## Nota sobre o webscrap (coleta de SI)

`webscrap/scraper.py` hoje fixa `idcurso=31` e `idcurriculo=3092` (CC, Niterói). Para coletar a grade de SI será preciso **parametrizar curso/currículo** no scraper — tarefa de execução da Fase 2 (`PLANO.md`), fora do escopo da edição de modelagem.
