---
sidebar_label: "Log da Sprint"
sidebar_position: 2
---

# Log da Sprint

## Testes Funcionais e Não Funcionais

&nbsp; A tabela de testes funcionais e não funcionais foi elaborada, validada e iterada ao longo da sprint. O método adotado consistiu em analisar os requisitos funcionais e não funcionais definidos na Sprint 1, disponíveis em ``docs/docs/sprints/sprint-01/Proposta-de-Arquitetura-do-Sistema.md``, e confrontá-los com as funcionalidades implementadas no backend e na interface do usuário, assegurando que todas as capacidades previstas foram corretamente desenvolvidas e se encontram operacionais. A documentação completa dos testes está disponível em: ``docs/docs/sprints/sprint-04/documentacao/Testes Funcionais e Não Funcionais.md``

## Interface do Usuário

&nbsp; A interface do usuário foi integralmente implementada nesta sprint. As telas do gestor, do operador e a tela informativa (tutorial) foram desenvolvidas com as respectivas funcionalidades de movimentação, visualização de logs, monitoramento dos sensores, histórico de operações e controle do tempo de operação.

&nbsp; Durante o desenvolvimento, foram identificadas dificuldades na integração da câmera (Módulo 2-B) com o frontend, causadas por restrições de permissões do navegador em relação ao protocolo WebSocket, bem como por limitações de processamento e memória da ESP32-CAM. Em consequência, a visualização em tempo real da câmera foi implementada com sucesso, porém a funcionalidade de modo expandido (ampliação da visualização no grid) foi descartada, mantendo-se a exibição exclusivamente no grid quadriculado padrão.

&nbsp; Houve também um incidente relacionado ao envio de comandos ao banco de dados: na aplicação do gestor, requisições concorrentes geraram múltiplos registros indevidos, comprometendo a integridade das tabelas de log de operação e exigindo a reinicialização dessas tabelas.

&nbsp; A documentação completa da interface do usuário está disponível em: ``docs/docs/sprints/sprint-04/documentacao/Interface do Usuário.md``

## Backend

&nbsp; Nesta sprint, os firmwares e a CLI foram modificados para suportar as novas funcionalidades: modo automático de descida/subida (Módulos 1-A e 2-A), sistema de heartbeat para monitoramento de conectividade (todos os módulos), intertravamento motobomba x balsa (Módulos 1-A e 2-A) e intertravamento sensores x balsa (Módulos 2-A e 2-C).

&nbsp; Foram realizadas correções no Módulo 2-B (câmera) para garantir sua integração com o frontend. A CLI unificada, o listener MQTT e parte do esquema do banco de dados foram adaptados para receber e processar as novas informações provenientes dos firmwares atualizados.

&nbsp; As limitações atuais do backend são de ordem de escalabilidade: o sistema suporta apenas uma bomba (bomba_id=1) e uma das quatro câmeras previstas.

&nbsp; A documentação completa do backend está disponível em: ``docs/docs/sprints/sprint-04/documentacao/Backend.md``