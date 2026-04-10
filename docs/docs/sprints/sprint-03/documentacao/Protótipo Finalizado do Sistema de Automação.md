---
sidebar_label: "Protótipo Finalizado do Sistema de Automação"
sidebar_position: 1
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Protótipo Finalizado do Sistema de Automação

---

## 1. Visão Geral do Protótipo

Ao final da Sprint 3, o protótipo do sistema de automação Autobombas encontra-se integrado: os módulos de movimentação (Z e XY), sensores de corrente e de proximidade, e a câmera ESP32-CAM comunicam-se com um backend central via MQTT e REST, com persistência em PostgreSQL. O fluxo operacional passa pelo comissionamento de endpoints da API e pela vinculação dos periféricos ao broker e ao serviço de automação, permitindo controle e monitoramento unificados. Os protocolos adotados como padrão na equipe — MQTT para comando em tempo real e HTTP/REST para gestão e auditoria — atendem aos requisitos funcionais e não funcionais previstos para esta etapa da arquitetura.

---

## 2. Módulo 1 — Movimentação Z

---

### 2.1. Módulo 1-A — Movimento de Descida e Subida (Z) — Motor de Passo

#### 2.1.1 Arquitetura de Hardware

A arquitetura de hardware deste módulo é focada no acionamento preciso de um carretel que sobe e desce a motobomba.
- **Microcontrolador:** ESP32, escolhido por possuir Wi-Fi integrado, permitindo a comunicação sem fio via MQTT com o backend do sistema.
- **Atuador:** Motor de Passo (28BYJ-48 5V), operado com o auxílio de um driver (ULN2003) para garantir o torque necessário.
- **Fonte de Alimentação:** O motor e o driver são alimentados diretamente pelo pino de 5V do próprio ESP32 (que, por sua vez, é alimentado via USB ou fonte externa compátivel com a placa).
- **Fluxo de Comunicação:** O ESP32 conecta-se à rede Wi-Fi local e se inscreve (subscribe) em um tópico MQTT do broker central para escutar os comandos de giro. Ao finalizar o movimento ou encontrar um erro, o microcontrolador publica (publish) seu status no broker.

#### 2.1.2 Integração com Banco de Dados

O registro das movimentações do eixo Z é crucial para a rastreabilidade e auditoria operacional, sendo feito em um banco de dados relacional **PostgreSQL**.

- **Tabela Relacional:** `movimentacao_z`
- **Modelo Lógico e Tipos de Dados:**
  - `id` (SERIAL PRIMARY KEY)
  - `bomba_id`, `operador_id` (INTEGER, Foreign Keys)
  - `comando_bruto` (VARCHAR) - Opcional para auditoria do comando exato digitado no CLI (ex: `/z down 20`).
  - `posicao_inicial_cm`, `deslocamento_solicitado_cm`, `deslocamento_real_cm`, `posicao_final_cm` (DECIMAL) - Logam as métricas físicas de profundidade.
  - `voltas_mqtt` (DECIMAL) - Tradução do deslocamento físico para quantidade de rotações do motor.
  - `status` (VARCHAR) - Estado da operação (`EM_ANDAMENTO`, `CONCLUIDO`, `ABORTADO`).
  - `timestamp_inicio`, `timestamp_fim` (TIMESTAMP).

- **Arquitetura de Persistência:**
  A persistência ocorre em duas etapas contínuas:
  1. Quando o operador emite o comando (via CLI/API), a API REST insere uma linha no banco com status `EM_ANDAMENTO` e os marcadores iniciais de centímetros e voltas.
  2. A API despacha o comando via MQTT para o ESP32. Quando o ESP32 envia de volta ao broker MQTT a mensagem sinalizando o fim da movimentação (ex: `LIVRE` ou `ABORTADO: <voltas>`), o módulo backend em Python (pelo `mqtt_service`) captura o evento assincronamente e atualiza aquele registro no PostgreSQL, fixando o `timestamp_fim` e alterando o status para `CONCLUIDO` ou `ABORTADO`.

#### 2.1.3 Endpoints / Sistema de Comunicação

A interação com este módulo se dá unindo requisições síncronas (REST) da interface com acionamentos em tempo real (MQTT) do Edge.

**Endpoints REST (Gerenciamento de Comandos):**

1. **Criar Movimentação (Envio de Comando)**
   - **Rota:** `POST /movimentacao-z/`
   - **Payload Json de Entrada:**
