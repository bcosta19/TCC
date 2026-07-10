# Revisão do modelo matemático (esboço)

> Avaliação de `modelo_matematico_orientador.md` — julho/2026.

## Veredito

Serve bem como esboço de modelo, acima do esperado para um primeiro rascunho. A
estrutura (problema → decisões de modelagem → conjuntos/parâmetros/variáveis →
hard → objetivo → papéis → resolução → pontos em aberto) está completa e
coerente; a classificação das turmas por dois eixos + horário fixo é elegante; o
horizonte anual está bem justificado (H12/O6); a Seção 9 (E1–E3) já dá um
desenho experimental de verdade. Dá para levar ao orientador, depois de apertar
os pontos abaixo.

## Pontos a apertar (do mais substantivo ao cosmético)

### 1. Granularidade de $`\mathcal{B}`$ × O5 — conceitual, o mais importante
Hoje $`\mathcal{B}`$ tem só 3 faixas grossas (manhã/tarde/noite, linha 43), então
os únicos "slots consecutivos no mesmo dia" são manhã→tarde e tarde→noite. Mas O5
— a distância entre aulas consecutivas, diferencial do trabalho — só faz sentido
se "consecutivo" for aula-após-aula (ex.: 8–10h → 10–12h). Com faixas de
meio-turno, o critério que dá nome ao TCC perde o sentido físico ("andar menos").
Não é só "dado que falta" (ponto 10.3): é uma **decisão de modelagem** que precede
os dados, porque define se O5 é mensurável. Deixar explícito — refinar
$`\mathcal{B}`$ para blocos-hora, ou reformular O5 sobre a granularidade real da
grade.

### 2. Natureza não-linear × "isto é um ILP?"
O texto só sinaliza O5 como avaliado direto (linha 239), mas H6, H7, H11 e O2
também têm produtos bilineares ($`x_{c,p}\,u_{c,h}`$, $`z_{c,r}\,u_{c,h}`$). Um
leitor esperando ILP tropeça. Vale uma frase na Seção 6 dizendo que essas
restrições, como O5, são não-lineares nas variáveis-base e são avaliadas
diretamente pelo avaliador da metaheurística (não se lineariza). Detalhe fino: O5
chamado de "quadrático" (linha 239) é na verdade grau 4 nas binárias
($`z\cdot u\cdot z\cdot u`$) — quadrático só se pensar em "ocupação-sala-slot"
como quantidade derivada.

### 3. $`\bar r_c`$ usado mas não definido
H7 (linha 149) fala em "sala fixa $`\bar r_c`$" para turma de fora que use sala do
IC, mas $`\bar r_c`$ não está na tabela de parâmetros (Seção 4, só há $`\bar q_c`$
e $`\bar p_c`$). Mesmo caso do ponto em aberto 10.4: se a resposta for "sim,
ocorre", definir o parâmetro; se puder ficar de fora, tirar a menção de H7.

### 4. Optativas dentro dos grupos $`\mathcal{C}_g`$ (H8/O5)
$`\mathcal{G}`$ é "turmas que um aluno cursa em conjunto" (linha 48), mas um aluno
não cursa todas as optativas de um período. Se $`\mathcal{C}_g`$ incluir
optativas, H8 proíbe duas optativas do mesmo período no mesmo slot — restrição
forte demais — e O5 conta deslocamento de aulas que o aluno pode nem ter juntas.
Dizer explicitamente se grupos são só de obrigatórias (usual em curriculum-based)
e como a optativa entra. Candidato a item novo da Seção 10.

### 5. O3 (janelas) e O6 (rodízio) sem fórmula
Estão só em prosa (linhas 225 e 241), enquanto O2, O4, O5 têm equação. Aceitável
para esboço, mas marcar "a formalizar" — O6 em especial mistura duas variáveis do
ano + parâmetro histórico e merece a expressão escrita.

### 6. (cosmético) H4 é redundante
Redundante com H2 + $`\mathcal{Q}_c`$ unitário para $`c\in\mathcal{C}^{\text{fix}}`$.
Não é erro — a redundância ajuda a leitura —, mas dá para citar como "reforço
explícito de H2" se quiser enxugar.

## Prioridade

- **Antes de mostrar ao orientador:** 1, 3, 4.
- **Rigor/apresentação:** 2, 5.
- **Opcional:** 6.
