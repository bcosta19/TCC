# Decisões de qualidade da instância CC/SI 2025

## 1. Encontros sem sala

Foram encontradas **12 turmas** com pelo menos um encontro sem sala.
A sala não foi inventada. O CSV de revisão registra candidatos históricos por código, mas a decisão é manter a sala nula até confirmação.

Arquivo: `revisao_salas_2025.csv`.

## 2. Turmas sem setor

Foram encontradas **8 turmas** sem setor.
Disciplinas externas não recebem setor do IC. Disciplinas `TCC` de optativa ou ementa variável ficam sem restrição de setor nesta versão.

Arquivo: `revisao_setores_2025.csv`.

## 3. Conflitos curriculares

Foram encontrados **10 grupos de conflito**; **10** foram confirmados nas grades oficiais.
Os conflitos confirmados permanecem restrições hard. As confirmações principais são CC-P5 (`TCC00226`/`TCC00312`) e SI-P1 (`TCC00332`/`TCC00354`).

Arquivo: `validacao_curricular_2025.csv`.

## 4. Capacidade das salas

A capacidade foi estimada por `max(CAP)` das turmas observadas em cada sala.
Essa regra é aceita para testes e permite ativar H10/O4, mas não é uma confirmação física: uma sala pode ter recebido apenas turmas menores.
A capacidade oficial deve substituir `capacidade_estimada` quando for obtida.

Arquivo: `salas_2025.csv`.

## 5. Recursos e laboratórios

Foram inferidas **42 turmas** com pelo menos um encontro de laboratório e **59 encontros** com exigência de laboratório.
Há **1 turma(s)** com recurso desconhecido; ela(s) não recebe(m) exigência inventada.
O prefixo `L` identifica laboratório e prédio separado. A compatibilidade é estrita no protótipo: encontros de laboratório vão para `L...` e encontros comuns não são enviados para `L...`.

Arquivos: `recursos_turmas_2025.csv` e `recursos_encontros_2025.csv`.

## Estado após as decisões

- Não preencher salas ausentes automaticamente.
- Não impor setor a externas e optativas/ementas variáveis.
- Manter conflitos curriculares confirmados como hard.
- Usar capacidade estimada apenas como parâmetro provisório.
- Confirmar os recursos desconhecidos e substituir a inferência histórica por cadastro oficial quando disponível.
