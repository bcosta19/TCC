# Relatorio do experimento sintetico reprodutivel - 2026 CC/SI

Execucao: 2026-09-07T20:44:51-03:00
Commit: `9cb06c1351a51f0ca1d34ef913ce466051bfc381`
Estado do worktree: `com alteracoes nao commitadas`
SHA-256 do codigo do benchmark: `fc8ff3546ea0fc613f15e791c2696619cc8701701126e9f26c58cc38d295870e`
Python: `3.14.7`
OptFrame disponivel no ambiente: `5.1.0`
SHA-256 da instancia: `071db3a126571c6652e4ac5f3250e4250a27c01b8cb29d6e9605126338fc1945`

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
| Turmas com horario flexivel | 173 |

## Hipoteses reproduziveis

| Parametro | Regra utilizada |
|---|---|
| capacidade_sala | `maximo_observado_2025_2026` |
| laboratorio_por_prefixo_l | `True` |
| prioridade_docente | `1.0` |
| h12_universo | `40_docentes_observados_selecionados_por_carga_e_matching_proxy_de_permanentes_HP1` |
| cotutoria_h12 | `fracionada` |
| horarios | `externas_e_servico_fixas_obrigatorias_flexiveis_no_setor_HP2_exploratorio` |
| habilitacao | `setor_historico_2025_mais_professor_observado` |

## Baseline e melhoria gulosa

| Configuracao | Score | Hard | Sala | Professor | Curriculo | Capacidade | Recursos | Descanso | H12 docentes | Deficit H12 | Dias | Janelas | Desperdicio | Preferencia |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline observado | 27003758.72 | 27 | 3 | 0 | 10 | 0 | 0 | 0 | 14 | 14.00 | 233 | 46 | 3521.00 | -79.28 |
| Melhoria gulosa integrada | 4002747.45 | 4 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | 2.00 | 214 | 38 | 2540.00 | -76.55 |

A passagem gulosa reduziu o score em **85,18%** e as violacoes hard em **85,19%**.

## Resultados multi-seed

| Algoritmo | Execucoes | Score medio | Desvio | Melhor score | Hard medio | Melhor hard | Deficit H12 medio | Melhor deficit | Tempo medio (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ILS | 5 | 2602782.65 | 547708.13 | 2002793.45 | 2.60 | 2 | 1.40 | 1.00 | 5.448 |
| SA | 5 | 1005267.95 | 706964.13 | 5446.40 | 1.00 | 0 | 0.20 | 0.00 | 5.198 |
| VNS | 5 | 2802751.15 | 836664.76 | 2002747.45 | 2.80 | 2 | 1.00 | 1.00 | 5.649 |

## Melhor resultado por algoritmo

| Algoritmo | Score | Melhoria score vs. baseline | Hard | Melhoria hard vs. baseline | Sala | Professor | Curriculo | H12 docentes | Deficit H12 | Janelas | Desperdicio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ILS | 2002793.45 | 92,58% | 2 | 92,59% | 0 | 0 | 1 | 1 | 1.00 | 38 | 2582.00 |
| SA | 5446.40 | 99,98% | 0 | 100,00% | 0 | 0 | 0 | 0 | 0.00 | 123 | 5116.00 |
| VNS | 2002747.45 | 92,58% | 2 | 92,59% | 0 | 0 | 1 | 1 | 1.00 | 36 | 2540.00 |

## Melhor solucao global

A melhor solucao foi produzida por **SA**. Ela alterou **89 atribuicoes de professor**, **61 padroes de horario** e **196 alocacoes de sala por encontro** em relacao ao baseline.

| Metrica | Baseline | Melhor global | Diferenca |
|---|---:|---:|---:|
| Hard: conflitos_sala | 3 | 0 | -3 |
| Hard: conflitos_professor | 0 | 0 | 0 |
| Hard: conflitos_curriculares | 10 | 0 | -10 |
| Hard: capacidade_insuficiente | 0 | 0 | 0 |
| Hard: recursos_incompativeis | 0 | 0 | 0 |
| Hard: descanso_insuficiente | 0 | 0 | 0 |
| Hard: carga_anual_insuficiente | 14 | 0 | -14 |
| Soft: dias_trabalhados | 233 | 243 | 10 |
| Soft: janelas | 46 | 123 | 77 |
| Soft: desperdicio_capacidade | 3521.00 | 5116.00 | 1595.00 |
| Soft: rodizio_semestre | 38 | 25 | -13 |
| Soft: preferencia_priorizada | -79.28 | -60.60 | 18.68 |
| Guia: deficit_carga_anual | 14.00 | 0.00 | -14.00 |

Os conflitos curriculares nao diminuem neste perfil porque as 150 turmas obrigatorias permanecem com horario fixo; somente optativas recebem dominio de horario sintetico. Essa limitacao e intencional e separa o teste de professores/salas da futura validacao dos horarios institucionais.

A melhor busca (SA) altera as metricas conforme a tabela acima. Como o comparador prioriza qualquer reducao hard, uma melhora hard pode aceitar piora nos criterios soft; o resultado evidencia um trade-off e nao demonstra superioridade geral de um algoritmo.

## Execucoes individuais

| Algoritmo | Seed | Score | Hard | Deficit H12 | Tempo (s) | Avaliacoes |
|---|---:|---:|---:|---:|---:|---:|
| ILS | 101 | 2002793.45 | 2 | 1.00 | 5.283 | 1500 |
| ILS | 202 | 2002803.45 | 2 | 1.00 | 5.459 | 1500 |
| ILS | 303 | 3002767.45 | 3 | 2.00 | 5.441 | 1500 |
| ILS | 404 | 3002781.45 | 3 | 1.00 | 5.448 | 1500 |
| ILS | 505 | 3002767.45 | 3 | 2.00 | 5.612 | 1500 |
| SA | 101 | 2005042.92 | 2 | 0.00 | 5.252 | 1500 |
| SA | 202 | 1005242.52 | 1 | 0.00 | 5.111 | 1500 |
| SA | 303 | 1005323.90 | 1 | 0.00 | 4.879 | 1500 |
| SA | 404 | 1005284.02 | 1 | 1.00 | 5.036 | 1500 |
| SA | 505 | 5446.40 | 0 | 0.00 | 5.711 | 1500 |
| VNS | 101 | 3002757.45 | 3 | 1.00 | 5.713 | 1500 |
| VNS | 202 | 2002750.65 | 2 | 1.00 | 5.737 | 1500 |
| VNS | 303 | 2002747.45 | 2 | 1.00 | 5.711 | 1500 |
| VNS | 404 | 3002737.40 | 3 | 1.00 | 5.674 | 1500 |
| VNS | 505 | 4002762.78 | 4 | 1.00 | 5.409 | 1500 |

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
