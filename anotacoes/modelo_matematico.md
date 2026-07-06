# Modelo matemático — alocação de horários e salas (IC/UFF)

> Rascunho da formalização (Fase 1 do `PLANO.md`). Notação em LaTeX para reaproveitar direto na monografia e no artigo. **Revisar com o orientador**, em especial: o que é restrição forte (hard) × fraca (soft), e os pesos $`w_\bullet`$ da função objetivo (incluindo os pesos por grade $`w^{\text{CC}}/w^{\text{SI}}`$).

O problema é uma variante do **University Course Timetabling Problem (UCTP)**, na vertente *curriculum-based course timetabling* (referência: ITC-2007, track 3), acrescida de **alocação de salas com distância** e das regras específicas do IC/UFF (setores por dia, horários fixos por semestre par/ímpar, jornada legal do professor, carga anual mínima de obrigatórias). O planejamento cobre **duas grades curriculares** — Ciência da Computação (CC) e Sistemas de Informação (SI) —, ambas do mesmo departamento e sob as mesmas regras; a única diferença entre elas é em qual período cada disciplina é cursada.

---

## 1. Decisão de modelagem

A unidade de **planejamento** é o **ano letivo** (semestres ímpar e par juntos): a carga anual de obrigatórias (H12) e o rodízio par/ímpar (O6) acoplam os dois semestres, então otimizá-los separadamente perderia exatamente essas restrições. A unidade a ser **programada** segue sendo a **turma** (uma oferta de uma disciplina num semestre; a paridade $`\sigma(c)`$, Seção 2, diz em qual dos dois semestres do ano ela ocorre). Cada turma precisa de três decisões acopladas:

1. **qual professor** a ministra;
2. **em qual padrão de horário** (conjunto de encontros semanais);
3. **em qual sala**.

A estratégia do orientador reduz o espaço de busca fixando parte disso como **dado de entrada** (parâmetro), não como variável. Para organizar o que é variável e o que é dado, cada turma é classificada por **dois eixos independentes**:

**Eixo 1 — responsabilidade (quem aloca):**

- $`\mathcal{C}^{\text{IC}}`$ — turmas **do próprio IC** (código `TCC*`). O IC decide professor e sala; o horário é variável (restrito por setor/paridade) ou fixo (disciplinas-serviço, abaixo).
- $`\mathcal{C}^{\text{out}}`$ — turmas de **outros departamentos** cursadas por alunos do IC (código não-`TCC`; ex.: Cálculo/`GMA`, Administração Aplicada à Engenharia/`TEP`). **Professor e horário são dados de entrada** — não cabe ao IC alocá-las. Entram no modelo apenas como **ocupação fixa do horário do aluno** (restrição H8) e, se ocorrerem em salas do IC, como ocupação de sala (H7).

**Eixo 2 — papel curricular (compõe os grupos $`\mathcal{G}`$ e diz o que tem encaixe livre):**

- $`\mathcal{C}^{\text{obr}}`$ — obrigatórias de cada período;
- $`\mathcal{C}^{\text{opt}}`$ — optativas (horário mais livre, quando são do IC).

> Os eixos são **ortogonais**: existe optativa de outro departamento (Administração Aplicada à Engenharia $`\in \mathcal{C}^{\text{out}}\cap\mathcal{C}^{\text{opt}}`$) e obrigatória de outro departamento (Cálculo $`\in \mathcal{C}^{\text{out}}\cap\mathcal{C}^{\text{obr}}`$). O **departamento** sai automaticamente do prefixo do código (`TCC*` = IC); o **papel curricular** (obrigatória/optativa por período) vem da grade do curso — lista a receber.

Atributo transversal — **horário fixo:**

- $`\mathcal{C}^{\text{fix}}\subseteq\mathcal{C}`$ — turmas com padrão de horário **dado**: todas as de $`\mathcal{C}^{\text{out}}`$ **mais** as disciplinas-serviço do IC (ex.: Estruturas de Dados, oferecida a outros cursos com prioridade máxima). Para elas $`y`$ é parâmetro.

Demais regras de domínio:

- **Setores** (algoritmos, redes, eng. de software, …) fixam os **dias da semana** das turmas do IC → restringem o domínio da variável de horário.
- O regime **par/ímpar** define, para cada obrigatória do IC, um padrão de horário previsto por paridade de semestre.

