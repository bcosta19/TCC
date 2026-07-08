# Modelo matemático — alocação de horários e salas do IC/UFF

> Formalização do problema para avaliação (julho/2026). As decisões que ainda estão em aberto aparecem reunidas na Seção 10.

## 1. O problema

A tarefa é montar o quadro de horários do Instituto de Computação: decidir, para cada turma ofertada, qual professor a ministra, em quais horários da semana ela ocorre e em qual sala. Na literatura, o problema corresponde a uma variante do *University Course Timetabling Problem* (UCTP) na vertente *curriculum-based* — a competição ITC-2007, na trilha de *curriculum-based course timetabling*, é a referência mais próxima —, acrescida da alocação de salas com um critério de distância e das regras próprias do IC: setores com dias fixos na semana, horários pré-definidos por semestre par/ímpar, jornada legal do professor e carga anual mínima de disciplinas obrigatórias.

Dois aspectos definem o escopo da formalização.

**Planejamento anual.** Todo professor do IC deve ministrar no mínimo três disciplinas obrigatórias por ano, e o rodízio de professores compara as atribuições dos semestres par e ímpar. As duas regras atravessam os semestres; por isso a unidade de planejamento é o ano letivo, com os dois semestres resolvidos em conjunto. Otimizar cada semestre isoladamente deixaria essas regras sem efeito.

**Duas grades curriculares.** As disciplinas de computação compõem os currículos de Ciência da Computação (CC) e de Sistemas de Informação (SI). Os dois cursos pertencem ao mesmo departamento e seguem as mesmas regras — professores, setores, salas e horários fixos são os mesmos. A diferença está só na grade: em qual período cada disciplina é cursada. Disciplina presente nas duas grades é ofertada como uma única turma, compartilhada, cursada por alunos dos dois cursos.

A motivação original do trabalho — reduzir a distância que os alunos percorrem entre salas de aulas consecutivas — permanece como critério de qualidade (O5, Seção 7) e é o que diferencia esta formulação das versões usuais de UCTP.

## 2. Decisões de modelagem

A unidade programada é a **turma**: uma oferta de uma disciplina em um dos semestres do ano. Cada turma envolve três decisões acopladas: o professor, o padrão de horário (conjunto dos encontros semanais) e a sala.

Nem tudo isso é variável. A estratégia de horários fixos transforma boa parte da grade em dado de entrada, e o modelo organiza essa divisão classificando as turmas por dois eixos independentes.

**Eixo 1 — responsabilidade (quem aloca).** As turmas do próprio IC (código `TCC*`), denotadas $`\mathcal{C}^{\text{IC}}`$, têm professor e sala decididos pelo instituto; o horário é variável (restrito pelo setor e pela paridade) ou fixo, no caso das disciplinas-serviço. Já as turmas de outros departamentos cursadas pelos alunos do IC ($`\mathcal{C}^{\text{out}}`$ — Cálculo é o exemplo típico) chegam com professor e horário prontos: não cabe ao IC alocá-las, e elas entram no modelo apenas como ocupação fixa na agenda do aluno (restrição H8) e, se ocorrerem em sala do IC, como ocupação de sala (H7).

**Eixo 2 — papel curricular.** Obrigatórias de cada período ($`\mathcal{C}^{\text{obr}}`$) e optativas ($`\mathcal{C}^{\text{opt}}`$), estas com horário mais livre quando são do IC.

Os eixos são ortogonais: existe obrigatória de outro departamento (Cálculo) e optativa de outro departamento (Administração Aplicada à Engenharia). O departamento de origem sai do prefixo do código (`TCC*` = IC); o papel curricular vem da grade de cada curso.

Transversal aos dois eixos há o atributo de **horário fixo**: $`\mathcal{C}^{\text{fix}}`$ reúne todas as turmas de $`\mathcal{C}^{\text{out}}`$ e mais as disciplinas-serviço do IC (as disciplinas de programação são o caso típico — atendem outros cursos e por isso têm prioridade máxima). Para essas turmas o horário é parâmetro, não variável.

