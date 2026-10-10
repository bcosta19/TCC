# Hipóteses provisórias e decisões — 10/10/2026

> Propostas pelo aluno em 10/10/2026, **pendentes de validação do orientador**.
> Não são diretrizes confirmadas nem dados institucionais. Servem para
> destravar a instância oficial de 2026 enquanto os dados do departamento não
> chegam. Se chegarem, a decisão manual substitui a inferência.

Aplicação: `scripts/prefill_inferences_2026.py`. As linhas preenchidas
recebem `validado=sim`, e a origem fica nas colunas `criterio_capacidade`,
`criterio_laboratorio`, `criterio_setor`, `criterio_habilitacao`,
`criterio_prioridade` e `criterio_referencia`, começando por `HP3`–`HP6` ou
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

- **70 linhas:** setor da planilha QH 2025 (`setor_historico_2025`).
- **29 linhas sem setor em 2025:** setor de disciplinas do mesmo assunto,
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
- Limitação: Christiano, Heleno e Leandro Santiago deram disciplinas em 2025,
  mas não têm turmas de CC/SI em 2026 (podem estar afastados). Eles entram nos
  domínios. A lista de permanentes de H12 deve ajudar a decidir se saem.
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

## Correção: frequência histórica congelada

As colunas `frequencia_historica_2023_2025` (habilitação) e
`ocorrencias_2023_2025` (prioridades) estavam vazias. A lógica do gerador
estava correta, mas as tabelas foram geradas em 21/08 com uma versão anterior
de `preferencias_2025.csv`, e a pipeline as preserva para não perder decisões.
Agora `build_review_tables_2026.py --atualizar-evidencias` recalcula só essas
colunas, e a pipeline executa esse passo sempre que preserva as tabelas. Nomes
sem histórico ficam vazios, e não com zero.

## Efeito na instância oficial (10/10/2026)

- Pendências do verificador: 1133 → 12. Restam o universo de H12 e as 11
  turmas do IC que aparecem na web mas não no PDF do QH (turmas X1/Z1,
  `TCC00240`, `TCC00274`…).
- A instância só acusa uma pendência de aplicação: `universo_h12`, ou seja, a
  lista de permanentes.
- 115 turmas com domínio gerado pelos padrões de dias do setor em 2025. Em 3
  delas o domínio tem só o horário observado, então ficam como fixas. Restam
  112 flexíveis.
- Preferências professor×disciplina não nulas na instância: 257 (antes da
  habilitação e da correção, eram 2).
