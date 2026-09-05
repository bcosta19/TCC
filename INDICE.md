# Índice do projeto

Guia de navegação do TCC sobre alocação de professores, horários e salas no
IC/UFF. Organizado por finalidade, com foco no trabalho de 2026.

**Como ler os arquivos:** dados observados descrevem o que foi coletado;
tabelas de revisão guardam decisões humanas; perfis sintéticos usam hipóteses
provisórias; relatórios de execução registram resultados de uma configuração
específica. Um resultado sintético não libera a instância institucional.

## Comece pelo seu objetivo

| Quero… | Onde começar |
|---|---|
| Entender o projeto e preparar o ambiente | [README](README.md) |
| Ver o planejamento e o que falta | [Plano](PLANO.md) e [pendências de dados](dados/PENDENCIAS.md) |
| Relembrar as diretrizes do orientador | [Orientação](anotacoes/orientacao.md) |
| Consultar restrições e função objetivo | [Modelo matemático](anotacoes/modelo_matematico.md) |
| Ver o protótipo validado e seus limites | [Validação de 04/09/2026](anotacoes/validacao_prototipo_2026_09_04.md) |
| Entender a discussão das turmas alternativas em H8 | [Investigação da opção 2](anotacoes/investigacao_h8_opcao2_2026_09_05.md) |
| Preencher ou conferir dados institucionais | [Tabelas de revisão](#tabelas-de-revisão-humana) |
| Consultar números dos experimentos | [Resultados e diagnósticos](#resultados-e-diagnósticos) |
| Trabalhar na monografia | [Texto e referências](#texto-e-referências) |
| Encontrar o código ou executar uma etapa | [Implementação e executores](#implementação-e-executores) |

## Mapa das pastas

| Pasta | Conteúdo |
|---|---|
| [anotacoes/](anotacoes/) | Orientações, modelagem, revisões e análises técnicas |
| [dados/brutos/](dados/brutos/) | Fontes como recebidas: PDFs, planilhas e outros insumos |
| [dados/processados/](dados/processados/) | Tabelas normalizadas, revisões, instâncias e relatórios; detalhamento abaixo |
| [webscrap/](webscrap/) | Coleta do quadro de horários, histórico e saídas da coleta |
| [src/model/](src/model/) | Leitura e classificação dos currículos |
| [src/eval/](src/eval/) | Avaliação, leitura de instância, recursos e checagem de trajetórias |
| [src/solve/](src/solve/) | Busca integrada, adaptador pyoptframe e validação das soluções |
| [scripts/](scripts/) | Comandos de coleta, construção, auditoria e experimentos |
| [tests/](tests/) | Testes automatizados |
| [prototipos/](prototipos/) | Exemplos de estudo: mochila e alocação de salas toy |
| [documento/](documento/) | Fonte LaTeX do texto do TCC |
| [modelo_artigo/](modelo_artigo/) | Pacote original do modelo LaTeX |
| [referencias/](referencias/) | Bibliografia e orientações para obter os materiais |

`optframe/` e `pyoptframe-dev/`, quando presentes, são clones locais de terceiros.
Não fazem parte do código autoral a editar. Arquivos de sessão e credenciais
não são necessários para navegar pelos resultados.

## Planejamento e modelagem

| Arquivo | Uso |
|---|---|
| [PLANO.md](PLANO.md) | Fases, cronograma original, riscos e atualizações técnicas datadas |
| [AGENTS.md](AGENTS.md) | Convenções de trabalho e política de colaboração com agentes |
| [orientacao.md](anotacoes/orientacao.md) | Diretrizes registradas, incluindo horizonte anual e retirada da distância |
| [modelo_matematico.md](anotacoes/modelo_matematico.md) | Formulação detalhada, H1–H12 e critérios soft |
| [modelo_matematico_orientador.md](anotacoes/modelo_matematico_orientador.md) | Apresentação do modelo voltada à discussão com o orientador |
| [revisao_modelo.md](anotacoes/revisao_modelo.md) | Notas de revisão da modelagem |
| [plano_mudanca_modelagem_cc_si.md](anotacoes/plano_mudanca_modelagem_cc_si.md) | Registro do planejamento da ampliação para CC/SI |
| [relatorio_geral_para_orientacao.md](anotacoes/relatorio_geral_para_orientacao.md) | Retrato de 23/08, com indicação das atualizações posteriores |

As formulações e hipóteses em discussão não devem ser confundidas com decisões
confirmadas. Para o estado técnico recente, consulte também os relatórios datados.

## Dados de entrada e tabelas de 2026

Visão geral: [dados/PENDENCIAS.md](dados/PENDENCIAS.md).
Detalhamento das saídas: [README dos dados processados](dados/processados/README.md),
que também contém histórico de 2025.

| Assunto | Arquivos | Como interpretar |
|---|---|---|
| Grades curriculares | [CC](dados/grade_cc.md), [SI](dados/grade_si.md) | Disciplinas e períodos, com fontes indicadas |
| Currículos normalizados | [curriculos_cc_si.csv](dados/processados/curriculos_cc_si.csv), [intersecao_curriculos_cc_si.csv](dados/processados/intersecao_curriculos_cc_si.csv) | Vínculos por curso e interseção por código |
| Coleta pública de 2026 | [turmas_2026_raw.csv](webscrap/turmas_2026_raw.csv) | Ofertas, horários, vagas e inscritos por curso |
| Extração geral dos PDFs | [turmas_2026.csv](dados/processados/turmas_2026.csv), [horarios_2026.csv](dados/processados/horarios_2026.csv), [salas_2026.csv](dados/processados/salas_2026.csv) | Quadro integral; não é apenas o recorte CC/SI |
| Recorte do solver | [turmas_2026_cc_si.csv](dados/processados/turmas_2026_cc_si.csv), [horarios_2026_cc_si.csv](dados/processados/horarios_2026_cc_si.csv), [salas_2026_cc_si.csv](dados/processados/salas_2026_cc_si.csv) | Turmas vinculadas ao recorte CC/SI |
| Vínculo PDF × web | [vagas_turmas_2026.csv](dados/processados/vagas_turmas_2026.csv) | Correspondências e dados das páginas de oferta |
| Ofertas fora do PDF | [turmas_web_sem_qh_2026.csv](dados/processados/turmas_web_sem_qh_2026.csv) | Ofertas coletadas sem vínculo com o quadro do IC |
| Classificação por currículo | [classificacao_curricular_2026.csv](dados/processados/classificacao_curricular_2026.csv) | Classificação a partir das grades |
| Classificação histórica provisória | [classificacao_curricular_proxy_2026.csv](dados/processados/classificacao_curricular_proxy_2026.csv) | Evidência de 2025; não equivale à classificação definitiva |
| Recursos observados | [recursos_turmas_2026.csv](dados/processados/recursos_turmas_2026.csv), [recursos_encontros_2026.csv](dados/processados/recursos_encontros_2026.csv) | Uso observado de salas/laboratórios; não é automaticamente requisito |
| Qualidade da extração | [normalizacao_docentes_2026.csv](dados/processados/normalizacao_docentes_2026.csv), [revisao_turmas_2026.csv](dados/processados/revisao_turmas_2026.csv) | Normalização e pendências dos registros extraídos |

### Tabelas de revisão humana

Ponto de entrada: [PENDENCIAS_VALIDACAO_2026.md](dados/processados/PENDENCIAS_VALIDACAO_2026.md).
Estas tabelas têm campos de decisão/validação; sua existência não significa que
já estejam preenchidas ou aprovadas. Preserve as decisões existentes.

| Decisão | Tabela |
|---|---|
| Classificação curricular pendente | [revisao_classificacao_curricular_2026.csv](dados/processados/revisao_classificacao_curricular_2026.csv) |
| Docentes abrangidos por H12 | [universo_h12_2026.csv](dados/processados/universo_h12_2026.csv) |
| Contagem de cotutoria | [politica_cotutoria_2026.csv](dados/processados/politica_cotutoria_2026.csv) |
| Capacidade e cadastro físico de salas | [cadastro_salas_2026.csv](dados/processados/cadastro_salas_2026.csv) |
| Recursos exigidos pelas disciplinas | [revisao_recursos_disciplinas_2026.csv](dados/processados/revisao_recursos_disciplinas_2026.csv) |
| Horários fixos ou flexíveis | [revisao_horarios_fixos_2026.csv](dados/processados/revisao_horarios_fixos_2026.csv) |
| Setores e dias autorizados | [revisao_setores_2026.csv](dados/processados/revisao_setores_2026.csv) |
| Habilitação docente por disciplina | [revisao_habilitacao_docente_2026.csv](dados/processados/revisao_habilitacao_docente_2026.csv) |
| Prioridade dos docentes | [revisao_prioridades_docentes_2026.csv](dados/processados/revisao_prioridades_docentes_2026.csv) |
| Tratamento das ofertas externas | [revisao_turmas_externas_2026.csv](dados/processados/revisao_turmas_externas_2026.csv) |
| Correspondências PDF × web e divergências | [revisao_vinculos_2026.csv](dados/processados/revisao_vinculos_2026.csv) |

[revisoes_2026_manifest.json](dados/processados/revisoes_2026_manifest.json)
registra os hashes das fontes das revisões; é controle de rastreabilidade,
não uma tabela para preencher decisões.

### Instâncias e configurações

| Arquivo | Papel |
|---|---|
| [config_sintetica_2026_v1.json](dados/config_sintetica_2026_v1.json) | Hipóteses e parâmetros do benchmark sintético |
| `dados/processados/instancia_2026_ic_observada.json` | Instância geral observada, gerada pela pipeline |
| `dados/processados/instancia_2026_cc_si.json` | Instância do recorte CC/SI, com controles de prontidão |
| `dados/processados/instancia_sintetica_2026_v1.json` | Perfil do recorte completado por proxies para testes |
| `solucao_*.json` nas pastas de execução | Atribuições retornadas pelas buscas e seus metadados |

Instâncias e soluções recriáveis são ignoradas pelo Git e podem não existir
em outro checkout. Gere-as pelos executores indicados abaixo. Capacidade mínima
observada e capacidade sintética não são capacidade física oficial.

## Resultados e diagnósticos

| Conjunto | Leitura inicial | Tabelas e detalhes |
|---|---|---|
| Auditoria geral de 2026 | [auditoria_2026.md](dados/processados/auditoria_2026.md) | [Conflitos candidatos gerais](dados/processados/conflitos_candidatos_2026.csv) |
| Auditoria do recorte CC/SI | [auditoria_2026_cc_si.md](dados/processados/auditoria_2026_cc_si.md) | [Conflitos candidatos CC/SI](dados/processados/conflitos_candidatos_2026_cc_si.csv) |
| Benchmark sintético de referência, SA/ILS/VNS | [Relatório](dados/processados/relatorio_experimento_sintetico_2026.md) | [CSV das execuções](dados/processados/resultados_experimento_sintetico_2026.csv); [registro técnico](anotacoes/registro_implementacao_benchmark_sintetico_2026.md) |
| Piloto SA nativo de 04/09 | [Relatório](dados/processados/piloto_optframe_20260904_final/relatorio.md) | [CSV](dados/processados/piloto_optframe_20260904_final/resultados.csv); [manifesto](dados/processados/piloto_optframe_20260904_final/manifesto.json) |
| Revisão técnica e próximos passos de 04/09 | [Validação do protótipo](anotacoes/validacao_prototipo_2026_09_04.md) | Correções, testes, limites e interpretação dos resultados |
| Dez sobreposições curriculares | [Diagnóstico](dados/processados/diagnostico_curricular_2026/relatorio.md) | [Conflitos](dados/processados/diagnostico_curricular_2026/conflitos.csv); [escolhas](dados/processados/diagnostico_curricular_2026/escolhas_por_grupo.csv); [fontes](dados/processados/diagnostico_curricular_2026/fontes.csv) |
| Investigação inicial da opção 2 de H8 | [Análise de 05/09](anotacoes/investigacao_h8_opcao2_2026_09_05.md) | [Artefatos exploratórios](dados/processados/investigacao_h8_opcao2_2026/) |
| Checagem implementada de H8, apenas recorte | [Relatório](dados/processados/h8_trajetorias_2026/recorte/relatorio.md) | [JSON com estados, pendências e trajetórias](dados/processados/h8_trajetorias_2026/recorte/resultado.json) |
| Checagem implementada de H8, com complemento local | [Relatório](dados/processados/h8_trajetorias_2026/ampliado/relatorio.md) | [JSON com estados, pendências e trajetórias](dados/processados/h8_trajetorias_2026/ampliado/resultado.json) |

**Diferença entre os diagnósticos de H8:** `diagnostico_curricular_2026/`
explica as sobreposições do contador atual; `investigacao_h8_opcao2_2026/`
guarda a exploração inicial; `h8_trajetorias_2026/` contém a checagem paralela
implementada, que verifica cobertura da grade e distingue dados incompletos.
Ela ainda não substitui H8 no score do solver.

## Implementação e executores

| Tarefa | Entrada no código |
|---|---|
| Rodar a pipeline de 2026 | [run_pipeline_2026.py](scripts/run_pipeline_2026.py) |
| Conferir prontidão institucional | [check_readiness_2026.py](scripts/check_readiness_2026.py) |
| Gerar o perfil sintético | [build_synthetic_instance_2026.py](scripts/build_synthetic_instance_2026.py) |
| Executar SA/ILS/VNS de referência | [run_synthetic_experiments_2026.py](scripts/run_synthetic_experiments_2026.py) |
| Executar o piloto SA nativo | [benchmark_optframe_sa_2026.py](scripts/benchmark_optframe_sa_2026.py) |
| Explicar as sobreposições curriculares | [diagnose_curriculum_conflicts_2026.py](scripts/diagnose_curriculum_conflicts_2026.py) |
| Executar a checagem paralela de trajetórias | [check_h8_trajectories_2026.py](scripts/check_h8_trajectories_2026.py) |
| Ler/classificar currículos | [curricula.py](src/model/curricula.py) |
| Avaliação de referência e leitura de JSON | [evaluator.py](src/eval/evaluator.py), [instance_io.py](src/eval/instance_io.py) |
| Avaliação usada durante a busca | [direct_objective.py](src/solve/direct_objective.py) |
| Construtivo, movimentos e buscas integradas | [integrated.py](src/solve/integrated.py) |
| Ponte para o BasicSA do OptFrame | [optframe_adapter.py](src/solve/optframe_adapter.py) |
| Integridade estrutural das soluções | [validation.py](src/solve/validation.py) |
| Lógica de H8 por trajetória | [trajectories.py](src/eval/trajectories.py) |
| Testes | [tests/](tests/), em particular [test_trajectories.py](tests/test_trajectories.py) |

Os comandos completos, dependências e opções de execução ficam no
[README](README.md). O gerador `build_review_tables_2026.py` cria tabelas de
revisão; para o uso normal, prefira a pipeline que preserva revisões existentes.

## Texto e referências

| Arquivo/pasta | Conteúdo |
|---|---|
| [documento/README.md](documento/README.md) | Compilação e organização das fontes |
| [documento/main.tex](documento/main.tex) | Arquivo principal do texto |
| [documento/secoes/](documento/secoes/) | Introdução, fundamentação, modelagem, solução, experimentos e conclusão |
| [modelo_artigo/](modelo_artigo/) | Modelo LaTeX original, separado do texto em desenvolvimento |
| [anotacoes/literatura.md](anotacoes/literatura.md) | Notas da revisão bibliográfica |
| [referencias/referencias.bib](referencias/referencias.bib) | Bibliografia canônica usada pelo texto |
| [referencias/README.md](referencias/README.md) | Organização e obtenção dos materiais bibliográficos |

## Histórico de 2025 e protótipos

Os arquivos `*_2025.*` em [dados/processados/](dados/processados/) e os
executores `*_2025.py` em [scripts/](scripts/) preservam as etapas anteriores.
São úteis para rastrear hipóteses e reproduzir testes antigos; seus números e
pendências não representam automaticamente a situação de 2026.

Pontos de entrada: [auditoria de 2025](dados/processados/auditoria_2025_cc_si.md),
[decisões de qualidade](dados/processados/decisoes_qualidade_2025.md),
[experimento não oficial](dados/processados/relatorio_experimento_nao_oficial_2025.md)
e [domínios de horários flexíveis](dados/processados/README_horarios_flexiveis.md).
Os [protótipos de estudo](prototipos/) são exemplos separados do solver integrado.

---

Atualizado em **05/09/2026**. Ao acrescentar uma nova família de tabelas ou um
relatório que substitua o ponto de entrada anterior, atualize a seção correspondente.
