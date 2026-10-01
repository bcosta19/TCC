# Hipóteses provisórias — 07/09/2026

> **Atualização 30/09/2026:** HP1 e HP2 foram decididas — ver
> [`decisoes_modelagem_2026_09_30.md`](decisoes_modelagem_2026_09_30.md).
> O texto abaixo preserva o registro original.
>
> Acordadas com o aluno, **pendentes de validação do orientador**.
> Não são diretrizes confirmadas. Valem para testes no perfil sintético;
> a instância institucional segue com `pronta_para_experimento=false`.

## HP1 — H12 só para permanentes
- H12 (mínimo de 3 obrigatórias/ano) vale só para docentes **permanentes do IC**.
- Temporários, substitutos e nomes com 1 turma só ficam fora do universo.
- Falta a lista oficial de permanentes — os 40 da sintética seguem como placeholder.
- Preenchimento oficial: `universo_h12_2026.csv` (`incluido_h12 = sim/nao`).

## HP2 — Fixo é só externo + serviço
- **Fixo (solver não mexe no horário):** turmas de outros departamentos (`C_out`, ex.: Cálculo) + disciplinas-serviço do IC (ex.: ED).
- **Flexível dentro do setor:** obrigatórias do IC podem trocar de faixa, desde que nos dias do setor.
- **Livre:** optativas do IC (menos projeto final).
- Preenchimento oficial: `revisao_horarios_fixos_2026.csv` (`horario_fixo = sim/nao`).
- Consequência assumida: com tudo fixo (perfil atual), H8 vira constante e os 10 choques do piloto não saem — não é bug, é efeito da decisão.

## Teste exploratório v2 (rodado em 07/09/2026, NÃO oficial)
- Perfil `sintetica_2026_v2_hp` (`dados/config_sintetica_2026_v2_hp.json`): H12 com os mesmos 40 como proxy de permanentes (HP1 aproximada); fixo = externas + `TCC00319` (serviço), obrigatórias do IC flexíveis no setor (173 flexíveis vs. 27 na v1).
- Benchmark (5 sementes, 1500 avaliações): baseline 27 → guloso 4 → **melhor SA 0 hard** (sala 0, curricular 0, H12 0); ILS/VNS 2. Custo: janelas 46→123, desperdício 3521→5116, dias 233→243.
- Piloto nativo (10 s/busca): referência 2/1/1/1/0, nativo 2/3/4/3/4 — espaço maior pede mais orçamento/parâmetros; sem conclusão sobre superioridade.
- Evidências: `dados/processados/relatorio_experimento_sintetico_2026_v2_hp.md`, `resultados_..._v2_hp.csv`, `piloto_optframe_20260907_204501/`. 94 testes OK.
- Leitura: soltar o horário destrava H8 mas piora os softs — trade-off a levar ao orientador junto com HP1/HP2.
