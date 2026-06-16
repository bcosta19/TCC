# Modelo matemático — alocação de horários e salas (IC/UFF)

> Rascunho da formalização (Fase 1 do `PLANO.md`). Notação em LaTeX para reaproveitar direto na monografia e no artigo. **Revisar com o orientador**, em especial: o que é restrição forte (hard) × fraca (soft), e os pesos $w_\bullet$ da função objetivo.

O problema é uma variante do **University Course Timetabling Problem (UCTP)**, na vertente *curriculum-based course timetabling* (referência: ITC-2007, track 3), acrescida de **alocação de salas com distância** e das regras específicas do IC/UFF (setores por dia, horários fixos por semestre par/ímpar, jornada legal do professor).

---

## 1. Decisão de modelagem

A unidade a ser programada é a **turma** (uma oferta de uma disciplina num semestre). Cada turma precisa de três decisões acopladas:

1. **qual professor** a ministra;
2. **em qual padrão de horário** (conjunto de encontros semanais);
3. **em qual sala**.

A estratégia do orientador reduz o espaço de busca fixando parte disso como **dado de entrada** (parâmetro), não como variável:

- **Disciplinas externas** (cursadas por outros cursos, ex.: Estruturas de Dados) têm **horário fixo** e prioridade máxima → o padrão de horário delas é parâmetro.
- **Setores** (algoritmos, redes, eng. de software, ...) fixam os **dias da semana** de cada turma → restringem o domínio da variável de horário.
- O regime **par/ímpar** define, para cada disciplina obrigatória, um padrão de horário previsto por paridade de semestre.

Apresento abaixo o **modelo completo** (todas as decisões como variáveis) e, na Seção 7, como a estratégia do orientador o particiona em estágios para o protótipo.

---

## 2. Conjuntos e índices

| Símbolo | Descrição |
|---|---|
| $\mathcal{C}$ | turmas a ofertar no semestre ($c$) |
| $\mathcal{P}$ | professores ($p$) |
| $\mathcal{R}$ | salas ($r$) |
| $\mathcal{D}$ | dias letivos da semana ($d$): seg…sáb |
| $\mathcal{B}$ | faixas horárias do dia ($b$): manhã (incl. 11–13h), tarde, noite (incl. 18h) |
| $\mathcal{H}=\mathcal{D}\times\mathcal{B}$ | *slots* de horário ($h$) |
| $\mathcal{Q}$ | padrões de horário ($q$): cada padrão é um conjunto de slots semanais, ex.: $\{\text{ter-}b,\ \text{qui-}b\}$ (2 encontros/semana) |
| $\mathcal{S}$ | setores/áreas do departamento ($s$): algoritmos, redes, eng. software, … |
| $\mathcal{G}$ | grupos curriculares ($g$): conjunto de turmas que um aluno de um período/ênfase cursa em conjunto |

Conjuntos derivados:
- $H_q \subseteq \mathcal{H}$: slots ocupados pelo padrão $q$; $\text{dias}(q)\subseteq\mathcal{D}$: dias do padrão $q$.
- $\mathcal{C}^{\text{obr}}, \mathcal{C}^{\text{opt}}, \mathcal{C}^{\text{ext}} \subseteq \mathcal{C}$: turmas obrigatórias, optativas e externas (partição).
- $\mathcal{P}_c \subseteq \mathcal{P}$: professores **habilitados** a ministrar a disciplina da turma $c$ (definidos pela planilha de setores/afinidade).
- $\mathcal{Q}_c \subseteq \mathcal{Q}$: padrões **admissíveis** para a turma $c$ (restritos pelos dias do setor de $c$; unitário/fixo se $c\in\mathcal{C}^{\text{ext}}$).
- $\mathcal{R}_c \subseteq \mathcal{R}$: salas compatíveis com os recursos exigidos por $c$.
- $\mathcal{C}_g \subseteq \mathcal{C}$: turmas do grupo curricular $g$.
- $s(c)\in\mathcal{S}$: setor da turma $c$.

