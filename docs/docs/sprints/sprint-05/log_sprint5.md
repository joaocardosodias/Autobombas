---
sidebar_label: "Log da Sprint"
sidebar_position: 2
---

# Log da Sprint

## Integração do Sistema

Nesta sprint, o foco foi a consolidação de todo o desenvolvimento realizado ao longo do projeto. Os cinco módulos de hardware (1-A motor de passo, 1-B leitura de corrente, 2-A movimentação XY, 2-B câmeras e 2-C sensores de proximidade), o backend Flask e o frontend React passaram por refinamento para que a integração fosse bem sucedida. A arquitetura foi atualizada na documentação para refletir o estado real do sistema, incluindo as mudanças de paradigma, a transição do modelo autônomo original para o modelo semiautônomo, no qual o operador controla manualmente a movimentação da balsa pela interface enquanto o backend fornece camadas automáticas de segurança (intertravamentos, parada de emergência e modo automático de profundidade). Os requisitos funcionais e não funcionais foram levantados e consolidados, e a narrativa pública foi estruturada para a apresentação final.

Documentação completa: [Integração do Sistema](./documentacao/Integra%C3%A7%C3%A3o%20do%20Sistema.md)

## Análise Financeira

A análise financeira do projeto foi elaborada contemplando a projeção de custos para implementação em escala industrial, com horizonte de 12 meses. A BOM (Bill of Materials) foi organizada por subsistema funcional, Controle Central, Atuação, Sensoriamento, Monitoramento Visual, Comunicação e Rede, e Infraestrutura Geral, mapeando os equivalentes industriais dos componentes utilizados no protótipo. O custo total dos componentes industriais é de **R$ 171.390,00**, e o custo total de implementação, incluindo software, mão de obra especializada e treinamento, chega a **R$ 675.710,00**. A análise de viabilidade aponta uma economia operacional anual de **R$ 130.080,00** em comparação ao cenário de operação manual, com payback estimado em aproximadamente **5,2 anos** para a primeira unidade e em torno de **20 meses** para cada balsa adicional equipada.

Documentação completa: [Análise Financeira](./documentacao/An%C3%A1lise%20Financeira.md)

## Roadmap

Os requisitos que permaneceram no backlog foram avaliados e organizados em um roadmap de desenvolvimento orientado pelo impacto operacional para a Itubombas e pela complexidade técnica. No curto prazo (1–3 meses), as prioridades são o slider de velocidade PWM, a proteção de rotas no frontend e a correção de registros duplicados identificados na Sprint 4. No médio prazo (3–6 meses), estão previstos a integração completa das quatro câmeras, a calibração do controle adaptativo de profundidade e o planejamento de rotas semi-automático. No longo prazo (6–12 meses), o roadmap contempla suporte a múltiplas bombas simultâneas, deploy em nuvem com CI/CD, substituição dos ESP32 por CLPs industriais e um sistema de relatórios gerenciais. A visão de evolução prioriza estabilidade e segurança nas fases iniciais, expandindo gradualmente as capacidades de automação conforme o sistema é validado em operação real.

Documentação completa: [Roadmap](./documentacao/Roadmap.md)

## Repositório

O repositório foi revisado para garantir conformidade com todos os critérios de entrega. O README foi atualizado com instruções claras de execução do sistema e da documentação Docusaurus. Todo o código-fonte, backend Flask, frontend React e firmwares dos módulos ESP32, está organizado no diretório `src/`. A documentação Docusaurus foi validada para execução correta a partir de um clone limpo do repositório. Foram realizadas revisões de segurança confirmando a ausência de dados sensíveis no histórico e o correto uso do `.gitignore` para arquivos `.env`. Reorganizações e limpezas pontuais foram feitas para garantir que a estrutura do repositório reflita o estado final do projeto.

## Fechamento do Projeto

A Sprint 5 encerra o ciclo de desenvolvimento do projeto Autobombas. Ao longo das cinco sprints, o sistema evoluiu desde a definição da arquitetura e pesquisa de UX (Sprint 1), passando pela prototipação dos módulos de hardware (Sprint 2), unificação da CLI e integração via MQTT (Sprint 3), implementação da interface do usuário e testes de usabilidade (Sprint 4), até a entrega final com o sistema funcionando de forma integrada (Sprint 5). Para o parceiro Itubombas, o projeto entrega rastreabilidade completa das operações, visibilidade em tempo real do estado do equipamento e uma interface que elimina a curva de aprendizado associada à operação manual anterior, reduzindo riscos operacionais e abrindo caminho para automação progressiva. A continuidade do sistema está orientada pelo roadmap estruturado nesta sprint, que prevê a evolução gradual das capacidades de automação, escala e integração industrial ao longo dos próximos 12 meses.
