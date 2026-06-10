# Plano de execução do TCC

**Tema**: Metaheurísticas aplicadas à alocação de horários e salas de aula no Instituto de Computação da UFF, com pyoptframe.

**Data deste plano**: 09/06/2026. Premissa de defesa ao final de 2026/2 (~novembro/dezembro). Detalhes das diretrizes do orientador em `anotacoes/orientacao.md`.

---

## Visão do problema

O problema real é uma variante do **University Course Timetabling Problem (UCTP)** com alocação de salas, envolvendo três stakeholders em conflito (chefia de departamento, coordenação de curso e instituto/salas). A estratégia do orientador de **horários fixos por semestre par/ímpar** e **setores por dia da semana** reduz bastante o espaço de busca: grande parte da grade é dado de entrada, e o núcleo de otimização passa a ser:

1. **Atribuição de professores às turmas** (respeitando setores, preferências, prioridade, rodízio e jornada);
2. **Encaixe das optativas** (horário livre) na grade;
3. **Alocação de salas** (capacidade, recursos/laboratórios, e **distância entre salas de aulas consecutivas** — a ideia original do trabalho, mantida como critério de qualidade).

Recomendação: tratar como **problema em estágios acoplados** no protótipo (horários majoritariamente fixos → professores → optativas → salas), com a metaheurística otimizando uma função objetivo ponderada que enxerga tudo. Isso é defensável no texto (decomposição clássica de timetabling) e viável no prazo.

### Restrições fortes (hard)
- Matérias externas têm horário fixo imutável (ex.: Estruturas de Dados seg/qua);
- Sem choque de professor (mesmo professor, mesmo horário);
- Sem choque de sala (mesma sala, mesmo horário);
- Pedidos de recurso atendidos (turma que precisa de laboratório vai para laboratório);
- Jornada legal do professor: descanso mínimo entre o fim de um dia e o início do outro (caso "aula até 22h + aula às 7h");
- Matérias do mesmo período da grade curricular não podem se chocar (aluno precisa conseguir cursar o período completo).

### Critérios de qualidade (soft / função objetivo)
- Preferência do professor pela matéria (frequência histórica do webscrap como proxy), ponderada pela prioridade do professor (antiguidade);
- Minimizar número de dias com aula por professor;
- Minimizar janelas (buracos) no dia do professor;
- Aderência das matérias do setor aos dias do setor (algoritmos ter/qui etc.);
- Capacidade da sala vs. tamanho da turma (penalizar falta de vaga e desperdício);
- **Distância percorrida pelos alunos entre aulas consecutivas** (ideia original — exige matriz de distância entre salas e a grade curricular por período);
- Rodízio de professores entre semestres par/ímpar.

---

## Fases

### Fase 1 — Formalização do problema (junho/2026)
- [ ] Escrever o **modelo matemático** (conjuntos, parâmetros, variáveis de decisão, restrições, função objetivo ponderada) em `anotacoes/` ou já em LaTeX — vira a seção de modelagem da monografia e do artigo.
- [ ] Definir a grade de horários da UFF como conjunto discreto de slots (dia × faixa horária, incluindo 11–13h e noite 18h).
- [ ] Revisão de literatura dirigida: UCTP (ITC-2007 curriculum-based course timetabling é o benchmark mais próximo), surveys de timetabling educacional, trabalhos brasileiros (SBPO) e artigos do OptFrame. Anotar em `anotacoes/literatura.md`.
- [ ] Validar a formalização com o orientador (especialmente pesos dos critérios e o que é hard vs. soft).

