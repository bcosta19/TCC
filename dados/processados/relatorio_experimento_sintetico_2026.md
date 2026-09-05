# Relatorio do experimento sintetico reprodutivel - 2026 CC/SI

Execucao: 2026-08-23T17:14:42-03:00
Commit: `eb29f5c4914c46059d178ecbd510116148d1ab71`
Estado do worktree: `com alteracoes nao commitadas`
SHA-256 do codigo do benchmark: `a93bb6ce3757cb3f4a5bbe310b6c656afbe21b7e14cee1eac4cb9455ca88cc5b`
Python: `3.14.7`
OptFrame disponivel no ambiente: `5.1.0`
SHA-256 da instancia: `74037128894a60cc4055bfd7d3045859460a74064227f3a879dc11f576f39a9e`

> Resultados nao oficiais. Capacidades, recursos, habilitacoes, prioridades, horarios flexiveis e universo H12 usam proxies documentadas. O benchmark valida a implementacao e nao substitui dados institucionais.

## Dados da instancia

| Indicador | Valor |
|---|---:|
| Turmas fisicas | 180 |
| Encontros semanais | 329 |
| Salas | 22 |
| Docentes no cadastro sintetico | 64 |
| Docentes no universo H12 sintetico | 40 |
| Turmas obrigatorias do IC | 150 |
| Turmas com professor movel | 146 |
| Turmas com horario flexivel | 27 |

## Hipoteses reproduziveis

| Parametro | Regra utilizada |
|---|---|
| capacidade_sala | `maximo_observado_2025_2026` |
| laboratorio_por_prefixo_l | `True` |
| prioridade_docente | `1.0` |
| h12_universo | `40_docentes_observados_selecionados_por_carga_e_matching` |
| cotutoria_h12 | `fracionada` |
| horarios | `obrigatorias_e_externas_fixas_optativas_flexiveis` |
| habilitacao | `setor_historico_2025_mais_professor_observado` |

## Baseline e melhoria gulosa

| Configuracao | Score | Hard | Sala | Professor | Curriculo | Capacidade | Recursos | Descanso | H12 docentes | Deficit H12 | Dias | Janelas | Desperdicio | Preferencia |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline observado | 27003758.72 | 27 | 3 | 0 | 10 | 0 | 0 | 0 | 14 | 14.00 | 233 | 46 | 3521.00 | -79.28 |
| Melhoria gulosa integrada | 12002755.95 | 12 | 0 | 0 | 10 | 0 | 0 | 0 | 2 | 2.00 | 215 | 36 | 2548.00 | -76.05 |

A passagem gulosa reduziu o score em **55,55%** e as violacoes hard em **55,56%**.

## Resultados multi-seed

