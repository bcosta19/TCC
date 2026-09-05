# Relatório geral do projeto para validação do orientador

> Atualização de 04/09/2026: este relatório preserva o retrato de 23/08.
> O BasicSA nativo já possui piloto e validação próprios. O diagnóstico das
> dez sobreposições encontrou escolhas de turmas alternativas sem choque no
> recorte; flexibilizar cinco ofertas não é uma necessidade demonstrada para
> permitir uma trajetória individual. Consulte
> [a validação atual](validacao_prototipo_2026_09_04.md) antes de usar as
> pendências e interpretações deste retrato histórico.

**Projeto:** Trabalho de Conclusão de Curso em Ciência da Computação — IC/UFF\
**Data do relatório:** 23/08/2026\
**Situação:** modelagem e implementação em estágio avançado de protótipo; benchmark técnico reproduzível concluído; instância e protocolo oficiais ainda pendentes de validação.

## 1. Resumo executivo

O trabalho estuda o problema integrado de atribuição de professores, horários
e salas de aula no Instituto de Computação da UFF. O problema é tratado como
uma variante do *Curriculum-Based Course Timetabling* (CB-CTT), ampliada pela
atribuição de professores, pelo horizonte anual e pelas regras específicas do
IC/UFF.

O objetivo geral registrado atualmente é:

> Modelar o problema integrado de atribuição de professores, horários e salas
> de aula no IC/UFF e investigar o uso de metaheurísticas por meio do
> pyoptframe para a geração e a avaliação de soluções.

O projeto já possui:

- pipeline de coleta e auditoria dos quadros de 2023/1 a 2026/2;
- grades curriculares de Ciência da Computação (CC) e Sistemas de Informação
  (SI), incluindo o mapeamento de disciplinas compartilhadas;
- formalização matemática com professor, padrão de horário e sala por
  encontro como decisões;
- avaliadores independentes e conferidos entre si;
- movimentos integrados de professor, horário e sala;
- implementações de referência de solução gulosa, SA, ILS e VNS;
- executor com múltiplas sementes e relatório automático;
- benchmark sintético baseado na estrutura real de 2026;
- 66 testes automatizados aprovados;
- ambiente com `optframe==5.1.0` instalado e importado.

O melhor resultado preliminar reduziu as violações hard de 27 para 10. Foram
eliminados os conflitos de sala e as violações H12 sem criar conflitos de
professor, capacidade, recursos ou descanso. As dez violações restantes são
conflitos curriculares associados a horários obrigatórios mantidos fixos no
perfil atual.

Esses resultados são **técnicos e não oficiais**. A estrutura da instância é
real, mas capacidades, recursos, habilitações, prioridades, horários flexíveis
e universo H12 ainda usam proxies documentadas.

## 2. Pontos prioritários para validação do orientador

As decisões abaixo são necessárias para transformar o benchmark em experimento
final e fechar os capítulos de modelagem e experimentos.

### 2.1 Escopo e título

- [ ] Confirmar que o escopo final contém as três decisões: professor,
  horário e sala.
- [ ] Confirmar que o planejamento deve permanecer anual, ligando os semestres
  por H12 e rodízio.
- [ ] Confirmar a manutenção conjunta das grades de CC e SI.
- [ ] Confirmar que o critério de distância entre salas permanece fora do
  escopo.
- [ ] Decidir se o título deve mencionar explicitamente a atribuição de
  professores.

O título atual do documento é:

> Metaheurísticas Aplicadas à Alocação de Horários e Salas de Aula no
> Instituto de Computação da UFF

Como a atribuição de professores é uma variável central, uma alternativa de
consistência textual seria:

> Metaheurísticas Aplicadas à Atribuição de Professores e à Alocação de
> Horários e Salas no Instituto de Computação da UFF

Essa alteração é apenas uma opção editorial e precisa de aprovação.

### 2.2 Restrições e função objetivo

- [ ] Confirmar a classificação final hard × soft de H8, H10 e H11.
- [ ] Confirmar H12 como hard no experimento oficial.
- [ ] Definir o universo institucional de docentes sujeitos a H12.
- [ ] Confirmar a unidade de contagem de H12 e o tratamento de cotutoria.
- [ ] Confirmar o descanso mínimo entre jornadas e sua fonte institucional.
- [ ] Definir os pesos ou a ordem de prioridade dos critérios soft.
- [ ] Confirmar se turma comum pode ocupar laboratório quando ele estiver
  livre, ou se isso deve ser proibido/penalizado.