### Fase 2 — Dados e instâncias (junho–julho/2026)
- [ ] Cobrar/receber a **planilha de setores** e demais itens de `dados/PENDENCIAS.md`.
- [ ] Limpar o webscrap (filtrar humanísticas, separar disciplinas do IC) e consolidar a matriz professor × disciplina de preferências.
- [ ] Estender o scraper para capturar **vagas e horários das turmas** (as `turma_url` já estão no CSV) — dá tamanhos de turma reais e a grade real como baseline.
- [ ] Definir um **formato de instância** (JSON) com: turmas, professores, setores, salas (capacidade/recursos/posição), horários fixos, optativas, preferências, prioridades, grade curricular por período.
- [ ] Gerar 3 níveis de instância: **toy** (validação manual), **real reduzida** (1 semestre, só IC) e **real completa**. O que faltar de dado real, sintetizar de forma plausível e documentar (o orientador liberou: "modelar próximo da realidade", sem compromisso com uso imediato).

### Fase 3 — Protótipo com pyoptframe (julho–agosto/2026)
- [ ] Estruturar `src/` como pacote: `model/` (entidades + leitura de instância), `eval/` (avaliador com decomposição por critério), `moves/` (vizinhanças), `solve/` (metaheurísticas).
- [ ] **Representação da solução**: por turma → (professor, slots de horário, sala); horários fixos ficam imutáveis na representação.
- [ ] **Construtivo guloso**: aloca primeiro as externas/fixas, depois obrigatórias por setor nos dias do setor, depois optativas, depois salas por melhor encaixe.
- [ ] **Vizinhanças (moves)**: trocar professor entre duas turmas; realocar professor de turma; mover optativa de slot; trocar sala de turma; trocar salas entre duas turmas.
- [ ] **Metaheurísticas via OptFrame**: começar com Simulated Annealing (já há experiência nos protótipos), depois ILS e/ou VNS. Comparar 2–3 — isso estrutura a seção experimental.
- [ ] Saída legível: grade gerada (dia × horário × sala) + relatório de violações e decomposição do objetivo por critério.

### Fase 4 — Experimentos (setembro/2026)
- [ ] Protocolo: N execuções por configuração (seeds distintas), tempo limite fixo, comparação por critério e agregado.
- [ ] Ajuste de parâmetros (grid simples; irace se der tempo).
- [ ] **Baseline forte**: comparar a solução da metaheurística com a **grade real da UFF** nos mesmos critérios — argumento central do trabalho.
- [ ] Cenário de ablação da ideia original: com e sem o critério de distância entre salas, medir o trade-off.
- [ ] (Opcional, se houver tempo) modelo MIP em instância pequena para limite inferior/validação.

### Fase 5 — Escrita (escrever junto, fechar em outubro–novembro/2026)
- [ ] Monografia no modelo do curso (`modelo_artigo/`): Introdução, Fundamentação (UCTP + metaheurísticas + OptFrame), Modelagem (Fase 1), Implementação (Fase 3), Experimentos (Fase 4), Conclusão.
- [ ] Condensar em **formato de artigo** (mesmo modelo LaTeX).
- [ ] Regra prática: ao fechar cada fase, escrever o capítulo correspondente — não deixar a escrita para o final.

---

## Cronograma resumido

| Mês | Entrega |
|---|---|
| Junho/2026 | Modelo formal + dados limpos + formato de instância |
| Julho/2026 | Instâncias prontas + protótipo v0 (construtivo + SA na instância toy) |
| Agosto/2026 | Vizinhanças completas + ILS/VNS rodando na instância real |
| Setembro/2026 | Experimentos + ablação do critério de distância |
| Outubro/2026 | Monografia completa em revisão |
| Novembro/2026 | Artigo + preparação da defesa |

## Riscos e mitigações

- **Dados não chegarem** (planilha de setores etc.) → sintetizar dados plausíveis e documentar; o orientador explicitou que aderência perfeita à prática não é requisito.
- **Escopo grande demais** → o corte mínimo defensável é: professores + salas com horários fixos dados (sem otimizar horário). Optativas e rodízio são as primeiras features a cortar se apertar.
- **pyoptframe limitar algo** → manter avaliador e moves em Python puro permite trocar o orquestrador (ex.: ILS manual) sem reescrever o modelo.
