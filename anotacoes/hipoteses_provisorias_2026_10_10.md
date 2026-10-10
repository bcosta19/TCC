# Hipóteses provisórias e decisões — 10/10/2026

> Propostas pelo aluno em 10/10/2026, **pendentes de validação do orientador**.
> Não são diretrizes confirmadas nem dados institucionais. Servem para
> destravar a instância oficial de 2026 enquanto os dados do departamento não
> chegam. Se chegarem, a decisão manual substitui a inferência.

Aplicação: `scripts/prefill_inferences_2026.py`. As linhas preenchidas
recebem `validado=sim`, e a origem fica nas colunas `criterio_capacidade`,
`criterio_laboratorio`, `criterio_setor`, `criterio_habilitacao`,
`criterio_prioridade`, `criterio_referencia` e `criterio_h12`, começando por `HP3`–`HP7` ou
`decisão 10/10/2026`. O script não altera linhas validadas manualmente
(critério sem esses prefixos). A instância oficial registra em
`manifesto_oficial.hipoteses_provisorias` quantas linhas de cada tabela vieram
de hipótese.

## HP3 — Capacidade da sala = maior número de vagas observado

- `capacidade_fisica` de cada sala = maior número de vagas
  (`capacidade_turma`) entre as turmas alocadas nela em 2026
  (`cadastro_salas_2026.csv`, coluna `capacidade_minima_observada`).
- É um **limite inferior**: a capacidade real pode ser maior. Por construção,
  a alocação observada não viola H10 (conferido: 0 violações).
- Efeito no modelo: a restrição de sala fica mais apertada do que a real.
  Salas pequenas como 315 (15) e 304 (24) só recebem turmas pequenas.
- 22 salas preenchidas.

## HP4 — Laboratório = turma observada em sala "L"

- A disciplina requer laboratório quando alguma turma dela teve encontro em
  sala de laboratório (identificador iniciado por "L", ex.: `L302`).
- Se a disciplina usou laboratório e também sala comum, o laboratório só é
  exigido nos encontros observados em laboratório.
- A decisão é **por código**: linhas do mesmo código com nomes diferentes
  contam juntas. O builder passou a tratar como alternância o caso em que uma
  linha usou só laboratório e outra só sala comum (ex.: `TCC00334`).
- 99 linhas: 9 só em laboratório, 14 alternaram, 76 sem laboratório.
  56 encontros exigem laboratório.
- Limitação: uma turma pode ter ido para laboratório por falta de sala comum,
  e não por necessidade didática. Os dados não permitem distinguir os casos.

## HP5 — Setor por planilha de 2025 ou por afinidade de assunto

- **68 linhas:** setor da planilha QH 2025 (`setor_historico_2025`), só quando o código tem um único setor em 2025.
- **31 linhas sem setor único em 2025:** setor de disciplinas do mesmo assunto. Inclui `TCC00357` (POO I), que na planilha aparece 2× em ENG.SOFT. e 1× em ALG.CPX. e ficou em ENG.SOFT. O setor é
  escolhido só entre os 13 setores de 2025, porque o domínio de horários usa
  os padrões de dias observados para o setor em 2025.
  Exemplos: Tópicos em BD → `B.D.`, Metaheurísticas e PLI → `ALG.CPX.`
  (mesmo setor de Pesquisa Operacional), Tópicos em Segurança → `REDES`
  (mesmo setor de Segurança da Informação).
- A tabela completa, com justificativa e confiança, está em
  `SETOR_POR_AFINIDADE` no script e na coluna `criterio_setor`.
- **Conferir primeiro (confiança baixa):**

  | Código | Disciplina | Setor inferido | Alternativa |
  |---|---|---|---|
  | `TCC00194` | Biologia Computacional | `ALG.CPX.` | `IA`, `COMP.NUM.` |
  | `TCC00237` | Tópicos em Automação I (Robótica) | `ARQ.SO.` | `IA`, `COMP.VIS.JOGOS` |
  | `TCC00241` | Tópicos em Computação I | `ALG.CPX.` | `COMP.VIS.JOGOS` (tema variável) |
  | `TCC00242` | Tópicos em Computação II | `COMP.NUM.` | tema variável |
  | `TCC00253` | Tópicos em Sistemas de Programação I | `LING.TEOR.` | `ESTR.PROG.` |
  | `TCC00371` | Ética em IA e Ciência de Dados | `IA` | `GER.SIST.TI` |

