---
sidebar_label: "Integração do Sistema"
sidebar_position: 1
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Documentação da Integração do Sistema
--- 

## 1. Visão Geral do Sistema
 
O projeto Itubombas/Autobombas tem como objetivo desenvolver um sistema de controle semi-automático para bombas de dragagem, permitindo que operadores comandem remotamente a movimentação e o posicionamento da motobomba por meio de uma interface web intuitiva. Esta sprint final consolida o trabalho desenvolvido ao longo das cinco sprints do projeto, integrando todos os módulos de hardware, o backend e o frontend em um sistema funcional e coeso.
 
Ao longo do desenvolvimento, o sistema evoluiu significativamente em relação à concepção original: partiu-se de uma proposta de operação totalmente automática para uma arquitetura semi-automática, onde o operador mantém controle direto sobre a movimentação da balsa e da motobomba com apoio visual de câmeras e sensores em tempo real. Essa mudança reflete um ajuste de escopo baseado nas limitações técnicas identificadas durante o desenvolvimento e nas necessidades reais das personas do projeto — Carlos (operador de campo) e Bruno (gestor remoto).
 
---

## 2. Sistema Integrado
 
### 2.1 Módulos e Comunicação
 
O sistema é composto por cinco módulos de hardware, um backend Flask e um frontend React que operam de forma integrada. A comunicação entre os módulos físicos e o backend ocorre via protocolo MQTT (broker Mosquitto), enquanto o frontend consome a API REST do backend com autenticação JWT. A única exceção é o Módulo 2-B (câmeras), cujo stream de vídeo é consumido diretamente pelo frontend via HTTP, sem intermediação do backend.
 
Abaixo estão descritos cada módulo e sua integração com o restante do sistema:
 
**Módulo 1-A — Motor de Passo / Profundidade**
 
O ESP32 responsável pelo controle do eixo Z recebe comandos publicados pelo backend no tópico MQTT `motor/<bomba_id>/comando`. Ao concluir o movimento, o ESP responde no tópico `motor/<bomba_id>/status`, e o backend atualiza o registro de posição no banco de dados. O frontend consome o endpoint `GET /movimentacao-z/posicao/<bomba_id>` a cada 3 segundos para exibir a profundidade atual na barra de progresso do Dashboard do Operador.
 
**Módulo 1-B — Leitura de Corrente**
 
O ESP32 do sensor de corrente publica leituras periodicamente no tópico `corrente/<bomba_id>/status`. O listener MQTT do backend persiste cada leitura na tabela `leituras_corrente`. O frontend consome o endpoint `GET /leituras-corrente/bomba/<bomba_id>/ultima` a cada 3 segundos para atualizar o gauge de amperagem em tempo real. O modo automático (backend) também consome essas leituras para decidir se a motobomba deve descer, subir ou permanecer estável.
 
**Módulo 2-A — Movimentação XY**
 
O frontend envia comandos direcionais via `POST /movimentacao-xy/`. O backend valida dois intertravamentos em cadeia — posição da motobomba no eixo Z e nível de risco dos sensores de proximidade — antes de publicar o comando no tópico `balsa/<bomba_id>/comando`. O ESP da balsa executa o movimento e o registro é persistido na tabela `movimentacao_xy`.
 
**Módulo 2-B — Câmeras ESP32-CAM**
 
Os ESP32-CAM transmitem stream de vídeo MJPEG diretamente via HTTP. O frontend consome o stream no endereço do dispositivo (`http://<ip>/stream`) e exibe o feed nos cards de câmera do Dashboard do Operador, sem passar pelo backend Flask. Atualmente a Câmera 1 (visão frontal) possui stream ativo; as demais aguardam integração de hardware.
 
**Módulo 2-C — Sensores de Proximidade**
 
O ESP32 dos sensores HC-SR04 publica leituras das quatro direções (frente, trás, esquerda, direita) no tópico `sensor/<bomba_id>/distancias`. O backend classifica cada direção em quatro níveis de risco (SEGURO, INFORMATIVO, ALERTA, CRÍTICO) e aciona parada de emergência automática via MQTT quando alguma direção atinge nível CRÍTICO. O frontend exibe alertas visuais no painel de sensores do Dashboard do Operador.
 
A tabela abaixo resume o fluxo de comunicação de cada módulo:
 
