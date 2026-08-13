# Comentários sobre o modelo matemático (rascunho meu)

> Registro histórico da auto-revisão de julho/2026. O item sobre distância foi
> encerrado pela decisão de 10/08/2026 de retirar esse critério do escopo; os
> demais itens continuam sujeitos à revisão do aluno e do orientador.

## Visão geral

O esboço está bom para um primeiro rascunho — melhor do que eu esperava. A
estrutura segue e os pontos duros estão lá. Mas tem quatro coisas que eu
gostaria de apertar antes de levar, e mais um par que dá para deixar para a
revisão final.

## O que tenho que decidir agora

### 1. Granularidade dos horários × antigo O5 — encerrado

O problema de granularidade associado ao deslocamento deixou de existir com a
retirada do critério. A definição de `B` ainda precisa representar corretamente
conflitos, janelas e descanso, mas não precisa mais sustentar aulas consecutivas
para calcular deslocamento.

### 2. `r_c` solto

H7 cita "sala fixa `r̄_c`" para turma de fora que use sala do IC, mas eu não
pus `r̄_c` na tabela de parâmetros (Seção 4 só tem `q̄_c` e `p̄_c`). Se isso
realmente acontece na prática, preciso definir o parâmetro; se não acontece,
tiro a menção.

### 3. Optativas nos grupos `C_g`

Hoje o texto diz que `G` é o conjunto de turmas que o aluno cursa em conjunto,
mas o aluno não cursa todas as optativas do período junto. Se eu deixar
optativas dentro de `C_g`, o H8 proíbe duas optativas do mesmo período no
mesmo slot (forte demais). Acho que tenho que ser explícito: grupos são só de
obrigatórias, e a optativa entra por outro mecanismo.

### 4. Linearidade

H6, H7, H11 e O2 têm produtos bilineares. Quem ler esperando ILP vai
tropeçar. Vale uma frase
deixando claro que essas restrições são não-lineares e que o avaliador da
metaheurística trata elas diretamente — não lineariza.

## O que dá para adiar

- O3 (janelas) e O5 (rodízio, após a renumeração) estão só em prosa enquanto
  O1/O2/O4 têm fórmula. Aceito para esboço, mas seria bom escrever O5 pelo menos, porque
  ele cruza as duas paridades e merece a expressão.
- H4 é redundante com H2 + `Q_c` unitário para `c ∈ C^fix`. Não é erro, mas
  posso citar como "reforço de H2" se quiser enxugar no futuro.

## O que vou mostrar para o orientador

1, 2 e 3. Os outros ficam para depois.
