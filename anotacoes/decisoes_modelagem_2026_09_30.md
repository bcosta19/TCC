# Decisões de modelagem — 30/09/2026

Decisões informadas pelo aluno em 30/09/2026 sobre as pendências levantadas
para a reunião com o orientador. Elas atualizam as hipóteses provisórias de
[`hipoteses_provisorias_2026_09_07.md`](hipoteses_provisorias_2026_09_07.md)
e as notas abertas de [`modelo_matematico.md`](modelo_matematico.md).

## Horários fixos e flexíveis (ex-HP2) — decidido

- **Fixo:** apenas turmas de outros departamentos (`C_out`) e
  disciplinas-serviço do IC.
- **Flexível dentro do setor:** obrigatórias do IC podem trocar de faixa,
  desde que nos dias do setor.
- **Livre:** optativas do IC (exceto projeto final).
- **Critério para "oferecida a outros cursos":** turma do IC com ao menos uma
  vaga alocada, na página pública da turma ("Vagas Alocadas"), para curso
  que não seja CC (31) nem SI (83) — inclusive IA e Ciência de Dados,
  Disciplina Isolada e CC de Rio das Ostras (alunos desses cursos em turmas
  de Niterói). Regra literal, sem mínimo de vagas.
- Aplicação automática por `scripts/prefill_fixed_schedules_2026.py`, que
  marca `validado=sim` e registra a evidência em `cursos_externos` e
  `criterio_horario`: 64 turmas do IC fixas, 115 flexíveis, 1 externa fixa.
- As vagas vêm da coleta de 15/08/2026; a página pode ter mudado depois (ex.:
  `2026-2-TCC00354-A1` mostra hoje uma vaga para Matemática que não estava na
  coleta). Recoletar com `run_pipeline_2026.py --refresh-web` antes do
  experimento final.

## Hard × soft — decidido

- **H8** (sem conflito de aluno): **hard**.
- **H11** (descanso entre dias): **hard**.
- **H10** (capacidade da sala): **pode ser relaxada** para *soft*, com
  penalidade. O peso ainda precisa ser definido junto com os demais pesos.
- O avaliador atual ainda conta H10 como hard (`capacidade_insuficiente`);
  a mudança para soft fica pendente da definição do peso.

## H8 com turmas da mesma disciplina — decidido

- Turmas A e B de uma mesma disciplina são **turmas distintas**: cada uma tem
  professor, sala e horário próprios, e cada uma deve estar livre de choque
  com as demais disciplinas do grupo curricular.
- Na prática, mantém-se o contador atual de H8 (sobreposição entre ofertas de
  códigos diferentes do mesmo grupo). A checagem por trajetória
  (`src/eval/trajectories.py`) continua apenas como diagnóstico auxiliar.

## H12 (ex-HP1) — decidido, sem fonte normativa

- Vale **só para docentes permanentes do IC**.
- Não existe hoje fonte normativa para H12; o texto deve apresentá-la como
  regra adotada no trabalho, não como norma institucional.
- Falta a lista oficial de permanentes (`universo_h12_2026.csv`).

## Disciplinas externas obrigatórias em H8 — decidido (opção 1)

- As 21 disciplinas obrigatórias de outros departamentos das grades de CC/SI
  (Cálculo, Física, Estatística etc.) entram em H8 como ocupação fixa.
- Como cada uma tem várias turmas abertas a CC/SI, fixa-se **uma turma de
  referência por disciplina, semestre e período**: a com mais alunos do curso
  inscritos (página pública da turma, "Vagas Alocadas") que não choque com as
  demais referências do período. A coluna `inscritos_curso_pct` mostra a
  concentração: em 28 das 38 referências ela passa de 50%; em Física
  (`GFI00158`), Cálculo II (`GMA00155`) e `GET00177` os alunos estão
  espalhados (21–38%) e a referência é fraca. As outras ficam
  como `alternativa_nao_modelada`.
- A escolha da turma de referência é uma hipótese a validar com a
  coordenação; o pré-preenchimento é feito por
  `scripts/prefill_external_references_2026.py` e não sobrescreve decisões
  humanas.
- Os experimentos exploratórios v1 e v2 foram rodados **sem** essas
  ocupações; seus números de H8 não são comparáveis aos da instância oficial.

## Cenários E1–E3 — mantidos

O escopo experimental mantém E1 (CC antes de SI), E2 (SI antes de CC) e E3
(conjunto).

## Classificação de `TCC00368` e `TCC00371` — decidido

- `TCC00368` (Pesquisa Operacional para SI): **optativa** (`optativa:SI`),
  apesar de aparecer vinculada a SI-P7 no QH 2025.
- `TCC00371` (Ética em IA e Ciência de Dados): **optativa** (`optativa:CC`,
  currículo em que a busca pública a retornou).
- Optativas não entram nos grupos curriculares de H8 nem contam para H12.

## Turmas com dois docentes — decidido

- Em 2026/2, `TCC00285-A1` (Análise e Projeto de Algoritmos) e
  `TCC00354-A1` (Fundamentos Matemáticos para Computação) aparecem com
  Martinhon e Raquel no PDF e na coleta web.
- Política de H12: `integral_para_cada_docente` (cada professor recebe +1).

## Aplicação à instância oficial

As tabelas de revisão são aplicadas ao JSON por
`scripts/build_official_instance_2026.py`, último passo da pipeline, que gera
`dados/processados/instancia_oficial_2026.json` sem proxies.

## Ainda em aberto

- Setor oficial das 115 turmas flexíveis (sem ele o domínio de horários não
  é gerado).
- Tratamento das 76 ofertas restantes de `revisao_turmas_externas_2026.csv`
  (65 optativas de outros departamentos e 11 turmas do IC ausentes do PDF).
- Pesos dos critérios soft, incluindo a penalidade de H10.
- Dados institucionais listados em [`../dados/PENDENCIAS.md`](../dados/PENDENCIAS.md).
