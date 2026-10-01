# Piloto tecnico do SA nativo no pyoptframe

Execucao: 2026-09-07T20:45:13.090902-03:00
Python 3.14.7; OptFrame 5.1.0.

Perfil sintetico existente, com proxies; pesos e dominios nao foram alterados.
Todos os resultados passaram pela validacao estrutural, pela equivalencia entre avaliadores e pela comparacao com a mesma entrada gulosa.

| Metodo | Seed | Hard | Deficit H12 | Score | Tempo (s) | Avaliacoes |
|---|---:|---:|---:|---:|---:|---:|
| baseline | - | 27 | 14.0 | 27003758.72 | 0.000 | 1 |
| guloso | - | 4 | 2.0 | 4002747.45 | 9.808 | 3123 |
| sa_referencia | 101 | 2 | 0.0 | 2005042.92 | 5.103 | 1500 |
| sa_referencia | 202 | 1 | 0.0 | 1005242.52 | 5.251 | 1500 |
| sa_referencia | 303 | 1 | 0.0 | 1005323.90 | 5.260 | 1500 |
| sa_referencia | 404 | 1 | 1.0 | 1005284.02 | 5.151 | 1500 |
| sa_referencia | 505 | 0 | 0.0 | 5446.40 | 5.010 | 1500 |
| sa_optframe | 101 | 2 | 3.0 | 2003262.87 | 10.066 | 369 |
| sa_optframe | 202 | 3 | 3.0 | 3003114.28 | 10.070 | 355 |
| sa_optframe | 303 | 4 | 2.0 | 4002747.45 | 10.063 | 342 |
| sa_optframe | 404 | 3 | 3.0 | 3003931.73 | 10.112 | 341 |
| sa_optframe | 505 | 4 | 2.0 | 4002747.45 | 10.067 | 349 |

## Limites de interpretacao

SA nativo: 10.0s por busca, alpha=0.98, iter_max=100, T0=1e8. SA de referencia: `{"avaliacoes": 1500, "resfriamento": 0.997, "temperatura_inicial": 1000000.0}`.
Os orcamentos e resfriamentos diferem; este piloto verifica integracao e nao estabelece superioridade entre implementacoes.
Semente controla vizinhanca Python; RNG interno nativo nao configurado. Parada por tempo varia entre execucoes.
O score reportado pelo avaliador difere da energia interna da busca. O manifesto e os metadados das solucoes preservam a configuracao usada.
As dez sobreposicoes curriculares permanecem no perfil fixo. Consulte o diagnostico de turmas alternativas antes de interpretar isso como impossibilidade de cursar um periodo.

## Reexecucao

```bash
.venv/bin/python scripts/benchmark_optframe_sa_2026.py 10.0
```

Cada execucao cria uma pasta nova. `manifesto.json` registra hashes e parametros; `resultados.csv` guarda todas as metricas. Instancia e solucoes JSON ficam locais e sao ignoradas pelo Git.
