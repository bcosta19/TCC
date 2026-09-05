# Validação do protótipo e próximos passos — 04/09/2026

O protótipo integrado executa o BasicSA nativo do pyoptframe sobre a instância
sintética de 2026. O piloto final produziu soluções conferidas por dois
avaliadores e por uma validação estrutural. A suíte passou de 70 para 81 testes.
O trabalho ainda precisa de decisões sobre turmas alternativas, protocolo
experimental e dados definitivos; esta rodada conclui a validação técnica
combinada, não a monografia nem os experimentos acadêmicos finais.

## Resultados do piloto final

Instância: 180 turmas, 329 encontros e 22 salas, com o perfil sintético já
existente. Foram mantidos pesos, horários fixos, habilitações, cotutoria e
universo H12 provisórios. Ambiente efetivamente usado: Python 3.14.7 e
OptFrame 5.1.0; Python 3.10 não foi verificado nesta rodada.

| Configuração | Violações hard | Docentes abaixo de H12 | Conflitos de sala | Janelas | Dias de aula somados por docente/semestre |
|---|---:|---:|---:|---:|---:|
| Baseline observado, avaliado com proxies | 27 | 14 | 3 | 46 | 233 |
| Entrada gulosa | 12 | 2 | 0 | 36 | 215 |
| Melhor SA de referência | 10 | 0 | 0 | 80 | 230 |
| Melhor BasicSA nativo | 10 | 0 | 0 | 107 | 237 |

O SA de referência zerou H12 em 3/5 execuções; o nativo, em 1/5. Ambos
preservaram as dez sobreposições curriculares congeladas. A redução hard do
baseline para o melhor nativo foi de 62,96%, acompanhada de piora em janelas e
dias de aula. O resultado não é uma solução plenamente viável sob H8 atual.

As duas buscas partiram da mesma solução gulosa. A referência usou 1.500
avaliações por semente; o nativo, dez segundos, com 422–471 avaliações
registradas pelo motor. Os resfriamentos e temperaturas também diferem.
Esses números validam a integração, mas não permitem atribuir superioridade
a um algoritmo ou comparar diretamente eficiência por avaliação.

A semente controla a vizinhança Python. O adaptador não configura o RNG
interno do OptFrame; a parada por tempo também varia com o ambiente. O fluxo
é reexecutável e rastreável, mas não se promete repetição exata do resultado
nativo. Esse ponto precisa ser resolvido ou explicitamente tratado antes do
protocolo experimental final.

Artefatos do piloto definitivo:

- [Relatório por execução](../dados/processados/piloto_optframe_20260904_final/relatorio.md).
- [Métricas completas em CSV](../dados/processados/piloto_optframe_20260904_final/resultados.csv).
- [Manifesto de ambiente, configurações e hashes](../dados/processados/piloto_optframe_20260904_final/manifesto.json).
- A instância de entrada e as dez soluções ficam na mesma pasta, localmente,
  em JSONs ignorados pelo Git.

## O que significam os dez conflitos curriculares

O diagnóstico recontou exatamente dez sobreposições, envolvendo dez ofertas.
Os horários das dez ofertas coincidem entre as extrações preservadas dos PDFs
e a coleta web local. Os grupos decorrem da grade SI versionada:

| Grupo | Semestre | Sobreposições | Existe uma escolha de turma por código sem choque no recorte? |
|---|---|---:|---|
| SI-P1 | 2026/1 | 4 | Sim |
| SI-P1 | 2026/2 | 4 | Sim |
| SI-P6 | 2026/1 | 2 | Sim |

Exemplo: em 2026/1, TCC00332-A1 coincide com TCC00354-A1, mas a combinação
TCC00332-A1 + TCC00354-B1 evita o choque. Para SI-P6, TCC00336-Z1 coincide
com TCC00338-A1, enquanto TCC00336-A1 oferece outra opção temporal.
As testemunhas completas incluem os demais códigos presentes em cada grupo.

O avaliador ignora choques entre seções do mesmo código, mas conta choques
entre ofertas de códigos distintos, mesmo quando são alternativas. Portanto,
há uma questão de interpretação de H8, e não evidência de que seja necessário
liberar cinco ofertas para permitir uma trajetória individual.

Isso não prova suficiência de vagas, elegibilidade de todas as seções,
atendimento coletivo dos alunos ou cobertura do currículo completo. Há
componentes externos fora do recorte. O diagnóstico não substitui um modelo
de matrícula ou de demanda e não muda H8 automaticamente.

