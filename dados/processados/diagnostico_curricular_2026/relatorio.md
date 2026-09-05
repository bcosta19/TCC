# Diagnóstico dos conflitos curriculares de 2026

SHA-256 da instância: `4c758cf2b612fd29be48239a1cf95e1aaf252e5a68132a348546efcde981e629`

10 sobreposições contadas pelo avaliador; 10 ofertas envolvidas.

| Semestre | Grupo | Códigos no recorte | Existe escolha sem choque? |
|---|---|---:|---|
| 2026-1 | SI-P1 | 5 | Sim |
| 2026-1 | SI-P6 | 4 | Sim |
| 2026-2 | SI-P1 | 4 | Sim |

As sobreposições são reais nos horários coletados, mas o contador atual exige ausência de choque entre todas as ofertas de códigos distintos do grupo. Ele ignora choques entre seções do mesmo código; não escolhe uma seção por disciplina.

O diagnóstico adicional busca uma turma por código do grupo. Uma escolha sem choque comprova apenas compatibilidade temporal individual no recorte. Não comprova atendimento de todos os alunos, suficiência de vagas, elegibilidade das seções ou viabilidade global da instância.

Não foi alterado H8 nem liberado horário obrigatório. Antes de flexibilizar horários, aluno e orientador devem decidir se H8 protege todas as ofertas ou trajetórias permitidas entre seções. A segunda interpretação exige modelar elegibilidade e, para atendimento coletivo, demanda/capacidade.

Evidências: `conflitos.csv` detalha as unidades contadas; `escolhas_por_grupo.csv` fornece testemunhas; `fontes.csv` confronta horários PDF e coleta web local. Grupos sem ofertas no recorte não são avaliados.
