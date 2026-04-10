---
sidebar_label: "Interface do Usuário"
sidebar_position: 2
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Documentação da interface do usuário 
--- 

## 1. Visão Geral da Interface do Usuário
 
A interface do usuário do sistema Itubombas representa a evolução da abordagem anterior baseada em linha de comando (CLI) para uma plataforma web interativa, executada localmente no ambiente de operação. Enquanto a CLI exigia que operadores e gestores interagissem com o sistema por meio de comandos textuais digitados manualmente — como `movZ descer(10)`, `FRENTE` ou `PARAR` — a nova interface oferece controles visuais intuitivos, indicadores em tempo real e feedback imediato, sem necessidade de memorizar sintaxe de comandos.
 
A transição ocorre no contexto da **Sprint 4**, cujo objetivo é disponibilizar uma forma de uso equivalente ao produto final, baseada no backlog de requisitos levantado junto às personas do projeto. A interface foi desenvolvida para operar diretamente integrada à API Flask do backend, de modo que cada interação do usuário na tela corresponde a uma requisição real à API — da mesma forma que os comandos da CLI faziam anteriormente. Isso simplifica a validação do sistema, pois a lógica de negócio permanece centralizada no backend, e a interface atua como camada de apresentação e controle.
 
A plataforma é composta por quatro telas principais: **Login**, **Dashboard do Operador**, **Sobre o Sistema** e **Gestão de Sessões** (Dashboard do Gestor), cada uma atendendo a fluxos específicos das personas Carlos (operador de campo) e Bruno (gestor remoto). A navegação entre telas é protegida por autenticação JWT, garantindo que apenas usuários autenticados acessem os recursos do sistema.
 
---

## 2. Requisitos Atendidos pela Interface

A interface desenvolvida na Sprint 4 contempla um subconjunto dos requisitos funcionais (RF) e não funcionais (RNF) definidos na [Proposta de Arquitetura do Sistema](/sprints/sprint-01/Proposta-de-Arquitetura-do-Sistema) e das user stories mapeadas no [Fluxo de Utilização da Solução](/sprints/sprint-02/documentacao/Mapeamento%20do%20Fluxo%20de%20Utilização%20da%20Solução). A tabela abaixo resume o estado de cobertura de cada requisito pela interface atual.

**Requisitos Funcionais**

| ID | Requisito | Status na Interface | Observação |
|---|---|---|---|
| RF-02 | Controle Remoto de Navegação | ✅ Implementado | Controle direcional XY no Dashboard do Operador (seção 5.1) |
| RF-05 | Leitura de Carga (Corrente) | ✅ Implementado | Gauge de amperagem em tempo real no Dashboard do Operador (seção 5.1) |
| RF-10 | Dashboard Operacional | ✅ Implementado | Dashboard do Operador com profundidade, corrente, câmeras e status (seção 5.1) |
| RF-01 | Planejamento de Rota | ⬜ Fora de escopo | Não previsto para esta sprint; requer integração com sistema de mapeamento |
| RF-03 | Geofencing | 🔶 Parcial | Sensores laterais de proximidade exibem alertas visuais (US-M1C-01), mas sem bloqueio automático via software |
| RF-04 | Posicionamento Inicial | ✅ Implementado | Controle manual de profundidade (eixo Z) implementado; Modo automático funcional |
| RF-06 | Controle Adaptativo de Guincho | ✅ Implementado | Lógica de ajuste automático de altura com base na corrente implementada no modo automático |
| RF-07 | Critério de Ponto Limpo | ⬜ Fora de escopo | Determinação automática de fim de dragagem contemplada, no entanto, o critério de ponto limpo foi substituído por operação semi-automática |
| RF-08 | Ciclo de Transição | ⬜ Fora de escopo | Ciclo automatizado de transição entre pontos não implementado foi substituído por operação semi-automática |
| RF-09 | Intertravamento de Movimento | ✅ Implementado | Bloqueio de propulsores condicionado ao estado da bomba implementado na interface; gerenciado pelo backend |

**Requisitos Não Funcionais**

| ID | Requisito | Status na Interface |
|---|---|---|
| RNF01 | Confiabilidade | ✅ Polling inteligente e tratamento de erros HTTP com redirecionamento em caso de sessão expirada (401) |
| RNF02 | Desempenho de atualização | ✅ Dados atualizados a cada 3–15 segundos via polling na API |
| RNF06 | Registro de eventos | ✅ Cada comando de movimentação (Z e XY) e leitura de corrente é persistido com timestamp |
| RNF07 | Clareza de interface | ✅ Indicadores visuais de status (Conectado/Desconectado/Atenção) com cores padronizadas |
| RNF08 | Simplicidade Operacional | ✅ Funcionalidades principais acessíveis em tela única (Dashboard), navegação com no máximo 2 cliques |
| RNF10 | Documentação | ✅ Presente documento via Docusaurus + tela "Sobre o Sistema" com tutoriais embutidos |
| RNF09 | Configurabilidade | ⬜ Tela de configurações prevista no menu lateral, mas ainda não implementada |

O mapeamento detalhado de cada user story por tela está disponível nas subseções de **Relação com User Stories** dentro da seção 5.

---

## 3. Tecnologias Utilizadas
 
A interface foi desenvolvida com as seguintes tecnologias:
 
**Frontend**
- **React 19** — biblioteca principal para construção da interface, utilizando hooks funcionais (`useState`, `useEffect`, `useRef`) e hooks customizados para encapsulamento da lógica de integração com a API
- **Vite** — ferramenta de build e servidor de desenvolvimento local
- **Tailwind CSS** — framework de utilitários CSS para estilização dos componentes
- **Lucide React** — biblioteca de ícones utilizada nos controles e indicadores visuais
- **Axios** — cliente HTTP para comunicação com a API Flask, configurado com interceptor automático de token JWT e redirecionamento em caso de expiração de sessão (erro 401)
- **React Router DOM** — gerenciamento de rotas com proteção de acesso para usuários não autenticados
 