Apresento abaixo o **modelo completo** (todas as decisões do IC como variáveis) e, na Seção 8, como essa estrutura o particiona em estágios para o protótipo.

---

## 2. Conjuntos e índices

| Símbolo | Descrição |
|---|---|
| $`\mathcal{C}`$ | turmas a ofertar no **ano letivo** ($`c`$) — os dois semestres, ímpar e par |
| $`\mathcal{P}`$ | professores ($`p`$) |
| $`\mathcal{R}`$ | salas ($`r`$) |
| $`\mathcal{D}`$ | dias letivos da semana ($`d`$): seg…sáb |
| $`\mathcal{B}`$ | faixas horárias do dia ($`b`$): manhã (incl. 11–13h), tarde, noite (incl. 18h) |
| $`\mathcal{H}=\mathcal{D}\times\mathcal{B}`$ | *slots* de horário ($`h`$) |
| $`\mathcal{Q}`$ | padrões de horário ($`q`$): cada padrão é um conjunto de slots semanais, ex.: $`\{\text{ter-}b,\ \text{qui-}b\}`$ (2 encontros/semana) |
| $`\mathcal{S}`$ | setores/áreas do departamento ($`s`$): algoritmos, redes, eng. software, … |
| $`\mathcal{K}`$ | grades curriculares ($`k`$): $`\{\text{CC},\text{SI}\}`$ — mesmo departamento e mesmas regras; diferem apenas em qual período cada disciplina é cursada |
| $`\mathcal{G}`$ | grupos curriculares ($`g`$): conjunto de turmas que um aluno de um período/ênfase cursa em conjunto; cada grupo pertence a uma grade: $`\mathcal{G}=\mathcal{G}^{\text{CC}}\cup\mathcal{G}^{\text{SI}}`$ |

Conjuntos derivados:
- $`H_q \subseteq \mathcal{H}`$: slots ocupados pelo padrão $`q`$; $`\text{dias}(q)\subseteq\mathcal{D}`$: dias do padrão $`q`$.
- **Classificação das turmas** (Seção 1): por responsabilidade $`\mathcal{C}=\mathcal{C}^{\text{IC}}\cup\mathcal{C}^{\text{out}}`$ (disjuntos); por papel curricular $`\mathcal{C}=\mathcal{C}^{\text{obr}}\cup\mathcal{C}^{\text{opt}}`$ (disjuntos); e o atributo transversal $`\mathcal{C}^{\text{fix}}\supseteq\mathcal{C}^{\text{out}}`$ (horário dado).
- $`\sigma(c)\in\{\text{ímpar},\text{par}\}`$: **paridade** (semestre do ano) da turma $`c`$. Semestres não interagem em slots: toda restrição/critério indexado por slot $`h`$ (H6–H8, H11, O2, O3, O5) vale **separadamente por semestre**, com as somas restritas às turmas da paridade correspondente — as fórmulas são escritas para um semestre genérico para não carregar a notação. Apenas H12 e O6 **atravessam** os semestres (por isso o horizonte é anual).
- $`\mathcal{P}`$: professores **do IC**; os de outros departamentos são exógenos e **não** pertencem a $`\mathcal{P}`$.
- $`\mathcal{P}_c \subseteq \mathcal{P}`$: professores **habilitados** a ministrar a turma $`c\in\mathcal{C}^{\text{IC}}`$ (planilha de setores/afinidade).
- $`\mathcal{Q}_c \subseteq \mathcal{Q}`$: padrões **admissíveis** para $`c`$ (restritos pelos dias do setor; **unitário** $`=\{\bar q_c\}`$ se $`c\in\mathcal{C}^{\text{fix}}`$).
- $`\mathcal{R}_c \subseteq \mathcal{R}`$: salas compatíveis com os recursos exigidos por $`c`$.
- $`\mathcal{C}_g \subseteq \mathcal{C}`$: turmas do grupo curricular $`g`$ — **inclui as de outros departamentos** ($`\mathcal{C}^{\text{out}}`$) que o período cursa (ex.: Cálculo), pois bloqueiam o horário do aluno.
- $`k(g)\in\mathcal{K}`$: grade do grupo $`g`$. Cada grupo contém turmas de **uma única paridade** (o período $`n`$ de uma grade ocorre num semestre determinado do ano).
- $`\mathcal{C}^{k}\subseteq\mathcal{C}`$: turmas presentes na grade $`k`$. Disciplina presente nas duas grades é **uma única turma compartilhada** (mesmo professor/sala/horário), $`c\in\mathcal{C}^{\text{CC}}\cap\mathcal{C}^{\text{SI}}`$, cursada por alunos dos dois cursos — ela aparece em grupos das duas grades (ex.: período 3 de CC e período 5 de SI). Também usado para congelar uma grade como plano de fundo nos experimentos (Seção 9).
- $`s(c)\in\mathcal{S}`$: setor da turma $`c`$ (definido só para $`c\in\mathcal{C}^{\text{IC}}`$).