Completam as regras de domínio os **setores** (algoritmos, redes, engenharia de software, …), que fixam os dias da semana das turmas do IC e assim reduzem o domínio da variável de horário, e o regime **par/ímpar**, que define para cada obrigatória o padrão de horário previsto conforme a paridade do semestre.

As seções 3 a 7 apresentam o modelo completo, com todas as decisões do IC como variáveis; a Seção 9 mostra como essa estrutura se decompõe em estágios na resolução.

## 3. Conjuntos e índices

| Símbolo | Descrição |
|---|---|
| $`\mathcal{C}`$ | turmas a ofertar no ano letivo ($`c`$) — os dois semestres, ímpar e par |
| $`\mathcal{P}`$ | professores do IC ($`p`$) |
| $`\mathcal{R}`$ | salas ($`r`$) |
| $`\mathcal{D}`$ | dias letivos da semana ($`d`$): seg…sáb |
| $`\mathcal{B}`$ | faixas horárias do dia ($`b`$): manhã (incluindo 11–13h), tarde e noite (incluindo 18h) |
| $`\mathcal{H}=\mathcal{D}\times\mathcal{B}`$ | *slots* de horário ($`h`$) |
| $`\mathcal{Q}`$ | padrões de horário ($`q`$): cada padrão é um conjunto de slots semanais, ex.: $`\{\text{ter-}b,\ \text{qui-}b\}`$ |
| $`\mathcal{S}`$ | setores/áreas do departamento ($`s`$): algoritmos, redes, eng. de software, … |
| $`\mathcal{K}`$ | grades curriculares ($`k`$): $`\{\text{CC},\text{SI}\}`$ |
| $`\mathcal{G}`$ | grupos curriculares ($`g`$): turmas que um aluno de um período/ênfase cursa em conjunto; $`\mathcal{G}=\mathcal{G}^{\text{CC}}\cup\mathcal{G}^{\text{SI}}`$ |

Conjuntos e atributos derivados:

- $`H_q \subseteq \mathcal{H}`$: slots ocupados pelo padrão $`q`$; $`\text{dias}(q)\subseteq\mathcal{D}`$: dias do padrão $`q`$.
- Classificação das turmas (Seção 2): $`\mathcal{C}=\mathcal{C}^{\text{IC}}\cup\mathcal{C}^{\text{out}}`$ e $`\mathcal{C}=\mathcal{C}^{\text{obr}}\cup\mathcal{C}^{\text{opt}}`$ (uniões disjuntas), com o atributo transversal $`\mathcal{C}^{\text{fix}}\supseteq\mathcal{C}^{\text{out}}`$ (horário dado).
- $`\sigma(c)\in\{\text{ímpar},\text{par}\}`$: paridade (semestre do ano) da turma $`c`$. Semestres não interagem em slots: toda restrição ou critério indexado por slot (H6–H8, H11, O2, O3, O5) vale separadamente em cada semestre, com as somas restritas às turmas da paridade correspondente. Para não carregar a notação, as fórmulas estão escritas para um semestre genérico; só H12 e O6 atravessam os semestres — e são justamente elas que exigem o horizonte anual.
- Professores de outros departamentos são exógenos e não pertencem a $`\mathcal{P}`$.
- $`\mathcal{P}_c \subseteq \mathcal{P}`$: professores habilitados a ministrar a turma $`c\in\mathcal{C}^{\text{IC}}`$ (a partir da planilha de setores).
- $`\mathcal{Q}_c \subseteq \mathcal{Q}`$: padrões admissíveis para $`c`$ (restritos aos dias do setor; unitário $`=\{\bar q_c\}`$ se $`c\in\mathcal{C}^{\text{fix}}`$).
- $`\mathcal{R}_c \subseteq \mathcal{R}`$: salas compatíveis com os recursos que $`c`$ exige.
- $`\mathcal{C}_g \subseteq \mathcal{C}`$: turmas do grupo curricular $`g`$ — incluindo as de outros departamentos que o período cursa, pois elas bloqueiam o horário do aluno.
- $`k(g)\in\mathcal{K}`$: grade do grupo $`g`$. Cada grupo contém turmas de uma única paridade (o período $`n`$ de uma grade ocorre num semestre determinado do ano).
- $`\mathcal{C}^{k}\subseteq\mathcal{C}`$: turmas presentes na grade $`k`$. Disciplina das duas grades é uma turma só, $`c\in\mathcal{C}^{\text{CC}}\cap\mathcal{C}^{\text{SI}}`$, que aparece em grupos das duas grades (por exemplo, no período 3 de CC e no período 5 de SI).
- $`s(c)\in\mathcal{S}`$: setor da turma $`c`$ (definido para $`c\in\mathcal{C}^{\text{IC}}`$).

