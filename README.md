# TCC — Alocação de horários e salas com metaheurísticas (UFF/IC)

Trabalho de Conclusão de Curso sobre a aplicação de metaheurísticas (via [pyoptframe](https://github.com/optframe/pyoptframe-dev)) ao problema de alocação de horários e salas de aula no Instituto de Computação da UFF.

**Comece por aqui**: [`PLANO.md`](PLANO.md) (plano de execução) e [`anotacoes/orientacao.md`](anotacoes/orientacao.md) (diretrizes do orientador).

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `anotacoes/` | Anotações de orientação e estudo |
| `dados/` | Dados do problema — ver `dados/PENDENCIAS.md` para o que falta obter |
| `webscrap/` | Scraper do quadro de horários da UFF + dados extraídos (2023/1–2025/2) |
| `prototipos/` | Protótipos de estudo do OptFrame (mochila com SA, alocação de salas toy) |
| `modelo_artigo/` | Modelo LaTeX oficial de TCC/artigo do curso + tutorial |
| `referencias/` | Bibliografia em PDF e TCC de exemplo |
| `optframe/` | Clone do OptFrame C++ (terceiro) |
| `pyoptframe-dev/` | Clone do pyoptframe (terceiro) — demos úteis em `demo/` |
| `src/` | (futuro) implementação do solver do TCC |

## Webscrap

Pipeline em `webscrap/`: `scraper.py` (coleta — requer login no idUFF) → `fix_names.py` (normaliza nomes de docentes) → `visualizar.py` (exploração no terminal). Saídas: `turmas_raw.csv` e `preferencias_professores.xlsx`.

> `uff_cookies.json` contém cookies de sessão e **não é versionado** (`.gitignore`).
