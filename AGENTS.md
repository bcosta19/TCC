# AGENTS.md

Contexto para agentes de IA (Claude Code, opencode, etc.) ao trabalhar neste repositório.

## O projeto

TCC de Ciência da Computação (UFF) sobre **metaheurísticas aplicadas à alocação de horários e salas de aula** no Instituto de Computação da UFF, implementado com **pyoptframe**. Defesa prevista para o fim de 2026/2 (~nov/dez). Além da monografia, haverá uma versão em **formato de artigo** (modelo em `modelo_artigo/`).

A ideia original era minimizar a distância entre salas de aulas consecutivas. Em 10/08/2026, aluno e orientador decidiram **retirar esse critério do escopo**. O trabalho permanece um problema de *timetabling* completo com atribuição de professores, horários e salas.

## Documentos-chave (ler antes de mexer em qualquer coisa)

- `PLANO.md` — plano de execução: fases, cronograma, modelagem (restrições hard/soft), riscos.
- `anotacoes/orientacao.md` — diretrizes do orientador: os 3 stakeholders em conflito, estratégia de horários fixos por semestre par/ímpar, setores por dia da semana, requisitos do protótipo.
- `dados/PENDENCIAS.md` — checklist dos dados que ainda faltam (destaque: planilha de setores que o orientador vai enviar).

## Estrutura

- `webscrap/` — pipeline autocontido de coleta do quadro de horários da UFF (2023/1–2025/2): `scraper.py` → `fix_names.py` → `visualizar.py`. Saídas: `turmas_raw.csv`, `preferencias_professores.xlsx`. O `uff_cookies.json` (sessão idUFF) existe só localmente e **não é versionado**.
- `prototipos/` — exemplos de estudo do OptFrame (mochila com SA, alocação de salas toy). Rodar de dentro da pasta de cada protótipo (caminhos relativos).
- `dados/` — `brutos/` (como chegaram) e `processados/` (instâncias limpas para o solver).
- `src/` — (futuro) implementação do solver do TCC: `model/`, `eval/`, `moves/`, `solve/`.
- `optframe/` e `pyoptframe-dev/` — clones de terceiros; não editar. Demos úteis em `pyoptframe-dev/demo/`.
- `referencias/`, `modelo_artigo/`, `anotacoes/` — bibliografia, modelo LaTeX oficial e anotações.

## Convenções

- Tudo em **português (pt-BR)**: comunicação, documentos, mensagens de commit.
- Commits **sem** trailer `Co-Authored-By:` de nenhum agente — a autoria é exclusivamente do aluno.
- Commits diretos na `main` (repositório pessoal, sem PRs).
- Mover arquivos versionados sempre com `git mv`.
- Python 3.10; dependências usadas até agora: pandas, requests, beautifulsoup4, playwright, plotext, rich, numpy, optframe.

## Escopo de uso dos agentes de IA — política

Os agentes de IA podem atuar como uma dupla de trabalho e raciocínio com o aluno, ajudando a avançar o projeto por meio de:

- **Programação**: sugestões de código, refatoração e debugging.
- **Organização de arquivos**: estrutura de pastas, nomes e `.gitignore`.
- **Clarificação de textos**: revisão de português e checagem de consistência entre documentos.
- **Discussão e planejamento**: propor próximos passos, levantar alternativas, explicar trade-offs e comparar vantagens, limitações e riscos.
- **Apoio à modelagem e aos experimentos**: discutir interpretações das diretrizes do orientador, restrições, função objetivo e métodos experimentais, apresentando justificativas e hipóteses explícitas para avaliação do aluno.

As decisões finais e a autoria acadêmica permanecem com o aluno. Hipóteses provisórias acordadas com ele podem ser implementadas e testadas antes da avaliação do orientador, mantendo sua identificação e permitindo ajustes posteriores. Não apresentar hipóteses como diretrizes confirmadas, nem inventar dados, fontes ou resultados. A redação substantiva da monografia permanece sob responsabilidade do aluno. Toda saída é revisada e editada pelo aluno antes de ser versionada.

**Restrições adicionais**: nenhum cookie de sessão (`uff_cookies.json`), senha ou dado pessoal é colado em prompts. Logs de sessão de IA (`anotacoes/contexto_sessao_*.md`) **não são versionados** — registre decisões em arquivos do projeto, não em logs. Veja a seção "Uso de inteligência artificial" do `README.md` para a versão pública desta política (que também vai para os agradecimentos da monografia).

## Estado atual (ago/2026)

Fase 1 (formalização): modelo matemático em `anotacoes/modelo_matematico.md` — UCTP *curriculum-based* + alocação de salas, sem critério de distância; ainda falta revisar hard×soft e pesos com o orientador. A pipeline inicial de dados e os protótipos de avaliação/solução estão em desenvolvimento. Pendências estão em `dados/PENDENCIAS.md`.
