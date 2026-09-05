# Investigação de H8 por trajetória individual — 05/09/2026

> Implementação posterior à investigação: a checagem paralela está disponível
> em `src/eval/trajectories.py` e `scripts/check_h8_trajectories_2026.py`.
> Ela verifica as obrigatórias das grades Markdown e reproduziu sete grupos
> com trajetória no recorte e 22 com complemento local; os demais são
> inconclusivos. H8 e score atuais foram preservados. Veja os comandos no
> [README](../README.md#h8-por-trajetória--checagem-paralela).

A opção 2 é implementável e encontra trajetórias nos dados examinados. Sua
adoção ainda exige delimitar as disciplinas obrigatórias de cada grupo e as
turmas elegíveis. A interpretação proposta é: para cada curso, período e
semestre, deve existir uma escolha de uma turma por disciplina obrigatória,
sem sobreposição entre quaisquer encontros dessas turmas.

Esta investigação é separada do solver: H8, função objetivo, horários e
instância de entrada não foram alterados. As recomendações abaixo são
propostas para discussão com o aluno, não diretrizes confirmadas do orientador.

## Evidência obtida

Foram examinados 32 grupos: oito períodos de CC e oito de SI, em dois
semestres. O filtro observacional aceita apenas turmas com vagas ofertadas
positivas para o respectivo curso (`31` para CC e `83` para SI, conforme o
campo de vagas; esses identificadores não são os filtros internos de busca).
Vagas ofertadas não significam vagas livres hoje nem autorização de matrícula
para qualquer aluno. Foram consideradas todas as reuniões semanais da turma.

| Análise | Trajetória encontrada | Inconclusivos por cobertura |
|---|---:|---:|
| Apenas códigos presentes no recorte do solver | 32 | A checagem temporal sozinha não detecta ausências |
| Cobertura literal das obrigatórias na grade versionada, sem ampliar o recorte | 7 grupos cobertos | 25 grupos com códigos ausentes |
| Recorte acrescido das ofertas ausentes disponíveis na coleta web local | 22 grupos cobertos com trajetória | 10 grupos incompletos |

No recorte foram enumeradas 109 combinações, das quais 92 não possuem choque.
O teste pequeno levou cerca de 4 ms nesta execução, sem contar carregamento;
não é benchmark de desempenho nem garantia de custo em instâncias maiores.
A busca ampliada usa poda e para ao encontrar uma testemunha.

Nos grupos dos dez conflitos anteriores:

| Grupo | Combinações no recorte com vagas para SI | Sem choque |
|---|---:|---:|
| SI-P1, 2026/1 | 16 | 8 |
| SI-P1, 2026/2 | 16 | 8 |
| SI-P6, 2026/1 | 2 | 1 |

As contagens incluem escolhas das demais disciplinas do grupo. Em SI-P1 de
2026/2, CGI00004 estava ausente do recorte; sua oferta web foi acrescentada
apenas na análise ampliada e ainda existe trajetória sem choque.
Em SI-P6 de 2026/1, a trajetória usa TCC00336-A1, com 52 vagas ofertadas para
SI. A turma Z1 que participa do choque tem apenas uma vaga ofertada para SI.
Logo, a alternativa temporal não depende de usar Z1 para o grupo inteiro.

Há divergência já registrada para CGI00004 em 2026/1: PDF 18h–22h na sexta,
web 18h–20h. A investigação preserva o intervalo do PDF presente na instância,
sem resolver a divergência por conta própria. A trajetória encontrada usa
esse intervalo mais longo.

Os dez grupos ainda incompletos são, nos dois semestres:

- CC-P7: TCC00351;
- CC-P8: TCC00352;
- SI-P4: GCI00116;
- SI-P5: GCI00126;
- SI-P7: TCC00364. O perfil sintético usa TCC00368 nesse grupo, mas uma
  equivalência definitiva entre os códigos não foi presumida.

A falta desses códigos no levantamento não prova ausência institucional da
oferta. Projetos finais e atividades podem exigir tratamento próprio. A
comparação considera códigos classificados como obrigatórios na tabela de
currículos; não representa todas as atividades acadêmicas nem optativas.

## Como implementar sem confundir dados ausentes e violações

1. Construir a lista de disciplinas esperadas a partir da grade aprovada,
   incluindo equivalências explicitamente aceitas. Não derivá-la somente das
   turmas que por acaso entraram na instância.
2. Associar a cada disciplina as turmas permitidas para o curso. Vagas
   ofertadas positivas são um filtro provisório útil, mas regras de turno,
   ingresso, pré-requisitos e turmas reservadas podem restringir a escolha.
3. Buscar uma turma por disciplina. Cada escolha deve ser compatível com
   todas as já selecionadas; a existência de pares compatíveis isolados não
   garante uma combinação global. Todos os encontros de uma turma são
   indivisíveis nesta hipótese.
4. Retornar uma testemunha verificável ou um resultado explícito:
   `trajetoria_encontrada`, `sem_trajetoria` ou `dados_incompletos`. Eventual
   limite de tempo também deve produzir resultado inconclusivo, nunca
   `sem_trajetoria` sem prova.
5. Manter o contador atual como diagnóstico de sobreposições entre ofertas.
   Para a nova H8, uma possibilidade é contar grupos completos sem trajetória.
   Essa contagem tem unidade diferente da atual e exige revisão da escala
   da busca; não se devem comparar scores antigos e novos como se fossem
   a mesma métrica.

Se for necessária uma indicação gradual para orientar a busca, pode-se
investigar quantas disciplinas no máximo cabem em uma trajetória sem choque.
Isso é uma hipótese adicional de métrica, não uma alteração implementada.
Ausências de dados devem permanecer separadas dessa medida.

As escolhas representam testemunhas individuais, não novas turmas físicas.
H6/H7 continuam avaliando todas as turmas ofertadas: escolher uma trajetória
para H8 não elimina aulas, professores ou salas das demais restrições. As
mesmas turmas compartilhadas podem aparecer nas testemunhas de CC e SI,
mas isso não demonstra capacidade de atender simultaneamente suas demandas.

## Consequência para o experimento atual

Nenhuma turma com grupo curricular avaliado tem horário flexível no perfil
sintético atual. Portanto, H8 por trajetória também permaneceria constante
nessas buscas: professor e sala não mudam a compatibilidade temporal.

No recorte, a nova interpretação estaria satisfeita já no baseline. Retirar
as dez penalidades antigas seria uma mudança de definição, não uma melhoria
produzida pelo SA. Isso não permite declarar viabilidade institucional, pois
persistem cobertura incompleta, elegibilidade não validada e parâmetros proxy.

A recomendação é implementar primeiro a checagem em paralelo ao avaliador
atual, com estados de cobertura e testemunhas, e completar as ofertas externas
como ocupações fixas. Só depois adotar a opção 2 como H8 de um perfil separado,
reavaliando baseline e soluções sob a mesma definição.

## Reexecução e limites

```bash
.venv/bin/python scripts/investigate_h8_option2_2026.py
```

[Artefatos](../dados/processados/investigacao_h8_opcao2_2026/recorte.json):
`recorte.json` contém contagens e testemunhas; `ampliado.json`, cobertura e
trajetórias com ofertas acrescentadas; `manifesto.json`, hashes de entradas e
código. A análise usa somente dados locais, sem nova consulta à UFF.
Os valores de gargalo por trajetória são mínimos de vagas ofertadas entre
suas turmas, não estimativas de capacidade coletiva ou de vagas disponíveis.

Foram conferidos casos pequenos em que cada par de disciplinas é compatível,
mas não existe combinação para três disciplinas, e em que um domínio está
vazio. Ambos foram corretamente rejeitados pela busca. O solver e os testes
existentes não foram modificados; não houve commit.