Como os dois cursos são do mesmo departamento, professores, setores e salas não se duplicam por grade. Por isso as restrições não mudam de forma com a segunda grade: H8 e O5 já somam sobre todos os grupos de $`\mathcal{G}`$; a novidade é que $`\mathcal{G}`$ passa a conter os grupos das duas grades.

## 4. Parâmetros

| Símbolo | Descrição |
|---|---|
| $`n_c \in \mathbb{Z}_+`$ | vagas (tamanho) da turma $`c`$ |
| $`\text{cap}_r \in \mathbb{Z}_+`$ | capacidade da sala $`r`$ |
| $`\rho_{c} \in \{0,1\}`$ | turma $`c`$ exige laboratório/recurso especial |
| $`\ell_r \in \{0,1\}`$ | sala $`r`$ é laboratório (e quais recursos possui) |
| $`\text{pref}_{p,c} \in [0,1]`$ | preferência do professor $`p`$ pela disciplina de $`c`$, estimada pela frequência histórica professor×disciplina no quadro de horários (2023/1–2025/2) |
| $`\pi_p \in [0,1]`$ | prioridade do professor $`p`$ (antiguidade/idade; maior = atendido primeiro) |
| $`\delta_{r,r'} \ge 0`$ | distância física entre as salas $`r`$ e $`r'`$ |
| $`\bar{q}_c \in \mathcal{Q}`$ | padrão de horário previsto/fixo de $`c`$ (por paridade; obrigatório se $`c\in\mathcal{C}^{\text{fix}}`$) |
| $`\bar{p}_c`$ | professor fixo de $`c`$ (dado de entrada para $`c\in\mathcal{C}^{\text{out}}`$) |
| $`\text{desc}_{\min}`$ | descanso mínimo, em horas, entre o fim do trabalho de um dia e o início do dia seguinte |
| $`w_\bullet \ge 0`$ | pesos dos termos da função objetivo (a calibrar) |
| $`w^{k} \ge 0`$ | peso da grade $`k`$ nos termos por currículo: $`w^{\text{CC}}, w^{\text{SI}}`$ (iguais = equidade entre os cursos) |

## 5. Variáveis de decisão

```math
x_{c,p}=\begin{cases}1 & \text{turma } c \text{ é ministrada por } p\\ 0 & \text{c.c.}\end{cases}
\qquad c\in\mathcal{C},\ p\in\mathcal{P}_c
```

```math
y_{c,q}=\begin{cases}1 & \text{turma } c \text{ recebe o padrão } q\\ 0 & \text{c.c.}\end{cases}
\qquad c\in\mathcal{C},\ q\in\mathcal{Q}_c
```

```math
z_{c,r}=\begin{cases}1 & \text{turma } c \text{ é alocada na sala } r\\ 0 & \text{c.c.}\end{cases}
\qquad c\in\mathcal{C},\ r\in\mathcal{R}_c
```

A ocupação em slot é uma variável derivada, que facilita escrever os conflitos:

```math
u_{c,h} = \sum_{q\in\mathcal{Q}_c \,:\, h\in H_q} y_{c,q} \in\{0,1\}
\qquad (\text{1 se } c \text{ tem aula no slot } h)
```

