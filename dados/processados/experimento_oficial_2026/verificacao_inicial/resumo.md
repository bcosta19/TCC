# Experimento oficial 2026 — verificacao_inicial

| Algoritmo | Execuções | Hard (mediana) | Acima do piso | Déficit H12 | Excesso H10 | Soft total (mediana) | Segundos |
|---|---|---|---|---|---|---|---|
| ils | 3 | 5 | 1 | 32 (piso 28) | 0 | 2.206 | 170 |
| sa | 3 | 4 | 0 | 29 (piso 28) | 52 | 2.002 | 172 |
| sa2 | 3 | 4 | 0 | 28 (piso 28) | 0 | 2.343 | 165 |
| vns | 3 | 4 | 0 | 31 (piso 28) | 0 | 2.059 | 158 |

Horário real: hard 15, déficit 48, soft 3.000. Partida gulosa: hard 5, déficit 33, soft 2.264.

Comparação pareada por semente contra `sa2` (lexicográfica e Wilcoxon exato por nível):

- `ils`: `sa2` melhor em 3, pior em 0, empate em 0 de 3; hard p=0.250, deficit_carga_anual p=0.250, soft_total p=0.500
- `sa`: `sa2` melhor em 3, pior em 0, empate em 0 de 3; hard p=1.000, deficit_carga_anual p=0.500, soft_total p=0.250
- `vns`: `sa2` melhor em 3, pior em 0, empate em 0 de 3; hard p=1.000, deficit_carga_anual p=0.250, soft_total p=0.250