**Backend (integração)**
- **Flask** — API REST que processa todos os comandos enviados pela interface
- **PostgreSQL / Supabase** — banco de dados relacional para persistência de leituras, movimentações e registros de operação
- **MQTT / Mosquitto** — protocolo de comunicação entre o backend e os módulos ESP32
 
**Execução**
A interface é executada exclusivamente em **ambiente local**, sem deploy em provedor de nuvem. O servidor de desenvolvimento Vite é iniciado na máquina do operador e acessa a API Flask e os dispositivos ESP32 via rede local (Wi-Fi compartilhado). Não há dependência de conexão externa com a internet durante a operação.
 
---


## 4. Retomada da Jornada de Usuário e User Stories

A interface foi projetada para atender às jornadas de duas personas definidas na [pesquisa de UX da Sprint 1](/sprints/sprint-01/UX-Research): **Carlos (Operador de Dragagem)** e **Bruno (Gestor de Operações)**. As user stories que fundamentam as funcionalidades implementadas foram originalmente documentadas no [Mapeamento do Fluxo de Utilização da Solução](/sprints/sprint-02/documentacao/Mapeamento%20do%20Fluxo%20de%20Utilização%20da%20Solução).

### 4.1 Personas

**Carlos — Operador de Dragagem**
Executa a dragagem em campo. Precisa de controle direto sobre a bomba e a balsa, com feedback visual imediato para tomar decisões rápidas em contexto operacional. Valoriza previsibilidade, segurança e apoio à decisão. Na interface, Carlos opera o **Dashboard do Operador** (seção 5.1) e consulta a tela **Sobre o Sistema** (seção 5.2) para tutoriais e referência técnica.

**Bruno — Gestor de Operações**
Acompanha múltiplas operações remotamente. Necessita de visão consolidada do histórico, rastreabilidade de operadores e identificação rápida de anomalias. Na interface, Bruno acessa o **Dashboard do Gestor** (seção 5.3) para visão geral das sessões e a tela **Detalhes da Sessão** (seção 5.4) para auditoria de operações individuais.

### 4.2 User Stories Contempladas

A tabela abaixo consolida todas as user stories implementadas na interface. O detalhamento de como cada uma é atendida por tela específica está nas subseções de **Relação com User Stories** da seção 5.

| ID | Módulo | Persona | User Story |
|---|---|---|---|
| US-M1A-01 | Movimentação Z | Operador | Comandar descida/subida da motobomba informando distância em cm, para posicionar na profundidade ideal sem calcular manualmente rotações do motor |
| US-M1A-02 | Movimentação Z | Gestor | Histórico completo de movimentações verticais com data, hora, direção e distância, para auditoria e identificação de padrões |
| US-M1B-01 | Leitura de Corrente | Operador | Visualizar corrente em tempo real da motobomba para entender desempenho da sucção e decidir posicionamento |
| US-M1B-02 | Leitura de Corrente | Gestor | Histórico de leituras com classificação automática do estado operacional para análise de padrões e manutenção |
| US-M2A-01 | Posicionamento XY | Operador | Botões direcionais para mover a balsa até o próximo ponto de dragagem |
| US-M2A-02 | Posicionamento XY | Operador | Slider de velocidade (0–100%) para ajuste fino dos propulsores |
| US-M2A-03 | Posicionamento XY | Operador | Botão de parada imediata para cortar propulsores e estabilizar a balsa |
| US-M2A-04 | Posicionamento XY | Operador | Destaque visual da direção acionada para confirmar registro do comando |
| US-M2A-05 | Posicionamento XY | Gestor | Tabela com todos os comandos de movimentação e timestamps para auditoria |
| US-M2A-06 | Posicionamento XY | Gestor | Persistência dos registros de movimentação em banco de dados para consulta a dias anteriores |
| US-M2B-01 | Câmera | Operador | Vídeo ao vivo das ESP32-CAM por ícone na plataforma, com modal sem sair da página |
| US-M2B-02 | Câmera | Gestor | Histórico automático de acessos às câmeras para auditoria |
| US-M1C-01 | Sensores de Proximidade | Operador | Alertas visuais claros quando a balsa estiver próxima das bordas |
| US-M1C-02 | Sensores de Proximidade | Gestor | Registro dos alertas de sensores para análise de incidentes e segurança |

:::note
A user story **US-M2A-02** (slider de velocidade PWM) está prevista no backlog, porém o controle de velocidade via slider ainda não foi integrado ao componente de controle direcional na Sprint 4. Os demais itens estão implementados conforme detalhado na seção 5.
:::

---

## 5. Telas e Funcionalidades Implementadas

Esta seção detalha cada tela da interface, organizada de forma padronizada: objetivo da tela, principais componentes visuais, fluxo de navegação, relação com os módulos físicos do sistema de automação, mapeamento com as user stories da seção 4 e a comparação entre a abordagem CLI anterior e o frontend atual. A interface é composta por quatro telas: o Dashboard do Operador (centro de controle em tempo real), a tela Sobre o Sistema (documentação e tutoriais), o Dashboard do Gestor (gestão de sessões) e a tela de Detalhes da Sessão (análise pós-operação).

---

### 5.1 Tela Dashboard do Operador

<p style={{textAlign: 'center'}}>Figura 1 - Tela Dashboard do Operador</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/OperadorDash.png").default} style={{width: 800}} alt="Tela Dashboard do Operador" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

<p style={{textAlign: 'center'}}>Figura 2 - Modal de visualização dos sensores</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <!-- Substitua a imagem, título e alt text-->
        <img src={require("/img/TelaSensores.png" ).default} style={{width: 800}} alt="Modal de visualização dos sensores" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

