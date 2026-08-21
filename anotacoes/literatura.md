# Referências bibliográficas e literatura do TCC

Este arquivo registra referências verificadas para a fundamentação do trabalho. As entradas BibTeX correspondentes estão em `referencias/referencias.bib` e `documento/referencias.bib`.

## Critério de revisão

- Metadados de artigos com DOI foram conferidos em registros editoriais/Crossref.
- A formulação da ITC-2007 foi conferida no relatório técnico oficial da trilha 3.
- A referência do OptFrame foi ajustada conforme a indicação de citação do repositório oficial.
- Não há, por enquanto, uma resolução institucional da UFF validada no repositório. As regras locais devem ser apresentadas como diretrizes levantadas com o orientador até a obtenção do documento aplicável.

---

## 1. Timetabling universitário

### Schaerf (1999) — *A Survey of Automated Timetabling*

Levantamento clássico sobre problemas de horários educacionais, incluindo as categorias escolar, exames e universitária.

- Periódico: *Artificial Intelligence Review*, 13(2), 87–127.
- DOI: `10.1023/A:1006576209967`.

### Lewis (2008) — *A Survey of Metaheuristic-Based Techniques for University Timetabling Problems*

Survey de técnicas metaheurísticas para timetabling universitário.

- Periódico: *OR Spectrum*, 30(1), 167–190.
- DOI: `10.1007/s00291-007-0097-0`.

### Babaei, Karimpour e Hadidi (2015) — *A Survey of Approaches for University Course Timetabling Problem*

Revisão de abordagens para UCTP.

- Periódico: *Computers & Industrial Engineering*, 86, 43–59.
- DOI: `10.1016/j.cie.2014.11.010`.

### Di Gaspero, McCollum e Schaerf (2007) — ITC-2007, trilha 3

Relatório técnico que define a trilha de *Curriculum-Based Course Timetabling* da ITC-2007. O documento especifica que uma solução atribui períodos **e salas** às aulas; portanto, a alocação de salas já integra o CB-CTT de referência.

- Tipo: relatório técnico.
- Número: `QUB/IEEE/Tech/ITC2007/CurriculumCTT/v1.0`.
- URL: <https://www.eeecs.qub.ac.uk/itc2007/curriculmcourse/report/curriculumtechreport.pdf>.

### Bettinelli et al. (2015) — *An Overview of Curriculum-Based Course Timetabling*

Visão geral de formulações e métodos para CB-CTT.

- Periódico: *TOP*, 23(2), 313–349.
- DOI: `10.1007/s11750-015-0366-z`.

---

## 2. Metaheurísticas

### Kirkpatrick, Gelatt e Vecchi (1983) — *Optimization by Simulated Annealing*

Artigo seminal do *Simulated Annealing*.

- Periódico: *Science*, 220(4598), 671–680.
- DOI: `10.1126/science.220.4598.671`.

### Lourenço, Martin e Stützle (2003) — *Iterated Local Search*

Referência para os componentes e princípios de ILS.

- Livro: *Handbook of Metaheuristics*, 320–353.
- DOI: `10.1007/0-306-48056-5_11`.

### Hansen e Mladenović (2001) — *Variable Neighborhood Search: Principles and Applications*

Referência para VNS.

- Periódico: *European Journal of Operational Research*, 130(3), 449–467.
- DOI: `10.1016/S0377-2217(00)00100-4`.

### Talbi (2009) — *Metaheuristics: From Design to Implementation*

Livro de referência sobre projeto e implementação de metaheurísticas.

---

## 3. OptFrame e pyoptframe

### Coelho et al. (2010) — *OptFrame: A Computational Framework for Combinatorial Optimization Problems*

Trabalho indicado pelo repositório oficial para apresentar o framework OptFrame.

- Evento: XLII Simpósio Brasileiro de Pesquisa Operacional.
- Páginas: 1887–1898.

### Coelho et al. (2020) — *Microbenchmark Studies in OptFrame: A 10-Year Anniversary*

Trabalho posterior sobre o histórico e microbenchmarks do OptFrame.

- DOI: `10.59254/sbpo-2020-122744`.

### pyoptframe

Bindings Python para o OptFrame Functional Core. O repositório consultado informa a versão 5.1.0 e autoria de Igor Machado Coelho.

- Repositório: <https://github.com/optframe/pyoptframe>.
- Situação no TCC: os protótipos de estudo usam pyoptframe, mas o código atual em `src/` ainda é um solver manual em Python e precisa ser integrado ao framework.

---

## 4. Contexto institucional da UFF

As seguintes regras foram registradas nas reuniões de orientação, mas ainda precisam de fonte institucional oficial:

- mínimo anual de três disciplinas obrigatórias;
- universo de professores abrangidos por esse mínimo;
- critério de prioridade entre professores;
- regra e duração do descanso entre jornadas;
- dias oficiais dos setores.

Uma versão local consultada anteriormente com o nome `Resolucao-TIC-2-2023.pdf`
era, na realidade, o artigo de Michael W. Carter (1989), *A Lagrangian
Relaxation Approach to the Classroom Assignment Problem*. O arquivo foi
retirado do repositório para evitar redistribuição de material bibliográfico e
para não ser confundido com uma resolução da UFF.