Para as turmas de horário ou professor dados, as variáveis ficam fixadas. Se $`c\in\mathcal{C}^{\text{out}}`$, então $`x_{c,\bar p_c}=1`$, $`y_{c,\bar q_c}=1`$ e $`z`$ não se aplica (a aula ocorre fora do IC, salvo indicação em contrário) — a turma participa só como ocupação fixa via $`u_{c,h}`$. Se $`c\in\mathcal{C}^{\text{fix}}\setminus\mathcal{C}^{\text{out}}`$ (disciplinas-serviço do IC), apenas o horário é fixo; professor e sala continuam sendo decisões do IC.

## 6. Restrições fortes (hard)

**(H1) Professor único.** Toda turma do IC tem exatamente um professor habilitado (as de outros departamentos já chegam com professor — H4b):

```math
\sum_{p\in\mathcal{P}_c} x_{c,p} = 1 \qquad \forall c\in\mathcal{C}^{\text{IC}}
```

**(H2) Horário único.**

```math
\sum_{q\in\mathcal{Q}_c} y_{c,q} = 1 \qquad \forall c\in\mathcal{C}
```

**(H3) Sala única**, para as turmas alocadas pelo IC:

```math
\sum_{r\in\mathcal{R}_c} z_{c,r} = 1 \qquad \forall c\in\mathcal{C}^{\text{IC}}
```

**(H4) Horário fixo** — disciplinas-serviço do IC e todas as de outros departamentos:

```math
y_{c,\bar{q}_c} = 1 \qquad \forall c\in\mathcal{C}^{\text{fix}}
```

**(H4b) Professor fixo** das turmas de outros departamentos:

```math
x_{c,\bar{p}_c} = 1 \qquad \forall c\in\mathcal{C}^{\text{out}}
```

**(H5) Setor fixa os dias.** Implícita no domínio: $`\mathcal{Q}_c`$ só contém padrões cujos dias coincidem com os do setor $`s(c)`$ (vale para as turmas do IC de horário variável; as de $`\mathcal{C}^{\text{fix}}`$ já têm horário dado por H4).

**(H6) Sem conflito de professor.** Um professor não ministra duas turmas no mesmo slot. Como $`\mathcal{P}`$ contém apenas professores do IC, o somatório ignora $`\mathcal{C}^{\text{out}}`$ — a jornada de docente externo é responsabilidade do departamento de origem:

```math
\sum_{c\in\mathcal{C}} x_{c,p}\, u_{c,h} \le 1 \qquad \forall p\in\mathcal{P},\ \forall h\in\mathcal{H}
```

**(H7) Sem conflito de sala.** Uma sala não recebe duas turmas no mesmo slot. As turmas de fora não têm $`z`$ e não entram (ocorrem fora do IC); se alguma usar sala do IC, entra com sala fixa $`\bar r_c`$:

```math
\sum_{c\in\mathcal{C}} z_{c,r}\, u_{c,h} \le 1 \qquad \forall r\in\mathcal{R},\ \forall h\in\mathcal{H}
```

**(H8) Sem conflito para o aluno.** Turmas do mesmo grupo curricular não coincidem em slot. Aqui as turmas de outros departamentos importam: $`\mathcal{C}_g`$ inclui as de $`\mathcal{C}^{\text{out}}`$ do período, com ocupação fixa, de modo que o horário do Cálculo de fato bloqueia os slots disponíveis para as obrigatórias daquele período:

```math
\sum_{c\in\mathcal{C}_g} u_{c,h} \le 1 \qquad \forall g\in\mathcal{G},\ \forall h\in\mathcal{H}
```

**(H9) Laboratório.** Turma que exige laboratório vai para sala compatível (já embutido em $`\mathcal{R}_c`$; explicitando):

```math
z_{c,r}=0 \quad \text{se } \rho_c=1 \text{ e } \ell_r=0 \qquad \forall c,\ \forall r
```

**(H10) Capacidade.** A sala alocada comporta o tamanho da turma:

```math
z_{c,r}=1 \;\Rightarrow\; n_c \le \text{cap}_r \qquad \forall c\in\mathcal{C},\ \forall r\in\mathcal{R}_c
```

