# CLAUDE.md

Contexto para o Claude Code ao trabalhar neste repositório.

## O projeto

TCC de Ciência da Computação (UFF) sobre **metaheurísticas aplicadas à alocação de horários e salas de aula** no Instituto de Computação da UFF, implementado com **pyoptframe**. Defesa prevista para o fim de 2026/2 (~nov/dez). Além da monografia, haverá uma versão em **formato de artigo** (modelo em `modelo_artigo/`).

A ideia original era minimizar a distância entre salas de aulas consecutivas (alunos andarem menos). O escopo cresceu para um problema de timetabling completo, mas **esse critério de distância deve ser mantido como diferencial/extensão** do trabalho.

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
- Commits **sem** trailer `Co-Authored-By: Claude` — a autoria é exclusivamente do aluno.
- Commits diretos na `main` (repositório pessoal, sem PRs).
- Mover arquivos versionados sempre com `git mv`.
- Python 3.10; dependências usadas até agora: pandas, requests, beautifulsoup4, playwright, plotext, rich, numpy, optframe.

## Estado atual (jun/2026)

Fase 1 (formalização): primeiro rascunho do modelo matemático em `anotacoes/modelo_matematico.md` — UCTP curriculum-based + alocação de salas com distância; falta revisar hard×soft e pesos com o orientador. Fase 2 (dados) ainda por começar. Bloqueio externo: aguardando a planilha de setores do orientador. Pendências de limpeza nos dados coletados estão em `dados/PENDENCIAS.md`.
