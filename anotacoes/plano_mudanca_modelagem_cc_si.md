# Anotações sobre a carga anual e as duas grades (rascunho)

> Rascunho de trabalho de 23/06/2026, com as duas diretrizes novas do
> orientador. Aplicado em 04/07/2026 — as mudanças 1–5 foram feitas nos quatro
> documentos. H12 ficou como mínimo ≥ 3 (não exatamente 3). Mantenho aqui só
> para lembrar o porquê. **Registro histórico:** as referências ao antigo O5
> e à ablação de distância foram superadas pela decisão de 10/08/2026 de
> retirar esse critério do escopo. A numeração O1–O6 abaixo é a numeração
> histórica anterior à remoção; no modelo atual o rodízio passou a ser O5.

## Contexto

O orientador passou duas coisas que mexem no modelo que está em
`anotacoes/modelo_matematico.md`:

1. **Carga anual** — todo professor do IC precisa ministrar pelo menos 3
   obrigatórias por ano. Isso acopla ímpar e par, e o modelo que eu tinha
   tratava cada semestre sozinho.
2. **Duas grades (CC e SI)** — as disciplinas de computação viram dois
   currículos. Mesmo departamento, mesmas regras, salas e professores
   compartilhados. A única diferença é em qual período cada disciplina cai.
   Disciplina nas duas grades é uma turma só (mesmo professor, sala, horário),
   cursada por alunos dos dois cursos.

Decisões que tomei e vou validar com o orientador:
- Disciplina nas duas grades = turma compartilhada (uma oferta só).
- "3 obrigatórias por ano" entra como mínimo, hard.

E ainda quero avaliar se vale a pena rodar 3 experimentos comparando ordens
de otimização das duas grades (seção mais abaixo).

Núcleo do entregável = os quatro documentos (`anotacoes/` e `PLANO.md`); as
tarefas de dados ficam listadas como desdobramento da Fase 2.

---

## Mudança 1 — `modelo_matematico.md` (a principal)

### 1a. Horizonte anual

- Seção 1: declarar que a unidade de planejamento agora é o ano (ímpar + par
  juntos), porque a carga anual e o rodízio atravessam os semestres.
- Seção 2: adicionar a paridade `σ(c) ∈ {ímpar, par}` por turma. O conjunto
  `C` passa a ter as turmas dos dois semestres.

### 1b. Currículos e grupos por grade

- Novo conjunto: `K = {CC, SI}`.
- Os grupos ficam indexados por grade: `G = G^CC ∪ G^SI`, com `k(g) ∈ K`.
  Turma compartilhada aparece nos grupos das duas grades. H8 e O5 não mudam
  de forma — continuam somando sobre todo `g`; só `G` que cresce.
- Novo conjunto derivado: `C^k ⊆ C` = turmas na grade `k` (compartilhadas
  ficam em `C^CC ∩ C^SI`). Uso isso para congelar uma grade como plano de
  fundo nos experimentos.

### 1c. H12 (carga mínima anual)

Acrescentar em H:

> H12: todo professor do IC ministra ao menos 3 turmas obrigatórias do IC no
> ano. Soma sobre os dois semestres.
> ```math
> Σ_{c ∈ C^IC ∩ C^obr} x_{c,p} ≥ 3   ∀ p ∈ P
> ```

- Anotar a viabilidade: precisa `|C^IC ∩ C^obr| ≥ 3 |P|` no ano. Se a oferta
  não comportar, H12 pode precisar de folga — verificar com o orientador.
- Registrar que H12 come a folga de O1 (preferência) e O6 (rodízio). É uma
  tensão real, sem termo novo em `Z` (já que é hard).

### 1d. Objetivo por grade

Reorganizar `Z` em **termos compartilhados** + **termos por currículo**:

- Compartilhados: O1, O2, O3, O4, O6.
- Por currículo: O5 vira `Φ^k_dist`; se H8 virar soft, mais um `Φ^k_aluno`.