(na prática, basta fixar $`z_{c,r}=0`$ sempre que $`n_c > \text{cap}_r`$.)

**(H11) Jornada legal — descanso entre dias.** Se o professor leciona na última faixa de um dia, não pode lecionar na primeira faixa do dia seguinte quando o intervalo fica abaixo de $`\text{desc}_{\min}`$. Em forma linear, para cada par de slots $`(h,h')`$ que viola o descanso:

```math
\sum_{c} x_{c,p}\,u_{c,h} + \sum_{c} x_{c,p}\,u_{c,h'} \le 1
\qquad \forall p,\ \forall (h,h')\in \text{ViolaDescanso}
```

**(H12) Carga mínima anual de obrigatórias.** Todo professor do IC ministra ao menos três turmas obrigatórias do IC no ano. A soma percorre os dois semestres — é, junto com O6, o que exige o horizonte anual:

```math
\sum_{c\,\in\,\mathcal{C}^{\text{IC}}\cap\,\mathcal{C}^{\text{obr}}} x_{c,p}\ \ge\ 3
\qquad \forall p\in\mathcal{P}
```

A restrição só é satisfazível se $`|\mathcal{C}^{\text{IC}}\cap\mathcal{C}^{\text{obr}}|\ge 3\,|\mathcal{P}|`$ no ano. Ela também aperta o resto do modelo: obrigar três obrigatórias por professor consome a folga que atenderia preferências (O1) e rodízio (O6). Essa tensão entre departamento e professores é real e desejada — e não gera termo novo na função objetivo, por ser restrição forte.

> H8, H10, H11 e H12 podem ser relaxadas para *soft* (penalização) caso inviabilizem as instâncias reais — é uma das decisões em aberto (Seção 10). A capacidade (H10) concentra o conflito chefia × coordenação × instituto (turma grande × vaga × sala); a carga anual (H12) é a candidata mais provável a precisar de folga.

## 7. Função objetivo (critérios de qualidade)

Minimiza-se a penalidade total ponderada; preferências entram como bônus (penalidade negativa). Com as duas grades, $`Z`$ separa os termos em dois blocos: os **compartilhados**, centrados em professor e sala e calculados uma única vez sobre todas as turmas (O1, O2, O3, O4, O6), e os **por currículo**, que dependem dos períodos de cada grade (O5 e, se H8 vier a ser relaxada, um termo de choque do aluno $`\Phi^{k}_{\text{aluno}}`$):

```math
\min\ Z \;=\; Z_{\text{compart}} \;+\; \sum_{k\in\mathcal{K}} w^{k}\,Z^{k}_{\text{curr}}
```

```math
Z_{\text{compart}} = \underbrace{-\,w_{\text{pref}}\sum_{c}\sum_{p\in\mathcal{P}_c}\pi_p\,\text{pref}_{p,c}\,x_{c,p}}_{\text{(O1) preferência} \times \text{prioridade}}
+ w_{\text{dias}}\,\Phi_{\text{dias}}
+ w_{\text{jan}}\,\Phi_{\text{jan}}
+ w_{\text{cap}}\,\Phi_{\text{cap}}
+ w_{\text{rod}}\,\Phi_{\text{rod}}
```

```math
Z^{k}_{\text{curr}} = w_{\text{dist}}\,\Phi^{k}_{\text{dist}}
\qquad k\in\mathcal{K}
\quad\bigl(+\; w_{\text{aluno}}\,\Phi^{k}_{\text{aluno}}\ \text{se H8 for relaxada para soft}\bigr)
```

Com $`w^{\text{CC}}=w^{\text{SI}}=1`$, $`Z`$ equivale à soma simples dos critérios O1–O6; os pesos por grade existem para o estudo de equidade entre os cursos (Seção 9).

**(O1) Preferência ponderada pela prioridade.** Professores mais prioritários (mais antigos) são atendidos primeiro em suas disciplinas preferidas — o critério da chefia ao distribuir turmas.

