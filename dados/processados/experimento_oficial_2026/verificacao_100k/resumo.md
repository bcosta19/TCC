# Experimento oficial 2026 — verificacao_100k

| Algoritmo | Execuções | Hard (mediana) | Acima do piso | Déficit H12 | Excesso H10 | Soft total (mediana) | Segundos |
|---|---|---|---|---|---|---|---|
| ils | 3 | 4 | 0 | 31 (piso 28) | 0 | 2.045 | 701 |
| sa2 | 3 | 4 | 0 | 28 (piso 28) | 0 | 1.863 | 646 |
| vns | 3 | 4 | 0 | 30 (piso 28) | 0 | 1.941 | 681 |

Horário real: hard 15, déficit 48, soft 3.000. Partida gulosa: hard 5, déficit 33, soft 2.264.

Comparação pareada por semente contra `sa2` (lexicográfica e Wilcoxon exato por nível):

- `ils`: `sa2` melhor em 3, pior em 0, empate em 0 de 3; hard p=1.000, deficit_carga_anual p=0.250, soft_total p=0.500
- `vns`: `sa2` melhor em 3, pior em 0, empate em 0 de 3; hard p=1.000, deficit_carga_anual p=0.500, soft_total p=1.000
