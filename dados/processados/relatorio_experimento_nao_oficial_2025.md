# Relatório do experimento não oficial — CC/SI 2025

Execução: 2026-08-11T23:23:38-03:00
Python: `3.14.6`

> Este relatório valida a implementação e a pipeline com dados provisórios. Não é resultado experimental oficial da monografia.

## Configuração e ressalvas

- Instância derivada do quadro QH 2025, filtrada para CC/SI.
- Capacidade de sala e requisito de laboratório são estimativas/inferências.
- Preferências usam frequência histórica do webscrap normalizada por disciplina.
- A prioridade de todos os professores foi fixada em `1.0` apenas para este teste.
- Domínios de professor usam professores observados no mesmo setor em QH 2025.
- Domínios de horário usam padrões de dias observados no mesmo setor e semestre.
- H12 foi ativada com mínimo de 3 obrigatórias por professor no ano.
- A instância tem 58 professores IC e 148 obrigatórias; H12 requer 174 alocações, portanto a configuração provisória é estruturalmente inviável para H12.
- O critério de distância não participa da avaliação nem dos solvers.
- 150 turmas IC receberam domínio de professor; 144 têm mais de um candidato.
- Arquivos de revisão gerados: `professores_por_setor_2025.csv` (72 linhas), `dominios_professores_turmas_2025.csv` (150 linhas), `dias_por_setor_2025.csv` (55 linhas) e `auditoria_h12_professores_2025.csv` (76 linhas).

## Resultados

| Configuração | Score | Hard | Sala | Currículo | H12 | Preferência | Dias | Janelas | Capacidade | Rodízio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline observado | 51002369.63 | 51 | 13 | 10 | 28 | -70.37 | 213 | 28 | 2172.00 | 27 |
| Baseline com salas provisórias | 51002627.63 | 51 | 13 | 10 | 28 | -70.37 | 213 | 28 | 2430.00 | 27 |
| SA — salas | 38004257.63 | 38 | 0 | 10 | 28 | -70.37 | 213 | 28 | 4060.00 | 27 |
| SA — salas e horários | 29004411.63 | 29 | 0 | 1 | 28 | -70.37 | 231 | 80 | 4144.00 | 27 |
| SA — professores (setor histórico) | 35002435.13 | 35 | 13 | 10 | 12 | -25.87 | 223 | 59 | 2172.00 | 7 |

## Validações automatizadas

- [x] distância ausente do avaliador
- [x] contagem de violações hard consistente
- [x] score consistente com hard + soft
- [x] H12 presente como restrição hard
- [x] SA de professores usou domínio histórico por setor, sem modo irrestrito
- [x] avaliador rápido e avaliador exato equivalentes (instância flexível)
- [x] avaliador rápido e avaliador exato equivalentes (baseline observado)
- [x] avaliador rápido e avaliador exato equivalentes (baseline provisório)
- [x] avaliador rápido e avaliador exato equivalentes (solução SA de salas)
- [x] avaliador rápido e avaliador exato equivalentes (solução SA de horários)
- [x] avaliador rápido e avaliador exato equivalentes (solução SA de professores)
- [x] professores atribuídos respeitam os domínios históricos (150 turmas verificadas)
- [x] SA de salas preservou a carga anual enquanto movimentou apenas salas
- [x] SA de professores não aumentou violações H12

## Interpretação técnica

Os solvers executaram sem depender de distância. O SA de salas pode melhorar conflitos e desperdício de capacidade, mas não pode alterar H12 porque sua vizinhança só troca salas. O SA de salas e horários também não altera professores; portanto, a carga anual permanece limitada pela atribuição histórica de entrada.

O SA de professores alterou H12 de 28 para 12 usando apenas professores observados no mesmo setor em 2025. Como a instância tem apenas 148 obrigatórias para 174 exigidas, H12 não pode zerar nesse recorte; o resultado valida a vizinhança e o domínio histórico, não substitui a tabela oficial de habilitação.

## Próxima etapa autorizada

1. Validar com o orientador se o histórico 2025 pode ser usado como proxy de habilitação por setor.
2. Validar a classificação obrigatória/optativa com as grades CC e SI.
3. Substituir a prioridade neutra por dados validados pelo orientador.
4. Trocar os dias observados por dias oficiais de setor quando a tabela oficial estiver fechada.
5. Repetir o teste com seeds distintas somente depois de revisar esses dados.