---
 
#### Objetivo da Tela
 
O Dashboard do Operador é o centro operacional do sistema Itubombas, concentrando em uma única interface todos os controles e indicadores necessários para conduzir uma operação de dragagem em tempo real. Ela permite que o operador monitore o estado do sistema, visualize o feed das câmeras, controle a profundidade da motobomba, acompanhe a amperagem e comande a movimentação direcional da balsa, tudo sem necessidade de alternar entre telas. Diferentemente da CLI anterior, que exigia a digitação de comandos textuais individuais para cada ação, esta tela oferece controles visuais imediatos com feedback em tempo real, reduzindo o tempo de resposta do operador e o risco de erro de digitação durante operações críticas.
 
---

#### Principais Componentes
 
**1. Cabeçalho — Identificação e Status de Conexão**
 
Exibe o título "Dashboard de controle", a hora atual e a data formatada. No canto superior direito é apresentado o indicador de conectividade do sistema, com três estados possíveis:
 
- **Conectado** (verde pulsante) — sistema com pelo menos um sensor ativo nos últimos minutos
- **Desconectado** (vermelho) — nenhum sensor enviou leitura recentemente
- **Atenção** (amarelo) — estado intermediário de alerta
 
O status é atualizado automaticamente a cada 15 segundos via polling na API `GET /sistema/status/{bomba_id}`, sem necessidade de recarregar a página.
 
**2. Menu Lateral — Navegação Global**
 
Painel fixo à esquerda com logotipo Itubombas e itens de navegação: Dashboard (ativo), Sobre o Sistema, Sensores e Configurações. Na parte inferior exibe o estado operacional do sistema com contagem de sensores ativos (ex.: "2 sensores ativos"), derivada diretamente da API de status do sistema. O botão "Sair" encerra a sessão e redireciona para a tela de login.
 
**3. Seção — Monitoramento de Câmeras**
 
Grade com quatro cards de câmera dispostos em linha. Cada card exibe:
 
- Badge de status (REC em vermelho pulsante, ONLINE em verde ou OFFLINE em cinza)
- Ícone de conexão WiFi visível ao passar o mouse
- Feed de vídeo ao vivo via stream MJPEG quando a URL do equipamento está configurada
- Nome e localização da câmera no rodapé do card
 
Atualmente a **Câmera 1 (Visão Frontal)** possui stream ativo via ESP32-CAM (`http://172.20.10.4/stream`). As câmeras 2, 3 e 4 estão com feed mockado, aguardando integração de hardware futuro.
 
**4. Painel de Controle — Controle de Profundidade**
 
Card com controles para movimentação vertical (eixo Z) da motobomba. Composto por:
 
- **Botão Subir** (chevron para cima) — envia comando de subida à motobomba
- **Botão Parar** (ícone de pausa) — interrompe o movimento em andamento
- **Botão Descer** (chevron para baixo) — envia comando de descida à motobomba
- **Barra de profundidade** — indicador visual vertical mostrando a posição atual em relação ao máximo de 20 metros
- **Valor numérico** — exibe a profundidade atual em metros com uma casa decimal
 
A posição atual é obtida via `GET /movimentacao-z/posicao/{bomba_id}` e atualizada a cada 3 segundos. Os comandos de subida e descida realizam um deslocamento de 5 cm por acionamento, calculando automaticamente as voltas necessárias com base no diâmetro do carretel da bomba (0,852 cm), via `POST /movimentacao-z/`.
 
**5. Painel de Controle — Amperagem**
 
Card com medidor tipo gauge (velocímetro) exibindo a corrente elétrica da motobomba em tempo real. Composto por:
 
- **Arco do gauge** — dividido em três zonas coloridas: verde (normal), amarelo (elevado) e vermelho (crítico)
- **Ponteiro animado** — aponta para o valor atual com transição suave
- **Valor numérico** — exibe a corrente em Amperes com 6 casas decimais
- **Badge de status** — classifica automaticamente como "Normal", "Elevado" ou "Crítico" com cor correspondente
 
Os dados são obtidos via `GET /leituras-corrente/bomba/{bomba_id}/ultima` a cada 3 segundos, porém **o polling só é iniciado quando o sistema estiver conectado**, evitando requisições desnecessárias e re-renderizações que impactariam a estabilidade do feed das câmeras.
 
**6. Painel de Controle — Controle Direcional**
 
Card com controles de movimentação horizontal (eixo XY) da balsa, organizados em cruz direcional:
 
- **Botão Frente** (chevron para cima)
- **Botão Trás** (chevron para baixo)
- **Botão Esquerda** (chevron para esquerda)
- **Botão Direita** (chevron para direita)
- **Botão Parar** (quadrado central) — interrompe qualquer movimentação em andamento
 
Cada acionamento direcional envia um comando via `POST /movimentacao-xy/` com a direção correspondente. O botão de parada envia um comando via `POST /movimentacao-xy/comando/{bomba_id}`. Os comandos de frente e trás estão implementados na interface mas dependem de expansão futura do backend para suporte completo.

---

#### Fluxo de Navegação
 
1. Operador realiza login e é redirecionado automaticamente para o Dashboard
2. Visualiza o status de conexão do sistema no cabeçalho
3. Monitora o feed das câmeras na seção superior
4. Acompanha a amperagem em tempo real no gauge central
5. Utiliza os controles de profundidade para posicionar a motobomba no eixo Z
6. Utiliza o controle direcional para movimentar a balsa no eixo XY
---

#### Relação com Módulos Físicos e Sistema de Automação
 
O Dashboard do Operador é a interface direta de todos os módulos físicos do sistema:
 