| Módulo | Hardware | Protocolo | Backend | Frontend |
|---|---|---|---|---|
| 1-A (Motor Z) | ESP32 | MQTT `motor/+/status` | Persiste em `movimentacao_z` | `GET /movimentacao-z/posicao` |
| 1-B (Corrente) | ESP32 | MQTT `corrente/+/status` | Persiste em `leituras_corrente` | `GET /leituras-corrente/.../ultima` |
| 2-A (Balsa XY) | ESP32 | MQTT `balsa/+/comando` | Valida intertravamentos e persiste em `movimentacao_xy` | `POST /movimentacao-xy/` |
| 2-B (Câmeras) | ESP32-CAM | HTTP MJPEG direto | — (sem intermediação) | Stream direto via `<img src>` |
| 2-C (Sensores) | ESP32 | MQTT `sensor/+/distancias` | Classifica risco, aciona emergência | `GET /leituras-distancia/.../status-proximidade` |
 
### 2.2 Demonstração de Funcionamento

O vídeo demonstrativo com o funcionamento completo do sistema pode ser acessado através do seguinte link: [Vídeo Demonstrativo - Integração do Sistema](https://drive.google.com/drive/folders/1Tw3vcC2bS4WI4hmI7dw6ylCuQ2N7blaR).

Abaixo estão apresentadas as evidências em imagens do sistema funcionando de forma integrada, destacando os principais painéis através dos quais ocorre a operação:


<p style={{textAlign: 'center'}}>Figura 1 - Tela do Dashboard Principal</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/teladash.png").default} style={{width: 800, maxWidth: "100%"}} alt="Tela do Dashboard Principal" />
    </div>
</div>

<p style={{textAlign: 'center'}}>Figura 2 - Tela de Monitoramento de Sensores</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/tela-sensores.png").default} style={{width: 800, maxWidth: "100%"}} alt="Tela de Monitoramento de Sensores" />
    </div>
</div>

<p style={{textAlign: 'center'}}>Figura 3 - Tela de Configurações</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/tela-config.png").default} style={{width: 800, maxWidth: "100%"}} alt="Tela de Configurações" />
    </div>
</div>

<p style={{textAlign: 'center'}}>Figura 4 - Tela Geral do Sistema</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/tela-sistema.png").default} style={{width: 800, maxWidth: "100%"}} alt="Tela Geral do Sistema" />
    </div>
</div>

Através destas telas, o operador pode acionar comandos manuais e configurar facilmente limiares automáticos. **Cabe destacar que todos os dados apresentados nestas demonstrações — como medições da distância dos sensores, consumo de corrente, posições do motor e status de conexão — estão sendo capturados ativamente do banco de dados e repassados em tempo real.** A aplicação provada está totalmente integrada, sem operar com dados "mockados" (simulados) para o hardware.

A única exceção nas capturas de tela acima é a imagem da câmera e seu status de gravação. Como o teste ilustrado ocorreu sem o feed de vídeo do recinto de testes final, o frame renderizado na tela de Câmeras foi mockado unicamente para atestar a disposição deste componente online na interface. Essa sinergia transparente entre hardware, backend e banco de dados propicia  veracidade ao controle semiautomático da draga.
 
---

## 3. Arquitetura Atual do Sistema

Esta seção apresenta a arquitetura do sistema conforme implementada na Sprint 5, refletindo o estado real da entrega final. São descritos o diagrama de blocos atualizado, as tecnologias utilizadas em cada camada e as mudanças ocorridas em relação à arquitetura originalmente planejada na Sprint 1.

### 3.1 Diagrama de Arquitetura

Abaixo está representado o diagrama da arquitetura atual do sistema:

<p style={{textAlign: 'center'}}>Figura 5 - Arquitetura Atual do Sistema</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/arquitetura_sistema.drawio.png").default} style={{width: 800}} alt="Arquitetura Atual do Sistema" />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

O sistema é composto por quatro camadas principais: a interface do operador (Frontend), o servidor de aplicação (Backend), a camada de comunicação via Broker MQTT/HTTP e os módulos de hardware embarcado baseados em ESP32. Toda a comunicação entre os módulos físicos e o backend ocorre por meio do protocolo MQTT, garantindo troca de mensagens leve e assíncrona.

### 3.2 Tecnologias Utilizadas
 
| Camada | Tecnologia | Finalidade |
|---|---|---|
| Frontend | React 19, Vite, Tailwind CSS | Interface do operador e gestor |
| Frontend | Axios, React Router DOM | Comunicação HTTP com JWT e gerenciamento de rotas |
| Frontend | Lucide React | Ícones dos controles e indicadores visuais |
| Backend | Flask, Python 3.12 | API REST e regras de negócio |
| Backend | Flask-JWT-Extended | Autenticação e proteção de rotas via JWT |
| Backend | Flasgger (Swagger) | Documentação automática dos endpoints |
| Banco de Dados | PostgreSQL / Supabase | Persistência de dados operacionais |
| Banco de Dados | psycopg2 | Driver de conexão com pool ao PostgreSQL |
| Comunicação | MQTT / Mosquitto | Comunicação bidirecional com módulos ESP32 |
| Comunicação | paho-mqtt | Cliente MQTT no backend |
| Hardware | ESP32 | Módulos de controle (motor Z, balsa XY, sensores) |
| Hardware | ESP32-CAM | Streaming de vídeo MJPEG via HTTP |
| Segurança | bcrypt | Hash seguro de senhas de usuários |
 

### 3.3 Mudanças em Relação à Arquitetura Original

Entre a arquitetura planejada na Sprint 1 e a implementada na Sprint 5, algumas funcionalidades foram removidas ou ajustadas, enquanto novas foram incorporadas, conforme descrito abaixo.

#### Funcionalidades removidas

| Funcionalidade | Justificativa |
|---|---|
| Planejamento de rota autônomo | A operação autônoma por rota pré-definida foi descartada em favor do controle manual direto pelo operador via interface, reduzindo a complexidade de implementação e aumentando a segurança operacional. |
| Geofencing | Sem planejamento de rota, a delimitação geográfica automática deixou de ser necessária. |
| Posicionamento automático | O sistema não possui parada automática por posição, o operador é responsável por comandar a parada manualmente pela interface. |
| Módulo de alimentação centralizado | Na Sprint 3, estava previsto um módulo de alimentação único (Bateria LI-ON 2S + LM2596 + KCD11-101) compartilhado entre todos os módulos. Na implementação final, apenas o módulo de câmera (ESP32A-CAM) utiliza alimentação por bateria. Os demais módulos ESP32 são alimentados via USB, conectados a uma fonte externa (ex: notebook), o que foi suficiente para o contexto de Prova de Conceito (PoC). |

#### Funcionalidades adicionadas

| Funcionalidade | Descrição |
|---|---|
| Configurações da balsa e motobomba | Adicionado ao módulo de Controle e Processamento, permitindo ao operador ajustar parâmetros operacionais da balsa e da motobomba diretamente pela interface. |

#### Síntese das mudanças

A principal mudança de paradigma foi a transição de um sistema **autônomo** (com planejamento de rota e geofencing) para um sistema **semiautônomo**, no qual o operador controla manualmente a movimentação e os equipamentos por meio do frontend. Essa decisão foi motivada pela maior confiabilidade e previsibilidade do comportamento do sistema em ambiente real, além de simplificar a implementação dos módulos de navegação e reduzir riscos operacionais.

---

## 4. Requisitos Funcionais e Não Funcionais
 
Ao longo do projeto, a mudança de arquitetura de sistema automático para semi-automático impactou diretamente o escopo de requisitos. Requisitos que dependiam de execução autônoma de rota foram substituídos por funcionalidades de controle manual assistido. As tabelas abaixo consolidam o estado final de todos os requisitos do sistema.
 
### 4.1 Requisitos Funcionais

Dos doze requisitos funcionais, oito foram implementados, um atendido parcialmente e três removidos do escopo após a migração para arquitetura semi-automática. Os requisitos descartados (RF-01, RF-07, RF-08) dependiam de execução autônoma incompatível com o protótipo e foram substituídos pelo controle manual via interface. Os entregues cobrem navegação XY com intertravamento, controle de profundidade Z com modo automático por limiares de corrente, dashboard unificado, gestão de sessões e heartbeat dos ESPs. O geofencing (RF-03) foi parcialmente atendido, com classificação de risco e bloqueio em nível crítico pelos sensores, mas sem delimitação por coordenadas geográficas.
 
| ID | Requisito | Status | Evidência | Observação |
|---|---|---|---|---|
| RF-01 | Planejamento de Rota |  Fora de escopo | — | Requisito original da Sprint 1; substituído pela abordagem semi-automática com controle manual pelo operador |
| RF-02 | Controle Remoto de Navegação |  Implementado | Controle direcional XY no Dashboard do Operador; comandos via `POST /movimentacao-xy/` | Requisito original da Sprint 1 |
| RF-03 | Geofencing |  Parcial | Sensores laterais exibem alertas visuais e bloqueiam movimentação em nível CRÍTICO via intertravamento no backend; sem delimitação geográfica por coordenadas | Requisito original da Sprint 1 |
| RF-04 | Posicionamento Inicial |  Implementado | Controle manual de profundidade (eixo Z) no Dashboard; modo automático ajusta posição com base na corrente | Requisito original da Sprint 1 |
| RF-05 | Leitura de Carga (Corrente) |  Implementado | Gauge de amperagem em tempo real no Dashboard do Operador, atualizado a cada 3 s via `GET /leituras-corrente/bomba/.../ultima` | Requisito original da Sprint 1 |
| RF-06 | Controle Adaptativo de Guincho |  Implementado | Modo automático (`auto_mode_service.py`) ajusta posição Z com base nos limiares de corrente configuráveis | Requisito original da Sprint 1 |
| RF-07 | Critério de Ponto Limpo |  Fora de escopo | — | Substituído pela operação semi-automática; operador decide o encerramento da dragagem com base no monitoramento visual |
| RF-08 | Ciclo de Transição |  Fora de escopo | — | Substituído pela operação semi-automática; transição entre pontos é realizada manualmente pelo operador via controle direcional |
| RF-09 | Intertravamento de Movimento |  Implementado | Bloqueio de movimentação XY condicionado à posição da motobomba (Z = 0) e ao nível dos sensores de proximidade; parada de emergência automática por MQTT | Requisito original da Sprint 1 |
| RF-10 | Dashboard Operacional |  Implementado | Dashboard do Operador com câmeras, controle Z, gauge de corrente, controle XY e status de conexão em tela única | Requisito original da Sprint 1 |
| RF-11 | Gestão de Sessões e Auditoria |  Implementado | Dashboard do Gestor com histórico paginado de sessões, filtros por data/operador/status e tela de Detalhes da Sessão com alertas e fases operacionais | Adicionado na Sprint 4 — necessário para atender a persona Bruno (gestor remoto) na arquitetura semi-automática |
| RF-12 | Sistema de Heartbeat |  Implementado | Endpoints `GET /sistema/heartbeat` e `GET /sistema/heartbeat/<tipo>/<id>`; pré-condição para modo automático e envio de comandos ao sensor de corrente | Adicionado na Sprint 5 — necessário para garantir visibilidade do estado dos ESPs em tempo real |
 
### 4.2 Requisitos Não Funcionais

Dos dez requisitos não funcionais, nove foram implementados e um atendido parcialmente. O sistema opera com polling a cada 3 s para dados operacionais e 15 s para status geral, autenticação JWT com hash bcrypt, reconexão automática MQTT e persistência timestamped de todas as operações. A interface concentra as funcionalidades em tela única com padrão semafórico e navegação em até dois cliques, sem dependência de internet em campo. O requisito parcial (RNF-09) refere-se à configurabilidade: limiares são ajustáveis via API REST.
 
| ID | Requisito | Status | Evidência | Observação |
|---|---|---|---|---|
| RNF-01 | Confiabilidade |  Implementado | Polling inteligente com tratamento de erros HTTP; redirecionamento automático em caso de sessão expirada (401); reconexão automática do listener MQTT | Requisito original da Sprint 1 |
| RNF-02 | Desempenho de atualização |  Implementado | Dados de corrente e posição Z atualizados a cada 3 s; status do sistema a cada 15 s via polling na API | Requisito original da Sprint 1 |
| RNF-03 | Segurança de acesso |  Implementado | Autenticação JWT em todos os endpoints REST; hash de senhas com bcrypt; interceptor Axios com renovação automática e redirecionamento em caso de token expirado | Requisito original da Sprint 1 |
| RNF-04 | Rastreabilidade |  Implementado | Todas as movimentações Z e XY, leituras de corrente e distância persistidas com timestamp; logs de operação consultáveis via `GET /logs`; identificação de operador em cada registro | Requisito original da Sprint 1 |
| RNF-05 | Operação em rede local |  Implementado | Interface executada via Vite em rede local; comunicação com Flask e ESPs via Wi-Fi compartilhado; sem dependência de internet durante operação | Requisito original da Sprint 1 |
| RNF-06 | Registro de eventos |  Implementado | Cada comando de movimentação Z e XY e cada leitura de corrente persistido com timestamp; paradas de emergência registradas automaticamente pelo backend | Requisito original da Sprint 1 |
| RNF-07 | Clareza de interface |  Implementado | Indicadores visuais com padrão semafórico consistente (verde/amarelo/vermelho) em indicador de conexão, gauge de amperagem e badges de status de sessões | Requisito original da Sprint 1 |
| RNF-08 | Simplicidade operacional |  Implementado | Todas as funcionalidades de operação acessíveis em tela única (Dashboard do Operador); navegação com no máximo 2 cliques | Requisito original da Sprint 1 |
| RNF-09 | Configurabilidade |  Parcial | Limiares de corrente e passo automático configuráveis via `PATCH /bombas/<bomba_id>/config`; limiares de proximidade ajustáveis via `PUT /leituras-distancia/limiares`; tela de Configurações no frontend não implementada | Requisito original da Sprint 1 |
| RNF-10 | Documentação |  Implementado | Documentação técnica via Docusaurus; tela "Sobre o Sistema" com tutoriais e avisos de segurança embutidos; documentação automática de endpoints via Flasgger/Swagger | Requisito original da Sprint 1 |
 
### 4.3 Requisitos Não Atendidos

Quatro requisitos não foram plenamente atendidos: três funcionais (RF-01, RF-07, RF-08) descartados na migração para semi-automático por dependerem de automação plena e posicionamento absoluto incompatíveis com o protótipo, e um não funcional (RNF-09) parcialmente implementado. As funções de planejamento de rota, critério de ponto limpo e ciclo de transição foram absorvidas pelo operador via controle manual e monitoramento visual. A configurabilidade já é suportada por endpoints REST, com a tela frontend prevista no roadmap.
 
| ID | Requisito Original | Motivo do Não Atendimento |
|---|---|---|
| RF-01 | Planejamento de Rota | Substituído pela operação semi-automática. O planejamento automático de rota exigiria sistema de posicionamento absoluto e precisão de hardware incompatíveis com o escopo do protótipo. O operador realiza o planejamento e execução manualmente via controle direcional na interface. Não previsto no roadmap atual. |
| RF-07 | Critério de Ponto Limpo | Substituído pela operação semi-automática. O critério automatizado de detecção de fim de dragagem dependia de lógica de análise de corrente complexa e de ciclo automático de transição (RF-08), ambos descartados na refatoração da arquitetura. O operador decide o encerramento com base no monitoramento visual das câmeras e da amperagem. Não previsto no roadmap atual. |
| RF-08 | Ciclo de Transição Automatizado | Substituído pela operação semi-automática. O ciclo automatizado de transição entre pontos de dragagem dependia da implementação de RF-01 (planejamento de rota) e RF-07 (critério de ponto limpo). Com a refatoração para controle manual, a transição entre pontos é realizada diretamente pelo operador via controle direcional XY. Não previsto no roadmap atual. |
| RNF-09 | Configurabilidade (tela frontend) | Parcialmente atendido via API — limiares de corrente e proximidade são configuráveis por endpoints REST. A tela de Configurações no frontend está prevista no roadmap para implementação futura, conforme detalhado na seção de Próximos Passos da documentação de interface. |
 
---

## 5. Conclusão
 
Esta sprint final entregou o sistema Itubombas integrado em sua totalidade, unificando cinco módulos de hardware ESP32, um backend Flask com comunicação MQTT e um frontend React em uma plataforma operacional coesa. O sistema permite que o operador controle a profundidade da motobomba, movimente a balsa nas quatro direções, monitore a corrente elétrica em tempo real e visualize o ambiente por câmeras integradas — tudo a partir de uma única tela, sem necessidade de memorizar comandos.
 
A refatoração para arquitetura semi-automática, embora tenha implicado o descarte de requisitos de automação plena, resultou em um sistema mais robusto e adequado ao contexto operacional real: o operador mantém controle direto sobre as decisões críticas, enquanto o backend fornece camadas de segurança automáticas (intertravamentos, parada de emergência, modo automático de profundidade) que reduzem o risco operacional.
 
Para o parceiro Itubombas, o sistema entrega rastreabilidade completa de operações, visibilidade em tempo real do estado do equipamento e uma interface que elimina a curva de aprendizado associada à CLI anterior. Os próximos passos naturais incluem a implementação da tela de Configurações, a integração das câmeras 2, 3 e 4 ao hardware real e a evolução do sistema de heartbeat para suportar múltiplas bombas simultaneamente.