```json
{
  "bomba_id": 1,
  "operador_id": 2,
  "comando_bruto": "/z down 20",
  "posicao_inicial_cm": 0.0,
  "deslocamento_solicitado_cm": 20.0,
  "voltas_mqtt": 7.4721
}
```
   - **Fluxo:** Ao receber o payload, a REST API insere no banco e realiza um publish MQTT para acionar o motor de passo.

2. **Atualizar Registro (Fim de Movimento ou Aborto)**
   - **Rota:** `PATCH /movimentacao-z/{registro_id}`
   - **Payload Json de Entrada:**
```json
{
  "status": "CONCLUIDO",
  "posicao_final_cm": 20.0
}
```

3. **Listar Histórico por Bomba**
   - **Rota:** `GET /movimentacao-z/bomba/{bomba_id}?limite=10`
   - **Retorno:** Lista com os últimos registros de operação Z daquela bomba.

4. **Recuperar Última Posição Conhecida**
   - **Rota:** `GET /movimentacao-z/posicao/{bomba_id}`
   - **Retorno JSON:** `{"posicao_cm": 20.0, "status": "CONCLUIDO", "timestamp_fim": "..."}`
   - **Fluxo:** Utilizado para calibrar o software na inicialização indicando onde o motor parou pela última vez.

5. **Fechar Registros Órfãos (Limpeza de Sessão)**
   - **Rota:** `PATCH /movimentacao-z/fechar-orfaos/{bomba_id}`
   - **Fluxo:** Altera o status de comandos travados como `EM_ANDAMENTO` para `ABORTADO` durante a iniciação segura do sistema.

**Mensagens MQTT (Broker Local/Remoto):**
- **Publicação (Backend -> ESP32):**
  - Tópico: `motor/<bomba_id>/cmd`
  - Payload via pub/sub estruturado (informando as `voltas_mqtt` e sentido `up/down`).
- **Escuta (ESP32 -> Backend):**
  - Tópico: `motor/<bomba_id>/status`
  - Payloads esperados de sucesso: `LIVRE`
  - Payloads de Falha/Interrupção: `ABORTADO:<voltas_executadas>`

#### 2.1.4 Vídeo Demonstrativo

O clipe abaixo apresenta o equipamento físico (ESP32 + Motor de Passo + Carretel) reagindo em conformidade à injeção de comandos enviados primeiramente a partir da CLI, trafegados pela Rota REST listada e entregues por meio de telemetria MQTT.

