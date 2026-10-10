# Protocolo experimental da instância oficial de 2026 — 10/10/2026

Decidido pelo aluno em 10/10/2026, a partir da análise da calibração do SA.
Configuração: `dados/config_oficial_2026.json`. Execução:
`scripts/run_official_experiments_2026.py`.

## Problema encontrado no SA de v1–v3

A energia do SA de referência é escalar e lexicográfica:
`hard × 10⁹ + déficit H12 × 10⁶ + excesso H10 × 10³ + soft`. Com os parâmetros
do v3 (T₀ = 10⁶, resfriamento 0,997 por avaliação, 1500 avaliações), a
temperatura vai de 10⁶ a cerca de 1,1 × 10⁴. Medindo 400 movimentos aleatórios
na instância oficial, a probabilidade de aceitar uma piora mediana fica:

| Nível | Piora mediana | Aceitação no início | No fim |
|---|---|---|---|
| Soft (normalizado) | 0,011 | 100% | 100% |
| Excesso H10 | 10 alunos | 99% | 40% |
| Déficit H12 | 1 turma | 37% | 0% |
| Hard | 2 violações | 0% | 0% |

No nível soft, o SA era um passeio aleatório: toda piora era aceita, e a
melhora vinha só de guardar a melhor solução vista. Isso já valia para v1–v3,
porque na escala bruta as pioras soft (1 a 50) também eram desprezíveis diante
de T ≈ 10⁴. Explica, por exemplo, as janelas que pioraram de 46 para 123 no
v2. **Deve ser relatado como limitação dos experimentos exploratórios.** Além
disso, uma avaliação custa cerca de 3 ms, então 1500 avaliações são só 5 s de
busca.

## SA lexicográfico em duas fases (`sa2`)

- Um movimento é decidido pelo **primeiro nível que muda**, na ordem
  (hard, déficit de H12, excesso de H10, soft). Se melhora, é aceito. Se piora
  num nível recozido na fase, é aceito com probabilidade exp(−Δ/T). Se piora
  num nível não recozido, é rejeitado. **Hard e excesso nunca pioram.**
- **Fase 1** (20% do orçamento): recoze o déficit de H12; o soft fica na
  temperatura inicial da fase 2, para não virar um passeio aleatório.
- **Fase 2** (80%): recoze só o soft; os níveis de cima só podem melhorar.
- **Calibração** no início de cada execução: 200 movimentos aleatórios a
  partir da solução inicial. Para cada nível recozido, T₀ aceita a piora
  mediana com 50% de probabilidade e T_f com 1%: T = mediana / ln(1/χ). O
  resfriamento é geométrico entre T₀ e T_f ao longo da fase. As amostras da
  calibração contam no orçamento.

## Demais escolhas

- **Partida:** a solução do guloso (determinística, calculada uma vez) para
  todos os algoritmos. O horário real é relatado como baseline.
- **Orçamento:** 100 mil avaliações por execução (cerca de 5 min), igual para
  todos os algoritmos. O BasicSA do OptFrame para por tempo e fica para depois.
- **Algoritmos:** `sa2`, ILS e VNS. O SA de v1–v3 (`sa`, parâmetros do v3)
  entra só como referência.
- **Sementes:** 3 de calibração (11, 22, 33), usadas só para ajustar e
  verificar, e 10 de avaliação (101 a 1010), usadas nos resultados do texto.
- **Análise:** comparação lexicográfica por semente e Wilcoxon pareado
  bilateral exato por nível (hard, déficit, soft). Os resultados são relatados
  em relação aos pisos estruturais (hard 4, déficit 28; lidos da instância) e ao horário real
  (soft normalizado = 3).
- Os cenários E1–E3 (CC antes de SI, SI antes de CC e conjunto) ainda
  precisam ser ligados ao executor. A instância atual corresponde ao E3.

## Verificação inicial (sementes de calibração 11, 22, 33)

Resultados em `dados/processados/experimento_oficial_2026/verificacao_inicial`
(20 mil avaliações) e `.../verificacao_100k` (100 mil). Pisos lidos da
instância: hard 4 (espelho TCC00332 × TCC00354) e déficit de H12 28. Esse
piso foi corrigido nesta verificação: o matching creditava 1/k às turmas com
dois docentes, mas a política decidida é a integral.

| Orçamento | Algoritmo | Hard | Déficit | Excesso | Soft (mediana) |
|---|---|---|---|---|---|
| 20 mil | sa2 | 4 | 28 | 0 | 2,343 |
| 20 mil | VNS | 4 | 31 | 0 | 2,059 |
| 20 mil | ILS | 5 | 32 | 0 | 2,206 |
| 20 mil | SA de v1–v3 | 4 | 29 | **52** | 2,002 |
| 100 mil | sa2 | 4 | 28 | 0 | **1,863** |
| 100 mil | VNS | 4 | 30 | 0 | 1,941 |
| 100 mil | ILS | 4 | 31 | 0 | 2,045 |

Horário real: hard 15, déficit 48, soft 3,000. Partida gulosa: hard 5,
déficit 33, soft 2,264.

- O `sa2` vence ILS e VNS nas 3 sementes, pela comparação lexicográfica, nos
  dois orçamentos. Com 100 mil avaliações também tem o melhor soft mediano.
  Com 3 sementes nenhum Wilcoxon é significativo (o menor p possível é 0,25);
  isso fica para as 10 sementes de avaliação.
- Com 20 mil avaliações, o soft do `sa2` ficou pior que o da partida: a fase 2
  teve só 16 mil avaliações. Com 100 mil, ele recupera.
- O SA de v1–v3 superlota salas (excesso mediano de 52 alunos), como a
  análise da calibração previa. Não serve mais de referência.
- Calibração medida: piora mediana de 1 turma no déficit (T de 1,44 a 0,22) e
  de 0,013–0,018 no soft (T de cerca de 0,02 a 0,003). Na fase 2 são aceitos
  cerca de 18% dos movimentos.
- **Em todos os algoritmos**, janelas (46 → 16–27), rodízio e preferência
  melhoram, mas dias trabalhados piora (233 → 242–259). É efeito dos pesos
  iguais depois da normalização: 1 janela (1/46) vale cerca de 5× um dia
  (1/233). Se dias trabalhados importar mais, ajustar `PESOS_SOFT_OFICIAL`.
- Tempo: cerca de 11 min por execução de 100 mil avaliações com 9 processos
  em paralelo. O protocolo completo (3 algoritmos × 10 sementes) leva cerca de
  40 min por cenário.
