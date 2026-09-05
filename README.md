# TCC — Alocação de professores, horários e salas no IC/UFF

Trabalho de Conclusão de Curso em Ciência da Computação na Universidade
Federal Fluminense sobre metaheurísticas aplicadas ao problema integrado de
atribuição de professores, horários e salas de aula.

O problema é modelado como uma variante de *Curriculum-Based Course
Timetabling* para as grades de Ciência da Computação (CC) e Sistemas de
Informação (SI). O critério de distância entre salas não faz parte do escopo
atual.

## Estado atual

- A modelagem matemática está em revisão, com restrições e pesos ainda
  dependentes de validação do orientador.
- A pipeline de 2026 extrai e audita os quadros de 2026/1 e 2026/2 e integra
  as grades de CC e SI.
- O recorte observado de 2026 contém 180 turmas físicas, 329 encontros, 61
  docentes observados e 22 salas.
- A instância de 2026 ainda não está liberada para experimentos: capacidades,
  recursos, setores, habilitações e o universo da regra H12 precisam de
  validação humana.
- Há busca integrada de professores, horários e salas, com guloso, SA, ILS e
  VNS de referência em Python, além do adaptador BasicSA nativo do
  [pyoptframe](https://github.com/optframe/pyoptframe-dev).
- O piloto nativo usa o perfil sintético de 2026 e confere as soluções com
  dois avaliadores e uma validação estrutural. O protocolo experimental final
  e o controle da semente interna do motor nativo permanecem pendentes.
- Os dez choques curriculares do perfil fixo envolvem turmas alternativas.
  Há escolhas sem choque por grupo no recorte; isso não comprova atendimento
  de todos os alunos nem elimina as violações segundo a regra H8 atual.

Veja o [plano de execução](PLANO.md), as
[diretrizes do orientador](anotacoes/orientacao.md) e as
[pendências de dados](dados/PENDENCIAS.md).

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `documento/` | Fonte LaTeX da monografia e capítulos |
| `src/` | Modelo, avaliadores e solvers |
| `scripts/` | Extração, construção, auditoria e experimentos |
| `tests/` | Testes automatizados do pipeline e dos avaliadores |
| `dados/brutos/` | Fontes institucionais preservadas como recebidas |
| `dados/processados/` | Tabelas normalizadas, revisões humanas e relatórios |
| `webscrap/` | Coleta do Quadro de Horários e preferências históricas |
| `prototipos/` | Exemplos de estudo isolados do OptFrame |
| `anotacoes/` | Modelagem, literatura e registros de orientação |
| `referencias/` | Bibliografia e instruções para fontes locais |
| `modelo_artigo/` | Pacote original do modelo oficial do curso |

Os CSVs em `dados/processados/` são preservados quando constituem entradas,
evidências de auditoria ou tabelas que exigem validação humana. Instâncias e
soluções JSON recriáveis são ignoradas pelo Git.

## Ambiente de desenvolvimento

O projeto usa Python 3.10. A partir da raiz:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Python 3.10 é a versão prevista nas convenções. A validação local de
04/09/2026 utilizou Python 3.14.7 e OptFrame 5.1.0; compatibilidade com 3.10
não foi verificada nessa rodada.

O Playwright é necessário somente para abrir o login interativo do idUFF.
Quando esse fluxo for usado, instale também o navegador local:

```bash
playwright install chromium
```

Os protótipos em `prototipos/` dependem adicionalmente de uma instalação
compatível do pyoptframe. Os repositórios de terceiros não são incorporados a
este repositório.

## Pipeline de dados de 2026

A execução offline reutiliza as fontes já coletadas:

```bash
python scripts/run_pipeline_2026.py --offline
```

Para atualizar também as páginas públicas do Quadro de Horários:

```bash
python scripts/run_pipeline_2026.py --refresh-web
```

O resultado permanece marcado como não pronto enquanto houver decisões
humanas pendentes. O relatório operacional está em
[`dados/processados/PENDENCIAS_VALIDACAO_2026.md`](dados/processados/PENDENCIAS_VALIDACAO_2026.md).

## Testes

```bash
python -m unittest discover -s tests -v
```

Os resultados preliminares de 2025 verificam o comportamento do software e
não constituem a comparação experimental final do TCC.

## Benchmark sintético de 2026

O perfil `sintetica_2026_v1` completa os campos ainda não validados usando
regras determinísticas derivadas dos dados versionados. Ele serve para validar
o fluxo integrado e não altera nem substitui as tabelas de revisão oficial.

```bash
python scripts/run_pipeline_2026.py --offline
python scripts/build_synthetic_instance_2026.py
python scripts/run_synthetic_experiments_2026.py
```

As hipóteses e os parâmetros ficam em
[`dados/config_sintetica_2026_v1.json`](dados/config_sintetica_2026_v1.json).
Os resultados agregados ficam em
[`dados/processados/relatorio_experimento_sintetico_2026.md`](dados/processados/relatorio_experimento_sintetico_2026.md)
e `dados/processados/resultados_experimento_sintetico_2026.csv`. Esses
resultados são explicitamente não oficiais; a instância institucional de 2026
continua bloqueada enquanto houver validações humanas pendentes.

### Piloto nativo e diagnóstico curricular

```bash
python scripts/build_synthetic_instance_2026.py
python scripts/diagnose_curriculum_conflicts_2026.py
python scripts/benchmark_optframe_sa_2026.py 10
```

O piloto cria uma pasta nova por execução, com manifesto, CSV e relatório;
instância e soluções JSON ficam locais. As duas buscas recebem a mesma
entrada gulosa, mas usam orçamentos e resfriamentos distintos. Portanto, o
piloto verifica integração, sem estabelecer superioridade estatística.
A semente controla a vizinhança Python; a aleatoriedade interna do OptFrame
e a parada por tempo impedem prometer repetição exata do resultado nativo.

Consulte o [relatório de validação e próximos passos](anotacoes/validacao_prototipo_2026_09_04.md)
e o [diagnóstico curricular](dados/processados/diagnostico_curricular_2026/relatorio.md).

### H8 por trajetória — checagem paralela

```bash
python scripts/check_h8_trajectories_2026.py dados/processados/instancia_sintetica_2026_v1.json --output-dir dados/processados/h8_trajetorias_2026/recorte
python scripts/check_h8_trajectories_2026.py dados/processados/instancia_sintetica_2026_v1.json --supplement-web webscrap/turmas_2026_raw.csv --output-dir dados/processados/h8_trajetorias_2026/ampliado
```

A checagem usa as obrigatórias das grades Markdown, verifica os dois semestres
do ano da instância e retorna `trajetoria_encontrada`, `sem_trajetoria` ou
`dados_incompletos`. O JSON inclui disciplinas ausentes, pendências e a
combinação escolhida com todos os encontros. `--max-nodes` limita o esforço
por grupo; atingir o limite gera resultado inconclusivo, com motivo explícito.

Vagas ofertadas positivas por curso são um filtro provisório de elegibilidade.
O complemento local supre apenas códigos ausentes por semestre; nunca troca
horários já presentes na solução. H8 atual, score e prontidão institucional
permanecem separados desse diagnóstico.

Resultado validado: sete grupos com trajetória e 25 incompletos no recorte;
22 com trajetória e dez incompletos com complemento. Consulte o
[relatório ampliado](dados/processados/h8_trajetorias_2026/ampliado/relatorio.md).

## Documento

A monografia é compilada a partir de `documento/main.tex`. Consulte
[`documento/README.md`](documento/README.md) para a convenção das fontes e
saídas. PDFs compilados devem ser publicados como versões de revisão ou
entrega, em vez de misturados às fontes.

## Dados sensíveis e arquivos locais

O scraper pode usar `webscrap/uff_cookies.json` para uma sessão idUFF. Esse
arquivo nunca deve ser versionado. Ambientes virtuais, logs, PDFs de consulta,
saídas geradas e artefatos de ferramentas de IA também permanecem locais.

## Uso de inteligência artificial

Ferramentas de IA generativa são usadas como apoio a programação, organização
de arquivos, clarificação textual e discussão do trabalho. Esse apoio inclui
proposição de alternativas, análise de trade-offs e discussão de modelagem e
métodos experimentais. Hipóteses provisórias acordadas com o autor podem ser
implementadas e testadas antes da avaliação do orientador, mantendo sua
identificação. As decisões finais e a redação substantiva permanecem sob
responsabilidade do autor, que revisa todo conteúdo antes de incorporá-lo ao
trabalho. Hipóteses não são apresentadas como diretrizes confirmadas.

Credenciais, cookies, dados pessoais e registros de sessões de IA não são
incluídos no repositório. A autoria dos commits e do trabalho é exclusivamente
do aluno.
