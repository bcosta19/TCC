# Registro da implementação do benchmark sintético de 2026

> Este registro descreve o benchmark de referência de 23/08. Para o piloto
> BasicSA nativo, a validação estrutural e a interpretação revisada dos
> conflitos entre turmas alternativas, consulte
> [a validação de 04/09/2026](validacao_prototipo_2026_09_04.md).

**Data do registro:** 23/08/2026\
**Situação:** benchmark técnico reproduzível concluído; experimento institucional oficial ainda pendente.

## 1. Objetivo do trabalho realizado

O objetivo foi transformar a infraestrutura existente em um fluxo executável
de ponta a ponta antes da chegada de todos os dados institucionais:

```text
dados observados de 2025/2026
→ instância sintética explicitamente identificada
→ solução inicial gulosa
→ SA, ILS e VNS
→ múltiplas sementes
→ CSV e relatório comparativo
```

O perfil sintético não substitui a instância oficial. Ele permite validar o
software, produzir resultados visíveis e preparar a troca futura das proxies
pelos valores aprovados pelo orientador.

## 2. Estado encontrado no início

- A pipeline de 2026 já produzia 180 turmas físicas, 329 encontros, 61 docentes
  observados e 22 salas.
- A instância oficial permanecia com capacidades, recursos, setores,
  habilitações, prioridades, horários fixos, cotutoria e universo H12
  pendentes.
- Os solvers anteriores eram separados e testados principalmente com a
  instância provisória de 2025.
- Na instância 2026, os solvers anteriores não encontrariam turmas móveis por
  falta dos domínios sintéticos necessários.
- O núcleo do projeto ainda não executava buscas pelo motor nativo do
  pyoptframe.

## 3. Alternativas consideradas

### 3.1 Aguardar todos os dados oficiais

Essa alternativa produziria dados mais fiéis, mas deixaria o desenvolvimento
do solver, dos experimentos e dos relatórios bloqueado por decisões externas.

### 3.2 Inventar uma instância completamente artificial

Seria simples de controlar, mas teria pouca relação com a escala e a estrutura
do problema do IC/UFF.

### 3.3 Completar os dados observados com proxies reproduzíveis

Foi a alternativa adotada. A estrutura de turmas, professores observados,
horários e salas continua vindo dos dados de 2026. Apenas os parâmetros
ausentes recebem proxies determinísticas, documentadas e separadas dos dados
oficiais.

## 4. Decisões adotadas no perfil sintético

| Parâmetro | Decisão provisória |
|---|---|
| Capacidade das salas | Maior demanda observada em 2025 ou 2026 |
| Laboratório | Sala cujo identificador começa com `L` |
| Recurso por encontro | Inferido a partir do uso histórico de sala comum/laboratório |
| Preferência docente | Frequência histórica professor × disciplina normalizada |
| Prioridade docente | Valor neutro `1.0` para todos |
| Setor | Setor histórico único observado em 2025 |
| Habilitação | Professores do setor histórico, incluindo o professor observado |
| Obrigatórias e externas | Horários mantidos fixos |
| Optativas | Horários flexíveis em padrões históricos compatíveis |
| Cotutoria em H12 | Crédito fracionado entre os cotutores |
| Universo H12 | 40 docentes observados selecionados por carga e viabilidade conjunta |

O universo H12 foi validado por matching bipartido. Os domínios oferecem
cobertura conjunta para os 118 créditos necessários (`118/118`). Essa
verificação evita considerar viável um conjunto no qual cada professor parece
ter opções individualmente, mas disputa as mesmas poucas turmas com outros
professores.

## 5. Implementação realizada

### 5.1 Instância sintética

- Configuração versionada em `dados/config_sintetica_2026_v1.json`.
- Gerador em `scripts/build_synthetic_instance_2026.py`.
- Separação entre professores observados e professores atribuídos pela solução.
- Registro das fontes, hipóteses e hashes usados na geração.
- Validação de domínios, salas, horários, H12 e cotutoria.

### 5.2 Avaliação

- Correção do cálculo de descanso entre dias não consecutivos.
- Correção do universo H12 explícito.
- Alinhamento da capacidade insuficiente entre os dois avaliadores.
- Separação da contagem oficial de H12 e do déficit de créditos.
- H12 oficial continua contando docentes abaixo do mínimo.
- O déficit H12 soma quantas obrigatórias ainda faltam para todos atingirem
  três.
- Instâncias com H12 indisponível são rejeitadas pela busca.

### 5.3 Busca integrada

- Núcleo comum em `src/solve/integrated.py`.
- Movimentos de professor, horário e sala.
- Aplicação e reversão exata dos movimentos.
- Melhoria gulosa integrada.
- Implementações de referência de Simulated Annealing, ILS e VNS.
- Mesmo avaliador, mesma instância e mesmo orçamento para todos os métodos.
- Cinco sementes: `101`, `202`, `303`, `404` e `505`.
- Orçamento de 1.500 avaliações por execução.

### 5.4 Proteção da pipeline oficial

- Tabelas de revisão existentes não são mais apagadas pela execução normal.
- Um conjunto parcial de tabelas bloqueia a pipeline em vez de recriar tudo.
- Perfis parciais não podem marcar a instância oficial como pronta.
- `dados/processados/revisoes_2026_manifest.json` registra os hashes das fontes
  usadas pelas revisões.
- Alteração de turmas, horários, salas, currículos, preferências ou dados web
  invalida a revisão anterior sem sobrescrever decisões humanas.

### 5.5 Ambiente e testes

- Ambiente virtual preparado com as dependências do projeto.
- `optframe==5.1.0` instalado e importado com sucesso.
- O benchmark atual ainda executa as implementações de referência em Python,
  não o motor nativo do OptFrame.
