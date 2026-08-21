# Pendências para Validação Humana — Instância 2026 (Instituto de Computação - UFF)

Este documento descreve detalhadamente os **12 itens de validação humana** necessários para transformar as instâncias observadas de 2026 em instâncias experimentais definitivas.

> **Importante**: Enquanto essas decisões não forem preenchidas e validadas nos respectivos arquivos CSV, a instância permanecerá tecnicamente marcada com `"pronta_para_experimento": false`. O avaliador e os solvers recusarão execuções experimentais não autorizadas.

---

## 1. Classificação Curricular de `TCC00368` (Pesquisa Operacional para SI)

- **Arquivo**: `dados/processados/revisao_classificacao_curricular_2026.csv`
- **Turmas**: `2026-1-TCC00368-A1` e `2026-2-TCC00368-A1`
- **Colunas a preencher**: `decisao`
- **Valores aceitos**: `obrigatoria:SI-P7`, `optativa:SI`, `optativa:CC`, `ignorar`
- **Evidências nos dados**:
  - Código `TCC00368` retornado na consulta pública do currículo de SI com vagas para SI (59 em 2026-1, 61 em 2026-2) e CC (2 em 2026-1).
  - Ausente das grades curriculares em Markdown versionadas no repositório (`dados/grade_si.md`).
  - No histórico de 2025 (`turmas_2025.csv`), aparecia vinculada ao período `SI-P7` com o nome "WEB AVANC. / PESQUISA OPERACIONAL PARA SI".
- **Impacto no modelo**:
  - Se confirmada como `SI-P7`, ativa restrição de conflito curricular (H3) com outras disciplinas do 7º período de SI e conta para o mínimo de obrigatórias (H12).
  - Se classificada como optativa, não gera conflito de período curricular nem conta em H12.

---

## 2. Classificação Curricular de `TCC00371` (Ética em IA e Ciência de Dados)

- **Arquivo**: `dados/processados/revisao_classificacao_curricular_2026.csv`
- **Turmas**: `2026-1-TCC00371-A1` e `2026-2-TCC00371-A1`
- **Colunas a preencher**: `decisao`
- **Valores aceitos**: `obrigatoria:CC-P*`, `optativa:CC`, `optativa:SI`, `ignorar`
- **Evidências nos dados**:
  - Código retornado na busca do currículo de CC com vagas distribuídas entre CC (10), SI (15 em 2026-2) e IA/CD (20/25).
  - Disciplina nova (não ofertada em 2025 e ausente das grades Markdown).
- **Impacto no modelo**:
  - Define se participa de grupo curricular obrigatório e cálculo de carga anual.

---

## 3. Universo Docente do IC para a Restrição H12 (Carga Anual Mínima)

- **Arquivo**: `dados/processados/universo_h12_2026.csv`
- **População**: 73 docentes mapeados (61 observados em 2026 + docentes da planilha de carga de 2025).
- **Colunas a preencher**: `incluido_h12`
- **Valores aceitos**: `sim` ou `nao`
- **Regras e Evidências**:
  - O recorte CC/SI de 2026 possui **149 turmas obrigatórias**.
  - Como a restrição H12 exige pelo menos **3 turmas obrigatórias por ano**, 149 turmas comportam no máximo $\lfloor 149 / 3 \rfloor = \mathbf{49}$ **docentes**.
  - Se o universo marcado como `sim` contiver mais de 49 docentes, o problema torna-se matematicamente inviável sem que haja folga de turmas.
  - Docentes em afastamento, chefia ou licença devem ser marcados como `nao`.

---

## 4. Política Institucional de Cotutoria

- **Arquivo**: `dados/processados/politica_cotutoria_2026.csv`
- **Turmas afetadas**:
  - `2026-2-TCC00285-A1` (Compiladores, Martinhon e Raquel)
  - `2026-2-TCC00354-A1` (Desenvolvimento Web, Martinhon e Raquel)
- **Colunas a preencher**: `politica_h12`, `professor_responsavel` (se aplicável)
- **Valores aceitos para `politica_h12`**:
  1. `integral_para_cada_docente`: cada professor da cotutoria recebe +1 na contagem de turmas de H12.
  2. `fracionada`: cada professor recebe $+1/k$ (ex.: +0.5 para 2 professores).
  3. `contar_para_um_responsavel`: apenas o docente indicado em `professor_responsavel` recebe +1.
  4. `nao_contabilizar_em_h12`: a turma não conta para H12 de nenhum docente.
- **Impacto no modelo**:
  - Enquanto a política estiver vazia, o avaliador declara H12 como **indisponível** (`None`).
  - Ambas as turmas são físicas únicas: não geram conflito de sala nem duplicam horários, mas ocupam a agenda de ambos os professores (conflitos, janelas, dias trabalhados e descanso).

---

## 5. Cadastro Físico Oficial de Salas de Aula

- **Arquivo**: `dados/processados/cadastro_salas_2026.csv`
- **População**: 22 salas observadas (16 salas comuns: 202, 204, 206, 213, 215, 217, 302, 304, 306, 308, 313, 315, 317, 319, 321, 404B; 6 laboratórios: L302, L303, L304, L305, L306, L307).
- **Colunas a preencher**: `capacidade_fisica`, `recursos_oficiais`, `validado`
- **Valores aceitos**:
  - `capacidade_fisica`: número inteiro positivo (capacidade real de assentos).
  - `validado`: `sim` ou `nao`.
- **Evidências nos dados**:
  - O arquivo registra `capacidade_minima_observada` (maior número de inscritos/vagas alocado na sala em 2026). A capacidade física real não deve ser menor do que a observada.
