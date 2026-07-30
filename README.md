# TCC — Alocação de horários e salas com metaheurísticas (UFF/IC)

Trabalho de Conclusão de Curso sobre a aplicação de metaheurísticas (via [pyoptframe](https://github.com/optframe/pyoptframe-dev)) ao problema de alocação de horários e salas de aula no Instituto de Computação da UFF.

**Comece por aqui**: [`PLANO.md`](PLANO.md) (plano de execução) e [`anotacoes/orientacao.md`](anotacoes/orientacao.md) (diretrizes do orientador).

## Uso de inteligência artificial

Uso assistido de ferramentas de IA generativa (Claude, via Claude Code) **apenas para**:

- **Programação**: sugestões de código, refatoração, debugging e esqueleto de scripts;
- **Organização de arquivos**: estruturação de pastas, nomes de arquivos, `.gitignore`;
- **Clarificação de textos**: revisão de português, padronização de formatação e checagem de consistência entre documentos.

Não delego à IA: decisões de modelagem, interpretação de diretrizes do orientador, formulação matemática, escolha de métodos e a redação substantiva. Todo conteúdo é revisto e editado por mim antes de ser versionado ou usado na monografia.

**Questões éticas**: nenhuma senha, cookie de sessão ou dado pessoal entra em prompt de IA. As conversas de desenvolvimento não são versionadas (logs de sessão ficam fora do repositório). Commits não contêm o trailer `Co-Authored-By: Claude` — a autoria do trabalho é exclusivamente minha. Esta nota também será incluída nos agradecimentos da monografia.

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