**(O2) Dias trabalhados — $`\Phi_{\text{dias}}`$.** Minimizar o número de dias com aula por professor. Com a auxiliar $`t_{p,d}\in\{0,1\}`$ (=1 se $`p`$ leciona no dia $`d`$):

```math
t_{p,d} \ge x_{c,p}\,u_{c,h}\quad \forall h\in d; \qquad \Phi_{\text{dias}}=\sum_{p}\sum_{d} t_{p,d}
```

**(O3) Janelas — $`\Phi_{\text{jan}}`$.** Minimizar buracos na agenda do professor: para cada professor e dia, contam-se os slots ociosos entre a primeira e a última aula do dia.

**(O4) Desperdício de capacidade — $`\Phi_{\text{cap}}`$.** Penalizar sala muito maior que a turma:

```math
\Phi_{\text{cap}}=\sum_{c}\sum_{r\in\mathcal{R}_c} z_{c,r}\,(\text{cap}_r - n_c)
```

**(O5) Distância percorrida pelos alunos — $`\Phi^{k}_{\text{dist}}`$** *(ideia original do trabalho)*. Para cada grupo curricular $`g`$ da grade $`k`$ e cada par de slots consecutivos $`(h,h')`$ no mesmo dia em que $`g`$ tem aulas nas salas $`r`$ e $`r'`$, soma-se $`\delta_{r,r'}`$:

```math
\Phi^{k}_{\text{dist}}=\sum_{g\in\mathcal{G}^{k}}\ \sum_{(h,h')\,\text{consec.}}\ \sum_{c,c'\in\mathcal{C}_g}\ \sum_{r,r'} \delta_{r,r'}\;(z_{c,r}\,u_{c,h})\,(z_{c',r'}\,u_{c',h'})
```

O termo é quadrático; na resolução por metaheurística ele é avaliado diretamente sobre a solução, sem linearizar. É o único critério que depende da grade — por isso fica em $`Z^{k}_{\text{curr}}`$, o que permite medir e ponderar CC e SI separadamente.

**(O6) Rodízio par/ímpar — $`\Phi_{\text{rod}}`$.** Penalizar manter o mesmo professor na mesma disciplina em semestres de paridade diferente, incentivando o rodízio. Com o horizonte anual, a comparação envolve as atribuições dos dois semestres do próprio ano (ambas variáveis do modelo) e a do ano anterior (parâmetro histórico).

Para os pesos, a sugestão de partida é normalizar cada termo em $`[0,1]`$ e atribuir importâncias — a calibração é uma das decisões da Seção 10. O termo de distância (O5) é o diferencial do trabalho e terá um estudo de ablação (com/sem) nos experimentos.

## 8. Onde cada papel aparece no modelo

Os papéis envolvidos na montagem do horário — e os conflitos entre eles — se traduzem no modelo assim:

| Papel | Onde aparece |
|---|---|
| Chefia de departamento (aloca professores, quer turma grande) | O1 (preferência × prioridade), H1, H10/O4 (tamanho × sala) |
| Coordenação de curso (representa os alunos, quer vaga) | H8 (sem choque para o aluno), H10 (vaga), O5 (deslocamento) |
| Coordenações de CC e SI entre si (disputam professores, salas e slots) | $`\mathcal{G}^{k}`$ em H8, $`\Phi^{k}_{\text{dist}}`$ (O5), pesos $`w^{k}`$, experimentos E1–E3 (Seção 9) |
| Instituto de Computação (administra as salas) | H3, H7, H9, H10, O4 |
| Departamento (carga docente anual) | H12 (mínimo de 3 obrigatórias/ano por professor) |
| Jornada legal do professor | H11, O2, O3 |
| Disciplinas-serviço do IC (horário prioritário, ex.: disciplinas de programação) | H4 (horário fixo), H5 |
| Disciplinas de outros departamentos (exógenas) | H4 (horário), H4b (professor), H8 (bloqueio do aluno) |

## 9. Estratégia de resolução e o estudo das duas grades

O modelo será resolvido por metaheurísticas (Simulated Annealing e, na sequência, ILS/VNS), em estágios acoplados mas com um único avaliador $`Z`$ enxergando a solução inteira:

