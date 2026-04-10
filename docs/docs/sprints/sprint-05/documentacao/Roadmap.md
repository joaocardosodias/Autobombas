---
sidebar_label: "Roadmap"
sidebar_position: 3
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Roadmap de Desenvolvimento
---

## 1. Visão Geral

Esta seção apresenta os itens que permanecem no backlog do projeto Autobombas e que não foram implementados na entrega final. Os requisitos não contemplados foram avaliados quanto à sua relevância técnica e de negócio, e estão organizados como um roadmap de desenvolvimento futuro para orientar a continuidade do sistema caso seja levado a um ambiente de produção industrial. As funcionalidades estão priorizadas considerando o impacto operacional para a Itubombas e a complexidade técnica de implementação.

---



## 2. Melhorias Previstas

**Curto prazo (1–3 meses):**
- **Slider de velocidade PWM (US-M2A-02):** Adicionar controle deslizante na interface do operador para ajustar a velocidade dos motores DC em tempo real via MQTT.
- **Proteção de rotas no frontend:** Implementar componente `ProtectedRoute` que redirecione usuários não autenticados ou sem permissão adequada, garantindo que gestores e operadores acessem apenas as telas pertinentes ao seu perfil.
- **Resolução de registros duplicados:** Corrigir o incidente identificado na Sprint 4 onde requisições concorrentes ao backend geravam registros duplicados nos logs de operação.

**Médio prazo (3–6 meses):**
- **Integração completa das 4 câmeras:** Revisar a arquitetura de streaming de vídeo para suportar 4 câmeras simultâneas no dashboard, avaliando alternativas ao WebSocket direto (ex.: RTSP via servidor intermediário ou MJPEG com proxy).
- **Calibração do controle adaptativo:** Realizar testes de campo com diferentes materiais de dragagem para calibrar os limiares de corrente do RF-06, validando os modos de auto-descida e auto-subida.
- **Planejamento de rotas semi-automático:** Implementar sugestão de rota em grade com possibilidade de ajuste manual pelo operador antes da execução, como passo intermediário ao RF-01 completo.
- **Modo tela cheia para câmeras:** Permitir expansão individual de cada feed de câmera para visualização em tela cheia.

**Longo prazo (6–12 meses):**
- **Escalabilidade para múltiplas bombas:** Refatorar o backend para suportar múltiplos dispositivos simultâneos, incluindo tópicos MQTT dinâmicos, modelo de dados multi-bomba e dashboard com visão consolidada.
- **Deploy em nuvem:** Empacotar o backend e frontend para implantação em infraestrutura de nuvem, com CI/CD automatizado e monitoramento de disponibilidade.
- **Substituição de ESP32 por CLP industrial:** Migrar o firmware dos módulos embarcados para controladores lógicos programáveis (CLP) com grau de proteção IP67, adequados ao ambiente industrial de dragagem.
- **Sistema de relatórios e analytics:** Dashboard gerencial com histórico de operações, métricas de eficiência e exportação de relatórios para análise pós-operação.

---

## 3. Visão de Longo Prazo

Caso o sistema Autobombas seja levado a produção industrial, a evolução do produto em um horizonte de 12 meses seguiria o seguinte cronograma:

| Fase | Período | Entregas Previstas |
|---|---|---|
| Fase 1 — Estabilização | Meses 1–3 | Tela de configurações (RNF09), slider de velocidade PWM, proteção de rotas no frontend, correção de registros duplicados, testes de integração end-to-end com hardware, documentação de operação para usuários finais |
| Fase 2 — Expansão | Meses 4–6 | Integração das 4 câmeras industriais IP67, calibração do controle adaptativo de guincho em campo, planejamento de rotas semi-automático, migração do banco de dados para infraestrutura de produção com backups automatizados |
| Fase 3 — Escala | Meses 7–9 | Suporte a múltiplas bombas simultâneas, deploy em nuvem com CI/CD, substituição dos ESP32 por CLPs industriais, implementação de telemetria remota para monitoramento à distância |
| Fase 4 — Maturidade | Meses 10–12 | Planejamento de rotas totalmente automático (RF-01), ciclo de transição automático (RF-08), sistema de relatórios e analytics gerencial, validação do sistema completo em operação real de dragagem com parceiro Itubombas |

Essa visão de evolução prioriza a estabilidade e segurança operacional nas fases iniciais, expandindo gradualmente as capacidades de automação e escala conforme o sistema é validado em cenários reais de uso.
