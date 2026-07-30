# Domínios provisórios de horários

O arquivo `instancia_2025_cc_si_flex.json` adiciona `horario_fixo`,
`padrao_horario_atual` e `dominio_horarios` às turmas.

Regra atual:

- disciplinas externas ficam fixas;
- projetos finais ficam fixos;
- turmas internas com período curricular ficam flexíveis;
- padrões candidatos são retirados dos horários observados no mesmo semestre;
- o setor restringe os dias candidatos aos dias observados para aquele setor.
- a exigência de laboratório é preservada por encontro; uma sala `L...` só é
  candidata para encontros marcados como laboratório, e salas comuns não são
  trocadas por laboratórios.

Essa regra é adequada para o primeiro experimento de horários, mas ainda é uma
aproximação. A disponibilidade real dos professores e os horários oficiais
devem substituir esses domínios posteriormente.

As salas `L...` também são consideradas outro prédio. A distância provisória
entre prédios é `3 + diferença de andar`, sem componente horizontal.
