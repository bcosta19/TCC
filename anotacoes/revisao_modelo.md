# Comentários sobre o modelo matemático (rascunho meu)

> Auto-revisão de `modelo_matematico_orientador.md` — julho/2026, antes de
> mostrar para o orientador. Está em ordem do que mais me incomoda para o que é
> puramente cosmético.

## Visão geral

O esboço está bom para um primeiro rascunho — melhor do que eu esperava. A
estrutura segue e os pontos duros estão lá. Mas tem quatro coisas que eu
gostaria de apertar antes de levar, e mais um par que dá para deixar para a
revisão final.

## O que tenho que decidir agora

### 1. Granularidade dos horários × O5 (esse é o principal)

O conjunto `B` está com três faixas: manhã, tarde e noite. Isso quer dizer que
"slots consecutivos no mesmo dia" só acontecem entre manhã→tarde e
tarde→noite. O O5 — a distância entre aulas consecutivas, que é a ideia
original do TCC — só faz sentido físico se "consecutivo" for aula-após-aula
(8h→10h, 10h→12h, etc.). Com a granularidade grossa, o critério perde a
interpretação de "aluno anda menos" e vira só um número abstrato. Isso não é
um problema de dado que falta: é uma decisão de modelagem que vem antes dos
dados. Tenho que refinar `B` para blocos-hora, ou reformular o O5 sobre a
grade real.

### 2. `r_c` solto

H7 cita "sala fixa `r̄_c`" para turma de fora que use sala do IC, mas eu não
pus `r̄_c` na tabela de parâmetros (Seção 4 só tem `q̄_c` e `p̄_c`). Se isso
realmente acontece na prática, preciso definir o parâmetro; se não acontece,
tiro a menção.

### 3. Optativas nos grupos `C_g`

Hoje o texto diz que `G` é o conjunto de turmas que o aluno cursa em conjunto,
mas o aluno não cursa todas as optativas do período junto. Se eu deixar
optativas dentro de `C_g`, o H8 proíbe duas optativas do mesmo período no
mesmo slot (forte demais) e o O5 conta deslocamento entre aulas que o aluno
pode nem fazer. Acho que tenho que ser explícito: grupos são só de
obrigatórias, e a optativa entra por outro mecanismo.

### 4. Linearidade

O texto sinaliza O5 como avaliado direto, mas H6, H7, H11 e O2 também têm
produtos bilineares. Quem ler esperando ILP vai tropeçar. Vale uma frase
deixando claro que essas restrições são não-lineares e que o avaliador da
metaheurística trata elas diretamente — não lineariza.

## O que dá para adiar

- O3 (janelas) e O6 (rodízio) estão só em prosa enquanto O1/O2/O4/O5 têm
  fórmula. Aceito para esboço, mas seria bom escrever O6 pelo menos, porque
  ele cruza as duas paridades e merece a expressão.
- H4 é redundante com H2 + `Q_c` unitário para `c ∈ C^fix`. Não é erro, mas
  posso citar como "reforço de H2" se quiser enxugar no futuro.

## O que vou mostrar para o orientador

1, 2 e 3. Os outros ficam para depois.