### 2.3 Horários e setores

- [ ] Validar a tabela oficial de setores, habilitações e dias por setor.
- [ ] Definir quais obrigatórias possuem horário realmente fixo.
- [ ] Definir quais optativas ou disciplinas de serviço podem mudar de
  horário.
- [ ] Avaliar a flexibilização seletiva das turmas envolvidas nos conflitos
  curriculares observados.

Os conflitos curriculares restantes estão concentrados principalmente em:

- `TCC00332 × TCC00354`, em 2026/1;
- `TCC00332 × TCC00354`, em 2026/2;
- `TCC00336 × TCC00338`, em 2026/1.

Uma análise de cobertura indica que liberar aproximadamente cinco ofertas —
quatro de `TCC00332` e uma de `TCC00336` — permitiria testar a eliminação dos
dez conflitos contabilizados sem liberar todas as 150 obrigatórias. Essa é uma
hipótese para teste de sensibilidade, não uma decisão de modelagem já tomada.

### 2.4 Dados institucionais

- [ ] Validar capacidades e recursos oficiais das 22 salas.
- [ ] Validar requisitos de laboratório por disciplina/encontro.
- [ ] Validar habilitações dos professores.
- [ ] Definir a prioridade real dos professores.
- [ ] Classificar as ofertas pendentes de `TCC00368` e `TCC00371`.
- [ ] Definir o tratamento das ofertas externas e seções alternativas.
- [ ] Confirmar os 19 vínculos não triviais entre PDF e sistema público.

### 2.5 Protocolo experimental

- [ ] Confirmar quais metaheurísticas integrarão a comparação final.
- [ ] Definir número de execuções, orçamento ou limite de tempo.
- [ ] Definir procedimento de calibração dos parâmetros.
- [ ] Confirmar a execução dos cenários E1, E2 e E3 para CC e SI.
- [ ] Confirmar as métricas estatísticas e gráficos esperados.

## 3. Problema estudado

O problema envolve três perspectivas institucionais:

| Papel | Interesse principal |
|---|---|
| Chefia/departamento | Distribuição de encargos, professores e turmas |
| Coordenação | Ausência de choques para os alunos e oferta de vagas |
| Instituto | Uso das salas, capacidades e recursos |

Cada turma do IC pode exigir três decisões:

1. professor responsável;
2. padrão de encontros semanais;
3. sala de cada encontro.

O planejamento é anual porque a carga mínima H12 e o rodízio relacionam os
dois semestres. Conflitos de professor, sala e currículo continuam separados
por semestre.

O trabalho considera simultaneamente CC e SI. Professores e salas são recursos
compartilhados. Uma disciplina presente nas duas grades pode corresponder a
uma única turma física, pertencente a grupos curriculares dos dois cursos.

## 4. Modelagem matemática atual

### 4.1 Decisões

- `x`: atribuição de professor à turma;
- `y`: atribuição de padrão de horário à turma;
- `z`: atribuição de sala por encontro.

### 4.2 Restrições hard modeladas

| Código | Restrição | Situação na implementação |
|---|---|---|
| H1 | Professor único/habilitado | Imposta pelos domínios; validação estrutural ainda pode ser ampliada |
| H2 | Padrão de horário único | Imposta pela representação e pelos movimentos |
| H3 | Sala por encontro | Imposta pela representação; falta contador estrutural completo para campos ausentes |
| H4 | Horário fixo | Respeitado pelos movimentos |
| H4b | Professor fixo externo | Respeitado pelo perfil atual |
| H5 | Dias do setor | Representado nos domínios sintéticos; dado oficial pendente |
| H6 | Sem conflito de professor | Implementado e testado |
| H7 | Sem conflito de sala | Implementado e testado |
| H8 | Sem conflito curricular | Implementado e testado |
| H9 | Compatibilidade de recursos | Implementado para laboratório |
| H10 | Capacidade da sala | Implementado com capacidade proxy |
| H11 | Descanso entre jornadas | Implementado e corrigido para dias não consecutivos |
| H12 | Mínimo anual de obrigatórias | Implementado com universo e cotutoria configuráveis |

### 4.3 Critérios soft

