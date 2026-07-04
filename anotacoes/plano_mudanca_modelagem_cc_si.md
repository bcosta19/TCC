# Plano: incorporar carga anual de obrigatórias e as duas grades (CC/SI) à modelagem

> Plano de ação gerado em 23/06/2026, decorrente de duas diretrizes novas do
> orientador. **Aplicado em 04/07/2026** (Mudanças 1–5 executadas nos quatro
> documentos; H12 confirmada como **mínimo ≥ 3**, não "exatamente 3"). Mantido como
> registro do racional das mudanças.

## Contexto

O orientador passou duas diretrizes novas que mudam o escopo do modelo formalizado em
`anotacoes/modelo_matematico.md`:

1. **Obrigação de carga anual** — todo professor do IC tem a obrigação de ministrar
   **3 disciplinas obrigatórias por ano**. Isso acopla os dois semestres (ímpar + par)
   num horizonte anual, que antes o modelo tratava como instâncias independentes por
   semestre.
2. **Duas grades curriculares** — as disciplinas de computação compõem **dois
   currículos**: Ciência da Computação (CC) e Sistemas de Informação (SI). Ambos são do
   **mesmo departamento** e seguem **as mesmas regras** (professores, setores, salas,
   horários fixos, par/ímpar). A única diferença é a grade: em qual período cada
   disciplina é cursada. Uma disciplina presente nas duas grades é **uma única turma
   compartilhada** (mesmo professor/sala/horário), cursada por alunos dos dois cursos.

Decisões já tomadas (a confirmar com o orientador no texto):
- Disciplina nas duas grades = **turma compartilhada** (1 oferta).
- A regra "3 obrigatórias/ano" entra como **restrição forte, mínimo ≥ 3**.

Além das mudanças de modelagem, avaliar a **viabilidade de 3 experimentos** comparando
ordens de otimização das duas grades (seção própria abaixo).

Núcleo do entregável = docs (`anotacoes/` e `PLANO.md`); tarefas de dados ficam
anotadas como desdobramento da Fase 2.

---

## Mudança 1 — `anotacoes/modelo_matematico.md` (principal)

### 1a. Horizonte anual (diretriz 1)
- Na Seção 1, declarar que a **unidade de planejamento passa a ser o ano letivo**
  (semestres ímpar e par juntos), porque a carga de obrigatórias e o rodízio (O6)
  acoplam os dois semestres.
- Na Seção 2, adicionar o atributo de **paridade de semestre** por turma:
  $\sigma(c)\in\{\text{ímpar},\text{par}\}$. O conjunto $\mathcal{C}$ passa a conter as
  turmas dos dois semestres do ano.

### 1b. Conjunto de currículos e grupos por grade (diretriz 2)
- Novo conjunto na tabela da Seção 2: $\mathcal{K}=\{\text{CC},\text{SI}\}$ (grades).
- Os grupos curriculares passam a ser indexados por grade:
  $\mathcal{G}=\mathcal{G}^{\text{CC}}\cup\mathcal{G}^{\text{SI}}$, cada $g$ com currículo
  $k(g)\in\mathcal{K}$. Uma **turma compartilhada** aparece em grupos das duas grades
  (ex.: período 3 de CC e período 5 de SI). **A forma de H8 e O5 não muda** — elas já
  somam sobre todo $g\in\mathcal{G}$; o que muda é que $\mathcal{G}$ agora contém os
  grupos das duas grades.
- Novo conjunto derivado: $\mathcal{C}^{k}\subseteq\mathcal{C}$ = turmas que aparecem na
  grade $k$ (compartilhadas pertencem a $\mathcal{C}^{\text{CC}}\cap\mathcal{C}^{\text{SI}}$).
  Usado para congelar plano de fundo nos experimentos sequenciais. Observar que
  professores ($\mathcal{P}$), setores ($\mathcal{S}$) e salas ($\mathcal{R}$) são
  **únicos e compartilhados** entre as grades (mesmo departamento) — não se duplicam.

### 1c. Nova restrição forte H12 (diretriz 1)
Na Seção 5, acrescentar:

> **(H12) Carga mínima anual de obrigatórias.** Todo professor do IC ministra ao menos
> 3 turmas obrigatórias do IC ao longo do ano:
> ```math
> \sum_{c\,\in\,\mathcal{C}^{\text{IC}}\cap\,\mathcal{C}^{\text{obr}}} x_{c,p}\ \ge\ 3
> \qquad \forall p\in\mathcal{P}
> ```
> (soma sobre os dois semestres do ano.)

- Anotar a **condição de viabilidade**:
  $|\mathcal{C}^{\text{IC}}\cap\mathcal{C}^{\text{obr}}|\ge 3\,|\mathcal{P}|$ (contando o
  ano inteiro), senão a instância é inviável — adicionar à nota de H8/H10/H11 que,
  apesar de escolhida hard, H12 pode precisar de **folga/relaxação** se a oferta não
  comportar; decisão a validar com o orientador.
- Registrar a **interação com O1**: forçar 3 obrigatórias/professor reduz a folga para
  atender preferências (O1) e para o rodízio (O6) — tensão real, sem termo novo na
  função objetivo (por ser hard).

### 1d. Decomposição da função objetivo por grade (Seção 6)
Reorganizar $Z$ em **termos compartilhados** + **termos por currículo**:
- **Compartilhados** (centrados em professor/sala, calculados uma vez sobre todas as
  turmas): O1 (pref×prioridade), O2 (dias), O3 (janelas), O4 (capacidade), O6 (rodízio).
- **Por currículo** (dependem dos períodos da grade): O5 distância vira
  $\Phi_{\text{dist}}^{k}$; se H8 for relaxada para soft, o choque de aluno também vira
  $\Phi_{\text{aluno}}^{k}$.

Forma combinada (usada no experimento conjunto):
```math
Z \;=\; Z_{\text{compart}} \;+\; \sum_{k\in\mathcal{K}} w^{k}\,Z^{k}_{\text{curr}}
```
com pesos por grade $w^{\text{CC}},w^{\text{SI}}$ (iguais = equidade; ajustados =
compensar a grade prejudicada). Adicionar $w^{\text{CC}},w^{\text{SI}}$ à tabela de
parâmetros (Seção 3) e à nota de calibração de pesos.

### 1e. Atualizações de coerência
- Seção 7 (mapa stakeholder→modelo): acrescentar linha "Coordenações de CC e SI
  disputando recursos compartilhados → H8/O5 por grade, pesos $w^{k}$" e "Departamento
  exige carga docente → H12".
- Seção 8 (decomposição em estágios): observar que congelar uma grade como plano de
  fundo para a outra **reusa o mesmo mecanismo** de $\mathcal{C}^{\text{fix}}$.
- Seção 9 (pendências): incluir (i) receber a **grade de SI por período**
  ($\mathcal{G}^{\text{SI}}$), (ii) mapear a **interseção CC∩SI** (quais turmas são
  compartilhadas), (iii) confirmar com o orientador se H12 é mínimo ≥3 ou exatamente =3
  e a folga de viabilidade.

---

## Mudança 2 — Seção "Estudo experimental das grades" (no `modelo_matematico.md` ou em `PLANO.md`, Fase 4)

Documentar os **3 experimentos** como o estudo do acoplamento entre currículos —
operacionaliza diretamente o tema dos stakeholders (duas coordenações disputando
professores/salas/slots compartilhados):

- **E1 (CC → SI):** otimiza considerando só $\mathcal{G}^{\text{CC}}$; congela as turmas
  de $\mathcal{C}^{\text{CC}}$ (compartilhadas **e** exclusivas de CC) como plano de
  fundo fixo; depois otimiza as turmas exclusivas de SI sujeitas a
  $\mathcal{G}^{\text{SI}}$ e ao plano de fundo já ocupado (professores/salas via
  H6/H7). Minimiza $Z_{\text{compart}} + Z^{\text{CC}}_{\text{curr}}$ na 1ª etapa e
  $Z_{\text{compart}} + Z^{\text{SI}}_{\text{curr}}$ na 2ª.
- **E2 (SI → CC):** simétrico.
- **E3 (conjunto):** modelo único com $\mathcal{G}^{\text{CC}}\cup\mathcal{G}^{\text{SI}}$
  ativos, minimizando $Z = Z_{\text{compart}} + w^{\text{CC}}Z^{\text{CC}}_{\text{curr}}
  + w^{\text{SI}}Z^{\text{SI}}_{\text{curr}}$. Rodar com **pesos iguais** (equidade) e,
  num E3', com **pesos ajustados** a partir da assimetria observada em E1/E2 (compensar
  o curso que sai pior quando vai por último).