- **Módulo 1-A (Motor de Passo / Profundidade)** — o Controle de Profundidade envia comandos MQTT ao ESP32 do motor via `POST /movimentacao-z/`, que converte as voltas em passos e executa o movimento físico. O feedback de posição retorna automaticamente via MQTT quando o motor conclui o movimento
- **Módulo 1-B (Leitura de Corrente)** — o gauge de Amperagem consome leituras enviadas pelo ESP32 do sensor de corrente via MQTT, salvas no banco e disponibilizadas pela API em tempo real
- **Módulo 2-A (Movimentação XY)** — o Controle Direcional envia comandos ao sistema de propulsão da balsa via `POST /movimentacao-xy/`, com registro persistente de cada acionamento
- **Módulo 2-B (Câmeras ESP32-CAM)** — a seção de câmeras consome diretamente o stream MJPEG dos ESP32-CAM via HTTP, sem intermediação do backend Flask 
---

#### Relação com User Stories

Esta tela atende às seguintes user stories (descritas na seção 4.2):

- **US-M1A-01** e **US-M1A-02** — via Controle de Profundidade
- **US-M1B-01** e **US-M1B-02** — via Gauge de Amperagem
- **US-M2A-01**, **US-M2A-03**, **US-M2A-04**, **US-M2A-05** e **US-M2A-06** — via Controle Direcional
- **US-M2B-01** — via Monitoramento de Câmeras
- **US-M1C-01** e **US-M1C-02** — via Painel de Sensores

---
#### Diferença entre CLI e Frontend
 
**Abordagem CLI (Anterior)**
 
- Controle de profundidade via comandos textuais: `movZ descer(10)`, `movZ subir(5)`
- Movimentação direcional via comandos: `FRENTE`, `TRAS`, `ESQUERDA`, `DIREITA`, `PARAR`
- Leitura de corrente solicitada manualmente via comando específico na CLI
- Sem visualização de câmeras integrada; acesso separado ao stream
- Sem indicador de conexão do sistema; operador sem visibilidade do estado dos sensores
- Feedback apenas textual: `[INFO] Movimento CONCLUÍDO` ou `[ERRO] Motor ocupado`
- Sem histórico visual de profundidade; operador sem referência da posição atual
 
**Abordagem Frontend (Atual)**
 
- **Controle de profundidade** com botões visuais e barra de progresso mostrando posição atual em metros
- **Controle direcional** em cruz com botões intuitivos e feedback visual imediato ao pressionar
- **Gauge de amperagem** com atualização automática a cada 3 segundos e classificação visual por cores
- **Feed de câmeras** integrado na mesma tela, sem necessidade de ferramentas externas
- **Indicador de conectividade** no cabeçalho mostrando estado do sistema em tempo real
- **Polling inteligente** — requisições de amperagem só ocorrem quando o sistema está conectado, preservando estabilidade do feed de vídeo
 
*Ganho principal: O operador passa a controlar todos os módulos físicos através de uma interface visual unificada, eliminando a necessidade de memorizar comandos de texto e reduzindo significativamente o tempo de resposta em situações operacionais críticas.*


### 5.2 Tela "Sobre o Sistema"

#### Objetivo da Tela

A tela "Sobre o Sistema" permite que o operador consulte a qualquer momento as informações técnicas do equipamento, compreenda as funcionalidades disponíveis no dashboard e acesse tutoriais de utilização sem abandonar a plataforma. Diferentemente da CLI anterior, que apresentava apenas indicadores de métrica durante a operação, esta tela oferece uma **visão completa e contextualizada do sistema** através de uma simulação funcional, permitindo ao operador familiarizar-se com o comportamento do equipamento antes e durante operações reais.

<p style={{textAlign: 'center'}}>Figura 3 - Tela Sobre o Sistema</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/SobreSistemaID-Features.png" ).default} style={{width: 800}} alt="Tela Sobre o Sistema" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

<p style={{textAlign: 'center'}}>Figura 4 - Tela Sobre o Sistema (Tutorial 1)</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/SobreSistemaTutorial1.png" ).default} style={{width: 800}} alt="Tela Sobre o Sistema (Tutorial 1)" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

<p style={{textAlign: 'center'}}>Figura 5 - Tela Sobre o Sistema (Tutorial 2)</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/SobreSistemaTutorial2.png" ).default} style={{width: 800}} alt="Tela Sobre o Sistema (Tutorial 2)" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

<p style={{textAlign: 'center'}}>Figura 6 - Tela Sobre o Sistema (Tutorial 3)</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/SobreSistemaTutorial3.png" ).default} style={{width: 800}} alt="Tela Sobre o Sistema (Tutorial 3)" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

<p style={{textAlign: 'center'}}>Figura 7 - Tela Sobre o Sistema (Tutorial 4)</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/SobreSistemaTutorial4.png" ).default} style={{width: 800}} alt="Figura 7 - Tela Sobre o Sistema (Tutorial 4)" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

<p style={{textAlign: 'center'}}>Figura 8 - Tela Sobre o Sistema (Alerta e Ajuda)</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/SobreSistemaAlertaAjuda.png" ).default} style={{width: 800}} alt="Tela Sobre o Sistema (Alerta e Ajuda)" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

## Principais Componentes

##### 1. **Card — Identificação do Equipamento de Simulação**
Exibe os dados técnicos simulados da bomba de dragagem, incluindo ID do equipamento, modelo, número de série, versão de firmware, data de instalação, última manutenção, capacidade, profundidade máxima, corrente e tensão operacional. Oferece uma referência visual rápida sobre o estado e especificações do equipamento em operação.

##### 2. **Cards — Funcionalidades do Sistema**
Apresenta os 6 recursos principais do dashboard em formato de cards descritivos:
- Monitoramento em Tempo Real
- Controle de Profundidade
- Movimentação Direcional
- Monitoramento Elétrico
- Sensores Térmicos
- Sensor de Vazão