| Código | Critério |
|---|---|
| O1 | Preferência por disciplina ponderada pela prioridade |
| O2 | Número de dias trabalhados |
| O3 | Janelas entre aulas |
| O4 | Desperdício de capacidade da sala |
| O5 | Rodízio de professores entre semestres |

Os pesos usados no benchmark são unitários e provisórios. As violações hard
recebem prioridade sobre os critérios soft. Para melhorar a orientação da
busca, H12 possui ainda uma métrica interna de déficit: quantas obrigatórias
faltam, no total, para todos os docentes atingirem três. Essa métrica não muda
a definição oficial de H12; ela apenas diferencia estados intermediários.

## 5. Dados disponíveis

### 5.1 Histórico 2023–2025

- 913 registros de turma/docente coletados do sistema público;
- seis semestres, de 2023/1 a 2025/2;
- matriz histórica professor × disciplina usada como proxy de preferência;
- quadro de 2025 usado para setores, padrões de horário e domínios provisórios.

### 5.2 Instância observada de 2026

| Indicador | Quantidade |
|---|---:|
| Turmas físicas CC/SI | 180 |
| Encontros semanais | 329 |
| Docentes observados | 61 |
| Salas observadas | 22 |
| Turmas obrigatórias no perfil sintético | 150 |
| Turmas com professor móvel | 146 |
| Turmas com horário flexível | 27 |

A pipeline preserva a origem dos dados, os vínculos PDF × sistema público, as
vagas por curso e a participação das turmas em grupos curriculares de CC e SI.

### 5.3 Pendências oficiais

O verificador do perfil baseline informa atualmente 366 mensagens de
pendência. Esse número inclui mais de uma mensagem para uma mesma entidade,
por exemplo campo vazio e falta de validação; não representa 366 decisões
independentes.

As pendências estão organizadas em 12 grupos:

1. classificação de `TCC00368`;
2. classificação de `TCC00371`;
3. universo H12;
4. política de cotutoria;
5. cadastro físico de salas;
6. recursos por disciplina;
7. horários fixos;
8. setores e padrões semanais;
9. habilitação docente;
10. prioridades docentes;
11. disciplinas externas e seções alternativas;
12. auditoria de vínculos não triviais.

## 6. Pipeline e reprodutibilidade

O fluxo offline atual é:

```text
PDFs e coleta web
→ extração e normalização
→ grades CC/SI
→ vínculo PDF × web
→ instância observada
→ auditorias
→ verificação das revisões
→ instância sintética
→ experimentos
→ relatório
```

Foram adicionadas proteções para os dados de revisão:

- a pipeline normal não apaga decisões humanas;
- conjunto parcial de arquivos bloqueia a execução;
- perfis parciais não liberam globalmente a instância oficial;
- um manifesto registra os hashes das fontes das revisões;
- mudanças nas fontes invalidam revisões antigas sem sobrescrevê-las.

Comandos atuais:

```bash
source .venv/bin/activate
python scripts/run_pipeline_2026.py --offline
python scripts/build_synthetic_instance_2026.py
python scripts/run_synthetic_experiments_2026.py
```

## 7. Implementação do solver

O núcleo integrado contém:

- atribuição corrente separada da alocação observada;
- avaliador direto, usado durante a busca;
- avaliador de referência em pandas, usado para conferência;
- movimentos reversíveis de professor, horário e sala;
- solução inicial e melhoria gulosa;
- SA, ILS e VNS usando o mesmo avaliador e os mesmos domínios;
- execução com múltiplas sementes;
- CSV detalhado e relatório Markdown automático.

O OptFrame 5.1.0 está instalado e o import foi validado. As buscas usadas no
relatório atual são implementações de referência em Python. A integração do
mesmo núcleo ao motor nativo do pyoptframe ainda precisa ser concluída para
atender literalmente ao objetivo geral atual.

## 8. Benchmark sintético

### 8.1 Motivo

A instância oficial ainda não está completa. Para não bloquear o
desenvolvimento, foi criado um perfil que mantém a estrutura real de 2026 e
completa os parâmetros ausentes por regras determinísticas e documentadas.

### 8.2 Proxies utilizadas

