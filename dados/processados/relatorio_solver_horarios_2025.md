# Execução do solver de salas e horários — 2025

Algoritmo: **Simulated Annealing**, com movimentos de horário e de sala.

## Configuração

- Seed: `2025`
- Iterações: `1000`
- Movimentos tentados: `948`
- Movimentos aceitos: `550`
- Turmas flexíveis: `148`
- Turmas fixas: externas e projetos finais, conforme a regra provisória de domínios.

## Comparação

| Métrica | Instância inicial | Melhor solução |
|---|---:|---:|
| Score | 23002611.0 | 1004583.0 |
| Violações hard | 23 | 1 |
| Conflitos de sala | 13 | 0 |
| Conflitos de professor | 0 | 0 |
| Conflitos curriculares | 10 | 1 |
| Recursos incompatíveis | 0 | 0 |
| Descanso insuficiente | 0 | 0 |
| Janelas | 28 | 112 |
| Desperdício estimado | 2172.0 | 3965.0 |
| Distância estimada | 171 | 266 |

Foram alteradas **135 turmas**: **102** tiveram horário alterado e **135** tiveram sala alterada. Alterações em turmas marcadas como fixas: **0**.

## Alterações encontradas

| ID | Código | Disciplina | Horário antes | Horário depois | Sala antes | Sala depois |
|---|---|---|---|---|---|---|
| 2025-1-TCC00284-A1 | TCC00284 | ALGORITMOS EM GRAFOS | sexta 09:00–13:00 | sexta 18:00–22:00 | sexta 09:00–13:00: 206 | sexta 18:00–22:00: 215 |
| 2025-1-TCC00285-A1 | TCC00285 | ANÁLISE E PROJETO DE ALGORITMOS | terca 11:00–13:00; quinta 11:00–13:00 | terca 14:00–16:00; quinta 14:00–16:00 | terca 11:00–13:00: 215; quinta 11:00–13:00: 215 | terca 14:00–16:00: 215; quinta 14:00–16:00: 404B |
| 2025-1-TCC00286-B1 | TCC00286 | ARQUITETURAS DE COMPUTADORES | terca 09:00–11:00; quinta 09:00–11:00 | terca 20:00–22:00; quinta 18:00–20:00 | terca 09:00–11:00: 308; quinta 09:00–11:00: 308 | terca 20:00–22:00: 308; quinta 18:00–20:00: 204 |
| 2025-1-TCC00336-A1 | TCC00336 | BANCO DE DADOS NÃO CONVENCIONAIS | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 20:00–22:00: 321; quarta 20:00–22:00: 321 | segunda 20:00–22:00: 321; quarta 20:00–22:00: 404B |
| 2025-1-TCC00287-A1 | TCC00287 | BANCO DE DADOS I | segunda 09:00–11:00; quarta 09:00–11:00 | segunda 07:00–09:00; quarta 18:00–20:00 | segunda 09:00–11:00: 321; quarta 09:00–11:00: 321 | segunda 07:00–09:00: 321; quarta 18:00–20:00: 321 |
| 2025-1-TCC00288-A1 | TCC00288 | BANCO DE DADOS II | segunda 07:00–09:00; quarta 07:00–09:00 | segunda 07:00–09:00; quarta 20:00–22:00 | segunda 07:00–09:00: L302; quarta 07:00–09:00: L302 | segunda 07:00–09:00: L307; quarta 20:00–22:00: L306 |
| 2025-1-TCC00289-A1 | TCC00289 | COMPILADORES | segunda 09:00–11:00; quarta 09:00–11:00 | segunda 09:00–11:00; quarta 16:00–18:00 | segunda 09:00–11:00: 215; quarta 09:00–11:00: 215 | segunda 09:00–11:00: 215; quarta 16:00–18:00: 302 |
| 2025-1-TCC00290-A1 | TCC00290 | COMPUTAÇÃO E SOCIEDADE | quinta 11:00–13:00 | quinta 09:00–11:00 | quinta 11:00–13:00: 217 | quinta 09:00–11:00: 217 |
| 2025-1-TCC00222-A1 | TCC00222 | COMPUTAÇÃO E SOCIEDADE PARA SISTEMAS DE INFORMAÇÃO | quinta 18:00–22:00 | quinta 18:00–22:00 | quinta 18:00–22:00: 213 | quinta 18:00–22:00: 215 |
| 2025-1-TCC00291-A1 | TCC00291 | COMPUTAÇÃO GRÁFICA | segunda 11:00–13:00; quarta 11:00–13:00 | segunda 11:00–13:00; quarta 11:00–13:00 | segunda 11:00–13:00: 319; quarta 11:00–13:00: 319 | segunda 11:00–13:00: 404B; quarta 11:00–13:00: 308 |
| 2025-1-TCC00226-X1 | TCC00226 | DESENVOLVIMENTO WEB | segunda 11:00–13:00; quarta 11:00–13:00 | segunda 11:00–13:00; quarta 18:00–20:00 | segunda 11:00–13:00: L302; quarta 11:00–13:00: L302 | segunda 11:00–13:00: L306; quarta 18:00–20:00: L305 |
| 2025-1-TCC00225-A1 | TCC00225 | ENGENHARIA DE SOFTWARE | terca 18:00–20:00; quinta 18:00–20:00 | terca 07:00–09:00; quinta 18:00–20:00 | terca 18:00–20:00: 217; quinta 18:00–20:00: 217 | terca 07:00–09:00: 217; quinta 18:00–20:00: 404B |
| 2025-1-TCC00293-A1 | TCC00293 | ENGENHARIA DE SOFTWARE II | segunda 09:00–11:00; quarta 09:00–11:00 | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 09:00–11:00: 217; quarta 09:00–11:00: 217 | segunda 20:00–22:00: 217; quarta 20:00–22:00: 217 |
| 2025-1-TCC00348-A1 | TCC00348 | ESTRUTURAS DE DADOS E SEUS ALGORITMOS | terca 11:00–13:00; quinta 11:00–13:00 | terca 14:00–16:00; quinta 11:00–13:00 | terca 11:00–13:00: 204; quinta 11:00–13:00: 204 | terca 14:00–16:00: 204; quinta 11:00–13:00: 404B |
| 2025-1-TCC00348-B1 | TCC00348 | ESTRUTURAS DE DADOS E SEUS ALGORITMOS | terca 11:00–13:00; quinta 11:00–13:00 | terca 14:00–16:00; quinta 14:00–16:00 | terca 11:00–13:00: 319; quinta 11:00–13:00: 319 | terca 14:00–16:00: 217; quinta 14:00–16:00: 319 |
| 2025-1-TCC00331-A1 | TCC00331 | ESTRUTURAS DE DADOS PARA SISTEMAS DE INFORMAÇÃO | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 07:00–09:00; quarta 18:00–20:00 | segunda 18:00–20:00: 404B; quarta 18:00–20:00: L306 | segunda 07:00–09:00: 404B; quarta 18:00–20:00: L306 |
| 2025-1-TCC00331-X1 | TCC00331 | ESTRUTURAS DE DADOS PARA SISTEMAS DE INFORMAÇÃO | terca 20:00–22:00; quinta 20:00–22:00 | terca 07:00–09:00; quinta 07:00–09:00 | terca 20:00–22:00: 308; quinta 20:00–22:00: L306 | terca 07:00–09:00: 319; quinta 07:00–09:00: L302 |
| 2025-1-TCC00296-A1 | TCC00296 | FUNDAMENTOS DE ARQUITETURAS DE COMPUTADORES | terca 14:00–16:00; quinta 14:00–16:00 | terca 18:00–20:00; quinta 18:00–20:00 | terca 14:00–16:00: 302; quinta 14:00–16:00: 302 | terca 18:00–20:00: 302; quinta 18:00–20:00: 302 |
| 2025-1-TCC00296-B1 | TCC00296 | FUNDAMENTOS DE ARQUITETURAS DE COMPUTADORES | terca 14:00–16:00; quinta 14:00–16:00 | terca 14:00–16:00; quinta 18:00–20:00 | terca 14:00–16:00: 321; quinta 14:00–16:00: 321 | terca 14:00–16:00: 321; quinta 18:00–20:00: 321 |
| 2025-1-TCC00332-B1 | TCC00332 | FUNDAMENTOS DE SISTEMAS DE INFORMAÇÃO | terca 20:00–22:00; quinta 20:00–22:00 | terca 11:00–13:00; quinta 16:00–18:00 | terca 20:00–22:00: 317; quinta 20:00–22:00: 317 | terca 11:00–13:00: 308; quinta 16:00–18:00: 302 |
| 2025-1-TCC00354-A1 | TCC00354 | FUNDAMENTOS MATEMÁTICOS PARA COMPUTAÇÃO | terca 18:00–20:00; quinta 18:00–20:00 | terca 07:00–09:00; quinta 07:00–09:00 | terca 18:00–20:00: 202; quinta 18:00–20:00: 202 | terca 07:00–09:00: 202; quinta 07:00–09:00: 202 |
| 2025-1-TCC00354-B1 | TCC00354 | FUNDAMENTOS MATEMÁTICOS PARA COMPUTAÇÃO | terca 20:00–22:00; quinta 20:00–22:00 | terca 16:00–18:00; quinta 20:00–22:00 | terca 20:00–22:00: 202; quinta 20:00–22:00: 202 | terca 16:00–18:00: 202; quinta 20:00–22:00: 202 |
| 2025-1-TCC00363-A1 | TCC00363 | GERÊNCIA DE PROJETOS E MANUT DE SOFTWARE | terca 20:00–22:00; quinta 20:00–22:00 | terca 09:00–11:00; quinta 11:00–13:00 | terca 20:00–22:00: 206; quinta 20:00–22:00: 206 | terca 09:00–11:00: 206; quinta 11:00–13:00: 206 |
| 2025-1-TCC00324-A1 | TCC00324 | GOVERNANÇA EM TECNOLOGIA DA INFORMAÇÃO | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 16:00–18:00; quarta 11:00–13:00 | segunda 20:00–22:00: 206; quarta 20:00–22:00: 206 | segunda 16:00–18:00: 213; quarta 11:00–13:00: 206 |
| 2025-1-TCC00298-A1 | TCC00298 | INTERFACE HOMEM MAQUINA | segunda 11:00–13:00; quarta 11:00–13:00 | segunda 20:00–22:00; quarta 09:00–11:00 | segunda 11:00–13:00: 202; quarta 11:00–13:00: 202 | segunda 20:00–22:00: 202; quarta 09:00–11:00: 202 |
| 2025-1-TCC00337-A1 | TCC00337 | INTRODUÇÃO A INTERAÇÃO HUMANO-COMPUTADOR | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 18:00–20:00: 206; quarta 18:00–20:00: 206 | segunda 18:00–20:00: 206; quarta 18:00–20:00: 213 |
| 2025-1-TCC00361-A1 | TCC00361 | INTRODUÇÃO AO DESENVOLVIMENTO WEB | sexta 18:00–22:00 | sexta 09:00–13:00 | sexta 18:00–22:00: L306 | sexta 09:00–13:00: L302 |
| 2025-1-TCC00301-A-A/B-A | TCC00301 | LABORATÓRIO DE PROGRAMAÇÃO DE JOGOS | terca 11:00–13:00; quinta 11:00–13:00 | terca 09:00–11:00; quinta 07:00–09:00 | terca 11:00–13:00: L305; quinta 11:00–13:00: L305 | terca 09:00–11:00: L303; quinta 07:00–09:00: L305 |
| 2025-1-TCC00344-A1 | TCC00344 | LABORATÓRIO DE PROGRAMAÇÃO PARALELA | segunda 07:00–09:00; quarta 07:00–09:00 | segunda 11:00–13:00; quarta 20:00–22:00 | segunda 07:00–09:00: L305; quarta 07:00–09:00: L305 | segunda 11:00–13:00: L305; quarta 20:00–22:00: L305 |
| 2025-1-TCC00346-A-A/C-A | TCC00346 | LABORATÓRIO DE RESOLUÇÃO DE PROBLEMAS | terca 16:00–18:00; quinta 16:00–18:00 | terca 20:00–22:00; quinta 20:00–22:00 | terca 16:00–18:00: L305; quinta 16:00–18:00: L305 | terca 20:00–22:00: L306; quinta 20:00–22:00: L304 |
| 2025-1-TCC00346-B-A/D-A | TCC00346 | LABORATÓRIO DE RESOLUÇÃO DE PROBLEMAS | terca 16:00–18:00; quinta 16:00–18:00 | terca 09:00–11:00; quinta 16:00–18:00 | terca 16:00–18:00: L306; quinta 16:00–18:00: L306 | terca 09:00–11:00: L306; quinta 16:00–18:00: L307 |
| 2025-1-TCC00355-E-A | TCC00355 | LABORATÓRIO DE RESOLUÇÃO DE PROBLEMAS | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 07:00–09:00; quarta 20:00–22:00 | segunda 20:00–22:00: L303; quarta 20:00–22:00: L303 | segunda 07:00–09:00: L303; quarta 20:00–22:00: L303 |
| 2025-1-TCC00355-F-A | TCC00355 | LABORATÓRIO DE RESOLUÇÃO DE PROBLEMAS | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 20:00–22:00: L306; quarta 20:00–22:00: L306 | segunda 20:00–22:00: L305; quarta 20:00–22:00: L302 |
| 2025-1-TCC00304-A1 | TCC00304 | LINGUAGENS DE PROGRAMAÇÃO | segunda 11:00–13:00; quarta 11:00–13:00 | segunda 16:00–18:00; quarta 20:00–22:00 | segunda 11:00–13:00: 215; quarta 11:00–13:00: 215 | segunda 16:00–18:00: 204; quarta 20:00–22:00: 204 |
| 2025-1-TCC00305-A1 | TCC00305 | LINGUAGENS FORMAIS E TEORIA DA COMPUTAÇÃO | segunda 07:00–09:00; quarta 07:00–09:00 | segunda 07:00–09:00; quarta 16:00–18:00 | segunda 07:00–09:00: 206; quarta 07:00–09:00: 206 | segunda 07:00–09:00: 215; quarta 16:00–18:00: 206 |
| 2025-1-TCC00306-A1 | TCC00306 | METODOS NUMERICOS | terca 09:00–11:00; quinta 09:00–11:00 | terca 16:00–18:00; quinta 20:00–22:00 | terca 09:00–11:00: 213; quinta 09:00–11:00: 213 | terca 16:00–18:00: 213; quinta 20:00–22:00: 213 |
| 2025-1-TCC00318-A1 | TCC00318 | PESQUISA OPERACIONAL | terca 09:00–11:00; quinta 09:00–11:00 | terca 09:00–11:00; quinta 20:00–22:00 | terca 09:00–11:00: 217; quinta 09:00–11:00: 217 | terca 09:00–11:00: 217; quinta 20:00–22:00: 206 |
| 2025-1-TCC00334-A1 | TCC00334 | PRINCIPIO DE BANCO DE DADOS | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 18:00–20:00: 321; quarta 18:00–20:00: 321 | segunda 18:00–20:00: 321; quarta 18:00–20:00: 204 |
| 2025-1-TCC00307-A1 | TCC00307 | PROGRAMAÇÃO CIENTÍFICA | terca 09:00–11:00; quinta 09:00–11:00 | terca 11:00–13:00; quinta 09:00–11:00 | terca 09:00–11:00: 215; quinta 09:00–11:00: 215 | terca 11:00–13:00: 204; quinta 09:00–11:00: 215 |
| 2025-1-TCC00366-A1 | TCC00366 | PROGRAMAÇÃO DE COMPUTADORES I | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 18:00–20:00; quarta 07:00–09:00 | segunda 18:00–20:00: 302; quarta 18:00–20:00: 302 | segunda 18:00–20:00: 213; quarta 07:00–09:00: 206 |
| 2025-1-TCC00366-B1 | TCC00366 | PROGRAMAÇÃO DE COMPUTADORES I | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 18:00–20:00; quarta 09:00–11:00 | segunda 18:00–20:00: 204; quarta 18:00–20:00: L305 | segunda 18:00–20:00: 204; quarta 09:00–11:00: L305 |
| 2025-1-TCC00308-A1 | TCC00308 | PROGRAMAÇÃO DE COMPUTADORES I | segunda 16:00–18:00; quarta 16:00–18:00 | segunda 11:00–13:00; quarta 09:00–11:00 | segunda 16:00–18:00: 313; quarta 16:00–18:00: L306 | segunda 11:00–13:00: 306; quarta 09:00–11:00: L303 |
| 2025-1-TCC00308-B1 | TCC00308 | PROGRAMAÇÃO DE COMPUTADORES I | segunda 16:00–18:00; quarta 16:00–18:00 | segunda 09:00–11:00; quarta 20:00–22:00 | segunda 16:00–18:00: L306; quarta 16:00–18:00: 308 | segunda 09:00–11:00: L307; quarta 20:00–22:00: 319 |
| 2025-1-TCC00356-B1 | TCC00356 | PROGRAMAÇÃO DE COMPUTADORES II | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 07:00–09:00; quarta 07:00–09:00 | segunda 20:00–22:00: L302; quarta 20:00–22:00: 319 | segunda 07:00–09:00: L302; quarta 07:00–09:00: 213 |
| 2025-1-TCC00347-A1 | TCC00347 | PROGRAMAÇÃO ESTRUTURADA | terca 09:00–11:00; quinta 09:00–11:00 | terca 11:00–13:00; quinta 18:00–20:00 | terca 09:00–11:00: L304; quinta 09:00–11:00: 204 | terca 11:00–13:00: L303; quinta 18:00–20:00: 213 |
| 2025-1-TCC00347-B1 | TCC00347 | PROGRAMAÇÃO ESTRUTURADA | terca 09:00–11:00; quinta 09:00–11:00 | terca 07:00–09:00; quinta 14:00–16:00 | terca 09:00–11:00: L306; quinta 09:00–11:00: 202 | terca 07:00–09:00: L305; quinta 14:00–16:00: 217 |
| 2025-1-TCC00328-B1 | TCC00328 | PROGRAMAÇÃO ORIENTADA A OBJETOS | segunda 16:00–18:00; quarta 16:00–18:00 | segunda 09:00–11:00; quarta 18:00–20:00 | segunda 16:00–18:00: 204; quarta 16:00–18:00: L304 | segunda 09:00–11:00: 202; quarta 18:00–20:00: L304 |
| 2025-1-TCC00357-A1 | TCC00357 | PROGRAMAÇÃO ORIENTADA A OBJETOS I | sexta 18:00–22:00 | sexta 09:00–13:00 | sexta 18:00–22:00: 215 | sexta 09:00–13:00: 204 |
| 2025-1-TCC00357-X1 | TCC00357 | PROGRAMAÇÃO ORIENTADA A OBJETOS I | terca 18:00–20:00; quinta 18:00–20:00 | terca 18:00–20:00; quinta 18:00–20:00 | terca 18:00–20:00: 308; quinta 18:00–20:00: L306 | terca 18:00–20:00: 404B; quinta 18:00–20:00: L305 |
| 2025-1-TCC00335-A1 | TCC00335 | PROJETO DE BANCO DE DADOS PARA SI | terca 20:00–22:00; quinta 20:00–22:00 | terca 20:00–22:00; quinta 20:00–22:00 | terca 20:00–22:00: 215; quinta 20:00–22:00: L302 | terca 20:00–22:00: 404B; quinta 20:00–22:00: L302 |
| 2025-1-TCC00312-A1 | TCC00312 | PROJETO DE SOFTWARE | segunda 11:00–13:00; quarta 11:00–13:00 | segunda 16:00–18:00; quarta 11:00–13:00 | segunda 11:00–13:00: 217; quarta 11:00–13:00: 217 | segunda 16:00–18:00: 217; quarta 11:00–13:00: 217 |
| 2025-1-TCC00338-A1 | TCC00338 | PROJETO DE SOFTWARE | terca 18:00–20:00; quinta 18:00–20:00 | terca 11:00–13:00; quinta 16:00–18:00 | terca 18:00–20:00: 206; quinta 18:00–20:00: 206 | terca 11:00–13:00: 404B; quinta 16:00–18:00: 215 |
| 2025-1-TCC00365-A1 | TCC00365 | QUALIDADE E TESTE DE SOFTWARE | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 18:00–20:00: 217; quarta 18:00–20:00: L304 | segunda 18:00–20:00: 217; quarta 18:00–20:00: L302 |
| 2025-1-TCC00359-A1 | TCC00359 | REDES DE COMPUTADORES | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 11:00–13:00; quarta 16:00–18:00 | segunda 20:00–22:00: 215; quarta 20:00–22:00: 215 | segunda 11:00–13:00: 215; quarta 16:00–18:00: 215 |
| 2025-1-TCC00313-A1 | TCC00313 | REDES DE COMPUTADORES I | terca 07:00–09:00; quinta 07:00–09:00 | terca 07:00–09:00; quinta 07:00–09:00 | terca 07:00–09:00: 213; quinta 07:00–09:00: 213 | terca 07:00–09:00: 321; quinta 07:00–09:00: 213 |
| 2025-1-TCC00314-A1 | TCC00314 | REDES DE COMPUTADORES II | terca 11:00–13:00; quinta 11:00–13:00 | terca 16:00–18:00; quinta 14:00–16:00 | terca 11:00–13:00: 306; quinta 11:00–13:00: 306 | terca 16:00–18:00: 302; quinta 14:00–16:00: 306 |
| 2025-1-TCC00341-A1 | TCC00341 | SEGURANÇA DA INFORMAÇÃO | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 11:00–13:00; quarta 11:00–13:00 | segunda 20:00–22:00: 213; quarta 20:00–22:00: 213 | segunda 11:00–13:00: 213; quarta 11:00–13:00: 321 |
| 2025-1-TCC00358-A1 | TCC00358 | SISTEMAS COMPUTACIONAIS | quinta 18:00–22:00 | quinta 18:00–22:00 | quinta 18:00–22:00: 321 | quinta 18:00–22:00: 217 |
| 2025-1-TCC00358-B1 | TCC00358 | SISTEMAS COMPUTACIONAIS | quinta 18:00–22:00 | quinta 18:00–22:00 | quinta 18:00–22:00: 308 | quinta 18:00–22:00: 213 |
| 2025-1-TCC00315-A1 | TCC00315 | SISTEMAS DISTRIBUÍDOS | terca 07:00–09:00; quinta 07:00–09:00 | terca 16:00–18:00; quinta 18:00–20:00 | terca 07:00–09:00: 317; quinta 07:00–09:00: 317 | terca 16:00–18:00: 317; quinta 18:00–20:00: 317 |
| 2025-1-TCC00362-A1 | TCC00362 | SISTEMAS DISTRIBUÍDOS PARA SISTEMAS DE INFORMAÇÃO | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 20:00–22:00: 204; quarta 20:00–22:00: 204 | segunda 20:00–22:00: 204; quarta 20:00–22:00: 321 |
| 2025-1-TCC00316-A1 | TCC00316 | SISTEMAS OPERACIONAIS | terca 11:00–13:00; quinta 11:00–13:00 | terca 07:00–09:00; quinta 11:00–13:00 | terca 11:00–13:00: 302; quinta 11:00–13:00: 302 | terca 07:00–09:00: 302; quinta 11:00–13:00: 215 |
| 2025-1-TCC00360-A1 | TCC00360 | VISUALIZAÇÃO DE DADOS | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 18:00–20:00: 317; quarta 18:00–20:00: 317 | segunda 18:00–20:00: 202; quarta 18:00–20:00: 217 |
| 2025-1-TCC00242-A1 | TCC00242 | Ementa Variável I / Graduação - Introdução à programação funcional - TCC0024X TÓPICOS EM COMPUTAÇÃO X | terca 20:00–22:00; quinta 20:00–22:00 | terca 18:00–20:00; quinta 07:00–09:00 | terca 20:00–22:00: 306; quinta 20:00–22:00: 306 | terca 18:00–20:00: 306; quinta 07:00–09:00: 306 |
| 2025-1-TCC00212-A1 | TCC00212 | Ementa Variável II / EMPREENDEDORISMO | terca 18:00–20:00; quinta 18:00–20:00 | terca 11:00–13:00; quinta 20:00–22:00 | terca 18:00–20:00: 313; quinta 18:00–20:00: 313 | terca 11:00–13:00: 313; quinta 20:00–22:00: 313 |
| 2025-2-TCC00284-A1 | TCC00284 | ALGORITMOS EM GRAFOS | terca 09:00–11:00; quinta 09:00–11:00 | terca 11:00–13:00; quinta 18:00–20:00 | terca 09:00–11:00: 308; quinta 09:00–11:00: 308 | terca 11:00–13:00: 217; quinta 18:00–20:00: 206 |
| 2025-2-TCC00285-A1 | TCC00285 | ANÁLISE E PROJETO DE ALGORITMOS | terca 11:00–13:00; quinta 11:00–13:00 | terca 11:00–13:00; quinta 11:00–13:00 | terca 11:00–13:00: 215; quinta 11:00–13:00: 215 | terca 11:00–13:00: 202; quinta 11:00–13:00: 202 |
| 2025-2-TCC00286-A1 | TCC00286 | ARQUITETURAS DE COMPUTADORES | terca 09:00–11:00; quinta 09:00–11:00 | terca 16:00–18:00; quinta 16:00–18:00 | terca 09:00–11:00: 302; quinta 09:00–11:00: 302 | terca 16:00–18:00: 302; quinta 16:00–18:00: 308 |
| 2025-2-TCC00286-B1 | TCC00286 | ARQUITETURAS DE COMPUTADORES | terca 09:00–11:00; quinta 09:00–11:00 | terca 09:00–11:00; quinta 09:00–11:00 | terca 09:00–11:00: 308; quinta 09:00–11:00: 308 | terca 09:00–11:00: 308; quinta 09:00–11:00: 217 |
| 2025-2-TCC00349-A1 | TCC00349 | AVALIAÇÃO DE DESEMPENHO | terca 07:00–09:00; quinta 07:00–09:00 | terca 18:00–20:00; quinta 07:00–09:00 | terca 07:00–09:00: 204; quinta 07:00–09:00: 204 | terca 18:00–20:00: 321; quinta 07:00–09:00: 204 |
| 2025-2-TCC00336-A1 | TCC00336 | BANCO DE DADOS NÃO CONVENCIONAIS | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 09:00–11:00; quarta 07:00–09:00 | segunda 20:00–22:00: sem sala; quarta 20:00–22:00: sem sala | segunda 09:00–11:00: 321; quarta 07:00–09:00: 217 |
| 2025-2-TCC00287-A1 | TCC00287 | BANCO DE DADOS I | segunda 07:00–09:00; quarta 07:00–09:00 | segunda 07:00–09:00; quarta 07:00–09:00 | segunda 07:00–09:00: 215; quarta 07:00–09:00: 215 | segunda 07:00–09:00: 404B; quarta 07:00–09:00: 215 |
| 2025-2-TCC00288-A1 | TCC00288 | BANCO DE DADOS II | segunda 11:00–13:00; quarta 11:00–13:00 | segunda 11:00–13:00; quarta 20:00–22:00 | segunda 11:00–13:00: 215; quarta 11:00–13:00: 215 | segunda 11:00–13:00: 321; quarta 20:00–22:00: 215 |
| 2025-2-TCC00289-A1 | TCC00289 | COMPILADORES | segunda 07:00–09:00; quarta 07:00–09:00 | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 07:00–09:00: 308; quarta 07:00–09:00: 308 | segunda 20:00–22:00: 302; quarta 20:00–22:00: 308 |
| 2025-2-TCC00290-A1 | TCC00290 | COMPUTAÇÃO E SOCIEDADE | quinta 11:00–13:00 | quinta 20:00–22:00 | quinta 11:00–13:00: 217 | quinta 20:00–22:00: 204 |
| 2025-2-TCC00222-A1 | TCC00222 | COMPUTAÇÃO E SOCIEDADE PARA SISTEMAS DE INFORMAÇÃO | quinta 18:00–22:00 | quinta 18:00–22:00 | quinta 18:00–22:00: 215 | quinta 18:00–22:00: 302 |
| 2025-2-TCC00291-A1 | TCC00291 | COMPUTAÇÃO GRÁFICA | segunda 11:00–13:00; quarta 11:00–13:00 | segunda 11:00–13:00; quarta 11:00–13:00 | segunda 11:00–13:00: 319; quarta 11:00–13:00: 319 | segunda 11:00–13:00: 319; quarta 11:00–13:00: 302 |
| 2025-2-TCC00226-A1 | TCC00226 | DESENVOLVIMENTO WEB | segunda 09:00–11:00; quarta 09:00–11:00 | segunda 09:00–11:00; quarta 16:00–18:00 | segunda 09:00–11:00: L302; quarta 09:00–11:00: L302 | segunda 09:00–11:00: L306; quarta 16:00–18:00: L302 |
| 2025-2-TCC00368-A1 | TCC00368 | P.O. PARA S.I. (WEB AVANC.) | terca 20:00–22:00; quinta 20:00–22:00 | terca 16:00–18:00; quinta 16:00–18:00 | terca 20:00–22:00: 313; quinta 20:00–22:00: 313 | terca 16:00–18:00: 306; quinta 16:00–18:00: 313 |
| 2025-2-TCC00225-A1 | TCC00225 | ENGENHARIA DE SOFTWARE | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 18:00–20:00: sem sala; quarta 18:00–20:00: sem sala | segunda 18:00–20:00: 302; quarta 18:00–20:00: sem sala |
| 2025-2-TCC00292-A1 | TCC00292 | ENGENHARIA DE SOFTWARE I | segunda 09:00–11:00; quarta 09:00–11:00 | segunda 09:00–11:00; quarta 20:00–22:00 | segunda 09:00–11:00: 213; quarta 09:00–11:00: 213 | segunda 09:00–11:00: 202; quarta 20:00–22:00: 213 |
| 2025-2-TCC00293-A1 | TCC00293 | ENGENHARIA DE SOFTWARE II | segunda 07:00–09:00; quarta 07:00–09:00 | segunda 07:00–09:00; quarta 07:00–09:00 | segunda 07:00–09:00: 213; quarta 07:00–09:00: 213 | segunda 07:00–09:00: 215; quarta 07:00–09:00: 302 |
| 2025-2-TCC00348-A1 | TCC00348 | ESTRUTURAS DE DADOS E SEUS ALGORITMOS | terca 11:00–13:00; quinta 11:00–13:00 | terca 11:00–13:00; quinta 11:00–13:00 | terca 11:00–13:00: 204; quinta 11:00–13:00: 204 | terca 11:00–13:00: 404B; quinta 11:00–13:00: 204 |
| 2025-2-TCC00331-A1 | TCC00331 | ESTRUTURAS DE DADOS PARA SISTEMAS DE INFORMAÇÃO | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 09:00–11:00; quarta 11:00–13:00 | segunda 18:00–20:00: 215; quarta 18:00–20:00: L302 | segunda 09:00–11:00: 215; quarta 11:00–13:00: L302 |
| 2025-2-TCC00296-A1 | TCC00296 | FUNDAMENTOS DE ARQUITETURAS DE COMPUTADORES | terca 14:00–16:00; quinta 14:00–16:00 | terca 14:00–16:00; quinta 11:00–13:00 | terca 14:00–16:00: 302; quinta 14:00–16:00: 302 | terca 14:00–16:00: 215; quinta 11:00–13:00: 213 |
| 2025-2-TCC00296-B1 | TCC00296 | FUNDAMENTOS DE ARQUITETURAS DE COMPUTADORES | terca 14:00–16:00; quinta 14:00–16:00 | terca 11:00–13:00; quinta 14:00–16:00 | terca 14:00–16:00: 215; quinta 14:00–16:00: 215 | terca 11:00–13:00: 204; quinta 14:00–16:00: 204 |
| 2025-2-TCC00332-A1 | TCC00332 | FUNDAMENTOS DE SISTEMAS DE INFORMAÇÃO | terca 18:00–20:00; quinta 18:00–20:00 | terca 16:00–18:00; quinta 07:00–09:00 | terca 18:00–20:00: 319; quinta 18:00–20:00: 319 | terca 16:00–18:00: 319; quinta 07:00–09:00: 215 |
| 2025-2-TCC00332-B1 | TCC00332 | FUNDAMENTOS DE SISTEMAS DE INFORMAÇÃO | terca 20:00–22:00; quinta 20:00–22:00 | terca 11:00–13:00; quinta 11:00–13:00 | terca 20:00–22:00: 204; quinta 20:00–22:00: 204 | terca 11:00–13:00: 302; quinta 11:00–13:00: 317 |
| 2025-2-TCC00354-A1 | TCC00354 | FUNDAMENTOS MATEMÁTICOS PARA COMPUTAÇÃO | terca 18:00–20:00; quinta 18:00–20:00 | terca 07:00–09:00; quinta 11:00–13:00 | terca 18:00–20:00: 308; quinta 18:00–20:00: 308 | terca 07:00–09:00: 308; quinta 11:00–13:00: 217 |
| 2025-2-TCC00363-A1 | TCC00363 | GERÊNCIA DE PROJETOS E MANUT DE SOFTWARE | terca 18:00–20:00; quinta 18:00–20:00 | terca 18:00–20:00; quinta 14:00–16:00 | terca 18:00–20:00: 202; quinta 18:00–20:00: 202 | terca 18:00–20:00: 202; quinta 14:00–16:00: 202 |
| 2025-2-TCC00324-A1 | TCC00324 | GOVERNANÇA EM TECNOLOGIA DA INFORMAÇÃO | sexta 18:00–22:00 | sexta 09:00–13:00 | sexta 18:00–22:00: 404B | sexta 09:00–13:00: 215 |
| 2025-2-TCC00297-A1 | TCC00297 | INTELIGÊNCIA ARTIFICIAL | terca 11:00–13:00; quinta 11:00–13:00 | terca 14:00–16:00; quinta 09:00–11:00 | terca 11:00–13:00: 302; quinta 11:00–13:00: 302 | terca 14:00–16:00: 302; quinta 09:00–11:00: 213 |
| 2025-2-TCC00298-A1 | TCC00298 | INTERFACE HOMEM MAQUINA | segunda 11:00–13:00; quarta 11:00–13:00 | segunda 09:00–11:00; quarta 07:00–09:00 | segunda 11:00–13:00: 206; quarta 11:00–13:00: 206 | segunda 09:00–11:00: 206; quarta 07:00–09:00: 206 |
| 2025-2-TCC00337-A1 | TCC00337 | INTRODUÇÃO A INTERAÇÃO HUMANO-COMPUTADOR | quinta 18:00–22:00 | quinta 18:00–22:00 | quinta 18:00–22:00: sem sala | quinta 18:00–22:00: 204 |
| 2025-2-TCC00361-A1 | TCC00361 | INTRODUÇÃO AO DESENVOLVIMENTO WEB | sabado 18:00–22:00 | sabado 14:00–18:00 | sabado 18:00–22:00: sem sala | sabado 14:00–18:00: L304 |
| 2025-2-TCC00300-A-A/B-A | TCC00300 | LABORATÓRIO DE DISPOSITIVOS MÓVEIS | terca 14:00–18:00 | terca 18:00–22:00 | terca 14:00–18:00: L307 | terca 18:00–22:00: L307 |
| 2025-2-TCC00301-A-A/B-A | TCC00301 | LABORATÓRIO DE PROGRAMAÇÃO DE JOGOS | terca 11:00–13:00; quinta 11:00–13:00 | terca 11:00–13:00; quinta 09:00–11:00 | terca 11:00–13:00: L305; quinta 11:00–13:00: L305 | terca 11:00–13:00: L304; quinta 09:00–11:00: L305 |
| 2025-2-TCC00344-A1 | TCC00344 | LABORATÓRIO DE PROGRAMAÇÃO PARALELA | segunda 09:00–11:00; quarta 09:00–11:00 | segunda 16:00–18:00; quarta 16:00–18:00 | segunda 09:00–11:00: L305; quarta 09:00–11:00: L305 | segunda 16:00–18:00: L305; quarta 16:00–18:00: L306 |
| 2025-2-TCC00346-A-A/C-A | TCC00346 | LABORATÓRIO DE RESOLUÇÃO DE PROBLEMAS | terca 16:00–18:00; quinta 16:00–18:00 | terca 20:00–22:00; quinta 20:00–22:00 | terca 16:00–18:00: L303; quinta 16:00–18:00: L303 | terca 20:00–22:00: L306; quinta 20:00–22:00: L307 |
| 2025-2-TCC00346-B-A/D-A | TCC00346 | LABORATÓRIO DE RESOLUÇÃO DE PROBLEMAS | terca 16:00–18:00; quinta 16:00–18:00 | terca 16:00–18:00; quinta 18:00–20:00 | terca 16:00–18:00: L305; quinta 16:00–18:00: L305 | terca 16:00–18:00: L305; quinta 18:00–20:00: L307 |
| 2025-2-TCC00355-E-A | TCC00355 | LABORATÓRIO DE RESOLUÇÃO DE PROBLEMAS | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 18:00–20:00; quarta 20:00–22:00 | segunda 20:00–22:00: L303; quarta 20:00–22:00: L303 | segunda 18:00–20:00: L303; quarta 20:00–22:00: L303 |
| 2025-2-TCC00355-F-A | TCC00355 | LABORATÓRIO DE RESOLUÇÃO DE PROBLEMAS | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 20:00–22:00: L305; quarta 20:00–22:00: L305 | segunda 20:00–22:00: L306; quarta 20:00–22:00: L304 |
| 2025-2-TCC00304-A1 | TCC00304 | LINGUAGENS DE PROGRAMAÇÃO | segunda 11:00–13:00; quarta 11:00–13:00 | segunda 20:00–22:00; quarta 16:00–18:00 | segunda 11:00–13:00: 302; quarta 11:00–13:00: 302 | segunda 20:00–22:00: 215; quarta 16:00–18:00: 206 |
| 2025-2-TCC00305-A1 | TCC00305 | LINGUAGENS FORMAIS E TEORIA DA COMPUTAÇÃO | segunda 09:00–11:00; quarta 09:00–11:00 | segunda 09:00–11:00; quarta 20:00–22:00 | segunda 09:00–11:00: 204; quarta 09:00–11:00: 204 | segunda 09:00–11:00: 204; quarta 20:00–22:00: 302 |
| 2025-2-TCC00306-A1 | TCC00306 | METODOS NUMERICOS | terca 09:00–11:00; quinta 09:00–11:00 | terca 09:00–11:00; quinta 09:00–11:00 | terca 09:00–11:00: 404B; quinta 09:00–11:00: 404B | terca 09:00–11:00: 404B; quinta 09:00–11:00: 215 |
| 2025-2-TCC00318-A1 | TCC00318 | PESQUISA OPERACIONAL | sexta 09:00–13:00 | sexta 18:00–22:00 | sexta 09:00–13:00: sem sala | sexta 18:00–22:00: 308 |
| 2025-2-TCC00334-A1 | TCC00334 | PRINCIPIO DE BANCO DE DADOS | quarta 18:00–20:00; sexta 18:00–20:00 | quarta 18:00–20:00; sexta 18:00–20:00 | quarta 18:00–20:00: 302; sexta 18:00–20:00: 302 | quarta 18:00–20:00: 204; sexta 18:00–20:00: 404B |
| 2025-2-TCC00307-A1 | TCC00307 | PROGRAMAÇÃO CIENTÍFICA | terca 07:00–09:00; quinta 07:00–09:00 | terca 09:00–11:00; quinta 20:00–22:00 | terca 07:00–09:00: 217; quinta 07:00–09:00: 217 | terca 09:00–11:00: 321; quinta 20:00–22:00: 217 |
| 2025-2-TCC00366-A1 | TCC00366 | PROGRAMAÇÃO DE COMPUTADORES I | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 11:00–13:00; quarta 11:00–13:00 | segunda 18:00–20:00: 308; quarta 18:00–20:00: 308 | segunda 11:00–13:00: 213; quarta 11:00–13:00: 308 |
| 2025-2-TCC00366-B1 | TCC00366 | PROGRAMAÇÃO DE COMPUTADORES I | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 16:00–18:00; quarta 07:00–09:00 | segunda 18:00–20:00: 302; quarta 18:00–20:00: 302 | segunda 16:00–18:00: 302; quarta 07:00–09:00: 321 |
| 2025-2-TCC00308-A1 | TCC00308 | PROGRAMAÇÃO DE COMPUTADORES I | segunda 16:00–18:00; quarta 16:00–18:00 | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 16:00–18:00: 313; quarta 16:00–18:00: 313 | segunda 18:00–20:00: 404B; quarta 18:00–20:00: 313 |
| 2025-2-TCC00308-B1 | TCC00308 | PROGRAMAÇÃO DE COMPUTADORES I | segunda 16:00–18:00; quarta 16:00–18:00 | segunda 16:00–18:00; quarta 16:00–18:00 | segunda 16:00–18:00: 308; quarta 16:00–18:00: 308 | segunda 16:00–18:00: 206; quarta 16:00–18:00: 308 |
| 2025-2-TCC00356-A1 | TCC00356 | PROGRAMAÇÃO DE COMPUTADORES II | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 18:00–20:00: L302; quarta 18:00–20:00: 202 | segunda 20:00–22:00: L302; quarta 20:00–22:00: 206 |
| 2025-2-TCC00356-B1 | TCC00356 | PROGRAMAÇÃO DE COMPUTADORES II | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 07:00–09:00; quarta 09:00–11:00 | segunda 20:00–22:00: L302; quarta 20:00–22:00: 202 | segunda 07:00–09:00: L307; quarta 09:00–11:00: 202 |
| 2025-2-TCC00347-A1 | TCC00347 | PROGRAMAÇÃO ESTRUTURADA | terca 09:00–11:00; quinta 09:00–11:00 | terca 07:00–09:00; quinta 14:00–16:00 | terca 09:00–11:00: L304; quinta 09:00–11:00: 202 | terca 07:00–09:00: L307; quinta 14:00–16:00: 404B |
| 2025-2-TCC00347-B1 | TCC00347 | PROGRAMAÇÃO ESTRUTURADA | terca 09:00–11:00; quinta 09:00–11:00 | terca 16:00–18:00; quinta 20:00–22:00 | terca 09:00–11:00: L304; quinta 09:00–11:00: 202 | terca 16:00–18:00: L303; quinta 20:00–22:00: 202 |
| 2025-2-TCC00347-X1 | TCC00347 | PROGRAMAÇÃO ESTRUTURADA | terca 16:00–18:00; quinta 16:00–18:00 | terca 14:00–16:00; quinta 20:00–22:00 | terca 16:00–18:00: L304; quinta 16:00–18:00: 202 | terca 14:00–16:00: L304; quinta 20:00–22:00: 206 |
| 2025-2-TCC00328-A1 | TCC00328 | PROGRAMAÇÃO ORIENTADA A OBJETOS | segunda 11:00–13:00; quarta 11:00–13:00 | segunda 11:00–13:00; quarta 07:00–09:00 | segunda 11:00–13:00: L307; quarta 11:00–13:00: 202 | segunda 11:00–13:00: L305; quarta 07:00–09:00: 202 |
| 2025-2-TCC00328-B1 | TCC00328 | PROGRAMAÇÃO ORIENTADA A OBJETOS | segunda 16:00–18:00; quarta 16:00–18:00 | segunda 16:00–18:00; quarta 16:00–18:00 | segunda 16:00–18:00: 202; quarta 16:00–18:00: 202 | segunda 16:00–18:00: 202; quarta 16:00–18:00: 204 |
| 2025-2-TCC00328-X1 | TCC00328 | PROGRAMAÇÃO ORIENTADA A OBJETOS | segunda 11:00–13:00; quarta 11:00–13:00 | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 11:00–13:00: 202; quarta 11:00–13:00: 202 | segunda 18:00–20:00: 213; quarta 18:00–20:00: 206 |
| 2025-2-TCC00335-A1 | TCC00335 | PROJETO DE BANCO DE DADOS | segunda 20:00–22:00; quarta 20:00–22:00 | segunda 07:00–09:00; quarta 09:00–11:00 | segunda 20:00–22:00: sem sala; quarta 20:00–22:00: sem sala | segunda 07:00–09:00: 202; quarta 09:00–11:00: sem sala |
| 2025-2-TCC00312-A1 | TCC00312 | PROJETO DE SOFTWARE | segunda 07:00–09:00; quarta 07:00–09:00 | segunda 07:00–09:00; quarta 11:00–13:00 | segunda 07:00–09:00: 215; quarta 07:00–09:00: 215 | segunda 07:00–09:00: 308; quarta 11:00–13:00: 213 |
| 2025-2-TCC00338-A1 | TCC00338 | PROJETO DE SOFTWARE | terca 20:00–22:00; quinta 20:00–22:00 | terca 16:00–18:00; quinta 20:00–22:00 | terca 20:00–22:00: 215; quinta 20:00–22:00: 215 | terca 16:00–18:00: 213; quinta 20:00–22:00: 215 |
| 2025-2-TCC00365-A1 | TCC00365 | QUALIDADE E TESTE DE SOFTWARE | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 11:00–13:00; quarta 11:00–13:00 | segunda 18:00–20:00: L306; quarta 18:00–20:00: 202 | segunda 11:00–13:00: L306; quarta 11:00–13:00: 321 |
| 2025-2-TCC00359-A1 | TCC00359 | REDES DE COMPUTADORES | quarta 20:00–22:00; sexta 20:00–22:00 | quarta 11:00–13:00; sexta 20:00–22:00 | quarta 20:00–22:00: 202; sexta 20:00–22:00: 202 | quarta 11:00–13:00: 202; sexta 20:00–22:00: 204 |
| 2025-2-TCC00313-A1 | TCC00313 | REDES DE COMPUTADORES I | terca 09:00–11:00; quinta 09:00–11:00 | terca 16:00–18:00; quinta 20:00–22:00 | terca 09:00–11:00: 319; quinta 09:00–11:00: 319 | terca 16:00–18:00: 217; quinta 20:00–22:00: 319 |
| 2025-2-TCC00314-A1 | TCC00314 | REDES DE COMPUTADORES II | terca 11:00–13:00; quinta 11:00–13:00 | terca 16:00–18:00; quinta 14:00–16:00 | terca 11:00–13:00: L307; quinta 11:00–13:00: L307 | terca 16:00–18:00: L302; quinta 14:00–16:00: L305 |
| 2025-2-TCC00341-A1 | TCC00341 | SEGURANÇA DA INFORMAÇÃO | quarta 18:00–22:00 | quarta 18:00–22:00 | quarta 18:00–22:00: 213 | quarta 18:00–22:00: 204 |
| 2025-2-TCC00358-A1 | TCC00358 | SISTEMAS COMPUTACIONAIS | quinta 18:00–22:00 | quinta 18:00–22:00 | quinta 18:00–22:00: 321 | quinta 18:00–22:00: 213 |
| 2025-2-TCC00315-A1 | TCC00315 | SISTEMAS DISTRIBUÍDOS | terca 09:00–11:00; quinta 09:00–11:00 | terca 09:00–11:00; quinta 07:00–09:00 | terca 09:00–11:00: 202; quinta 09:00–11:00: 202 | terca 09:00–11:00: 206; quinta 07:00–09:00: 404B |
| 2025-2-TCC00362-A1 | TCC00362 | SISTEMAS DISTRIBUÍDOS PARA SISTEMAS DE INFORMAÇÃO | terca 18:00–22:00 | terca 14:00–18:00 | terca 18:00–22:00: sem sala | terca 14:00–18:00: 308 |
| 2025-2-TCC00316-A1 | TCC00316 | SISTEMAS OPERACIONAIS | terca 11:00–13:00; quinta 11:00–13:00 | terca 18:00–20:00; quinta 14:00–16:00 | terca 11:00–13:00: 215; quinta 11:00–13:00: 215 | terca 18:00–20:00: 215; quinta 14:00–16:00: 215 |
| 2025-2-TCC00360-A1 | TCC00360 | VISUALIZAÇÃO DE DADOS | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 18:00–20:00; quarta 18:00–20:00 | segunda 18:00–20:00: 319; quarta 18:00–20:00: 319 | segunda 18:00–20:00: 204; quarta 18:00–20:00: 319 |
| 2025-2-TCC00241-A1 | TCC00241 | Ementa Variável I -  TÓPICOS EM COMPUTAÇÃO X - Tópicos em Computação X | terca 18:00–20:00; quinta 18:00–20:00 | terca 18:00–20:00; quinta 18:00–20:00 | terca 18:00–20:00: sem sala; quinta 18:00–20:00: sem sala | terca 18:00–20:00: 206; quinta 18:00–20:00: 319 |
| 2025-2-TCC00230-A1 | TCC00230 | Ementa Variável II -  TÓPICOS ESPECIAIS EM SEGURANÇA DA INFORMAÇÃO | sexta 18:00–22:00 | sexta 18:00–22:00 | sexta 18:00–22:00: L303 | sexta 18:00–22:00: L305 |

## Interpretação

A busca respeita a distinção entre salas comuns e laboratórios e eliminou os conflitos de sala. Os conflitos hard restantes são curriculares; nenhum conflito de professor, capacidade, recurso ou descanso permaneceu.

O aumento de janelas, desperdício e distância mostra o compromisso entre viabilidade e qualidade: nesta execução o peso das restrições hard dominou a função objetivo. Os domínios de horário ainda são provisórios e foram gerados a partir dos horários históricos observados.

Capacidades e distâncias continuam estimadas; a distância usa custo 3 para troca de prédio mais diferença de andar. A solução serve como primeiro teste reprodutível da pipeline, não como grade oficial pronta para publicação.
