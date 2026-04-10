---
sidebar_label: "Log da Sprint"
sidebar_position: 2
---

# Log da Sprint

## UX

&nbsp; Na Sprint 2, foi implementado o mapeamento do fluxo de utilização da solução, com definição de user flow e elaboração de wireframes. As personas e a jornada do usuário definidas na Sprint 1 foram utilizadas como base para estruturar a navegação, organizar as telas e priorizar funcionalidades. Os requisitos levantados anteriormente foram convertidos em fluxos operacionais, relacionando usuários, módulos do sistema e pontos de registro no banco de dados.

## Protótipo do Sistema de Automação

&nbsp; Na Sprint 2, a arquitetura definida anteriormente foi aplicada de forma prática, estruturando o sistema em cinco submódulos: **1A, 1B, 2A, 2B e 2C**. Essa organização consolidou a separação de responsabilidades e orientou tanto a implementação técnica quanto a documentação no arquivo `Protótipo do Sistema de Automação.md`.

&nbsp; O submódulo **1A** implementa a movimentação no eixo Z da motobomba, enquanto o **1B** trata da leitura de corrente de operação e sua interpretação. O **2A** contempla a movimentação horizontal da balsa (XY), o **2B** a visualização da câmera e o **2C** o monitoramento de sensores de fallback. Cada submódulo passou a conter descrição de hardware e comandos de execução via CLI.

&nbsp; Também foi implementada a padronização das CLIs por módulo e iniciada a modelagem do banco de dados para registrar leituras, movimentações e alertas. A Sprint 2 marcou a transição da definição arquitetural para a organização executável do sistema, integrando hardware, lógica de controle e estrutura de dados.