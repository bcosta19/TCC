# Orientações do professor orientador

> Registro estruturado das diretrizes passadas pelo orientador (registrado em 09/06/2026).

## Escopo geral

- **Tema**: metaheurísticas aplicadas ao problema de alocação de salas de aula e horários no contexto da UFF (Instituto de Computação).
- **Ferramenta**: pyoptframe (OptFrame com bindings Python).
- Não se preocupar com utilidade prática imediata do sistema; o objetivo é **modelar algo próximo da realidade**, útil para trabalhos futuros.
- A ideia original era **minimizar a distância entre salas de horários consecutivos**. Em 10/08/2026, aluno e orientador decidiram retirar esse critério do escopo; localização de salas e deslocamento deixam de compor os dados, o modelo e os experimentos.
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
   - Questões legais de jornada de trabalho;
   - Carga anual: obrigação de ministrar **no mínimo 3 disciplinas obrigatórias por ano** (restrição do departamento, não preferência — ver diretrizes de 23/06/2026 abaixo).

## Diretrizes novas (23/06/2026)

1. **Carga anual de obrigatórias**: todo professor do IC tem a obrigação de ministrar **no mínimo 3 disciplinas obrigatórias por ano** (forma de mínimo ≥ 3 confirmada pelo orientador). Acopla os semestres ímpar e par num **horizonte anual** de planejamento — no modelo, restrição forte H12.
2. **Duas grades curriculares (CC e SI)**: as disciplinas de computação compõem dois currículos — Ciência da Computação e Sistemas de Informação. **Mesmo departamento, mesmas regras** (professores, setores, salas, horários fixos, par/ímpar); a única diferença é em qual período cada disciplina é cursada. Disciplina presente nas duas grades é **uma única turma compartilhada** (mesmo professor/sala/horário), cursada por alunos dos dois cursos.

Ambas incorporadas ao `modelo_matematico.md` (horizonte anual, conjuntos por grade, H12, função objetivo por currículo e experimentos E1–E3).

## Estado atual (atualizado em 10/08/2026)

- Webscrap concluído: turmas e docentes de 2023/1 a 2025/2 do quadro de horários da UFF (curso 31 — Ciência da Computação, Niterói), com contagem professor × disciplina como proxy de preferência.
- Pendência conhecida: filtrar as optativas humanísticas que vieram junto na extração.
- 04/07/2026: diretrizes de 23/06 (carga anual + grades CC/SI) aplicadas à modelagem. Pendências novas de dados: grade curricular de SI por período e mapa das disciplinas compartilhadas CC∩SI (o webscrap cobriu só CC).
- 10/08/2026: critério de distância entre salas retirado por decisão conjunta do aluno e do orientador; alocação de salas permanece baseada em conflitos, capacidade e recursos.