- **Impacto no modelo**:
  - Ativa H10 (capacidade física suficiente) e O4 (minimização de capacidade ociosa).

---

## 6. Recursos Especiais e Exigência de Laboratório por Disciplina

- **Arquivo**: `dados/processados/revisao_recursos_disciplinas_2026.csv`
- **População**: 99 disciplinas do recorte 2026.
- **Colunas a preencher**: `requer_laboratorio`, `recursos_requeridos`, `validado`
- **Valores aceitos**:
  - `requer_laboratorio`: `sim` ou `nao`.
  - `validado`: `sim` ou `nao`.
- **Evidências nos dados**:
  - O arquivo indica `usou_sala_comum`, `usou_laboratorio`, `alternou_tipo_de_sala` e `salas_observadas`.
- **Impacto no modelo**:
  - Ativa H11 (compatibilidade obrigatória de recursos e laboratórios).

---

## 7. Horários Fixos Institucionais

- **Arquivo**: `dados/processados/revisao_horarios_fixos_2026.csv`
- **População**: 180 turmas CC/SI de 2026.
- **Colunas a preencher**: `horario_fixo`, `validado`
- **Valores aceitos**: `sim` ou `nao`
- **Evidências nos dados**:
  - Disciplinas externas (ex.: Física, Cálculo, Administração) têm horários definidos por outros departamentos e devem ser marcadas como `horario_fixo = sim`.
  - Disciplinas do IC têm flexibilidade para otimização pelo solver (`horario_fixo = nao`), salvo determinação em contrário da coordenação.
- **Impacto no modelo**:
  - Define quais turmas podem ter seus horários alterados pelo solver em Fase 2.

---

## 8. Setores Departamentais e Padrões Semanais

- **Arquivo**: `dados/processados/revisao_setores_2026.csv`
- **População**: 99 disciplinas de 2026.
- **Colunas a preencher**: `setor_oficial`, `validado`
- **Evidências nos dados**:
  - Mapeia o setor histórico de 2025 e os dias da semana observados em 2026 e 2025.
- **Impacto no modelo**:
  - Fornece o domínio de dias da semana em que as disciplinas do setor podem ser ofertadas (diretriz da orientação: setores por dia).

---

## 9. Habilitação Docente por Disciplina

- **Arquivo**: `dados/processados/revisao_habilitacao_docente_2026.csv`
- **População**: 235 pares disciplina × docente.
- **Colunas a preencher**: `habilitado`, `validado`
- **Valores aceitos**: `sim` ou `nao`
- **Evidências nos dados**:
  - Registra a frequência histórica de alocação (2023–2025), o setor histórico e a observação em 2026.
- **Impacto no modelo**:
  - Restringe os candidatos viáveis para atribuição de professores no solver.

---

## 10. Prioridades Docentes e Pesos da Função Objetivo

- **Arquivo**: `dados/processados/revisao_prioridades_docentes_2026.csv`
- **População**: 73 docentes cadastrados/observados.
- **Colunas a preencher**: `prioridade`, `validado`
- **Valores aceitos**: número decimal $\ge 0$ (ex.: prioridade por tempo de casa, titulação ou neutra $= 1.0$).
- **Impacto no modelo**:
  - Modula o bônus de atendimento de preferências (O5).

---

## 11. Disciplinas Externas e Seções Alternativas

- **Arquivo**: `dados/processados/revisao_turmas_externas_2026.csv`
- **População**: 248 ofertas públicas não vinculadas ao PDF do IC ou de departamentos externos.
- **Colunas a preencher**: `tratamento_no_modelo`
- **Valores aceitos**: `fixar_horario_e_sala`, `ignorar_fora_do_ic`, `reserva_vagas`
- **Impacto no modelo**:
  - Define o tratamento de turmas compartilhadas com outros cursos da UFF.

---

## 12. Auditoria de Vínculos Não Triviais e Divergências de Horário

- **Arquivo**: `dados/processados/revisao_vinculos_2026.csv`
- **População**: 19 vínculos auditados.
- **Casos principais**:
  1. `2026-1-CGI00004-A1`: PDF indica sexta 18:00–22:00 (4h) enquanto página pública indica Sex 18:00–20:00 (2h). Preservado o horário do PDF no baseline.
  2. `2026-2-TCC00301-A1`: Linha compactada `A-A/B-A` expandida em `AA` (Ter 11–13) e `BA` (Qui 11–13).
  3. `2026-2-TCC00346-A1`: Linha compactada `A-A/C-A` expandida em `AA` (Ter 16–18) e `BA` (Qui 16–18).
  4. 11 turmas de optativas em 2026-2 que vieram sem código de turma no PDF (`SEM-TURMA`) e foram vinculadas pelo horário exato à turma `A1` pública.
  5. `TCC00307` e `TCC00344`: Turmas com nomenclatura normalizada (`B1A1` $\to$ `A1`, `A1` $\to$ `AA`).
- **Colunas a preencher**: `decisao` (opcional caso a coordenação aprove a correspondência sugerida).

---

## Como Validar e Executar

Após o preenchimento dos arquivos CSV acima:

1. Execute o verificador de prontidão:
   ```bash
   python scripts/check_readiness_2026.py --profile completo
   ```
2. Caso todas as decisões tenham sido registradas, o verificador atualizará automaticamente `"pronta_para_experimento": true` no arquivo `dados/processados/instancia_2026_cc_si.json`.
3. Os solvers e avaliadores poderão ser executados normalmente.