- Limitação do builder: o setor é **um por código**. Códigos de tópicos com
  tema variável (`TCC00241`, `TCC00242`) recebem um único setor para todas as
  ofertas.
- Nos setores de 2025, os dias não são únicos: `ENG.SOFT.`, por exemplo, usou
  seg/qua e ter/qui. Por isso o domínio de cada turma flexível combina os
  padrões de dias do setor no mesmo semestre (paridade).

## HP6 — Habilitação = já deu a disciplina em 2025 ou 2026

- Cada linha de `revisao_habilitacao_docente_2026.csv` é um par (disciplina,
  docente) observado no QH 2026 (143) ou na planilha QH 2025 (92). A regra
  marca `habilitado=sim` em todos os pares cujo nome está no cadastro docente
  (carga 2025 e QH 2026).
- 6 pares ficam `nao`: nomes que são artefatos da planilha 2025 (`FECHADA`,
  marcação de turma fechada; `_Simone_` e `ChristianoGCI`, variantes de nome;
  `Gyslla`, ausente da carga 2025 e do QH 2026).
- Resultado: 177 turmas do IC com professor a escolher, todas com ao menos um
  candidato; 43 delas com um único candidato (professor efetivamente fixo).
- Christiano, Heleno e Leandro Santiago deram disciplinas em 2025, mas não
  têm turmas de CC/SI em 2026. Christiano Braga (professor associado) e
  Leandro Santiago (professor adjunto) são permanentes, confirmado em
  10/10/2026 nas páginas do IC/UFF e no Escavador. Eles continuam habilitados.
  A inclusão deles em H12 fica para a lista de permanentes.
- **Heleno** (corrigido manualmente em 10/10/2026): professor substituto,
  segundo o Escavador e o ResearchGate. A carga 2025 marca "até 15/01/2026", e
  ele não aparece no QH 2026. Os 3 pares dele (`TCC00357`, `TCC00361`,
  `TCC00366`) ficam `habilitado=nao`, e ele fica fora de H12
  (`universo_h12_2026.csv`).

## Decisões do aluno em 10/10/2026

Não são inferências. São escolhas de escopo do aluno, a comunicar ao orientador:

- **Prioridade dos professores fora do escopo.** O requisito 7 do
  `orientacao.md` (lista ordenada por prioridade) não será modelado. Todos os
  docentes recebem `prioridade=1` em `revisao_prioridades_docentes_2026.csv`,
  e o critério `preferencia_priorizada` vira a soma das preferências
  históricas, sem peso por professor. Se a lista chegar, basta preenchê-la.
- **Optativas de outros departamentos ignoradas.** As 65 ofertas sem
  tratamento em `revisao_turmas_externas_2026.csv` com código de outro
  departamento (TEP, GFI, GLC, STE, TEC, CGI, TET, GET) ficam
  `ignorar_fora_do_ic`: são optativas que alunos de CC/SI podem cursar e não
  entram em H8 nem nas salas do IC.

## Decisão de 10/10/2026: H12 relaxada para soft (confirmada com o orientador)

H12 (mínimo de 3 obrigatórias por ano) deixa de ser hard na instância oficial
de 2026. O mínimo continua sendo a meta, mas uma solução com docente abaixo
de 3 passa a ser viável, penalizada pelo déficit (turmas faltantes).

**Motivação (evidências levantadas em 10/10/2026):**

- No QH observado de 2026, **33 dos 61 docentes** deram menos de 3
  obrigatórias de CC/SI no ano (distribuição: 3 com 0, 10 com 1, 20 com 2).
  Com H12 hard no recorte CC/SI, o próprio horário real seria inviável.
- 15 docentes da carga 2025 não têm turma de CC/SI em 2026. Dois deles são
  permanentes confirmados: Christiano Braga (associado) e Leandro Santiago
  (adjunto). A hipótese do aluno é que sejam exceções, com carga fora do
  recorte (outros cursos, CEDERJ, pós) ou abatimentos.