1. fixar o plano de fundo — professor e horário das turmas de $`\mathcal{C}^{\text{out}}`$, horário das disciplinas-serviço, dias por setor;
2. construção gulosa — professores das turmas do IC priorizando O1, depois o encaixe das optativas, depois salas por melhor ajuste de capacidade e recurso;
3. busca local sobre vizinhanças que trocam professor, padrão de horário e sala das turmas do IC, guiada por $`Z`$ e pelas penalidades das restrições relaxadas.

Sobre esse esqueleto, proponho três experimentos para estudar o acoplamento entre as grades — na prática, o conflito entre as coordenações de CC e SI disputando os mesmos professores, salas e slots:

- **E1 (CC → SI).** Otimiza considerando só $`\mathcal{G}^{\text{CC}}`$; congela as turmas de $`\mathcal{C}^{\text{CC}}`$ (compartilhadas e exclusivas de CC) como plano de fundo fixo; depois otimiza as turmas exclusivas de SI sujeitas a $`\mathcal{G}^{\text{SI}}`$ e ao plano de fundo já ocupado. Minimiza $`Z_{\text{compart}} + Z^{\text{CC}}_{\text{curr}}`$ na primeira etapa e $`Z_{\text{compart}} + Z^{\text{SI}}_{\text{curr}}`$ na segunda.
- **E2 (SI → CC).** Simétrico a E1.
- **E3 (conjunto).** As duas grades ativas ao mesmo tempo, minimizando $`Z = Z_{\text{compart}} + w^{\text{CC}}Z^{\text{CC}}_{\text{curr}} + w^{\text{SI}}Z^{\text{SI}}_{\text{curr}}`$, primeiro com pesos iguais (equidade); numa variante E3', com pesos ajustados para compensar o curso que sai pior nos sequenciais.

As métricas do estudo: decompor $`Z`$ por grade e por critério, medir o "custo de ir depois" (a assimetria entre E1 e E2) e comparar a otimização conjunta com as sequenciais — a expectativa é que E3 equilibre melhor os dois cursos. O custo de implementação é baixo, porque congelar uma grade reusa o mecanismo de plano de fundo do estágio 1, e o avaliador decomposto já fornece $`Z^{\text{CC}}`$ e $`Z^{\text{SI}}`$ separados.

Uma ressalva: nos experimentos sequenciais, as turmas compartilhadas ficam inteiramente decididas pela primeira grade — o segundo curso só otimiza suas exclusivas. Quanto maior a interseção CC∩SI, menor a liberdade do segundo estágio. O tamanho desse efeito é um dos resultados a medir, não um defeito do método.

## 10. Pontos em aberto

1. **Hard × soft.** H8 (choque do aluno), H10 (capacidade) e H11 (descanso) estão como restrições fortes; se inviabilizarem as instâncias reais, a proposta é relaxá-las com penalização na função objetivo. A mesma pergunta vale para H12: se a oferta anual de obrigatórias do IC ficar abaixo de $`3\,|\mathcal{P}|`$, não existe solução viável — nesse caso, admite-se folga?
2. **Pesos.** Calibração dos $`w_\bullet`$ (proposta: normalizar cada termo em $`[0,1]`$ e atribuir importâncias) e dos pesos por grade $`w^{\text{CC}}/w^{\text{SI}}`$, que começam iguais.
3. **Dados que faltam.** Planilha de setores (define $`\mathcal{S}`$, $`\mathcal{P}_c`$ e os dias de cada setor); grade de SI por período (define $`\mathcal{G}^{\text{SI}}`$ e a interseção CC∩SI); lista de obrigatórias × optativas por período; salas com capacidade, recursos e localização (para a matriz $`\delta_{r,r'}`$); e a grade de horários real para fechar as faixas $`\mathcal{B}`$ e os padrões $`\mathcal{Q}`$.
4. **Caso particular.** Alguma disciplina de outro departamento ocorre em sala do IC? Se sim, ela entra em H7 com sala fixa.