> **Recursos únicos, restrições inalteradas:** professores ($`\mathcal{P}`$), setores ($`\mathcal{S}`$) e salas ($`\mathcal{R}`$) são **compartilhados** entre as grades (mesmo departamento) — não se duplicam por grade. Por isso **H8 e O5 não mudam de forma** com as duas grades: elas já somam sobre todo $`g\in\mathcal{G}`$; o que muda é que $`\mathcal{G}`$ agora contém os grupos das duas grades.

---

## 3. Parâmetros

| Símbolo | Descrição |
|---|---|
| $`n_c \in \mathbb{Z}_+`$ | nº de vagas (tamanho) da turma $`c`$ |
| $`\text{cap}_r \in \mathbb{Z}_+`$ | capacidade da sala $`r`$ |
| $`\rho_{c} \in \{0,1\}`$ | turma $`c`$ exige laboratório/recurso especial |
| $`\ell_r \in \{0,1\}`$ | sala $`r`$ é laboratório (e quais recursos possui) |
| $`\text{pref}_{p,c} \in [0,1]`$ | preferência do professor $`p`$ pela disciplina de $`c`$ (proxy: frequência histórica no webscrap) |
| $`\pi_p \in [0,1]`$ | prioridade do professor $`p`$ (antiguidade/idade; maior = atendido primeiro) |
| $`\delta_{r,r'} \ge 0`$ | distância física entre as salas $`r`$ e $`r'`$ (matriz de distâncias) |
| $`\bar{q}_c \in \mathcal{Q}`$ | padrão de horário **previsto/fixo** de $`c`$ (par/ímpar; obrigatório se $`c\in\mathcal{C}^{\text{fix}}`$) |
| $`\bar{p}_c`$ | professor **fixo** de $`c`$ (dado de entrada para $`c\in\mathcal{C}^{\text{out}}`$; exógeno ao IC) |
| $`\text{desc}_{\min}`$ | descanso mínimo (em horas) entre o fim do trabalho de um dia e o início do dia seguinte |
| $`w_\bullet \ge 0`$ | pesos dos termos da função objetivo (a calibrar) |
| $`w^{k} \ge 0`$ | peso da grade $`k\in\mathcal{K}`$ nos termos por currículo de $`Z`$: $`w^{\text{CC}}, w^{\text{SI}}`$ — iguais = equidade entre os cursos; ajustados = compensar a grade prejudicada (Seções 6 e 9) |

---

## 4. Variáveis de decisão

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

Variável auxiliar de **ocupação em slot** (derivada, facilita escrever conflitos):

```math
u_{c,h} = \sum_{q\in\mathcal{Q}_c \,:\, h\in H_q} y_{c,q} \in\{0,1\}
\qquad (\text{1 se } c \text{ tem aula no slot } h)
```

> **Domínios fixados.** Para $`c\in\mathcal{C}^{\text{out}}`$ (outros departamentos), professor e horário são parâmetros: $`x_{c,\bar p_c}=1`$ e $`y_{c,\bar q_c}=1`$, e $`z`$ **não se aplica** (a aula ocorre fora do IC, salvo indicação contrária) — essas turmas entram só como ocupação fixa via $`u_{c,h}`$. Para $`c\in\mathcal{C}^{\text{fix}}\setminus\mathcal{C}^{\text{out}}`$ (disciplinas-serviço do IC, ex.: Estruturas de Dados), apenas o horário é fixo ($`y_{c,\bar q_c}=1`$); professor ($`x`$) e sala ($`z`$) seguem sendo variáveis do IC.

---

## 5. Restrições fortes (hard)

**(H1) Atribuição única de professor.** Toda turma **do IC** tem exatamente um professor habilitado (as de outros departamentos já têm professor fixo — H4b):

```math
\sum_{p\in\mathcal{P}_c} x_{c,p} = 1 \qquad \forall c\in\mathcal{C}^{\text{IC}}
```