- A carga docente de 2025 prevê abatimentos de carga horária ("CH mínima
  semanal de 12h, salvo abatimentos para 8h ou cargos que permitam isenção").
  59 dos 71 docentes têm algum abatimento, 45 deles por credenciamento na pós.
  **Cuidado:** os abatimentos são de carga horária semanal, não da regra das 3
  obrigatórias. Indicam que o departamento admite exceções, mas não provam que
  elas valem para H12.

**Como fica no modelo e no código:**

- Objetivo lexicográfico: (violações hard, déficit de H12, demais soft). O
  déficit já era o segundo nível; a mudança é que a contagem de docentes
  abaixo de 3 sai das violações hard e vai para `relaxadas` (objetivo direto)
  ou para `metadata` (avaliador).
- Na prática, o solver continua tentando cumprir H12 antes de otimizar
  janelas, dias e preferências. Só deixa de descartar soluções por isso.
- Parâmetro `h12_modo` no payload: padrão `hard`, para que os experimentos
  v1–v3 e de 2025 continuem reproduzíveis; `soft` na instância oficial,
  configurado em `H12_MODO_OFICIAL` (`scripts/check_readiness_2026.py`).
  Voltar atrás exige trocar só essa constante.
- O limite de 49 docentes no verificador e o erro de "H12 inviável" na
  validação só valem com H12 hard. Com soft, a instância registra
  `h12_cobertura`, cujo `piso_deficit` é o mínimo de turmas faltantes que
  nenhuma solução consegue evitar.
- A lista de permanentes (`universo_h12_2026.csv`) continua necessária para
  calcular o déficit.

**Confirmado com o orientador** (informado pelo aluno em 10/10/2026): H12
passa a ser soft, revendo a diretriz de 23/06/2026, que a tratava como
"restrição do departamento, não preferência".

## Extensão da regra das turmas de referência (10/10/2026)

A regra de 30/09 escolhia a turma externa de referência evitando choque só
com as outras referências do período. Agora ela também evita as turmas do IC
de horário fixo do período: nenhum dos dois lados pode se mover, então esse
choque virava um piso estrutural de H8. Aplicação:
`prefill_external_references_2026.py --sobrescrever`, que agora desfaz as
escolhas anteriores da regra antes de reaplicá-la (antes, a referência antiga
permanecia e a disciplina ficava com duas).

- Piso estrutural de H8 na instância oficial: 8 → 2 sobreposições.
- Referências alteradas (concentração de inscritos do curso):
  - 2026/1 `GET00177`: F1 → C1 (27% → 23%). F1 chocava com `TCC00306-A1`.
  - 2026/2 `GMA00155`: N9 → Q1 (23% → 22%). N9 chocava com `TCC00286-B1`.
  - 2026/2 `GAN00144`: F2 → B2 (48% → 11%). F2 chocava com
    `TCC00356-A1` (20–22). Na prática, o aluno de SI-P2 pode fazer F2 e
    `TCC00356-B1` (18–20) sem choque, mas o contador de H8 não considera
    turmas paralelas (decisão de 30/09). A troca evita esse artefato, ao custo
    de uma referência pouco representativa.
- Sobra 1 par fixa × fixa, só com turmas do IC: `TCC00332-B1` × `TCC00354-A1`
  (SI-P1, 2026/2). Ver a seção seguinte.

## Par TCC00332 × TCC00354 (piso de H8 restante) — mantido

Em SI-P1 de 2026/2, as duas disciplinas têm turmas paralelas em espelho:
`TCC00332` A1 (ter/qui 20–22) e B1 (18–20); `TCC00354` A1 (18–20) e B1
(20–22). O aluno combina 332-B1 com 354-B1, ou 332-A1 com 354-A1, sem choque.
O contador de H8 (decisão de 30/09) não considera turmas paralelas e acusa
332-B1 × 354-A1. As duas são fixas pela regra literal de 30/09: 332-B1 tem 5
vagas para Engenharia de Telecomunicações, e 354-A1 tem 1 vaga para Farmácia.

Decisão: manter. As sobreposições são um piso estrutural conhecido, que é
um artefato do contador e não um choque real para o aluno. Depois da recoleta
de 10/10, a 354-B1 também ficou fixa (1 vaga para Matemática), e a outra
metade do espelho (332-A1 × 354-B1, 20–22) entrou no piso: são 4
sobreposições. Os resultados
devem relatar as violações hard acima desse piso. Alternativas descartadas:
- tornar 354-A1 flexível contraria a regra literal de 30/09 (sem mínimo de
  vagas);
- mudar o contador de H8 contraria a decisão de 30/09 de mantê-lo.

## HP7 — Universo de H12 pela página de docentes do IC/UFF

- Fonte: `scripts/scrape_ic_docentes_2026.py` coleta nome e cargo das 65
  páginas listadas em https://www.ic.uff.br/docentes/ e grava
  `dados/brutos/docentes_ic_2026.csv` (coleta de 10/10/2026). São 61 com
  cargo, 2 sem cargo na página (Flávio Seixas, Igor Machado Coelho) e 4
  páginas de ex-docentes (homenagens).
- Regra: entra em H12 quem está na página com cargo de carreira permanente
  (auxiliar, assistente, adjunto, associado, titular). Quem não está na página
  fica fora. Os nomes são casados pelo nome completo normalizado ou pelo
  conjunto de palavras.
- Resultado em `universo_h12_2026.csv` (coluna `criterio_h12`): 62 docentes
  em H12, sendo 61 pela página e o Christiano Braga por decisão manual
  (associado, ausente da página).
- **A página não é um cadastro completo.** Dois exemplos: Christiano Braga é
  associado e não aparece; Plastino era coordenador da pós em 2025 e também
  não aparece. Fora da página e com turmas em 2026: Andre Silveira, João
  Pimentel, Mauricio, Miguel e Thiago (substitutos ou contratações recentes?).
  Fora da página e sem turmas de CC/SI em 2026: Ana Carolina, Dante, Heleno
  (substituto), John, Plastino e Simone. Com H12 soft, errar aqui só muda
  quem é penalizado.
- Piso do déficit de H12 (`h12_cobertura`): 29 turmas. As 148 obrigatórias,
  com as habilitações atuais, cobrem 143 dos 172 créditos exigidos. Helena
  está em H12 sem nenhuma obrigatória habilitada (déficit 3 inevitável).

## Turmas do IC ausentes do PDF do QH (10/10/2026)

As 11 turmas do IC que aparecem na coleta web mas não no PDF ficam
`ignorar_fora_do_pdf` (valor novo): 6 turmas Z1 com 1–3 vagas (arranjos
individuais), 2 seções extras X1 (`TCC00202`, `TCC00226`) e 2 tópicos
pequenos (`TCC00240`, `TCC00274`). A instância parte do planejamento oficial
(o PDF).

## Decisão de 10/10/2026: critérios soft normalizados pelo horário observado

Antes, os critérios soft eram somados brutos (peso 1), cada um na sua unidade.
No horário observado de 2026: desperdício de capacidade 2290 lugares, dias
trabalhados 233, preferência −79, janelas 46, rodízio 38. O desperdício
dominava: 10 lugares vazios valiam mais que 9 janelas, e atender a disciplina
preferida de um docente valia no máximo o mesmo que 1 lugar vazio.

Agora, na instância oficial, cada critério é dividido pelo módulo do seu
valor no horário observado, e todos têm peso 1 (`normalizacao_soft` no
payload, calculada por `soft_normalization()` em
`build_official_instance_2026.py`). No horário observado, cada penalidade vale
1, a preferência vale −1 e o total soft é 3. A ordem lexicográfica continua:
(hard, déficit de H12, total soft).

- Pesos: `PESOS_SOFT_OFICIAL` no builder (vazio = todos 1). Se o orientador
  priorizar algum critério, basta ajustar ali.
- Efeito, num guloso de uma passada: janelas 38 → 33, rodízio 36 → 31,
  déficit 34 → 33, preferência um pouco melhor; dias trabalhados 233 → 251.
  Agora os critérios contam em fração do horário observado: 1 janela (1/46)
  pesa cerca de 5× mais que 1 dia trabalhado (1/233).
- Sem `normalizacao_soft`, vale a soma bruta. Assim os experimentos v1–v3
  continuam reproduzíveis.
- **Recalibrar o SA:** as temperaturas dos configs (ex.: `temperatura_inicial`
  = 1e6 no v3) foram pensadas para a escala bruta. Com a normalização, as
  diferenças no nível soft são da ordem de 0,01.
- A referência depende da instância: se as vagas forem recoletadas
  (`--refresh-web`), a referência muda junto.

## Decisão de 10/10/2026: H10 soft como terceiro nível lexicográfico

A decisão de 30/09 já permitia relaxar H10 (capacidade) para soft, mas faltava
o peso. Optou-se por prioridade lexicográfica, como em H12, em vez de um peso
na soma:

- Medida: excesso = alunos acima da capacidade, somado por (turma, sala)
  (`guidance.excesso_capacidade`; a contagem de turmas vai para `relaxadas`).
- Ordem: (hard, déficit de H12, excesso de H10, total soft normalizado).
- Por que não um peso na soma normalizada: no horário observado o excesso é 0
  (a HP3 define as capacidades a partir dele), então não há referência para
  normalizar. Pela régua do desperdício (lugares) com peso 1, tirar uma
  janela compensaria cerca de 50 alunos sem lugar. Qualquer outro peso seria
  arbitrário.
- Por que abaixo de H12: as capacidades da HP3 são limites inferiores, então
  um excesso pequeno pode nem existir na sala real.
- Os movimentos de sala passam a propor salas menores que a turma (no fim da
  fila), o que antes era bloqueado em `candidate_rooms`.
- Controle: `h10_modo` no payload (padrão `hard`; `H10_MODO_OFICIAL = "soft"`
  em `check_readiness_2026.py`). Os experimentos anteriores não mudam.
- Efeito no guloso: nenhum. O excesso continua 0, porque só compensa quando
  reduz violações hard ou o déficit de H12.

## Recoleta das vagas (10/10/2026)

A coleta pública de 15/08 foi refeita (`webscrap/scrape_2026.py`, 431
turmas). Horários: nenhuma mudança. Inscritos mudaram em 170 turmas, vagas em
58, e o conjunto de cursos com vaga em 34. Turmas: 6 novas (5 seções de
`CGI00002` e `TCC00241-Z1`) e 2 removidas (`CGI00002-A1` e `TCC00243-Z1`).

A pipeline recusa tabelas de revisão quando as fontes mudam, e a opção
`--refresh-review-templates` apagaria as decisões. Criou-se
`scripts/refresh_review_evidence_2026.py`, que gera as tabelas numa cópia
temporária e leva para as reais só as colunas de evidência, casando linhas
por chave. As decisões não mudaram em nenhuma linha (conferido tabela a
tabela). Depois foram reaplicadas as regras, nesta ordem:
`prefill_fixed_schedules_2026.py`,
`prefill_external_references_2026.py --sobrescrever` e
`prefill_inferences_2026.py`.

Efeitos:
- 5 turmas do IC passaram a fixas (64 → 69), todas por 1 vaga para outro
  curso, aplicando a regra literal de 30/09: `TCC00298-A1`, `TCC00314-A1`,
  `TCC00328-A1`, `TCC00354-B1` e `TCC00360-A1` (2026/2). Restam 107 turmas
  flexíveis na instância. **A regra sem mínimo de vagas é sensível**: 1 aluno
  de outro curso fixa a turma inteira.
- 2 turmas de referência mudaram: `CGI00002` (A1, removida → F1) e
  `GSI00433` (B1 → A1), pelos inscritos atualizados.
- Piso de H8: 2 → 4 (o espelho TCC00332 × TCC00354 inteiro). Piso do déficit
  de H12: 29 (não mudou).
- Referência da normalização: o desperdício passou de 2290 para 2229; os
  demais termos não mudaram.

## Correção: frequência histórica congelada

As colunas `frequencia_historica_2023_2025` (habilitação) e
`ocorrencias_2023_2025` (prioridades) estavam vazias. A lógica do gerador
estava correta, mas as tabelas foram geradas em 21/08 com uma versão anterior
de `preferencias_2025.csv`, e a pipeline as preserva para não perder decisões.
Agora `build_review_tables_2026.py --atualizar-evidencias` recalcula só essas
colunas, e a pipeline executa esse passo sempre que preserva as tabelas. Nomes
sem histórico ficam vazios, e não com zero.

## Efeito na instância oficial (10/10/2026, após a recoleta)

- **`pronta_para_experimento = true`.** O verificador não tem pendências e a
  validação estrutural não tem erros (era 1133 pendências no início do dia).
- 217 turmas, 107 com horário flexível e 177 com professor a escolher.
- H12 soft (62 docentes no universo, piso do déficit = 29) e H10 soft
  (excesso de capacidade como terceiro nível). Critérios soft normalizados
  pelo horário observado.
- Piso estrutural de H8 = 4 (espelho TCC00332 × TCC00354, artefato do
  contador).
- Horário real de 2026 avaliado no modelo: 15 violações hard, déficit de H12
  = 48 e excesso de capacidade = 0. Um guloso de uma passada chega a 5 hard
  (todas de H8, 1 acima do piso), déficit 33, excesso 0 e total soft 2,26
  (o horário real vale 3).