**Métricas:** decompor $Z$ em $Z^{\text{CC}}$ e $Z^{\text{SI}}$ por critério; medir o
"custo de ir depois" (assimetria E1 vs E2); comparar E3 (pesos iguais) contra os
sequenciais (E3 deve equilibrar melhor por ser global vs. lexicográfico-guloso).

**Veredito de viabilidade (registrar no texto):** viável e coerente; **custo marginal de
implementação baixo**, pois reutiliza (i) o mecanismo de plano de fundo fixo de
$\mathcal{C}^{\text{fix}}$ e (ii) a decomposição do avaliador por critério.
**Ressalva a reportar:** com turma compartilhada, no sequencial as turmas da interseção
ficam 100% determinadas pela 1ª grade — o 2º curso só otimiza suas exclusivas; se CC∩SI
for grande, o 2º estágio tem pouca liberdade. **Isso é um resultado a medir (tamanho da
interseção × assimetria), não um defeito do método.**

---

## Mudança 3 — `anotacoes/orientacao.md`

Registrar as duas diretrizes novas: (a) carga de 3 obrigatórias/ano por professor;
(b) duas grades CC/SI, mesmo departamento e mesmas regras, separação só da grade, com
disciplinas compartilhadas. Atualizar a nota de "Estado atual" e o item 8 (critérios de
qualidade do professor) com a carga anual.

## Mudança 4 — `PLANO.md`

- "Visão do problema": registrar horizonte **anual** e as **duas grades**.
- Fase 2 (dados): tarefa de **coletar a grade de SI** e mapear interseção CC∩SI; formato
  de instância passa a carregar paridade $\sigma(c)$ e pertinência por grade.
- Fase 4 (experimentos): incluir E1/E2/E3 como bloco experimental das grades, ao lado da
  ablação do critério de distância.
- Riscos: H12 pode inviabilizar instância (oferta insuficiente) → prever folga/soft de
  contingência.

## Mudança 5 — Dados (`dados/PENDENCIAS.md` + nota no webscrap)

- Adicionar ao checklist: **grade curricular de SI por período**; **idcurso/idcurriculo
  de SI** em Niterói; **mapa de disciplinas compartilhadas** CC∩SI.
- Anotar que `webscrap/scraper.py` hoje fixa `idcurso=31` e `idcurriculo=3092` (CC); para
  coletar SI será preciso **parametrizar o curso/currículo** (tarefa de execução da Fase
  2, fora do escopo desta edição de modelagem).

---

## Arquivos a editar

- `anotacoes/modelo_matematico.md` — núcleo (Seções 1, 2, 3, 5, 6, 7, 8, 9 + seção de
  experimentos).
- `PLANO.md` — visão, Fase 2, Fase 4, riscos.
- `anotacoes/orientacao.md` — registrar diretrizes novas.
- `dados/PENDENCIAS.md` — itens de dados de SI e interseção.
- (Desdobramento Fase 2, não nesta edição) `webscrap/scraper.py` — parametrizar curso.

## Verificação

Como a mudança é documental, validar por **consistência**, não por execução:
1. Toda nova notação ($\mathcal{K}$, $\mathcal{G}^{k}$, $\mathcal{C}^{k}$, $\sigma(c)$,
   $w^{k}$, H12) aparece nas tabelas de conjuntos/parâmetros antes de ser usada.
2. Coerência cruzada entre `modelo_matematico.md`, `PLANO.md` e `orientacao.md`
   (horizonte anual e duas grades descritos de forma compatível).
3. Conferência da definição de variável/fixo por etapa em E1/E2/E3 (nenhuma turma fica
   sem etapa que a aloque; plano de fundo cresce de forma consistente).
4. Renderização das fórmulas no GitHub (o repo já teve ajuste para isso — commit
   `a6aab9a`): revisar blocos ```math``` novos.
5. Revisar com o orientador os pontos em aberto: H12 mínimo vs. exato e folga de
   viabilidade; pesos $w^{\text{CC}}/w^{\text{SI}}$; existência e tamanho da interseção
   CC∩SI.