| Parâmetro | Proxy |
|---|---|
| Capacidade da sala | Maior demanda observada em 2025/2026 |
| Laboratório | Prefixo `L` |
| Recursos | Uso histórico por encontro |
| Preferência | Frequência histórica normalizada |
| Prioridade | `1.0` para todos |
| Setor | Setor histórico único de 2025 |
| Habilitação | Professores históricos do setor |
| Horários | Obrigatórias fixas; optativas em padrões históricos |
| Cotutoria | Crédito H12 fracionado |
| Universo H12 | 40 docentes selecionados com matching conjunto viável |

O matching H12 confirmou cobertura de `118/118` créditos necessários.

### 8.3 Configuração experimental preliminar

- cinco sementes: `101`, `202`, `303`, `404` e `505`;
- orçamento de 1.500 avaliações por algoritmo e semente;
- mesma instância e solução gulosa inicial;
- avaliadores conferidos em todas as soluções registradas;
- pesos soft unitários e provisórios.

## 9. Resultados preliminares

### 9.1 Viabilidade

| Método | Hard total | Docentes abaixo de H12 | Déficit H12 |
|---|---:|---:|---:|
| Baseline observado | 27 | 14 | 14 |
| Guloso integrado | 12 | 2 | 2 |
| Melhor SA | 10 | 0 | 0 |
| Melhor ILS | 11 | 1 | 1 |
| Melhor VNS | 11 | 1 | 1 |

O SA zerou H12 em três das cinco sementes sem criar conflitos de professor.

### 9.2 Melhor solução

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

As violações hard caíram 62,96%. As dez restantes são curriculares e estão
congeladas porque o perfil mantém as obrigatórias em seus horários observados.

### 9.3 Aplicabilidade prática

#### Guloso

Produz rapidamente uma grade inicial melhor e foi responsável pela maior parte
da redução inicial.

#### Simulated Annealing

Foi mais eficaz para viabilidade. Na prática, pode reduzir o trabalho manual de
redistribuir disciplinas para professores abaixo de H12 e de corrigir salas.
O custo observado foi o aumento das janelas em algumas soluções.

#### ILS

Produziu soluções próximas da viabilidade completa, preservando melhor janelas
e desperdício. Pode ser útil para refinar uma grade que já está quase pronta.

#### VNS

Alterna sistematicamente professor, horário e sala. Pode ser útil para procurar
soluções equilibradas e evitar insistir em apenas um tipo de ajuste.

Uma sequência prática ainda não testada como protocolo final seria:

```text
guloso → SA para viabilidade → ILS/VNS para refinamento soft
```

## 10. Interpretação e limites dos resultados

Os resultados permitem concluir tecnicamente que:

1. a pipeline experimental funciona de ponta a ponta;
2. os movimentos integrados conseguem melhorar o quadro observado;
3. a solução gulosa tem papel importante;
4. a métrica de déficit ajuda a busca a atender H12;
5. SA, ILS e VNS apresentam comportamentos complementares;
6. os conflitos curriculares exigem flexibilização seletiva de horários para
   serem tratados.

Os resultados ainda não permitem concluir que:

- um algoritmo é estatisticamente superior;
- os parâmetros sintéticos representam as regras oficiais do IC;
- a solução encontrada deve ser adotada institucionalmente;
- o protocolo atual é o protocolo final da monografia.

## 11. Estado da documentação acadêmica

### 11.1 Introdução

Já contém contexto, stakeholders, objetivo geral, objetivos específicos e
organização do texto. Precisa de fontes institucionais e validação do título e
do escopo.

### 11.2 Fundamentação

Já apresenta UCTP, CB-CTT, SA, ILS, VNS, OptFrame e pyoptframe. A bibliografia
canônica possui 13 referências citadas. Ainda falta ampliar trabalhos
relacionados, principalmente aplicações comparáveis e trabalhos brasileiros.

### 11.3 Modelagem

É a seção mais madura. Contém conjuntos, parâmetros, variáveis, H1–H12 e
O1–O5. Ainda precisa de validação de hard × soft, pesos, H12, setores,
capacidades e recursos.

### 11.4 Implementação

O texto existente descreve a versão inicial dos solvers. Precisa ser atualizado
com o gerador sintético, o núcleo integrado, o matching H12, o déficit H12,
SA/ILS/VNS e o executor multi-seed.

### 11.5 Experimentos

O capítulo atual ainda apresenta principalmente o planejamento e a validação
de 2025. O benchmark de 2026 pode entrar como **validação preliminar da
implementação**, claramente separado do experimento oficial.