**(H2) Atribuição única de horário.**

```math
\sum_{q\in\mathcal{Q}_c} y_{c,q} = 1 \qquad \forall c\in\mathcal{C}
```

**(H3) Atribuição única de sala** (turmas alocadas pelo IC):

```math
\sum_{r\in\mathcal{R}_c} z_{c,r} = 1 \qquad \forall c\in\mathcal{C}^{\text{IC}}
```

**(H4) Horário fixo** (disciplinas-serviço do IC + todas as de outros departamentos):

```math
y_{c,\bar{q}_c} = 1 \qquad \forall c\in\mathcal{C}^{\text{fix}}
```

**(H4b) Professor fixo das de outros departamentos** (o IC não as aloca):

```math
x_{c,\bar{p}_c} = 1 \qquad \forall c\in\mathcal{C}^{\text{out}}
```

**(H5) Setor fixa os dias.** Implícita no domínio: $`\mathcal{Q}_c`$ só contém padrões com $`\text{dias}(q)`$ iguais aos dias do setor $`s(c)`$ (vale para $`c\in\mathcal{C}^{\text{IC}}`$ de horário variável; as de $`\mathcal{C}^{\text{fix}}`$ já têm horário dado por H4).

**(H6) Sem conflito de professor.** Um professor do IC não ministra duas turmas no mesmo slot (como $`\mathcal{P}`$ são só professores do IC, o somatório ignora $`\mathcal{C}^{\text{out}}`$ — jornada de docente externo é problema do departamento dele):

```math
\sum_{c\in\mathcal{C}} x_{c,p}\, u_{c,h} \le 1 \qquad \forall p\in\mathcal{P},\ \forall h\in\mathcal{H}
```

**(H7) Sem conflito de sala.** Uma sala do IC não recebe duas turmas no mesmo slot (as de $`\mathcal{C}^{\text{out}}`$ não têm $`z`$, logo não entram — supõe-se que ocorrem fora do IC; se alguma usar sala do IC, entra com sala fixa $`\bar r_c`$):

```math
\sum_{c\in\mathcal{C}} z_{c,r}\, u_{c,h} \le 1 \qquad \forall r\in\mathcal{R},\ \forall h\in\mathcal{H}
```

**(H8) Sem conflito de aluno.** Turmas do mesmo grupo curricular não coincidem em slot. **Aqui as de outros departamentos importam**: $`\mathcal{C}_g`$ inclui as $`\mathcal{C}^{\text{out}}`$ do período (com $`u`$ fixo por H4), de modo que o horário fixo do Cálculo bloqueia, de fato, os slots em que o IC pode pôr suas obrigatórias daquele período:

```math
\sum_{c\in\mathcal{C}_g} u_{c,h} \le 1 \qquad \forall g\in\mathcal{G},\ \forall h\in\mathcal{H}
```

**(H9) Recurso/laboratório.** Turma que exige laboratório vai para sala compatível (já embutido em $`\mathcal{R}_c`$; explicitando):

```math
z_{c,r}=0 \quad \text{se } \rho_c=1 \text{ e } \ell_r=0 \qquad \forall c,\ \forall r
```

**(H10) Capacidade da sala.** A sala alocada comporta o tamanho da turma:

```math
z_{c,r}=1 \;\Rightarrow\; n_c \le \text{cap}_r \qquad \forall c\in\mathcal{C},\ \forall r\in\mathcal{R}_c
```

(forma linear simples: fixar $`z_{c,r}=0`$ sempre que $`n_c > \text{cap}_r`$.)

**(H11) Jornada legal — descanso entre dias.** Para todo professor $`p`$ e par de dias consecutivos $`(d,d{+}1)`$: se $`p`$ leciona na última faixa de $`d`$, não pode lecionar na primeira faixa de $`d{+}1`$ quando o intervalo for menor que $`\text{desc}_{\min}`$. Em forma linear, para cada par de slots $`(h,h')`$ que viola o descanso:

```math
\sum_{c} x_{c,p}\,u_{c,h} + \sum_{c} x_{c,p}\,u_{c,h'} \le 1
\qquad \forall p,\ \forall (h,h')\in \text{ViolaDescanso}
```

**(H12) Carga mínima anual de obrigatórias.** Todo professor do IC ministra **ao menos 3** turmas obrigatórias do IC ao longo do ano (forma de mínimo confirmada pelo orientador). A soma percorre as turmas dos **dois semestres** — é, junto com O6, o que obriga o horizonte anual:

```math
\sum_{c\,\in\,\mathcal{C}^{\text{IC}}\cap\,\mathcal{C}^{\text{obr}}} x_{c,p}\ \ge\ 3
\qquad \forall p\in\mathcal{P}
```

**Viabilidade:** exige $`|\mathcal{C}^{\text{IC}}\cap\mathcal{C}^{\text{obr}}|\ge 3\,|\mathcal{P}|`$ no ano; caso contrário a instância é inviável. **Interação com O1/O6:** obrigar 3 obrigatórias por professor consome a folga usada para atender preferências (O1) e rodízio (O6) — tensão real entre departamento e professores, sem termo novo em $`Z`$ (por ser hard).

> **Nota:** H8, H10, H11 e H12 podem ser relaxadas para *soft* (penalização) caso tornem instâncias inviáveis — decisão a tomar com o orientador. A capacidade (H10), em particular, encarna o conflito chefia × coordenação × instituto (turma grande × vaga × sala); a carga anual (H12) encarna o conflito departamento × professor e é a candidata mais provável a precisar de folga, se a oferta de obrigatórias não comportar 3 por professor.

---

## 6. Função objetivo (critérios soft)

Minimizar a penalidade total ponderada (preferências entram como bônus, i.e., penalidade negativa). Com as duas grades, $`Z`$ se organiza em **termos compartilhados** — centrados em professor/sala, calculados uma única vez sobre todas as turmas (O1, O2, O3, O4, O6) — e **termos por currículo** — os que dependem dos períodos de cada grade (O5 e, se H8 for relaxada para soft, um choque de aluno $`\Phi^{k}_{\text{aluno}}`$):

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

**(O1) Preferência ponderada pela prioridade.** Professores mais prioritários (antigos) atendidos primeiro em suas disciplinas preferidas — atende a chefia/professor.

**(O2) Dias trabalhados — $`\Phi_{\text{dias}}`$.** Minimizar o nº de dias com aula por professor. Com auxiliar $`t_{p,d}\in\{0,1\}`$ (=1 se $`p`$ leciona no dia $`d`$):

```math
t_{p,d} \ge x_{c,p}\,u_{c,h}\quad \forall h\in d; \qquad \Phi_{\text{dias}}=\sum_{p}\sum_{d} t_{p,d}
```

**(O3) Janelas — $`\Phi_{\text{jan}}`$.** Minimizar buracos (slots vagos entre duas aulas no mesmo dia) por professor: para cada $`p,d`$, contar slots ociosos entre a primeira e a última aula do dia.

**(O4) Desperdício de capacidade — $`\Phi_{\text{cap}}`$.** Penalizar sala muito maior que a turma:

```math
\Phi_{\text{cap}}=\sum_{c}\sum_{r\in\mathcal{R}_c} z_{c,r}\,(\text{cap}_r - n_c)
```

**(O5) Distância percorrida pelos alunos — $`\Phi^{k}_{\text{dist}}`$** *(ideia original do trabalho)*. Para cada grupo curricular $`g`$ **da grade $`k`$** e cada par de slots **consecutivos** $`(h,h')`$ no mesmo dia em que $`g`$ tem aulas nas salas $`r`$ e $`r'`$, somar $`\delta_{r,r'}`$:

```math
\Phi^{k}_{\text{dist}}=\sum_{g\in\mathcal{G}^{k}}\ \sum_{(h,h')\,\text{consec.}}\ \sum_{c,c'\in\mathcal{C}_g}\ \sum_{r,r'} \delta_{r,r'}\;(z_{c,r}\,u_{c,h})\,(z_{c',r'}\,u_{c',h'})
```

(termo quadrático; no protótipo é avaliado diretamente sobre a solução, sem linearizar. É o único critério que depende da grade — por isso $`Z^{k}_{\text{curr}}`$ o carrega por currículo, permitindo medir e ponderar CC e SI separadamente.)

**(O6) Rodízio par/ímpar — $`\Phi_{\text{rod}}`$.** Penalizar manter o mesmo professor na mesma disciplina em semestres de paridade diferente (incentiva rodízio). Com o horizonte anual, a comparação é entre as atribuições dos **dois semestres do próprio ano** (ambas variáveis do modelo) e com a do ano anterior (parâmetro histórico) — junto com H12, é o critério que atravessa os semestres.

