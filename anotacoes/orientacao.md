# Orientações do professor orientador

> Registro estruturado das diretrizes passadas pelo orientador (registrado em 09/06/2026).

## Escopo geral

- **Tema**: metaheurísticas aplicadas ao problema de alocação de salas de aula e horários no contexto da UFF (Instituto de Computação).
- **Ferramenta**: pyoptframe (OptFrame com bindings Python).
- Não se preocupar com utilidade prática imediata do sistema; o objetivo é **modelar algo próximo da realidade**, útil para trabalhos futuros.
- Ideia original do trabalho: **minimizar a distância entre salas de horários consecutivos** para os alunos andarem menos. O problema se mostrou maior, mas a ideia deve ser mantida como critério/extensão se possível.
- Entrega futura: TCC (monografia) + versão em **formato de artigo**.

## Os três papéis (stakeholders) e seus conflitos

1. **Chefia de departamento** — define horário e alocação do professor, junto com a coordenação.
   - Conflito: a chefia "briga" pelo professor, a coordenação "briga" pelos alunos.
   - Chefia quer turmas grandes.
2. **Coordenação de curso** — representa os alunos; alunos cobram vagas da coordenação.
   - Conflito com chefia sobre tamanho das turmas.
3. **Instituto de Computação** — administra as salas.
   - Professores fazem pedidos ao instituto (ex.: laboratório).
   - Conflito também com o tamanho das turmas (capacidade da sala).

## Estratégias práticas (experiência do orientador)

### Horários fixos por semestre par/ímpar
- Horário é a parte mais complicada por causa dos desejos dos professores.
- Solução: **horário fixo** — uma matéria tem um horário no semestre ímpar (1) e outro no semestre par (2), repetindo ano a ano.
- Algumas matérias têm horário fixo **nos dois semestres**, por questão de jornada de trabalho do professor (ex.: professor que chega às 7h não pode dar aula à noite).
- Tática: jogar professor para o horário de **11h às 13h** e colocar a aula da noite mais cedo (**18h**).

### Setores (áreas do departamento)
- Existe uma lista de professores com mais afinidade/problema para dar cada matéria, organizada em **setores**: algoritmos, redes, engenharia de software, etc.
- **Existe uma planilha com esses setores — o orientador vai enviar.**
- Cada setor fica nos **mesmos dias da semana**. Ex.: algoritmos → terça e quinta.
- **Exceção**: Estruturas de Dados → segunda e quarta. Motivo: é **matéria externa** (outros cursos além da computação cursam), e matéria externa tem **prioridade maior**.
- Vantagens de grupos no mesmo dia:
  - Maior chance de combinar matérias (manhã/noite);
  - Legalidade da jornada (evitar ficar até o último horário da noite e dar aula às 7h no dia seguinte).

### Critérios a estabelecer
- Grupos de matérias (setores);
- Rodízio de professores;
- Professores se adaptam aos horários fixos;
- Regras para semestre par e ímpar, com professores diferentes para cada.

## O que o protótipo tem que considerar (requisitos)

1. **Lista de matérias externas com horário fixo** → alta prioridade, já são dadas, não se alteram.
2. **Lista de áreas/setores do departamento** (algoritmos, redes, eng. de software, ...).
3. **Alocação de horários prevista para as matérias** no semestre par e no ímpar.
4. **Lista de salas disponíveis** com capacidades e recursos.
5. **Lista de matérias optativas** (horário livre) que cada professor pretende oferecer.
6. **Preferências dos professores por matérias** (lista hipotética — webscrap do quadro de horários já feito).
7. **Lista ordenada de professores por prioridade** (ex.: idade/antiguidade).
8. **Critérios de qualidade para o professor**:
   - Número de dias trabalhados;
   - Horas de descanso entre jornadas;
   - Janelas sem aula no dia (minimizar);
   - Questões legais de jornada de trabalho.

## Estado atual (09/06/2026)

- Webscrap concluído: turmas e docentes de 2023/1 a 2025/2 do quadro de horários da UFF (curso 31 — Ciência da Computação, Niterói), com contagem professor × disciplina como proxy de preferência.
- Pendência conhecida: filtrar as optativas humanísticas que vieram junto na extração.
