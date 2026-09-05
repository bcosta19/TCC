# Piloto tecnico do SA nativo no pyoptframe

Execucao: 2026-09-04T22:51:07.874147-03:00
Python 3.14.7; OptFrame 5.1.0.

Perfil sintetico existente, com proxies; pesos e dominios nao foram alterados.
Todos os resultados passaram pela validacao estrutural, pela equivalencia entre avaliadores e pela comparacao com a mesma entrada gulosa.

| Metodo | Seed | Hard | Deficit H12 | Score | Tempo (s) | Avaliacoes |
|---|---:|---:|---:|---:|---:|---:|
| baseline | - | 27 | 14.0 | 27003758.72 | 0.000 | 1 |
| guloso | - | 12 | 2.0 | 12002755.95 | 9.214 | 2423 |
| sa_referencia | 101 | 11 | 1.0 | 11003580.35 | 6.009 | 1500 |
| sa_referencia | 202 | 10 | 0.0 | 10004332.95 | 5.858 | 1500 |
| sa_referencia | 303 | 10 | 0.0 | 10003723.47 | 6.006 | 1500 |
| sa_referencia | 404 | 10 | 0.0 | 10004230.58 | 5.961 | 1500 |
| sa_referencia | 505 | 11 | 1.0 | 11004422.43 | 5.937 | 1500 |
| sa_optframe | 101 | 12 | 2.0 | 12002755.95 | 10.054 | 471 |
| sa_optframe | 202 | 12 | 2.0 | 12002755.95 | 10.049 | 460 |
| sa_optframe | 303 | 10 | 0.0 | 10004080.75 | 10.091 | 456 |
| sa_optframe | 404 | 12 | 2.0 | 12002755.95 | 10.057 | 444 |
| sa_optframe | 505 | 11 | 1.0 | 11003305.53 | 10.148 | 422 |

## Limites de interpretacao

SA nativo: 10.0s por busca, alpha=0.98, iter_max=100, T0=1e8. SA de referencia: `{"avaliacoes": 1500, "temperatura_inicial": 1000000.0, "resfriamento": 0.997}`.
Os orcamentos e resfriamentos diferem; este piloto verifica integracao e nao estabelece superioridade entre implementacoes.
Semente controla vizinhanca Python; RNG interno nativo nao configurado. Parada por tempo varia entre execucoes.
O score reportado pelo avaliador difere da energia interna da busca. O manifesto e os metadados das solucoes preservam a configuracao usada.
As dez sobreposicoes curriculares permanecem no perfil fixo. Consulte o diagnostico de turmas alternativas antes de interpretar isso como impossibilidade de cursar um periodo.

## Reexecucao

```bash
.venv/bin/python scripts/benchmark_optframe_sa_2026.py 10.0
```

Cada execucao cria uma pasta nova. `manifesto.json` registra hashes e parametros; `resultados.csv` guarda todas as metricas. Instancia e solucoes JSON ficam locais e sao ignoradas pelo Git.