- Suíte final: 66 testes aprovados.
- Avaliador direto e avaliador de referência conferidos nas soluções
  registradas.

## 6. Resultados principais

### 6.1 Comparação de viabilidade

| Método | Violações hard | Docentes abaixo de H12 | Déficit H12 |
|---|---:|---:|---:|
| Baseline observado | 27 | 14 | 14 |
| Guloso integrado | 12 | 2 | 2 |
| Melhor SA | 10 | 0 | 0 |
| Melhor ILS | 11 | 1 | 1 |
| Melhor VNS | 11 | 1 | 1 |

O SA zerou H12 em três das cinco sementes (`202`, `303` e `404`) sem criar
conflitos de professor.

### 6.2 Melhor solução encontrada

| Critério | Baseline | Melhor SA | Diferença |
|---|---:|---:|---:|
| Conflitos de sala | 3 | 0 | -3 |
| Conflitos de professor | 0 | 0 | 0 |
| Conflitos curriculares | 10 | 10 | 0 |
| Capacidade insuficiente | 0 | 0 | 0 |
| Recursos incompatíveis | 0 | 0 | 0 |
| Descanso insuficiente | 0 | 0 | 0 |
| Docentes abaixo de H12 | 14 | 0 | -14 |
| Dias trabalhados | 233 | 230 | -3 |
| Janelas | 46 | 80 | +34 |
| Desperdício de capacidade | 3.521 | 3.453 | -68 |
| Rodízio | 38 | 29 | -9 |

As violações hard caíram de 27 para 10, redução de 62,96%. As dez violações
restantes são conflitos curriculares que não podem ser corrigidos neste perfil,
pois os horários das obrigatórias foram mantidos fixos.

### 6.3 Comportamento prático dos métodos

- O guloso produziu a maior melhoria inicial com baixo custo.
- O SA foi o método mais eficaz para eliminar H12 e reduzir o trabalho manual
  de viabilização da grade.
- ILS e VNS deixaram apenas uma pendência H12 e conservaram melhor janelas e
  desperdício.
- O melhor SA aceitou mais janelas para eliminar a última violação H12. Isso
  mostra o conflito entre viabilidade e conforto docente.

## 7. Conclusões principais

1. O fluxo técnico completo é executável e reproduzível.
2. A solução observada possui espaço relevante para melhoria automática.
3. Uma boa solução inicial é responsável por grande parte do ganho.
4. O déficit H12 fornece orientação que a contagem binária de docentes não
   fornecia; após sua inclusão, o SA passou a zerar H12.
5. SA é mais indicado para buscar viabilidade e reduzir correções manuais de
   professores.
6. ILS e VNS são úteis para produzir alternativas mais equilibradas e reduzir
   o trabalho manual de acabamento.
7. Os métodos são complementares. Um fluxo futuro promissor é guloso → SA
   para viabilidade → ILS/VNS para refinamento soft.
8. Não se pode declarar superioridade estatística com cinco sementes e
   parâmetros provisórios.
9. Os resultados validam o software, não uma política oficial da UFF.

## 8. É possível executar uma instância real?

### Resposta curta

**Sim, tecnicamente; não, ainda não como experimento institucional oficial.**

O projeto já usa uma instância estruturalmente real: as 180 turmas, 329
encontros, professores observados, horários e salas vêm dos quadros de 2026.
Essa instância pode ser carregada, completada por proxies e executada de ponta
a ponta, como demonstrado pelo benchmark.

Ainda não é correto chamar o resultado de experimento oficial porque os
seguintes parâmetros continuam sintéticos ou pendentes de validação:

- capacidades físicas e recursos oficiais das salas;
- setores e dias oficiais;
- habilitações docentes;
- prioridades reais;
- universo institucional de H12;
- política oficial de cotutoria;
- horários realmente fixos ou flexíveis;
- classificação das ofertas curriculares pendentes;
- pesos finais e classificação hard × soft.

Além disso, ainda falta uma etapa que aplique automaticamente todos os CSVs de
revisão oficial ao JSON definitivo. O verificador confirma preenchimento e
protege a prontidão, mas a materialização completa das decisões oficiais na
instância deve ser implementada antes do experimento final.

Portanto, o estado atual permite:

- rodar testes realistas na escala real do problema;
- comparar algoritmos e validar a implementação;
- demonstrar melhorias sobre o quadro observado;
- preparar tabelas e gráficos preliminares.

O estado atual ainda não permite:

- afirmar que a solução é uma recomendação institucional;
- usar os números como resultado final da monografia;
- concluir superioridade dos algoritmos;
- substituir a validação do orientador.

## 9. Próximas etapas para o experimento oficial

1. Preencher e validar os CSVs institucionais pendentes.
2. Implementar a aplicação das revisões oficiais ao JSON final.
3. Validar pesos, hard × soft e universo H12 com o orientador.
4. Integrar e executar as buscas pelo motor nativo do pyoptframe.
5. Definir o protocolo final de sementes, orçamento e calibração.
6. Executar novamente o mesmo fluxo sem proxies.
7. Produzir análise estatística e interpretação acadêmica final.

## 10. Artefatos relacionados

- Configuração: `dados/config_sintetica_2026_v1.json`.
- Gerador: `scripts/build_synthetic_instance_2026.py`.
- Solver integrado: `src/solve/integrated.py`.
- Executor: `scripts/run_synthetic_experiments_2026.py`.
- Resultados: `dados/processados/resultados_experimento_sintetico_2026.csv`.
- Relatório automático: `dados/processados/relatorio_experimento_sintetico_2026.md`.
- Manifesto de revisão: `dados/processados/revisoes_2026_manifest.json`.