---

## 3. Parâmetros

| Símbolo | Descrição |
|---|---|
| $n_c \in \mathbb{Z}_+$ | nº de vagas (tamanho) da turma $c$ |
| $\text{cap}_r \in \mathbb{Z}_+$ | capacidade da sala $r$ |
| $\rho_{c} \in \{0,1\}$ | turma $c$ exige laboratório/recurso especial |
| $\ell_r \in \{0,1\}$ | sala $r$ é laboratório (e quais recursos possui) |
| $\text{pref}_{p,c} \in [0,1]$ | preferência do professor $p$ pela disciplina de $c$ (proxy: frequência histórica no webscrap) |
| $\pi_p \in [0,1]$ | prioridade do professor $p$ (antiguidade/idade; maior = atendido primeiro) |
| $\delta_{r,r'} \ge 0$ | distância física entre as salas $r$ e $r'$ (matriz de distâncias) |
| $\bar{q}_c \in \mathcal{Q}$ | padrão de horário **previsto/fixo** de $c$ (par/ímpar; obrigatório se $c\in\mathcal{C}^{\text{ext}}$) |
| $\text{desc}_{\min}$ | descanso mínimo (em horas) entre o fim do trabalho de um dia e o início do dia seguinte |
| $w_\bullet \ge 0$ | pesos dos termos da função objetivo (a calibrar) |

---

## 4. Variáveis de decisão

$$
x_{c,p}=\begin{cases}1 & \text{turma } c \text{ é ministrada por } p\\0&\text{c.c.}\end{cases}
\qquad c\in\mathcal{C},\ p\in\mathcal{P}_c
$$

$$
y_{c,q}=\begin{cases}1 & \text{turma } c \text{ recebe o padrão de horário } q\\0&\text{c.c.}\end{cases}
\qquad c\in\mathcal{C},\ q\in\mathcal{Q}_c
$$

$$
z_{c,r}=\begin{cases}1 & \text{turma } c \text{ é alocada na sala } r\\0&\text{c.c.}\end{cases}
\qquad c\in\mathcal{C},\ r\in\mathcal{R}_c
$$

Variável auxiliar de **ocupação em slot** (derivada, facilita escrever conflitos):

$$
u_{c,h} = \sum_{q\in\mathcal{Q}_c \,:\, h\in H_q} y_{c,q} \in\{0,1\}\qquad (\text{1 se } c \text{ tem aula no slot } h)
$$

---

## 5. Restrições fortes (hard)

**(H1) Atribuição única de professor.** Toda turma tem exatamente um professor habilitado:

$$\sum_{p\in\mathcal{P}_c} x_{c,p} = 1 \qquad \forall c\in\mathcal{C}$$

**(H2) Atribuição única de horário.**

$$\sum_{q\in\mathcal{Q}_c} y_{c,q} = 1 \qquad \forall c\in\mathcal{C}$$

**(H3) Atribuição única de sala.**

$$\sum_{r\in\mathcal{R}_c} z_{c,r} = 1 \qquad \forall c\in\mathcal{C}$$

**(H4) Horário fixo das externas** (prioridade máxima):

$$y_{c,\bar{q}_c} = 1 \qquad \forall c\in\mathcal{C}^{\text{ext}}$$

**(H5) Setor fixa os dias.** Implícita no domínio: $\mathcal{Q}_c$ só contém padrões com $\text{dias}(q)$ iguais aos dias do setor $s(c)$ (exceção das externas, já tratada em H4).

**(H6) Sem conflito de professor.** Um professor não ministra duas turmas no mesmo slot:

$$\sum_{c\in\mathcal{C}} x_{c,p}\, u_{c,h} \le 1 \qquad \forall p\in\mathcal{P},\ \forall h\in\mathcal{H}$$

**(H7) Sem conflito de sala.** Uma sala não recebe duas turmas no mesmo slot:

$$\sum_{c\in\mathcal{C}} z_{c,r}\, u_{c,h} \le 1 \qquad \forall r\in\mathcal{R},\ \forall h\in\mathcal{H}$$

**(H8) Sem conflito de aluno.** Turmas do mesmo grupo curricular não coincidem em slot:

$$\sum_{c\in\mathcal{C}_g} u_{c,h} \le 1 \qquad \forall g\in\mathcal{G},\ \forall h\in\mathcal{H}$$

**(H9) Recurso/laboratório.** Turma que exige laboratório vai para sala compatível (já embutido em $\mathcal{R}_c$; explicitando):

$$z_{c,r}=0 \quad \text{se } \rho_c=1 \text{ e } \ell_r=0 \qquad \forall c,\ \forall r$$

**(H10) Capacidade da sala.**

$$\sum_{c\in\mathcal{C}} z_{c,r}\,u_{c,h}\cdot n_c \le \text{cap}_r \quad\text{para a turma ocupando } r \text{ em } h
\;\Longleftrightarrow\; z_{c,r}=1 \Rightarrow n_c \le \text{cap}_r$$
(forma linear simples: $z_{c,r}=0$ sempre que $n_c > \text{cap}_r$.)

**(H11) Jornada legal — descanso entre dias.** Para todo professor $p$ e par de dias consecutivos $(d,d{+}1)$: se $p$ leciona na última faixa de $d$, não pode lecionar na primeira faixa de $d{+}1$ quando o intervalo $< \text{desc}_{\min}$. Em forma linear, para cada par de slots $(h,h')$ que viola o descanso:

$$\sum_{c} x_{c,p}u_{c,h} + \sum_{c} x_{c,p}u_{c,h'} \le 1
\quad \forall p,\ \forall (h,h')\in \text{ViolaDescanso}$$

> **Nota:** H8, H10 e H11 podem ser relaxadas para *soft* (penalização) caso tornem instâncias inviáveis — decisão a tomar com o orientador. A capacidade (H10), em particular, encarna o conflito chefia × coordenação × instituto (turma grande × vaga × sala).

---

## 6. Função objetivo (critérios soft)

Minimizar a penalidade total ponderada (preferências entram como bônus, i.e., penalidade negativa):

$$
\min\ Z = \underbrace{-\,w_{\text{pref}}\!\!\sum_{c}\sum_{p\in\mathcal{P}_c}\pi_p\,\text{pref}_{p,c}\,x_{c,p}}_{\text{(O1) preferência×prioridade}}
\;+\; w_{\text{dias}}\,\Phi_{\text{dias}}
\;+\; w_{\text{jan}}\,\Phi_{\text{janelas}}
\;+\; w_{\text{cap}}\,\Phi_{\text{desperdício}}
\;+\; w_{\text{dist}}\,\Phi_{\text{distância}}
\;+\; w_{\text{rod}}\,\Phi_{\text{rodízio}}
$$

**(O1) Preferência ponderada pela prioridade.** Professores mais prioritários (antigos) atendidos primeiro em suas disciplinas preferidas — atende a chefia/professor.

**(O2) Dias trabalhados — $\Phi_{\text{dias}}$.** Minimizar o nº de dias com aula por professor. Com auxiliar $t_{p,d}\in\{0,1\}$ (=1 se $p$ leciona no dia $d$):

$$t_{p,d} \ge x_{c,p}\,u_{c,h}\quad \forall h\in d;\qquad \Phi_{\text{dias}}=\sum_{p}\sum_{d} t_{p,d}$$

**(O3) Janelas — $\Phi_{\text{janelas}}$.** Minimizar buracos (slots vagos entre duas aulas no mesmo dia) por professor: para cada $p,d$, contar slots ociosos entre a primeira e a última aula do dia.

**(O4) Desperdício de capacidade — $\Phi_{\text{desperdício}}$.** Penalizar sala muito maior que a turma:

$$\Phi_{\text{desperdício}}=\sum_{c}\sum_{r\in\mathcal{R}_c} z_{c,r}\,(\text{cap}_r - n_c)$$

**(O5) Distância percorrida pelos alunos — $\Phi_{\text{distância}}$** *(ideia original do trabalho)*. Para cada grupo curricular $g$ e cada par de slots **consecutivos** $(h,h')$ no mesmo dia em que $g$ tem aulas nas salas $r$ e $r'$, somar $\delta_{r,r'}$:

$$\Phi_{\text{distância}}=\sum_{g}\sum_{(h,h')\,\text{consec.}}\;\sum_{c,c'\in\mathcal{C}_g}\sum_{r,r'} \delta_{r,r'}\;(z_{c,r}u_{c,h})(z_{c',r'}u_{c',h'})$$
(termo quadrático; no protótipo é avaliado diretamente sobre a solução, sem linearizar.)

**(O6) Rodízio par/ímpar — $\Phi_{\text{rodízio}}$.** Penalizar manter o mesmo professor na mesma disciplina em semestres de paridade diferente (incentiva rodízio), comparando com a atribuição do semestre anterior (parâmetro histórico).

> **Pesos $w_\bullet$:** calibrar com o orientador. Sugestão de partida: normalizar cada termo para $[0,1]$ e atribuir pesos por importância declarada. O termo de distância (O5) é o diferencial do trabalho e merece um estudo de *ablação* (com/sem) nos experimentos.

---

## 7. Mapa stakeholder → restrição/critério

| Stakeholder (orientação) | Onde aparece no modelo |
|---|---|
| Chefia de departamento (briga pelo professor, quer turma grande) | O1 (preferência/prioridade), H1, H10/O4 (tamanho×sala) |
| Coordenação (briga pelos alunos, quer vaga) | H8 (sem choque p/ aluno), H10 (vaga), O5 (deslocamento) |
| Instituto de Computação (salas) | H3, H7, H9, H10, O4 |
| Jornada legal do professor | H11, O2, O3 |
| Prioridade máxima das externas | H4, H5 (exceção dos dias) |

---

## 8. Decomposição em estágios (para o protótipo OptFrame)

Para caber no prazo e refletir o fluxo real, o protótipo resolve em estágios acoplados, mas com **um único avaliador** $Z$ enxergando a solução inteira:

1. **Fixar** externas (H4) e os dias por setor (H5);
2. **Construtivo guloso**: atribuir professores ($x$) priorizando O1; depois encaixar optativas em $\mathcal{Q}_c$; depois salas ($z$) por melhor encaixe de capacidade/recurso;
3. **Busca local / metaheurística** (SA → ILS/VNS) sobre vizinhanças que mexem em $x$, $y$ e $z$, guiada por $Z$ e pelas penalidades das restrições hard relaxáveis.

**Representação da solução (OptFrame):** para cada turma $c$, a tripla $(\text{prof}_c,\ \text{pad}_c,\ \text{sala}_c)$; turmas externas têm $\text{pad}_c$ imutável.

**Vizinhanças (moves):**
- trocar professor entre duas turmas / realocar professor de uma turma;
- mover optativa para outro padrão admissível;
- trocar sala de uma turma / trocar salas entre duas turmas.

**Avaliador decomposto** por termo (O1–O6 + penalidades de H6–H11 relaxadas), para relatório por critério e para *delta-evaluation* eficiente dos moves.

---

## 9. Pendências para fechar o modelo

- [ ] Definir o conjunto exato de faixas $\mathcal{B}$ e padrões $\mathcal{Q}$ (grade de horários real da UFF, incluindo 11–13h e noite 18h).
- [ ] Receber a planilha de setores → define $\mathcal{S}$, $\mathcal{P}_c$ e os dias de cada setor.
- [ ] Definir $\mathcal{G}$ (grupos curriculares por período) a partir da grade do curso → necessário para H8 e O5.
- [ ] Obter posições/distâncias das salas ($\delta_{r,r'}$) → necessário para O5.
- [ ] Decidir hard × soft de H8, H10, H11 e calibrar pesos $w_\bullet$ com o orientador.