Cada card inclui ícone, título e descrição breve da funcionalidade, facilitando compreensão rápida das capacidades do sistema.

##### 3. **Accordeons — Tutoriais de Utilização**
Seção expansível com 4 tutoriais interativos organizados por funcionalidade:
- Controles de Movimentação
- Monitoramento de Câmeras
- Painel de Sensores
- Medidor de Amperagem

Cada accordeon detalha passo a passo como utilizar a funcionalidade correspondente, fornecendo orientação prática sem necessidade de consultar documentação externa.

##### 4. **Bloco — Avisos de Segurança**
Caixa de alerta destacada em tom amarelo contendo as principais indicações de segurança que o operador deve observar durante toda operação:
- Monitoramento constante de indicadores de amperagem
- Respeito aos limites de profundidade do fabricante
- Ação imediata em alertas vermelhos
- Cumprimento do cronograma de manutenção preventiva

##### 5. **Seção — Precisa de Ajuda?**
Fornece acesso rápido ao suporte técnico da Itubombas, com telefone e e-mail de contato direto para casos em que o operador necessite assistência além dos tutoriais.

#### Fluxo de Navegação

1. Operador acessa "Sobre o Sistema" via menu lateral
2. Visualiza automaticamente a seção de identificação do equipamento
3. Lê os cards de funcionalidades para entender o escopo do sistema
4. Expande accordeons conforme necessidade para aprender como utilizar cada funcionalidade
5. Consulta avisos de segurança antes de iniciar operação
6. Se necessário, contata suporte via números/e-mail exibidos na tela

#### Relação com Módulos Físicos e Sistema de Automação

A tela "Sobre o Sistema" simula dados reais de uma operação de dragagem para contextualizar o operador:

- **Equipamento simulado**: Bomba modelo G06-AutoBombas POC com especificações técnicas reais (profundidade máxima 35cm, faixa de corrente 0-0,33mA)
- **Métricas exibidas**: Reproduzem valores que o operador encontrará durante operações reais (timestamp de última manutenção, status operacional "Operacional")
- **Funcionalidades demonstradas**: Os 6 cards mapeiam diretamente para os módulos físicos (sensores, câmeras, motores), preparando o operador para interpretar feedback em tempo real

Esta abordagem torna a interface didática, reduzindo a curva de aprendizado antes da primeira operação prática.

#### Relação com User Stories

Esta tela contextualiza e documenta, por meio de cards e tutoriais, todas as user stories listadas na seção 4.2:

- **US-M1A-01** e **US-M1A-02** — via Card "Controle de Profundidade"
- **US-M1B-01** e **US-M1B-02** — via Card "Monitoramento Elétrico" e tutorial "Medidor de Amperagem"
- **US-M2A-01** a **US-M2A-06** — via Card "Movimentação Direcional" e tutorial "Controles de Movimentação"
- **US-M2B-01** e **US-M2B-02** — via Card "Monitoramento em Tempo Real" e tutorial "Monitoramento de Câmeras"
- **US-M1C-01** e **US-M1C-02** — via Card "Monitoramento em Tempo Real" e seção "Avisos de Segurança"

#### Diferença entre CLI e Frontend

##### **Abordagem CLI (Anterior)**
- Baseada em linha de comando sem interface visual
- Exibia apenas métricas criptografadas ou números durante execução
- Operador recebia feedback binário: "comando aceito" ou "erro"
- Ausência de documentação integrada; operador precisava consultar manuais externos
- Difícil visualização de dados históricos

##### **Abordagem Frontend (Atual)**
- **Interface gráfica intuitiva** com cards, icons e layout responsivo
- **Simulação contextualizada** mostrando dados reais do equipamento antes da operação
- **Documentação embutida** em forma de 6 cards explicativos + 4 tutoriais interativos
- **Alertas destacados** em blocos visuais (avisos de segurança em box amarelo)
- **Acesso imediato a suporte** via contato telefônico/email na mesma tela
- **Histórico persistente** com timestamps integrado em toda operação, acessível para auditoria posterior

**Ganho principal**: O operador não precisa memorizar comandos; ele compreende o sistema visualmente e tem informações sempre disponíveis na plataforma, reduzindo dependência de treinamento externo e aumentando segurança operacional.

### 5.3 Tela "Dashboard Gestor"

<p style={{textAlign: 'center'}}>Figura 9 - Dashboard do Gestor</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <!-- Substitua a imagem, título e alt text-->
        <img src={require("/img/GestorDash.png" ).default} style={{width: 800}} alt="Dashboard do Gestor" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>



---

#### Objetivo da Tela

A tela "Gestão de Sessões" é a tela principal do sistema Itubombas, funcionando como ponto central de controle e acompanhamento das operações das bombas de dragagem. Ela permite que o operador visualize o histórico completo de sessões, filtre registros por data, status e operador, e acesse os detalhes individuais de cada operação. Diferentemente da CLI anterior, que não oferecia visibilidade histórica das sessões, esta tela provê uma visão consolidada e paginada de todas as operações realizadas, facilitando auditoria, acompanhamento de equipe e identificação rápida de alertas em andamento.

---

#### Principais Componentes

**1. Cabeçalho — Identificação da Tela**

Exibe o título "Gestão de Sessões", subtítulo descritivo ("Acompanhamento de operações das bombas"), hora atual e data formatada (ex.: Terça-feira, 10 de março). No canto superior direito é exibido o indicador de conectividade do sistema ("Conectado — Sistema"), mantendo o operador informado sobre o estado da conexão em tempo real.

**2. Barra de Filtros**

Permite ao operador refinar a listagem de sessões por três dimensões:

- **Todas as datas** — seletor de período para filtrar por intervalo de datas
- **Todos** — filtro de operador responsável pela sessão
- **Todas** — filtro de status da sessão (Finalizada, Em Andamento, Alerta)

Os filtros são aplicados de forma combinada, permitindo consultas específicas sem necessidade de ferramentas externas.

**3. Tabela — Histórico de Sessões**

Componente central da tela, apresenta as sessões em formato tabular com as seguintes colunas:

- **Sessão** — identificador único sequencial da operação (ex.: #001, #002)
- **Início** — horário de início da operação
- **Fim** — horário de encerramento da operação
- **Operador** — nome do responsável pela sessão
- **Status** — indicador visual colorido do estado atual: "Finalizada" (cinza), "Em Andamento" (laranja), "Alerta" (vermelho)
- **Ação** — botão "Detalhar" com ícone de visualização para acesso ao detalhamento completo da sessão

O contador no canto superior direito da tabela indica o total de sessões encontradas (ex.: "8 sessões encontradas").

**4. Paginação**

Navegação entre páginas de resultados com controles de "Anterior" e "Próximo", além de botões numerados para acesso direto a cada página. O rodapé da tabela exibe o resumo de registros visíveis (ex.: "Mostrando 1 a 5 de 8 sessões").

**5. Menu Lateral — Navegação Global**

Painel fixo à esquerda com o logotipo Itubombas e os itens de navegação principais: Dashboard (ativo/selecionado), Sobre o Sistema, Sensores (com indicador de submenus), Configurações e Sair. Na parte inferior exibe o status operacional do sistema e quantidade de sensores ativos (ex.: "Sistema Operacional — 12 sensores ativos").

---

#### Fluxo de Navegação

1. Operador acessa o sistema e é direcionado automaticamente ao Dashboard (Gestão de Sessões)
2. Visualiza a lista paginada de sessões com status em destaque visual
3. Aplica filtros conforme necessidade (data, operador, status)
4. Identifica sessões com status "Alerta" ou "Em Andamento" para priorização
5. Clica em "Detalhar" para acessar o detalhamento completo de uma sessão específica
6. Pode navegar entre páginas para consultar sessões mais antigas

---

#### Relação com Módulos Físicos e Sistema de Automação

A tela "Gestão de Sessões" agrega e consolida dados gerados pelos módulos físicos durante cada operação:

- **Registro automático de sessão** — cada ativação do sistema físico (bomba, sensores, motores) cria automaticamente uma entrada na lista com timestamp de início
- **Status derivado de alertas** — sessões marcadas como "Alerta" refletem acionamento dos sensores de segurança (amperagem crítica, temperatura elevada, proximidade) durante a operação
- **Rastreabilidade de operador** — cada sessão registra o responsável, permitindo correlacionar eventos com o operador que realizou os comandos físicos de movimentação e controle
- **Indicador de sensores ativos** — o rodapé do menu lateral ("12 sensores ativos") reflete o estado atual dos módulos físicos conectados

---

#### Relação com User Stories

Esta tela atende às user stories do gestor (descritas na seção 4.2):

- **US-M1A-02** — rastreabilidade de movimentações Z via histórico de sessões
- **US-M1B-01** — sessões com status "Alerta" refletem corrente elevada
- **US-M2A-05** e **US-M2A-06** — consolidação e persistência dos comandos XY por sessão
- **US-M2B-02** — registro implícito de acessos às câmeras por sessão
- **US-M1C-01** — alertas de proximidade refletidos no status da sessão

---

#### Diferença entre CLI e Frontend

**Abordagem CLI (Anterior)**

- Sem registro visual de sessões anteriores
- Operador não tinha visão consolidada de operações passadas
- Ausência de filtros; busca por logs exigia acesso a arquivos do sistema
- Status operacional disponível apenas durante execução ativa
- Sem identificação de operador responsável por cada operação
- Paginação inexistente; logs em texto puro de difícil leitura

**Abordagem Frontend (Atual)**

- Histórico completo de sessões com identificadores únicos e timestamps
- Visão consolidada paginada com contador de sessões encontradas
- Filtros combinados por data, operador e status sem ferramentas externas
- Status persistente visível mesmo após encerramento da sessão
- Rastreabilidade completa com nome do operador em cada registro
- Paginação com navegação intuitiva e resumo de registros exibidos

*Ganho principal: O operador passa a ter visibilidade total sobre o histórico operacional, podendo identificar padrões, auditar operações passadas e localizar rapidamente sessões com alertas — capacidade inexistente na abordagem anterior baseada em CLI.*

---

### 5.4 Tela Detalhes da Sessão

<p style={{textAlign: 'center'}}>Figura 4 - Tela de Detalhamento por Sessão</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <!-- Substitua a imagem, título e alt text-->
        <img src={require("/img/GestorporBomba.png" ).default} style={{width: 800}} alt="Tela de Detalhamento por Sessão" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

---

#### Objetivo da Tela

A tela "Detalhes da Sessão" oferece uma análise aprofundada de uma operação específica de dragagem, permitindo que o operador ou gestor examine cronologicamente todos os alertas registrados, compreenda a distribuição temporal das fases operacionais e consulte os metadados completos da sessão. Acessada a partir do botão "Detalhar" na tela de Gestão de Sessões, ela transforma dados brutos de sensores e comandos em uma narrativa visual estruturada da operação, viabilizando auditoria técnica, identificação de gargalos e planejamento de manutenções corretivas.

---

#### Principais Componentes

**1. Cabeçalho da Sessão**

Exibe o identificador da sessão em destaque (ex.: "Sessão #001"), subtítulo "Detalhes da operação", horário atual e data. Inclui botão "Voltar para Gestão" para retorno à listagem de sessões sem perda de contexto, além do indicador de conectividade do sistema no canto superior direito.

**2. Cards de Metadados — Resumo Operacional**

Quatro cards horizontais sintetizam as informações essenciais da sessão:

- **Data** — data de realização da operação (ex.: 09/03/2026)
- **Operador** — nome do responsável pela operação (ex.: Carlos Silva)
- **Duração** — tempo total de operação calculado automaticamente (ex.: 4h 30min)
- **Status** — estado final da sessão com badge visual (ex.: "Finalizada")

Cada card possui ícone representativo, rótulo descritivo e valor em destaque, permitindo leitura rápida dos dados-chave sem necessidade de navegar pelo restante da tela.

**3. Histórico de Alertas**

Painel esquerdo com listagem cronológica de todos os eventos de alerta registrados pelos sensores durante a sessão. Cada entrada contém:

- **Timestamp** — horário exato do evento (ex.: 08:12, 08:18)
- **Tipo de sensor** — identificação da origem do alerta (Movimento XY, Corrente, Profundidade)
- **Valor percentual** — intensidade da leitura no momento do alerta (ex.: 80%, 92%)
- **Classificação visual** — badge colorido indicando severidade: "Atenção" (laranja), "Crítico" (vermelho), "Normal" (cinza)

O painel inclui controle de filtro (ícone de funil + "Filtrar") para refinar a visualização por tipo de sensor ou classificação, facilitando análise focada em eventos específicos.

**4. Fases da Operação**

Painel direito com visualização gráfica da distribuição temporal das fases operacionais da sessão. Composto por:

- **Barras de progresso individuais** — uma barra por fase (Buscando, Intermediário, Dragando) mostrando a porcentagem do tempo total dedicada a cada etapa, com cores distintas: verde escuro (Buscando), laranja/amarelo (Intermediário) e verde acinzentado (Dragando)
- **Linha do Tempo Completa** — representação horizontal integrada exibindo proporcionalmente as três fases no intervalo total da sessão (ex.: 08:00 às 12:30), com as mesmas cores das barras individuais para consistência visual

Esta visualização permite identificar rapidamente se a operação seguiu o padrão esperado ou se houve desvios nas proporções de tempo entre fases.

---

#### Fluxo de Navegação

1. Operador localiza sessão desejada na tela de Gestão de Sessões
2. Clica em "Detalhar" na linha correspondente da tabela
3. Visualiza automaticamente os cards de metadados no topo da tela
4. Analisa o Histórico de Alertas identificando eventos críticos por horário e tipo
5. Consulta as Fases da Operação para verificar distribuição temporal e identificar desvios
6. Utiliza filtro de alertas se necessário para análise focada em sensor específico
7. Retorna à Gestão de Sessões via botão "Voltar para Gestão" sem perda de filtros aplicados

---

#### Relação com Módulos Físicos e Sistema de Automação

A tela "Detalhes da Sessão" consolida e apresenta dados coletados diretamente pelos módulos físicos durante toda a operação:

- **Módulo 1-B (Leitura de Corrente)** — alertas de "Corrente" no histórico refletem leituras da motobomba acima do limiar configurado; o valor percentual (ex.: 92% — Crítico) é derivado da faixa operacional 0–0,33mA do equipamento
- **Módulo 2-A (Movimentação)** — os eventos de "Movimento XY" no histórico registram comandos direcionais executados durante a sessão, com indicação de intensidade e hora de ocorrência
- **Módulo 1-A (Motor de Passo / Profundidade)** — alertas de "Profundidade" indicam acionamentos do motor de passo com leituras próximas ou além do limite de 35cm do equipamento
- **Fases da Operação** — as três fases (Buscando, Intermediário, Dragando) mapeiam diretamente para os estados operacionais do conjunto balsa + bomba + sistema de ancoragem durante a missão

---

#### Relação com User Stories

Esta tela detalha individualmente os dados que a tela de Gestão de Sessões (seção 5.3) consolida em visão geral. Atende às seguintes user stories (descritas na seção 4.2):

- **US-M1A-02** — via Fases da Operação (timeline de movimentações Z)
- **US-M1B-01** e **US-M1B-02** — via Histórico de Alertas (corrente com classificação automática)
- **US-M2A-05** e **US-M2A-06** — via Cards de Metadados e Histórico de Alertas (movimentação XY com timestamps)
- **US-M2B-02** — via log cronológico completo de eventos
- **US-M1C-01** e **US-M1C-02** — via alertas de sensores laterais com severidade e timestamp

---

#### Diferença entre CLI e Frontend

**Abordagem CLI (Anterior)**

- Alertas exibidos apenas durante execução; sem persistência histórica
- Sem distinção visual de severidade; todos os alertas tinham o mesmo formato textual
- Ausência de metadados consolidados (duração calculada, nome do operador)
- Fases operacionais não mapeadas ou exibidas; operador sem noção de progresso
- Sem timeline visual; cronologia de eventos exigia leitura de logs texto sequencial
- Sem filtro de eventos; análise pós-operação era manual e demorada

**Abordagem Frontend (Atual)**

- Histórico persistente de alertas com timestamps acessível a qualquer momento pós-operação
- Badges coloridos por severidade (Crítico/Atenção/Normal) com filtro integrado
- Cards de metadados calculados automaticamente (duração, status, operador, data)
- Visualização das fases operacionais com barras de progresso e timeline completa
- Linha do tempo integrada mostrando proporção real de cada fase no intervalo da sessão
- Filtro de alertas por tipo e severidade para análise técnica focada e eficiente

*Ganho principal: O operador e gestor passam a ter acesso a uma análise estruturada pós-operação, com dados de sensores, fases e metadados organizados visualmente — eliminando a necessidade de interpretar logs de texto bruto e reduzindo significativamente o tempo de análise de ocorrências.*

## 6. Navegação e Usabilidade

### 6.1 Estrutura de Navegação

A navegação entre telas é realizada por meio do menu lateral (Sidebar), presente em todas as telas autenticadas. O menu oferece acesso direto às rotas principais:

| Item do Menu | Rota | Tela |
|---|---|---|
| Dashboard | `/dashboard` | Dashboard do Operador (Carlos) ou Dashboard do Gestor (Bruno) |
| Sobre o Sistema | `/sobre` | Informações técnicas e tutoriais |
| Sensores | — | Abre modal de sensores sobre a tela atual |
| Sair | `/auth/login` | Encerra sessão e redireciona ao login |

O fluxo de entrada segue o caminho: Login → Dashboard, com redirecionamento automático após autenticação bem-sucedida. A raiz `/` redireciona para `/auth/login`, garantindo que o ponto de entrada seja sempre a tela de autenticação. Os fluxos de navegação específicos de cada tela estão detalhados nas subseções de Fluxo de Navegação da seção 5.

### 6.2 Autenticação e Proteção de Rotas

O sistema utiliza JWT (JSON Web Token) armazenado no `localStorage` após login via `POST /auth/login`. Todas as requisições à API incluem automaticamente o token no header `Authorization: Bearer` por meio de um interceptor Axios. Em caso de expiração do token (HTTP 401), o sistema limpa a sessão local e redireciona o usuário para a tela de login, evitando estados inconsistentes.

### 6.3 Decisões de UX

As decisões de usabilidade foram orientadas pelos requisitos RNF07 (Clareza de Interface) e RNF08 (Simplicidade Operacional), considerando o contexto operacional de campo onde o operador precisa de respostas rápidas e inequívocas:

- **Tela única para operação** — o Dashboard do Operador concentra câmeras, controles e indicadores em uma única view, eliminando a necessidade de alternar entre telas durante operação ativa
- **Hierarquia visual por cores** — estados do sistema seguem o padrão semafórico: verde (normal/conectado), amarelo (atenção/elevado) e vermelho (crítico/desconectado), aplicado consistentemente no indicador de conexão, gauge de amperagem e badges de status de sessões
- **Feedback imediato ao toque** — botões de controle direcional e profundidade utilizam `active:scale-95` para confirmar visualmente o registro do comando, sem depender de resposta da API
- **Polling condicional** — requisições de amperagem são disparadas apenas quando o sistema está conectado, evitando re-renderizações que impactariam a estabilidade do feed de vídeo das câmeras
- **Indicador de conectividade persistente** — presente no cabeçalho de todas as telas, atualizado a cada 15 segundos, mantendo o operador sempre ciente do estado do sistema
- **Contagem de sensores ativos** — exibida no rodapé do menu lateral, fornecendo visão periférica do estado dos módulos físicos sem ocupar espaço da área operacional

### 6.4 Estados de Erro e Feedback

| Situação | Comportamento |
|---|---|
| Credenciais inválidas no login | Mensagem de erro exibida no formulário, sem redirecionamento |
| Token JWT expirado (401) | Sessão encerrada automaticamente com redirecionamento ao login |
| Sistema desconectado | Indicador vermelho no cabeçalho; polling de amperagem pausado |
| Câmera offline | Badge "OFFLINE" em cinza no card correspondente; demais câmeras não afetadas |
| Comando enviado com sucesso | Feedback visual imediato no botão (escala) + atualização do indicador correspondente no próximo ciclo de polling |

---

## 7. Limitações e Próximos Passos da Interface

As quatro telas implementadas, Dashboard do Operador, Sobre o Sistema, Dashboard do Gestor e Detalhes da Sessão, cobrem as jornadas principais das duas personas do projeto. Carlos (operador) consegue executar toda a operação de dragagem a partir de uma única tela com controles visuais, enquanto Bruno (gestor) dispõe de visão consolidada de sessões e ferramentas de auditoria pós-operação. A transição de CLI para interface gráfica elimina a necessidade de memorização de comandos e reduz significativamente o risco de erro operacional.

### 7.1 Limitações Atuais

| Limitação | Descrição |
|---|---|
| **Execução local** | A interface roda exclusivamente via servidor de desenvolvimento Vite em rede local; não há deploy em nuvem ou empacotamento para distribuição |
| **Dados mockados** | As câmeras 2, 3 e 4 utilizam feed simulado (apenas a Câmera 1 possui stream real via ESP32-CAM). A tela "Sobre o Sistema" utiliza dados de demonstração estáticos para o equipamento |
| **Slider de velocidade (US-M2A-02)** | O controle de velocidade PWM dos propulsores via slider (0–100%) está previsto no backlog mas ainda não foi integrado ao componente de controle direcional |
| **Tela de Configurações** | O item "Configurações" no menu lateral está presente visualmente, porém sem funcionalidade implementada (RNF09 — Configurabilidade) |
| **Proteção de rotas** | As rotas `/dashboard` e `/sobre` não possuem guarda de autenticação no nível do React Router; a proteção ocorre apenas por interceptação de respostas 401 da API |
| **Dashboard do Gestor e Detalhes da Sessão** | Telas projetadas e documentadas com protótipos visuais, porém ainda não integradas como rotas no frontend React (implementação prevista para próxima sprint) |

### 7.2 Próximos Passos

- **Implementar rotas do Gestor** — integrar as telas de Gestão de Sessões e Detalhes da Sessão como páginas React com rotas protegidas e consumo real da API
- **Proteção de rotas com `ProtectedRoute`** — adicionar componente de guarda que valide a existência e validade do token JWT antes de renderizar telas autenticadas
- **Slider de velocidade PWM** — implementar o controle de velocidade dos propulsores (US-M2A-02) no painel de controle direcional
- **Tela de Configurações** — desenvolver interface para parametrização de limites operacionais (área, corrente, profundidade) conforme RNF09