> **Pesos $`w_\bullet`$:** calibrar com o orientador. Sugestão de partida: normalizar cada termo para $`[0,1]`$ e atribuir pesos por importância declarada. O termo de distância (O5) é o diferencial do trabalho e merece um estudo de *ablação* (com/sem) nos experimentos. Os pesos por grade $`w^{\text{CC}}/w^{\text{SI}}`$ partem **iguais** (equidade) e podem ser ajustados a partir da assimetria observada em E1/E2 (Seção 9).

---

## 7. Mapa stakeholder → restrição/critério

| Stakeholder (orientação) | Onde aparece no modelo |
|---|---|
| Chefia de departamento (briga pelo professor, quer turma grande) | O1 (preferência/prioridade), H1, H10/O4 (tamanho×sala) |
| Coordenação (briga pelos alunos, quer vaga) | H8 (sem choque p/ aluno), H10 (vaga), O5 (deslocamento) |
| Instituto de Computação (salas) | H3, H7, H9, H10, O4 |
| Jornada legal do professor | H11, O2, O3 |
| Disciplinas-serviço do IC (horário prioritário, ex.: ED) | H4 (horário fixo), H5 |
| Disciplinas de outros departamentos (exógenas) | H4 (horário), H4b (professor), H8 (bloqueio do aluno) |
| Coordenações de CC e SI (disputam professores/salas/slots compartilhados) | $`\mathcal{G}^{k}`$ em H8, $`\Phi^{k}_{\text{dist}}`$ (O5), pesos $`w^{k}`$, experimentos E1–E3 (Seção 9) |
| Departamento — carga docente anual | H12 (mínimo de 3 obrigatórias/ano por professor) |

---

## 8. Decomposição em estágios (para o protótipo OptFrame)

Para caber no prazo e refletir o fluxo real, o protótipo resolve em estágios acoplados, mas com **um único avaliador** $`Z`$ enxergando a solução inteira:

1. **Fixar** o plano de fundo: professor+horário de $`\mathcal{C}^{\text{out}}`$ (H4b/H4) e horário das disciplinas-serviço $`\mathcal{C}^{\text{fix}}`$ (H4); aplicar os dias por setor (H5);
2. **Construtivo guloso**: atribuir professores ($`x`$) das turmas do IC priorizando O1; depois encaixar optativas do IC em $`\mathcal{Q}_c`$; depois salas ($`z`$) por melhor encaixe de capacidade/recurso;
3. **Busca local / metaheurística** (SA → ILS/VNS) sobre vizinhanças que mexem em $`x`$, $`y`$ e $`z`$ das turmas do IC, guiada por $`Z`$ e pelas penalidades das restrições hard relaxáveis.

**Representação da solução (OptFrame):** para cada turma $`c\in\mathcal{C}^{\text{IC}}`$, a tripla $`(\text{prof}_c,\ \text{pad}_c,\ \text{sala}_c)`$ — com $`\text{pad}_c`$ imutável se $`c\in\mathcal{C}^{\text{fix}}`$. As turmas de $`\mathcal{C}^{\text{out}}`$ ficam como **plano de fundo fixo** (professor + horário dados), só para checar H8.

**Vizinhanças (moves):**
- trocar professor entre duas turmas / realocar professor de uma turma;
- mover optativa para outro padrão admissível;
- trocar sala de uma turma / trocar salas entre duas turmas.

**Avaliador decomposto** por termo (O1–O6 + penalidades de H6–H12 relaxadas), para relatório por critério e para *delta-evaluation* eficiente dos moves.

> **Reuso nos experimentos por grade (Seção 9):** congelar uma grade como plano de fundo para otimizar a outra usa **o mesmo mecanismo** de plano de fundo fixo do estágio 1: as turmas da grade congelada entram como ocupação fixa de professor/sala/horário (via H6/H7), tal como $`\mathcal{C}^{\text{out}}`$/$`\mathcal{C}^{\text{fix}}`$. E o avaliador decomposto já entrega as métricas por grade ($`Z^{\text{CC}}`$ vs. $`Z^{\text{SI}}`$) sem trabalho extra.

---

## 9. Estudo experimental do acoplamento entre grades (E1–E3)

CC e SI disputam professores, salas e slots compartilhados — é a materialização do conflito entre stakeholders (duas coordenações sobre o mesmo departamento). Três experimentos comparam **ordens de otimização** das grades:

- **E1 (CC → SI):** otimiza considerando só $`\mathcal{G}^{\text{CC}}`$; congela as turmas de $`\mathcal{C}^{\text{CC}}`$ (compartilhadas **e** exclusivas de CC) como plano de fundo fixo; depois otimiza as turmas exclusivas de SI sujeitas a $`\mathcal{G}^{\text{SI}}`$ e ao plano de fundo já ocupado (professores/salas via H6/H7). Minimiza $`Z_{\text{compart}} + Z^{\text{CC}}_{\text{curr}}`$ na 1ª etapa e $`Z_{\text{compart}} + Z^{\text{SI}}_{\text{curr}}`$ na 2ª.
- **E2 (SI → CC):** simétrico a E1.
- **E3 (conjunto):** modelo único com $`\mathcal{G}^{\text{CC}}\cup\mathcal{G}^{\text{SI}}`$ ativos, minimizando $`Z = Z_{\text{compart}} + w^{\text{CC}}Z^{\text{CC}}_{\text{curr}} + w^{\text{SI}}Z^{\text{SI}}_{\text{curr}}`$ com **pesos iguais** (equidade); num **E3'**, pesos ajustados a partir da assimetria observada em E1/E2 (compensar o curso que sai pior quando vai por último).

**Métricas:** decompor $`Z`$ em $`Z^{\text{CC}}`$ e $`Z^{\text{SI}}`$ por critério; medir o **"custo de ir depois"** (assimetria E1 vs. E2); comparar E3 (otimização global) contra os sequenciais (lexicográfico-guloso) — a expectativa é que E3 equilibre melhor os dois cursos.

**Viabilidade:** custo marginal de implementação **baixo** — reusa (i) o mecanismo de plano de fundo fixo de $`\mathcal{C}^{\text{fix}}`$ (Seção 8) e (ii) a decomposição do avaliador por critério. **Ressalva:** com turmas compartilhadas, no sequencial as turmas de $`\mathcal{C}^{\text{CC}}\cap\mathcal{C}^{\text{SI}}`$ ficam 100% determinadas pela 1ª grade — o 2º curso só otimiza suas exclusivas; se a interseção for grande, o 2º estágio tem pouca liberdade. Isso é um **resultado a medir** (tamanho da interseção × assimetria), não um defeito do método.

---

## 10. Pendências para fechar o modelo

- [ ] Definir o conjunto exato de faixas $`\mathcal{B}`$ e padrões $`\mathcal{Q}`$ (grade de horários real da UFF, incluindo 11–13h e noite 18h). **Em andamento:** webscrap já extrai horário/vagas por turma; tabular a distribuição real dos padrões.
- [ ] Receber a planilha de setores → define $`\mathcal{S}`$, $`\mathcal{P}_c`$ e os dias de cada setor.
- [ ] Receber a **lista de obrigatórias × optativas** por período → define $`\mathcal{C}^{\text{obr}}/\mathcal{C}^{\text{opt}}`$ e compõe os grupos $`\mathcal{G}`$. (A divisão IC × outro departamento já sai automaticamente do prefixo do código: `TCC*` = IC.)
- [ ] Definir $`\mathcal{G}`$ (grupos curriculares por período, **para as duas grades**) a partir da grade de cada curso, **incluindo as disciplinas de outros departamentos** que cada período cursa → necessário para H8 e O5.
- [ ] Receber a **grade de SI por período** → define $`\mathcal{G}^{\text{SI}}`$ e $`\mathcal{C}^{\text{SI}}`$ — e mapear a **interseção CC∩SI** (quais turmas são compartilhadas; o tamanho dela condiciona os experimentos E1/E2 da Seção 9).
- [ ] Confirmar com o orientador se alguma disciplina de $`\mathcal{C}^{\text{out}}`$ ocorre em **sala do IC** (se sim, entra em H7 com sala fixa $`\bar r_c`$).
- [ ] Obter posições/distâncias das salas ($`\delta_{r,r'}`$) → necessário para O5.
- [ ] Decidir hard × soft de H8, H10, H11 e calibrar pesos $`w_\bullet`$ (incluindo $`w^{\text{CC}}/w^{\text{SI}}`$) com o orientador.
- [ ] Validar com o orientador a contingência de **H12** (mínimo ≥ 3, já confirmado): se a oferta de obrigatórias não comportar $`3\,|\mathcal{P}|`$ no ano, cabe folga/relaxação para soft?
