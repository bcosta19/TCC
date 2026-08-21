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
- Avaliadores e protótipos de *Simulated Annealing* foram implementados em
  Python e validados inicialmente com dados de 2025.
- A integração dos componentes com
  [pyoptframe](https://github.com/optframe/pyoptframe-dev) e o protocolo
  experimental comparativo ainda estão em desenvolvimento.

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

Ferramentas de IA generativa são usadas apenas como apoio a programação,
organização de arquivos e clarificação textual. Não são delegadas decisões de
modelagem, interpretação das diretrizes do orientador, escolha de métodos
experimentais ou redação substantiva. Todo conteúdo é revisto pelo autor antes
de ser incorporado ao trabalho.

Credenciais, cookies, dados pessoais e registros de sessões de IA não são
incluídos no repositório. A autoria dos commits e do trabalho é exclusivamente
do aluno.