[Evidências e testemunhas](../dados/processados/diagnostico_curricular_2026/relatorio.md)
em três CSVs: contagem detalhada, escolha por grupo e confronto das fontes.

## Correções e validações técnicas

- O teste de não piora aceitava qualquer número não negativo de violações.
  Agora compara a chave real do objetivo com a solução gulosa.
- A reversibilidade passou a verificar o estado completo; movimentos de
  professor, horário e sala são desfeitos e refeitos em testes explícitos.
- O benchmark anterior calculava a gulosa, mas iniciava as buscas no baseline.
  O executor agora usa a mesma entrada gulosa para ambas.
- O piloto salva métricas, soluções e manifesto; confere hard, soft e déficit
  H12 entre avaliador direto e referência. Também confere a energia nativa
  contra a solução retornada e rejeita resultados piores que a entrada.
- A validação estrutural detecta turmas perdidas/duplicadas, sala ausente ou
  desconhecida, atribuições inconsistentes, mudanças de dados estáticos e
  mudanças de professor/horário fora dos domínios ou das condições fixas.
  Ela complementa os contadores existentes, sem reformular H1–H12.
- Tempo e parâmetros inválidos e H12 indisponível são rejeitados antes de
  iniciar a busca nativa; a entrada também passa pela validação estrutural.
- O hash da base da instância sintética estava antigo. A regeneração em
  memória mostrou diferenças apenas em `readiness_profiles` e no hash da
  base. A instância foi regenerada antes do piloto final, preservando os
  dados usados pela busca. O executor agora rejeita configuração/base com
  hash divergente do manifesto sintético.
- A validação do gerador sintético retornou zero erros; cobertura e hashes
  das tabelas de revisão conferem. A instância institucional continua com
  `pronta_para_experimento=false`.
- Suíte completa: 81 testes aprovados; após o último reforço da validação
  estrutural, seus cinco testes focados também passaram. Diff sem erros de
  whitespace. Não foi refeita a coleta web nem a pipeline integral.

As verificações cobrem o núcleo e o piloto desta rodada. Não equivalem a uma
auditoria exaustiva de toda entrada possível, de todos os solvers e de toda a
modelagem. As tabelas institucionais existentes foram preservadas. README e
PLANO receberam o estado atual; os relatórios antigos ganharam referências
para esta atualização. A política pública de IA foi alinhada ao AGENTS.md.

## Próximos passos recomendados

1. **Fechar uma hipótese provisória para H8 com o aluno.** Manter a regra atual
   é simples e comparável ao benchmark existente, mas exige ausência de
   choque entre ofertas alternativas. Proteger trajetórias permitidas é mais
   próximo da escolha individual, mas precisa explicitar elegibilidade das
   seções; atendimento coletivo também exige demanda e vagas. A recomendação
   é usar o diagnóstico como evidência e definir essa semântica antes de
   flexibilizar horários. Nenhuma dessas mudanças foi aplicada nesta rodada.
2. **Preparar o protocolo nativo.** Investigar o controle do RNG interno,
   definir orçamento e calibração comparáveis e registrar o custo do
   construtivo. Se houver gargalo na ponte Python/nativo, medi-lo antes de
   otimizar. Não ampliar a comparação para ILS/VNS nativos antes de fechar
   esse contrato de execução.
3. **Aplicar os CSVs de revisão ao JSON definitivo.** O verificador existente
   verifica preenchimento/prontidão; falta a materialização integral das
   decisões institucionais na instância consumida pelo solver. Implementar
   isso preservando a origem dos valores e sem preencher ausências como se
   fossem dados oficiais.
4. **Definir dados e hipóteses finais.** As checagens atuais produzem 366
   mensagens no perfil baseline e 1.671 no conjunto completo; são mensagens
   de campos e validações, não esse número de decisões independentes.
   Setores, habilitações, salas, prioridades e política institucional ainda
   precisam de validação ou de hipóteses aceitas para o estudo.
5. **Executar o estudo e fechar o texto.** Com instância e protocolo definidos,
   executar as comparações escolhidas, produzir gráficos e análise, atualizar
   a descrição técnica da monografia e concluir resultados/discussão/artigo.
   O texto LaTeX não foi reescrito nem compilado nesta rodada.

## Como reexecutar

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/build_synthetic_instance_2026.py
.venv/bin/python scripts/diagnose_curriculum_conflicts_2026.py
.venv/bin/python scripts/benchmark_optframe_sa_2026.py 10
```

O último comando cria uma nova pasta de piloto, sem sobrescrever o definitivo.
Alterações desta rodada e alterações que já existiam permanecem locais, sem
commit ou push.