Forma combinada:

```math
Z = Z_compart + Σ_{k ∈ K} w^k Z^k_curr
```

Com `w^CC = w^SI = 1` por padrão. Adicionar `w^CC, w^SI` à tabela de
parâmetros.

### 1e. Coerência

- Seção 7 (stakeholders): linha para coordenações CC/SI disputando recursos
  compartilhados; linha para carga docente → H12.
- Seção 8 (estágios): notar que congelar uma grade reusa o mecanismo de
  `C^fix`.
- Seção 9 (pendências): receber grade de SI, mapear interseção CC∩SI,
  confirmar H12 mínimo vs. exato e a folga.

---

## Mudança 2 — Experimentos E1–E3 (no `modelo_matematico.md` ou no `PLANO.md`)

Três experimentos comparando ordens de otimização das duas grades. É a
materialização do conflito entre stakeholders:

- **E1 (CC → SI)**: otimiza só `G^CC`, congela turmas de `C^CC` (compartilhadas
  e exclusivas) como plano de fundo; depois otimiza as exclusivas de SI
  sujeitas a `G^SI` e ao plano de fundo (H6/H7).
- **E2 (SI → CC)**: simétrico.
- **E3 (conjunto)**: modelo único com `G^CC ∪ G^SI` ativos. Rodar com pesos
  iguais (E3) e com pesos ajustados pela assimetria observada em E1/E2 (E3').

Métricas: decompor `Z` em `Z^CC` e `Z^SI` por critério; medir o "custo de ir
depois" (assimetria E1 vs. E2); comparar E3 com os sequenciais.

Viabilidade: custo de implementação é baixo — reuso do plano de fundo fixo
de `C^fix` e da decomposição por critério do avaliador. A ressalva é que, com
turmas compartilhadas, no sequencial as turmas de `C^CC ∩ C^SI` ficam
travadas pela 1ª grade — o 2º curso só otimiza as exclusivas. Se a
interseção for grande, o 2º estágio tem pouca folga. Isso é um **resultado
a medir** (tamanho da interseção × assimetria), não um defeito do método.

---

## Mudança 3 — `orientacao.md`

Registrar as duas diretrizes novas e atualizar o estado atual.

## Mudança 4 — `PLANO.md`

- Visão: registrar horizonte anual e duas grades.
- Fase 2: tarefa de coletar a grade de SI e mapear interseção; formato de
  instância passa a carregar `σ(c)` e pertinência por grade.
- Fase 4: E1/E2/E3 sem ablação de distância, pois esse critério saiu do escopo em 10/08/2026.
- Riscos: H12 pode inviabilizar a instância → prever folga/soft de
  contingência.

## Mudança 5 — `dados/PENDENCIAS.md`

Adicionar: grade de SI por período, idcurso/idcurrículo de SI, mapa CC∩SI.
E anotar que `scraper.py` hoje fixa curso 31 / currículo 3092 (CC) — para
coletar SI vai precisar parametrizar (tarefa da Fase 2, fora desta edição).

---

## O que vou editar

- `modelo_matematico.md` — Seções 1, 2, 3, 5, 6, 7, 8, 9 + seção de
  experimentos.
- `PLANO.md` — visão, Fase 2, Fase 4, riscos.
- `orientacao.md` — diretrizes novas.
- `PENDENCIAS.md` — SI e interseção.

## Como vou validar

Como é mudança de documento, valido por consistência, não por execução:

1. Toda notação nova (`K`, `G^k`, `C^k`, `σ(c)`, `w^k`, H12) aparece nas
   tabelas antes de ser usada.
2. Coerência cruzada entre os três documentos.
3. Nenhuma turma fica sem etapa que a aloque em E1/E2/E3.
4. Fórmulas renderizam no GitHub (o repo já teve ajuste para isso).
5. Rever com o orientador: H12 mínimo vs. exato, pesos `w^CC/w^SI`, tamanho
   da interseção CC∩SI.
