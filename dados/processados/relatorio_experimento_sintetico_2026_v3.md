# Relatorio do experimento sintetico reprodutivel - 2026 CC/SI

Execucao: 2026-09-30T23:28:25-03:00
Commit: `af5858f5b5eddfe7e698a63519ae94b8567ae847`
Estado do worktree: `com alteracoes nao commitadas`
SHA-256 do codigo do benchmark: `24ba86b3589c6f4842305be1f3a3e1290b41eb70c74129c63a458fc9f9c5237b`
Python: `3.14.7`
OptFrame disponivel no ambiente: `5.1.0`
SHA-256 da instancia: `38e5a58f046f9f04a688e4f8c7c4c545085d7efc69822fc0ef7bc2c58f881b74`

> Resultados nao oficiais. Capacidades, recursos, habilitacoes, prioridades, horarios flexiveis e universo H12 usam proxies documentadas. O benchmark valida a implementacao e nao substitui dados institucionais.

## Dados da instancia

| Indicador | Valor |
|---|---:|
| Turmas fisicas | 217 |
| Encontros semanais | 392 |
| Salas | 22 |
| Docentes no cadastro sintetico | 64 |
| Docentes no universo H12 sintetico | 40 |
| Turmas obrigatorias do IC | 148 |
| Turmas com professor movel | 146 |
| Turmas com horario flexivel | 111 |

## Hipoteses reproduziveis

| Parametro | Regra utilizada |
|---|---|
| capacidade_sala | `maximo_observado_2025_2026` |
| laboratorio_por_prefixo_l | `True` |
| prioridade_docente | `1.0` |
| h12_universo | `40_docentes_observados_selecionados_por_carga_e_matching_proxy_de_permanentes` |
| cotutoria_h12 | `integral_para_cada_docente` |
| horarios | `revisao_horarios_fixos_2026` |
| habilitacao | `setor_historico_2025_mais_professor_observado` |
| turmas_externas_referencia | `True` |

## Baseline e melhoria gulosa

| Configuracao | Score | Hard | Sala | Professor | Curriculo | Capacidade | Recursos | Descanso | H12 docentes | Deficit H12 | Dias | Janelas | Desperdicio | Preferencia |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline observado | 34003758.72 | 34 | 3 | 0 | 18 | 0 | 0 | 0 | 13 | 13.00 | 233 | 46 | 3521.00 | -79.28 |
| Melhoria gulosa integrada | 11002752.45 | 11 | 0 | 0 | 9 | 0 | 0 | 0 | 2 | 2.00 | 219 | 33 | 2547.00 | -75.55 |

A passagem gulosa reduziu o score em **67,64%** e as violacoes hard em **67,65%**.

## Resultados multi-seed

| Algoritmo | Execucoes | Score medio | Desvio | Melhor score | Hard medio | Melhor hard | Deficit H12 medio | Melhor deficit | Tempo medio (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ILS | 5 | 10802770.50 | 447197.41 | 10002799.45 | 10.80 | 10 | 1.40 | 1.00 | 4.950 |
| SA | 5 | 9204389.72 | 836425.32 | 8004703.33 | 9.20 | 8 | 0.20 | 0.00 | 4.754 |
| VNS | 5 | 10602785.47 | 547749.61 | 10002748.23 | 10.60 | 10 | 1.20 | 1.00 | 5.480 |

## Melhor resultado por algoritmo

| Algoritmo | Score | Melhoria score vs. baseline | Hard | Melhoria hard vs. baseline | Sala | Professor | Curriculo | H12 docentes | Deficit H12 | Janelas | Desperdicio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ILS | 10002799.45 | 70,58% | 10 | 70,59% | 0 | 0 | 9 | 1 | 1.00 | 40 | 2585.00 |
| SA | 8004703.33 | 76,46% | 8 | 76,47% | 0 | 0 | 8 | 0 | 0.00 | 95 | 4398.00 |
| VNS | 10002748.23 | 70,58% | 10 | 70,59% | 0 | 0 | 9 | 1 | 1.00 | 35 | 2540.00 |

## Melhor solucao global

A melhor solucao foi produzida por **SA**. Ela alterou **77 atribuicoes de professor**, **35 padroes de horario** e **127 alocacoes de sala por encontro** em relacao ao baseline.

| Metrica | Baseline | Melhor global | Diferenca |
|---|---:|---:|---:|
| Hard: conflitos_sala | 3 | 0 | -3 |
| Hard: conflitos_professor | 0 | 0 | 0 |
| Hard: conflitos_curriculares | 18 | 8 | -10 |
| Hard: capacidade_insuficiente | 0 | 0 | 0 |
| Hard: recursos_incompativeis | 0 | 0 | 0 |
| Hard: descanso_insuficiente | 0 | 0 | 0 |
| Hard: carga_anual_insuficiente | 13 | 0 | -13 |
| Soft: dias_trabalhados | 233 | 245 | 12 |
| Soft: janelas | 46 | 95 | 49 |
| Soft: desperdicio_capacidade | 3521.00 | 4398.00 | 877.00 |
| Soft: rodizio_semestre | 38 | 24 | -14 |
| Soft: preferencia_priorizada | -79.28 | -58.67 | 20.62 |
| Guia: deficit_carga_anual | 13.00 | 0.00 | -13.00 |

Os conflitos curriculares nao diminuem neste perfil porque as 148 turmas obrigatorias permanecem com horario fixo; somente optativas recebem dominio de horario sintetico. Essa limitacao e intencional e separa o teste de professores/salas da futura validacao dos horarios institucionais.

A melhor busca (SA) altera as metricas conforme a tabela acima. Como o comparador prioriza qualquer reducao hard, uma melhora hard pode aceitar piora nos criterios soft; o resultado evidencia um trade-off e nao demonstra superioridade geral de um algoritmo.

## Execucoes individuais

| Algoritmo | Seed | Score | Hard | Deficit H12 | Tempo (s) | Avaliacoes |
|---|---:|---:|---:|---:|---:|---:|
| ILS | 101 | 11002752.45 | 11 | 2.00 | 4.903 | 1500 |
| ILS | 202 | 11002752.45 | 11 | 2.00 | 4.913 | 1500 |
| ILS | 303 | 11002792.70 | 11 | 1.00 | 4.925 | 1500 |
| ILS | 404 | 10002799.45 | 10 | 1.00 | 4.999 | 1500 |
| ILS | 505 | 11002755.45 | 11 | 1.00 | 5.013 | 1500 |
| SA | 101 | 10005433.45 | 10 | 0.00 | 4.831 | 1500 |
| SA | 202 | 10002872.45 | 10 | 1.00 | 4.945 | 1500 |
| SA | 303 | 9004664.05 | 9 | 0.00 | 4.674 | 1500 |
| SA | 404 | 9004275.32 | 9 | 0.00 | 4.634 | 1500 |
| SA | 505 | 8004703.33 | 8 | 0.00 | 4.688 | 1500 |
| VNS | 101 | 10002748.23 | 10 | 1.00 | 5.456 | 1500 |
| VNS | 202 | 10002763.45 | 10 | 1.00 | 5.502 | 1500 |
| VNS | 303 | 11002811.78 | 11 | 1.00 | 5.431 | 1500 |
| VNS | 404 | 11002851.45 | 11 | 1.00 | 5.495 | 1500 |
| VNS | 505 | 11002752.45 | 11 | 2.00 | 5.516 | 1500 |

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
