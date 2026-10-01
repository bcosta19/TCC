# Artigo do TCC

Versão em formato de artigo, seguindo o modelo oficial do curso
(`modelo_artigo/ModeloTCC_Artigo_CC_Latex.zip`): capa, folha de aprovação,
ficha catalográfica, título bilíngue, resumo/abstract, Introdução,
Desenvolvimento, Conclusão, Referências (ABNT, autor-data), Apêndices A–D e
Agradecimentos.

## Como compilar no Overleaf

1. Envie `../artigo_overleaf.zip` em *New Project → Upload Project*
   (o zip contém esta pasta, sem o README).
2. Compilador: **pdfLaTeX** (padrão). Documento principal: `main.tex`.
3. Se o pdfLaTeX apontar algum erro de pacote, troque para **XeLaTeX** em
   *Menu → Compiler*. A versão atual foi testada com XeTeX (Tectonic 0.15),
   gerando 33 páginas sem erros, sem referências indefinidas e sem linhas
   estouradas.

Para recriar o zip depois de editar os arquivos, a partir da raiz do repositório:

```bash
cd artigo && zip -r ../artigo_overleaf.zip main.tex pretextuais.tex postextuais.tex referencias.bib secoes
```

## Organização

| Arquivo | Conteúdo |
|---|---|
| `main.tex` | Preâmbulo, formatação do modelo e ordem das partes |
| `pretextuais.tex` | Capa, folha de aprovação e ficha catalográfica |
| `secoes/00_resumo.tex` | Títulos, autoria, resumo, abstract e datas |
| `secoes/01_introducao.tex` | 1. Introdução, objetivos, contribuições |
| `secoes/02_fundamentacao.tex` | 2.1 Fundamentação teórica e trabalhos relacionados |
| `secoes/03_problema_modelagem.tex` | 2.2 Caracterização e 2.3 Modelagem matemática |
| `secoes/04_dados_instancias.tex` | 2.4 Dados, instância observada e perfis sintéticos |
| `secoes/05_metodo.tex` | 2.5 Representação, movimentos, meta-heurísticas, pyoptframe |
| `secoes/06_experimentos_resultados.tex` | 2.6 Protocolo e 2.7 Resultados e discussão |
| `secoes/07_conclusao.tex` | 3. Conclusão e trabalhos futuros |
| `postextuais.tex` | Apêndices A–D e Agradecimentos |
| `referencias.bib` | Cópia de `../referencias/referencias.bib` com campos ABNT |

Os títulos seguem o modelo: seções numeradas em negrito e caixa alta,
citações autor-data com `\cite` (entre parênteses) e `\citeonline` (no texto),
legenda de figura abaixo e de tabela acima, com a fonte na legenda.

## Origem dos números

Todos os números vêm de artefatos do repositório; nenhum resultado foi
estimado ou inventado.

- Instância e auditoria: `dados/processados/auditoria_2026_cc_si.md`.
- Perfil v1: `dados/processados/relatorio_experimento_sintetico_2026.md` e CSV.
- Perfil v2: `dados/processados/relatorio_experimento_sintetico_2026_v2_hp.md` e CSV.
- Piloto nativo: `dados/processados/piloto_optframe_20260904_final/` (v1) e
  `piloto_optframe_20260907_204501/` (v2).
- H8: `dados/processados/diagnostico_curricular_2026/` e `h8_trajetorias_2026/`.
- Hipóteses HP1/HP2: `anotacoes/hipoteses_provisorias_2026_09_07.md`.

## Pendências marcadas no texto

Os trechos `\pendente{...}` aparecem em vermelho no PDF. Busque por
`\pendente` para encontrá-los e remova todos antes da versão final.

**Dados pessoais e formais**
- E-mails idUFF do autor e do orientador (`secoes/00_resumo.tex`).
- Banca, data de aprovação e ficha catalográfica (`pretextuais.tex`).
- Agradecimentos pessoais e revisão da declaração de uso de IA (`postextuais.tex`).
- Endereço público do repositório, se houver (`postextuais.tex`).

**Decisões com o orientador**
- Fonte normativa de H12, prioridade e descanso (`01_introducao.tex`).
- Hard × soft de H8, H10 e H11; universo de H12; pesos dos critérios (`03_problema_modelagem.tex`).
- Hipóteses HP1/HP2 do perfil v2 (`04_dados_instancias.tex`).
- Semântica de H8 para turmas alternativas (`06_…` e `07_conclusao.tex`).
- Manter ou retirar os cenários E1–E3 (`01_introducao.tex` e `06_…`).

**Experimentos definitivos**
- Instância oficial, protocolo final, teste estatístico e gráficos de convergência (`06_…`).
- Máquina usada nos experimentos (`06_…`).
- Controle da semente interna do OptFrame e ILS/VNS nativos (`05_metodo.tex`).
- Atualizar resumo, abstract, resultados, discussão e conclusão com os números finais.

**Texto e referências**
- Trabalhos relacionados aplicados, por exemplo do SBPO (`02_fundamentacao.tex`).
- Data de acesso do relatório da ITC-2007 (`referencias.bib`).
- Comandos exatos de reprodução do perfil v2 (`postextuais.tex`).