### 11.6 Conclusão e artigo

A conclusão substantiva ainda não foi escrita. O artigo ainda não foi
produzido. Ambos dependem dos experimentos oficiais e da interpretação final.

## 12. O que já pode ser escrito

As seguintes partes podem avançar imediatamente, sujeitas à revisão do aluno:

1. contexto e delimitação do problema;
2. descrição dos stakeholders;
3. fundamentação de UCTP/CB-CTT e metaheurísticas;
4. metodologia de coleta e auditoria dos dados;
5. representação da instância e da solução;
6. arquitetura dos avaliadores e movimentos;
7. descrição técnica de SA, ILS e VNS;
8. metodologia do benchmark sintético;
9. validação de software e resultados preliminares;
10. limitações das proxies e ameaças à validade.

As seguintes partes devem aguardar validação:

1. formulação final de hard × soft;
2. pesos definitivos;
3. definição institucional de H12;
4. instância oficial;
5. protocolo experimental final;
6. comparação estatística final;
7. discussão substantiva e conclusão.

## 13. É possível rodar uma instância real agora?

### Resposta objetiva

**É possível rodar uma instância estruturalmente real e obter resultados
reproduzíveis. Ainda não é possível chamar essa execução de experimento
institucional oficial.**

Já são reais:

- turmas e encontros de 2026;
- professores observados;
- horários observados;
- salas observadas;
- vagas por curso;
- grupos curriculares de CC e SI;
- turmas compartilhadas.

Ainda são sintéticos ou pendentes:

- capacidade física das salas;
- recursos oficiais;
- setores e dias oficiais;
- habilitações;
- prioridades;
- universo H12;
- política de cotutoria;
- horários fixos/flexíveis;
- pesos da função objetivo.

Também falta implementar a aplicação automática das revisões oficiais ao JSON
definitivo. Hoje a pipeline protege e verifica as revisões, mas ainda não
materializa todos os campos validados na instância final.

## 14. Plano sugerido após a orientação

1. Registrar as respostas do orientador nos CSVs e na modelagem.
2. Implementar a aplicação das revisões ao JSON oficial.
3. Atualizar o capítulo de modelagem com as decisões confirmadas.
4. Atualizar o capítulo de implementação com o núcleo atual.
5. Integrar os componentes ao motor nativo do pyoptframe.
6. Executar um teste oficial pequeno para validar os dados.
7. Fechar protocolo e parâmetros.
8. Rodar todas as sementes e cenários finais.
9. Gerar tabelas, gráficos e análise estatística.
10. Escrever resultados, discussão, conclusão e versão em artigo.

## 15. Arquivos para consulta na orientação

| Assunto | Arquivo |
|---|---|
| Plano e cronograma | `PLANO.md` |
| Diretrizes do orientador | `anotacoes/orientacao.md` |
| Modelo matemático detalhado | `anotacoes/modelo_matematico.md` |
| Literatura | `anotacoes/literatura.md` |
| Pendências de dados | `dados/PENDENCIAS.md` |
| Pendências operacionais 2026 | `dados/processados/PENDENCIAS_VALIDACAO_2026.md` |
| Registro técnico do benchmark | `anotacoes/registro_implementacao_benchmark_sintetico_2026.md` |
| Configuração sintética | `dados/config_sintetica_2026_v1.json` |
| Relatório de resultados | `dados/processados/relatorio_experimento_sintetico_2026.md` |
| Resultados por execução | `dados/processados/resultados_experimento_sintetico_2026.csv` |
| Fonte da monografia | `documento/main.tex` |

## 16. Síntese para a reunião

O projeto deixou de ser apenas uma proposta de modelagem e passou a possuir um
protótipo integrado, reproduzível e testado na escala observada de 2026. O
principal bloqueio para o experimento final não é mais a execução do solver,
mas a validação dos parâmetros institucionais e sua incorporação à instância
oficial.

As decisões mais urgentes são:

1. confirmar escopo e título;
2. fechar H12 e cotutoria;
3. validar setores, habilitações e horários fixos;
4. validar salas e recursos;
5. definir hard × soft e pesos;
6. confirmar o protocolo experimental e os cenários CC/SI.

Com essas respostas, a implementação atual pode ser reaproveitada para gerar a
instância oficial, repetir os experimentos e iniciar a redação dos capítulos
de resultados e conclusão.