- **[Vídeo Demonstrativo - Motor Z (Módulo 1-A)](https://drive.google.com/file/d/13jXK5rGGRaOPiG4BkNaIR0iZUR18c1vY/view?usp=drive_link)**

---

### 2.2. Módulo 1-B — Leitura de Corrente de Operação

&nbsp; Nesta sprint foi realizada uma evolução do módulo de leitura de corrente desenvolvido anteriormente. O sistema passou por duas mudanças principais: a substituição do Arduino Uno pelo ESP32 e a implementação de comunicação utilizando o protocolo MQTT.

&nbsp; Enquanto na Sprint 02 os dados eram transmitidos do microcontrolador para o computador por comunicação serial, nesta etapa os dados passam a ser enviados por meio de rede Wi-Fi, utilizando um broker MQTT para intermediar a comunicação entre o dispositivo embarcado e a aplicação de software.

&nbsp; Além disso, foi desenvolvida uma API responsável por receber as leituras enviadas pelos dispositivos, processar essas informações e armazená-las em banco de dados. Essa arquitetura aproxima o protótipo de sistemas reais de Internet das Coisas (IoT), permitindo transmissão de dados em tempo real e integração com outras aplicações.

#### 2.2.1 Arquitetura de Hardware

##### 2.2.1.1 Microcontrolador e Circuito de Medição

&nbsp; A principal alteração no hardware foi a substituição da placa Arduino Uno pela placa **ESP32**, que possui **conectividade Wi-Fi integrada**. Essa mudança permite que o microcontrolador envie dados diretamente pela rede, eliminando a necessidade de comunicação serial contínua com o computador.

&nbsp; O circuito de medição permanece baseado no mesmo princípio utilizado na sprint anterior. Um potenciômetro de 100kΩ é utilizado para variar manualmente a tensão aplicada ao circuito, simulando diferentes valores de corrente elétrica.

&nbsp; Essa tensão é aplicada a um resistor de 10kΩ, que atua como resistor shunt. A partir da queda de tensão nesse resistor, o microcontrolador realiza a leitura analógica e calcula a corrente elétrica utilizando a Lei de Ohm.

&nbsp; A leitura analógica é realizada pelo **pino GPIO 34** do ESP32, substituindo a entrada analógica A0 utilizada anteriormente no Arduino.

&nbsp; O ESP32 possui conversor analógico-digital (ADC) com resolução de 12 bits, produzindo valores entre 0 e 4095 para tensões entre 0 V e 3,3 V. Esses valores são convertidos em tensão e posteriormente em corrente elétrica considerando o valor conhecido do resistor presente no circuito.

&nbsp; Além da corrente elétrica, também é calculado o **percentual da leitura** em relação ao fundo de escala do ADC, utilizado posteriormente para **classificação das condições de operação**.

##### 2.2.1.2 Alimentação do Sistema

&nbsp; O ESP32 é alimentado por meio de um cabo USB conectado ao computador, que fornece energia para o funcionamento do microcontrolador e para o circuito montado em protoboard.

&nbsp; Essa conexão também permite a programação do firmware e a visualização de informações de depuração por meio do monitor serial da Arduino IDE durante o desenvolvimento e testes do sistema.

##### 2.2.1.3 Lista de Componentes

| Componente              | Quantidade | Descrição                                         |
|-------------------------|------------|---------------------------------------------------|
| ESP32                   | 1          | Microcontrolador com conectividade Wi-Fi integrada |
| Protoboard              | 1          | Utilizada para montagem do circuito sem solda     |
| Resistor de 10kΩ        | 1          | Utilizado como resistor shunt para medição de tensão |
| Potenciômetro de 100kΩ  | 1          | Permite variar manualmente a tensão do circuito   |
| Jumpers                 | Vários     | Fios utilizados para realizar as conexões elétricas |
| Cabo USB                | 1          | Utilizado para alimentação e programação do ESP32 |

#### 2.2.2 Integração com Banco de Dados

&nbsp; Para permitir o armazenamento e a consulta das leituras de corrente, foi desenvolvida uma **API em Python utilizando o framework Flask**, responsável por integrar os dispositivos IoT com o banco de dados do sistema.

&nbsp; Nesse modelo, o ESP32 envia as leituras utilizando o protocolo **MQTT**, enquanto a API atua como cliente assinante desse broker, recebendo automaticamente as mensagens publicadas pelo dispositivo.

&nbsp; Sempre que uma nova leitura é recebida, a API executa um processo de interpretação dos dados e registra essas informações no banco de dados por meio da camada de repositórios da aplicação.

&nbsp; Cada leitura registrada contém informações relacionadas ao estado de operação da motobomba. Entre os principais dados armazenados estão:

- identificação da bomba associada à leitura
- identificação do operador
- valor da corrente elétrica medida
- percentual da leitura em relação ao fundo de escala
- classificação da corrente
- sugestão operacional
- data e horário da leitura

&nbsp; Esse conjunto de informações permite manter um **histórico estruturado das condições de operação do sistema**, possibilitando consultas posteriores e análise do comportamento da corrente ao longo do tempo.

&nbsp; O sistema permite duas formas de registro das leituras. A primeira ocorre de forma **automática**, sempre que o ESP32 publica uma nova mensagem no broker MQTT. A segunda ocorre **sob demanda**, quando uma aplicação cliente solicita explicitamente uma nova leitura por meio de um endpoint da API.

&nbsp; Essa abordagem permite tanto o **monitoramento contínuo do sistema** quanto a realização de **leituras específicas** quando necessário.

#### 2.2.3 Endpoints / Sistema de Comunicação

&nbsp; A comunicação entre os componentes do sistema ocorre por meio de duas tecnologias principais: MQTT e API REST.

&nbsp; O protocolo MQTT é utilizado para a transmissão das leituras de corrente do ESP32 para o servidor, enquanto a API REST permite que aplicações cliente consultem e manipulem as informações registradas no banco de dados.

##### 2.2.3.1 Comunicação MQTT

&nbsp; No sistema desenvolvido, o ESP32 atua como publicador de mensagens, enviando periodicamente as leituras de corrente para um tópico MQTT. A API atua como assinante desse tópico, recebendo automaticamente os dados publicados.

&nbsp; As mensagens enviadas pelo dispositivo são transmitidas em formato JSON e contêm as informações necessárias para o processamento da leitura.

&nbsp; Um exemplo de payload utilizado para telemetria de corrente é apresentado a seguir:

```
{
  "corrente_a": 0.00032,
  "percentual": 72.1,
  "operador_id": 1
}
```
&nbsp; Após receber essa mensagem, a API interpreta os dados enviados, aplica a lógica de classificação da corrente conforme descrito anteriormente na Seção 2.2 e registra a leitura no banco de dados.

##### 2.2.3.2.Endpoints da API

&nbsp; Além da comunicação automática via MQTT, a API disponibiliza endpoints HTTP que permitem consultar e manipular os dados registrados no sistema.

**Criar Leitura de Corrente Manual**

```
POST /leituras-corrente/
```

&nbsp; Permite registrar manualmente uma nova leitura de corrente no sistema. Esse endpoint é utilizado principalmente para testes ou simulação de dados, permitindo inserir leituras mesmo na ausência do dispositivo físico.

**Listar Leituras de uma Bomba**

```
GET /leituras-corrente/bomba/{bomba_id}
```

&nbsp; Retorna todas as leituras de corrente associadas a uma bomba específica, permitindo analisar o histórico de operação do equipamento ao longo do tempo.

**Obter Última Leitura**

```
GET /leituras-corrente/bomba/{bomba_id}/ultima
```

&nbsp; Retorna a leitura de corrente mais recente registrada para a bomba especificada, sendo útil para aplicações de monitoramento em tempo real.

**Solicitar Nova Leitura ao Dispositivo**

```
POST /leituras-corrente/solicitar/{bomba_id}
```

&nbsp; Esse endpoint permite que uma aplicação cliente solicite que o ESP32 realize uma nova leitura de corrente.

&nbsp; Ao receber essa requisição, a API envia uma mensagem MQTT ao dispositivo correspondente solicitando a realização da leitura. O ESP32 então realiza a leitura do sensor e publica o resultado no broker MQTT, permitindo que a API capture automaticamente os dados e registre a nova leitura no banco de dados.


#### 2.2.4 Vídeo Demonstrativo

&nbsp; O [vídeo](https://drive.google.com/file/d/1xSdur_bUbPqAvZZ0eSjdKd1bPwb8sZCo/view?usp=drive_link) demonstra o funcionamento do Módulo 1-B após a migração para o ESP32 e a implementação da comunicação via MQTT. Nele é possível observar o circuito montado em protoboard, a leitura do potenciômetro simulando diferentes valores de corrente e o recebimento dessas leituras pela aplicação no computador, onde os dados são processados e exibidos no terminal.

---

## 3. Módulo 2 — Movimentação XY e Periféricos de Supervisão

---

### 3.1. Módulo 2-A — Posicionamento da Balsa e Ancoragem

#### 3.1.1 Arquitetura de Hardware

O módulo 2-A é responsável pelo posicionamento da balsa no eixo horizontal (XY). No protótipo atual, esse movimento é simulado por uma esteira de prototipação que se desloca para a esquerda ou para a direita. O cérebro do sistema é um **ESP32**, que recebe comandos via **Wi-Fi/MQTT** e aciona um **motor DC** por meio de um driver **L298N**.

A fonte de alimentação utilizada é de **12 V DC**. O ESP32 se conecta ao broker MQTT assim que liga e fica aguardando comandos. Ao receber uma instrução (ex.: `"esquerda"`), ele liga o motor na direção correta. Ao receber `"parar"`, desliga o motor. O estado atual é sempre publicado de volta no tópico de status para que o backend saiba o que está acontecendo.

#### 3.1.2 Integração com Banco de Dados

Cada movimentação da balsa é registrada no banco de dados PostgreSQL, na tabela `movimentacao_xy`. O registro guarda: qual bomba se moveu, quem deu o comando, a direção (`esquerda` ou `direita`), quanto tempo o motor ficou ativo e se o movimento foi concluído normalmente ou interrompido.

O registro é criado quando o operador inicia o movimento e atualizado quando o movimento termina. Se a sessão for encerrada de forma inesperada, os registros em aberto são automaticamente marcados como `INTERROMPIDO` na próxima vez que a CLI for iniciada.

#### 3.1.3 Endpoints / Sistema de Comunicação

A comunicação funciona em duas camadas:

- **CLI → Backend (API REST):** o operador digita um comando na CLI, que chama a API. A API salva o movimento no banco e repassa o comando para o ESP32 via MQTT.
- **Backend → ESP32 (MQTT):** o comando chega ao ESP32 pelo tópico `balsa/{id}/bomba`, e o ESP32 responde publicando seu status em `balsa/{id}/status`.

Os principais endpoints da API são:

| Método | Rota | O que faz |
|---|---|---|
| `POST` | `/movimentacao-xy/` | Inicia um movimento e publica o comando MQTT |
| `PATCH` | `/movimentacao-xy/{id}` | Finaliza o movimento com duração e status |
| `POST` | `/movimentacao-xy/comando/{bomba_id}` | Envia comando pontual (ligar, desligar, parar) |
| `GET` | `/movimentacao-xy/bomba/{bomba_id}` | Consulta histórico de movimentos |

Exemplo de payload enviado ao ESP32:

```json
{ "acao": "esquerda", "operador_id": 2 }
```

#### 3.1.4 Vídeo Demonstrativo

https://youtube.com/shorts/bDUsYEz8RYM

---

### 3.2. Módulo 2-B — Inspeção Visual com Câmera

#### 3.2.1 Arquitetura de Hardware

O módulo de inspeção visual é responsável pela captura de imagens do ambiente monitorado, permitindo a observação remota do sistema. Para isso, foi utilizado o microcontrolador ESP32-CAM, que integra um processador ESP32 com um módulo de câmera, possibilitando a aquisição e transmissão de imagens via rede Wi-Fi.

A alimentação do módulo é realizada por meio de uma fonte de 5 V regulada, proveniente de um regulador de tensão LM2596, que recebe energia de um sistema de 2 baterias de lítio colocadas em série.

A comunicação do módulo ocorre através da rede Wi-Fi, permitindo que o ESP32-CAM envie o fluxo de imagens para outros componentes do sistema ou para um computador na mesma rede. Dessa forma, as imagens capturadas podem ser acessadas remotamente por meio de um navegador.

Essa arquitetura permite que o módulo opere de forma independente dentro do sistema, realizando a captura e transmissão das imagens necessárias para a inspeção visual do ambiente monitorado. Além disso, vale ressaltar que esse sistema de alimentação pode ser implementado em todos os outros módulos, porém por enquanto está integrado apenas no Módulo 2-B.

### 3.3. Módulo 2-C — Fallback de  Sensores

#### 3.3.1 Arquitetura de Hardware

O Módulo 2-C atua como um sistema de percepção espacial para a balsa, monitorando a distância em relação às bordas e obstáculos. A arquitetura física conta com:
- **Microcontrolador:** ESP32, escolhido por processar ativamente os dados dos sensores e assegurar conectividade contínua via Wi-Fi/MQTT.
- **Sensores Ultrassônicos (Distanciamento):** Quatro sensores HC-SR04 posicionados para cobrir os eixos ortogonais (Frente, Trás, Esquerda e Direita). Estes sensores garantem uma leitura direcional independente com alcance parametrizado no firmware para um teto máximo de 3.0 metros, prevenindo anomalias de leitura em ambientes abertos.
- **Microcontrolador / Pinos:** Os gatilhos (`TRIG`) e retornos (`ECHO`) são conectados a portas digitais do ESP32 (ex: pinos 4/32 para frente, 5/33 para trás, 18/34 para esquerda, 19/35 para direita).
- **Fonte de Alimentação:** Alimentação padrão de 5V para operação dos sensores, com os sinais de retorno tipicamente compatibilizados para o nível lógico de 3.3V do ESP32.
- **Comunicação e Disparo:** A cada 500 milissegundos o ESP32 realiza as medições de hardware em uníssono, compila em um pacote JSON e publica espontaneamente no broker como telemetria periódica. Além disso, o sistema escuta ativamente o broker para requisições assíncronas de leitura sob demanda.

#### 3.3.2 Integração com Banco de Dados

Todas as leituras de distanciamento são persistidas no PostgreSQL na tabela da API correspondente (`leituras_distancia`). O fluxo de integração operacional se dá da seguinte forma:

- **Recebimento Contínuo:** O módulo backend em Python monitora os eventos publicados pelo ESP32 via MQTT. Cada mensagem de telemetria recebida contendo as 4 distâncias é processada.
- **Registro no Banco de Dados:** O backend valida e salva as informações no banco de dados, vinculando as leituras de distância (Frente, Trás, Esquerda e Direita) à bomba respectiva e ao operador ativo.
- **Histórico Operacional:** Essa persistência constante cria um histórico detalhado do posicionamento da balsa durante a operação, permitindo consultas posteriores ao perfil de deslocamento e às aproximações das margens ou barreiras através da CLI.

#### 3.3.3 Endpoints / Sistema de Comunicação

O fluxo comunicacional deste módulo faz uso restrito de conexões MQTT ultrarrápidas em conjunto com endpoints REST que gerenciam a visualização na CLI.

**Mensagens MQTT (Broker Local/Remoto):**
- **Publicação Contínua (ESP32 -> Backend):**
  - Tópico: `sensor/<bomba_id>/distancias`
  - Payload padrão publicado ativamente a cada 500ms atestando a integridade do perímetro:
```json
{
  "frente_m": 1.25,
  "tras_m": 0.89,
  "esq_m": 3.0,
  "dir_m": 2.1
}
```
- **Escuta de Comandos (Backend -> ESP32):**
  - Tópico: `sensor/<bomba_id>/comando`
  - Payload demandado pelo Backend para forçar disparo e renovar a leitura: `{"acao": "ler_distancia"}`

**Endpoints REST (Módulo API):**

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/leituras-distancia/` | Cria e registra manualmente um novo pacote com as quatro medidas espaciais no banco (usado para testes/fallback). |
| `GET` | `/leituras-distancia/bomba/{bomba_id}/ultima` | Recupera imediatamente na API a telemetria espacial mais recente guardada no sistema. |
| `GET` | `/leituras-distancia/bomba/{bomba_id}?limite=X` | Traz o registro histórico em formato de lista, informando o vetor de distâncias em cada instante. |
| `POST` | `/leituras-distancia/solicitar/{bomba_id}` | Emite por via HTTP o comando MQTT, solicitando que o Edge compute as bordas proativamente. |

#### 3.3.4 Vídeo Demonstrativo
 
 No clipe abaixo, observa-se o sistema operando e realizando a medição contínua da distância frente a obstáculos no ambiente de testes.  
 À medida que um anteparo/parede se aproxima, as alterações métricas são computadas instantaneamente pelas leituras ultrassônicas e refletidas nos pacotes MQTT processados pela API do sistema.
 
 - **[Vídeo Demonstrativo - Medição de Sensores (Módulo 2-C)](https://drive.google.com/file/d/1-G9i-uzYXQbHc6tvp4jUmPUSM8OXCs7m/view?usp=drive_link)**

---

## 4. Requisitos Atendidos
 
 A seguir, encontra-se a rastreabilidade global da entrega desta etapa em relação à matriz de requisitos do projeto. Os itens abaixo referem-se à arquitetura validada ao longo das Sprints 1 a 3 que fundamentam este Protótipo Funcional.
 
 **Funcionais:**
 - **[RF-01] Controle de Movimentação em Eixo Z:** Atendido pelo **Módulo 1-A** (Motor de Passo + Carretel acionado via backend/MQTT). Evidência: Vídeo demonstrativo no item 2.1.4.
 - **[RF-02] Monitoramento de Corrente:** Atendido pelo **Módulo 1-B** (Leitura analógica validada via ESP32 e salva no DB). Evidência: Vídeo demonstrativo no item 2.2.4.
 - **[RF-03] Controle Direcional XY:** Atendido pelo **Módulo 2-A** (Motor DC para movimentação esquerda/direita e frente/tras da esteira simulada). Evidência: Vídeo demonstrativo no item 3.1.4.
 - **[RF-04] Telemetria e Fallback de Choque:** Atendido pelo **Módulo 2-C** (Quatro sensores HC-SR04 publicando distanciamento de até 3 metros). Evidência: Vídeo demonstrativo no item 3.3.4.
 - **[RF-05] Interface de Comando Centralizada:** Atendido pelo **Módulo CLI (super-cli-unificado.py) e Backend REST Padrão**, que agora orquestram todas as funcionalidades através do banco PostgreSQL unindo os comandos diretos do operador e a telemetria assíncrona recebida do Broker MQTT. 
 
 **Não Funcionais:**
 - **[RNF-01] Conectividade Sem Fio e Escalável:** Validado em **todos os Módulos (1A, 1B, 2A, 2B, 2C)**. A substituição definitiva das placas originais (ex. Arduino Uno) por ESP32 atestam o projeto rodando inteiramente sobre Wi-Fi e protocolo pub/sub leve (MQTT), além de baratear o conjunto.
 - **[RNF-02] Rastreabilidade de Log:** Atendido pela arquitetura de banco de dados do **Backend**. Todas as leituras e requisições de movimento exigem login (JWT) e autenticação de operador. Comandos interrompidos ou finalizados também gravam logs exatos de início, finalização e metadados no SGBD PostgreSQL.

---