| Algoritmo | Execucoes | Score medio | Desvio | Melhor score | Hard medio | Melhor hard | Deficit H12 medio | Melhor deficit | Tempo medio (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SA | 5 | 10404057.96 | 547671.05 | 10003723.47 | 10.40 | 10 | 0.40 | 0.00 | 5.789 |
| ILS | 5 | 11202770.75 | 447205.32 | 11002751.95 | 11.20 | 11 | 1.40 | 1.00 | 8.313 |
| VNS | 5 | 11202772.72 | 447202.97 | 11002744.62 | 11.20 | 11 | 1.20 | 1.00 | 8.684 |

## Melhor resultado por algoritmo

| Algoritmo | Score | Melhoria score vs. baseline | Hard | Melhoria hard vs. baseline | Sala | Professor | Curriculo | H12 docentes | Deficit H12 | Janelas | Desperdicio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SA | 10003723.47 | 62,95% | 10 | 62,96% | 0 | 0 | 10 | 0 | 0.00 | 80 | 3453.00 |
| ILS | 11002751.95 | 59,25% | 11 | 59,26% | 0 | 0 | 10 | 1 | 1.00 | 31 | 2548.00 |
| VNS | 11002744.62 | 59,25% | 11 | 59,26% | 0 | 0 | 10 | 1 | 1.00 | 29 | 2544.00 |

## Melhor solucao global

A melhor solucao foi produzida por **SA**. Ela alterou **60 atribuicoes de professor**, **14 padroes de horario** e **92 alocacoes de sala por encontro** em relacao ao baseline.

| Metrica | Baseline | Melhor global | Diferenca |
|---|---:|---:|---:|
| Hard: conflitos_sala | 3 | 0 | -3 |
| Hard: conflitos_professor | 0 | 0 | 0 |
| Hard: conflitos_curriculares | 10 | 10 | 0 |
| Hard: capacidade_insuficiente | 0 | 0 | 0 |
| Hard: recursos_incompativeis | 0 | 0 | 0 |
| Hard: descanso_insuficiente | 0 | 0 | 0 |
| Hard: carga_anual_insuficiente | 14 | 0 | -14 |
| Soft: dias_trabalhados | 233 | 230 | -3 |
| Soft: janelas | 46 | 80 | 34 |
| Soft: desperdicio_capacidade | 3521.00 | 3453.00 | -68.00 |
| Soft: rodizio_semestre | 38 | 29 | -9 |
| Soft: preferencia_priorizada | -79.28 | -68.53 | 10.75 |
| Guia: deficit_carga_anual | 14.00 | 0.00 | -14.00 |

Os conflitos curriculares nao diminuem neste perfil porque as 150 turmas obrigatorias permanecem com horario fixo; somente optativas recebem dominio de horario sintetico. Essa limitacao e intencional e separa o teste de professores/salas da futura validacao dos horarios institucionais.

A melhor busca (SA) altera as metricas conforme a tabela acima. Como o comparador prioriza qualquer reducao hard, uma melhora hard pode aceitar piora nos criterios soft; o resultado evidencia um trade-off e nao demonstra superioridade geral de um algoritmo.

## Execucoes individuais

| Algoritmo | Seed | Score | Hard | Deficit H12 | Tempo (s) | Avaliacoes |
|---|---:|---:|---:|---:|---:|---:|
| SA | 101 | 11003580.35 | 11 | 1.00 | 6.504 | 1500 |
| SA | 202 | 10004332.95 | 10 | 0.00 | 5.069 | 1500 |
| SA | 303 | 10003723.47 | 10 | 0.00 | 5.403 | 1500 |
| SA | 404 | 10004230.58 | 10 | 0.00 | 5.626 | 1500 |
| SA | 505 | 11004422.43 | 11 | 1.00 | 6.345 | 1500 |
| ILS | 101 | 11002751.95 | 11 | 1.00 | 6.853 | 1500 |
| ILS | 202 | 11002820.95 | 11 | 1.00 | 7.774 | 1500 |
| ILS | 303 | 11002763.95 | 11 | 1.00 | 8.438 | 1500 |
| ILS | 404 | 11002760.95 | 11 | 2.00 | 8.993 | 1500 |
| ILS | 505 | 12002755.95 | 12 | 2.00 | 9.508 | 1500 |
| VNS | 101 | 11002744.62 | 11 | 1.00 | 9.395 | 1500 |
| VNS | 202 | 11002757.62 | 11 | 1.00 | 8.768 | 1500 |
| VNS | 303 | 11002823.20 | 11 | 1.00 | 8.881 | 1500 |
| VNS | 404 | 11002784.45 | 11 | 1.00 | 8.891 | 1500 |
| VNS | 505 | 12002753.70 | 12 | 2.00 | 7.488 | 1500 |

## Validacoes executadas

- [x] Mesma instancia e mesmo avaliador para todos os algoritmos.
- [x] Avaliador direto e avaliador de referencia equivalentes em todas as solucoes registradas.
- [x] Mesmos orcamentos de avaliacao configurados por algoritmo.
- [x] 5 sementes explicitas e versionadas.
- [x] Professor observado separado da atribuicao corrente.
- [x] Turmas fixas nao pertencem as vizinhancas correspondentes.
- [x] Capacidades e recursos sinteticos identificados por fonte.
- [x] Matching bipartido confirma cobertura conjunta dos creditos H12 sinteticos.
- [x] Solucoes e resultados vinculados ao hash da instancia.
- [x] Melhor solucao nunca pior que a entrada gulosa no comparador hard/soft.

## Reproducao

```bash
python scripts/run_pipeline_2026.py --offline
python scripts/build_synthetic_instance_2026.py
python scripts/run_synthetic_experiments_2026.py
```

## Limitacoes

- O pacote nativo `optframe==5.1.0` foi importado, mas este relatorio usa as implementacoes de referencia em Python; a execucao nativa das buscas permanece uma etapa separada.
- Os pesos soft sao unitarios e provisorios.
- O universo H12 de 40 docentes e uma hipotese sintetica de viabilidade, nao uma lista institucional.
- Capacidades sao limites inferiores observados, nao capacidades fisicas oficiais.
- Habilitacoes e horarios flexiveis sao derivados do historico de 2025.

## Leitura tecnica

A comparacao mede se as vizinhancas integradas conseguem melhorar a mesma solucao inicial sob um avaliador comum. Diferencas entre algoritmos neste benchmark servem para validar o software e orientar a etapa oficial; nao sustentam, isoladamente, conclusoes sobre a grade real da UFF.
