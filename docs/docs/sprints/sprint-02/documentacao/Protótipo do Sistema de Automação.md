---
sidebar_label: "Protótipo do Sistema de Automação"
sidebar_position: 3
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Protótipo do Sistema de Automação

---

## 1. Visão Geral do Protótipo

&nbsp; O Autobombas é um sistema de automação desenvolvido para a Itubombas, com o objetivo de controlar e monitorar remotamente uma motobomba subaquática em ambiente de dragagem. O sistema é composto por múltiplos módulos — abrangendo movimentação vertical (eixo Z), leitura de sensores de corrente, navegação horizontal (eixo XY), visualização via câmera e detecção de proximidade por sensores de fallback — que foram desenvolvidos de forma independente nesta sprint, com foco em compreender o funcionamento isolado de cada feature antes de uma futura integração.

&nbsp; O controle de cada módulo é feito por meio de uma CLI (Command Line Interface), que permite ao operador interagir com o hardware de forma programática. O conjunto de microcontroladores utilizados varia entre ESP32 e Arduino, de acordo com as necessidades de cada módulo. Todas as operações relevantes são registradas em um banco de dados relacional, garantindo rastreabilidade e auditoria das ações realizadas.

&nbsp; A integração dos módulos em uma interface frontend unificada está prevista para etapas futuras do projeto, quando o operador poderá controlar o sistema completo por meio de uma aplicação visual.

&nbsp; Esta documentação descreve a arquitetura atual do sistema, os módulos desenvolvidos, as decisões de projeto, as instruções para execução e o log de evolução ao longo da sprint.

---


## 2. Módulo 1 — Movimentação Z

&nbsp; A movimentação de subida e descida (Z) da balsa é subdividida em duas partes — **1-A** (movimento de descida e subida) e **1-B** (leitura de corrente).

---

### 2.1. Módulo 1-A — Movimento de Descida e Subida (Z) — Motor de Passo

&nbsp; Este submódulo é responsável por controlar a movimentação no eixo Z (vertical) da bomba de dragagem, processando comandos lineares (em centímetros) e convertendo-os em ações cinemáticas de rotação por meio de um microcontrolador que se comunica via MQTT.

#### 2.1.1 Problema Proposto

&nbsp; A operação da bomba de dragagem exige um posicionamento vertical (eixo Z) preciso e seguro. O operador necessita de um sistema que permita enviar comandos de deslocamento em centímetros exatos (ex: descer 10 cm), eliminando a necessidade de calcular manualmente o número de voltas do motor. Além disso, o sistema requer travas lógicas para evitar o desenrolamento excessivo do cabo de içamento e um mecanismo de interrupção imediata (emergência) para prevenir colisões com a estrutura da balsa.

#### 2.1.2 Princípio de Funcionamento

&nbsp; O sistema é dividido em duas frentes: o cérebro (CLI) e o atuador (Edge). O operador interage com uma interface de linha de comando (CLI) em Python que calcula a conversão do deslocamento desejado com base no diâmetro mecânico do carretel (Ø 5.0 cm). Essa CLI publica os *payloads* em um broker MQTT local (`10.89.165.89`). 

&nbsp; Na ponta (Edge), um microcontrolador ESP32 recebe a instrução, converte-a em passos e aciona o motor através de um driver. O firmware implementa uma rampa de aceleração e desaceleração cinemática (variando o delay de passo entre 2500μs e 800μs) para garantir movimentos suaves. Em caso de interrupção ou emergência, o sistema realiza um recálculo de odometria, baseando-se nos passos executados até o aborto, e envia a nova posição real para o broker.

#### 2.1.3 Lista de Componentes

| Componente | Quantidade | Descrição |
|------------|-----------|-----------|
| **ESP32** | 1 | Microcontrolador (Atuador/Edge) operando via Wi-Fi. |
| **ULN2003AN** | 1 | Driver do motor de passo (Array de transistores Darlington, máx 500mA por canal). |
| **28BYJ-48** | 1 | Motor de passo (5V DC, unipolar, 4 fases, redução mecânica de 1/64, 4096 passos/volta em *half-step*). |
| **Fonte Chaveada 5V/2A** | 1 | Fonte de alimentação externa. GND unificado com o ESP32, mas VCC isolado. |

#### 2.1.4 Montagem do Circuito

&nbsp; Abaixo, apresentamos a matriz de prototipação, o vídeo de funcionamento e o esquema elétrico, destacando a isolação do VCC do motor do pino 3V3 do ESP32 para proteção contra correntes de *flyback*.


<p style={{textAlign: 'center'}}>Figura 1 - Montagem do Circuito e Prototipação 1-A</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={useBaseUrl('/img/imgPrototipacao2.jpeg')} style={{width: '100%', maxWidth: 800}} alt="Foto do Protótipo de movimentação em Z" />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

&nbsp; O circuito foi projetado com foco na segurança do microcontrolador. O pino GND da fonte chaveada 5V/2A é unificado com o GND do ESP32, garantindo a mesma referência de tensão. No entanto, a alimentação positiva (VCC) do driver ULN2003AN vem diretamente da fonte externa, mantendo-se totalmente isolada do regulador de tensão interno de 3.3V do ESP32, o que o protege contra picos reversos do motor.

#### 2.1.5 Limitações do Protótipo

* **Limites Físicos de Curso:** O sistema de software está travado para operar estritamente no intervalo de 0.0 cm a 200.0 cm de desenrolamento da corda, evitando colisões superiores e o limite final do cabo.
* **Capacidade de Corrente:** O driver ULN2003AN suporta um máximo de 500mA por canal, o que limita o torque de içamento (carga máxima que a bomba pode ter sem perder passos).
* **Race Conditions:** Para evitar concorrência e o envio de múltiplos comandos simultâneos, o sistema foi limitado à execução síncrona visual mediante o *lock* de estado (`OCUPADO` / `LIVRE`).

#### 2.1.6 Código Arduino

&nbsp; Partes principais do firmware em C++ focado na comunicação MQTT, manipulação das rampas de aceleração e tratamento da interrupção de emergência.

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
// ... (Configurações de rede e MQTT 10.89.165.89) ...

// Variáveis do motor e odometria
int delayPasso = 2500; 
float posicaoAtualPassos = 0;
bool emMovimento = false;

void callbackMQTT(char* topic, byte* payload, unsigned int length) {
  String msg = "";
  for (int i = 0; i < length; i++) { msg += (char)payload[i]; }
  
  if (msg == "EMERGENCIA") {
    pararMotorImediatamente();
    publicarOdometriaFallback();
  } else {
    // Processar alvo em voltas e iniciar movimento
    // Status passa para OCUPADO
  }
}

void loop() {
  client.loop();
  
  if (emMovimento) {
    // Lógica de movimentação em half-step (4096 passos/volta)
    // Rampa de aceleração: reduz o delayPasso gradualmente de 2500us até 800us
    executarPasso();
  }
}

void pararMotorImediatamente() {
  emMovimento = false;
  // Desliga todas as bobinas do ULN2003AN para evitar superaquecimento
}
```

&nbsp; No *callback* MQTT há um trecho crítico para casos de emergência:

```cpp
if (msg == "EMERGENCIA") {
  pararMotorImediatamente();
  publicarOdometriaFallback();
}
```

&nbsp; **Por que é importante:** Este trecho garante a segurança do sistema ao tratar o sinal de parada com prioridade máxima. Ele interrompe o hardware instantaneamente e reporta a última posição via MQTT para evitar que o sistema perca a referência da altura do cabo.

&nbsp; Já no `loop()` principal o coração da movimentação é observado:

```cpp
if (emMovimento) {
  // Rampa de aceleração: reduz o delayPasso gradualmente de 2500us até 800us
  executarPasso();
}
```

&nbsp; **Por que é importante:** Representa o núcleo da execução física. A lógica de rampa de aceleração é essencial para evitar que o motor de passo perca torque ou sofra vibrações excessivas em partidas bruscas, garantindo suavidade e precisão no deslocamento.

#### 2.1.7 Código Python

&nbsp; Estrutura principal da CLI que realiza a conversão matemática (diâmetro de 5.0 cm) e interage com o Broker MQTT, implementando o mecanismo de *lock* (Prevenção de Race Conditions).

```python
import paho.mqtt.client as mqtt
import math
import sys

DIAMETRO_CARRETEL_CM = 5.0
CIRCUNFERENCIA_CM = math.pi * DIAMETRO_CARRETEL_CM
status_motor = "LIVRE"

def calcular_voltas(distancia_cm):
    return distancia_cm / CIRCUNFERENCIA_CM

def on_message(client, userdata, msg):
    global status_motor
    payload = msg.payload.decode()
    if msg.topic == "bomba/z/status":
        status_motor = payload

def enviar_comando_z(comando, distancia=0):
    global status_motor
    if status_motor == "OCUPADO":
        print("[ERRO] Motor ocupado. Aguarde o término do movimento.")
        return
        
    voltas = calcular_voltas(distancia)
    
    if comando == "descer":
        print(f"[SUCESSO] Traduzido para: +{voltas:.4f} voltas")
        # client.publish("bomba/z/cmd", f"descer:{voltas}")
    elif comando == "subir":
         print(f"[SUCESSO] Traduzido para: -{voltas:.4f} voltas")
        # client.publish("bomba/z/cmd", f"subir:{voltas}")

# Captura de Ctrl+C para Emergência
try:
    # Loop de prompt da CLI
    pass
except KeyboardInterrupt:
    print("[!!!] ENVIANDO SINAL DE EMERGÊNCIA")
    # client.publish("bomba/z/cmd", "EMERGENCIA")
    sys.exit(0)
```

&nbsp; A conversão matemática é feita por:

```python
def calcular_voltas(distancia_cm):
    return distancia_cm / CIRCUNFERENCIA_CM
```

&nbsp; **Por que é importante:** Este trecho realiza a abstração matemática necessária para a operação. Ele traduz a unidade de medida do usuário (centímetros) para a grandeza rotacional (voltas) baseada na geometria real do carretel físico.

&nbsp; O mecanismo de *lock* aparece neste bloco:

```python
if status_motor == "OCUPADO":
    print("[ERRO] Motor ocupado. Aguarde o término do movimento.")
    return
```

&nbsp; **Por que é importante:** Implementa o mecanismo de lock lógico. Ele impede que novos comandos sejam enviados enquanto o motor ainda está em execução, prevenindo conflitos de dados e garantindo que o hardware siga uma sequência de comandos organizada.

#### 2.1.8 CLI

&nbsp; A Interface de Linha de Comando (CLI) atua como o cérebro da operação. Ela processa as validações e persiste os dados gerados na tabela log_movimentacao_z para permitir auditorias por parte dos gestores.

<p style={{textAlign: 'center'}}>Figura 2 - Montagem do Circuito e Prototipação 1-A</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={useBaseUrl('/img/imgPrototipacao.jpeg')} style={{width: '100%', maxWidth: 800}} alt="Foto do Protótipo de movimentação em Z" />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

 &nbsp; Pré-requisito: Mosquitto rodando no IP 10.89.165.89:1883
 Dependências: pip install paho-mqtt

#### Inicialização do módulo

&nbsp; $ python cli_motor.py

#### Exemplo: Liberar 25.5 cm de cabo

```bash
CLI> movZ descer(25.5)
[SUCCESSO] Traduzido para: +1.6233 voltas
Aguardando motor...
[INFO] Movimento CONCLUÍDO
```

<p style={{textAlign: 'center'}}>Figura 3 - CLI 1-A em funcionamento</p>
    <div style={{margin: 25}}>
        <div style={{textAlign: 'center'}}>
            <img src={useBaseUrl('/img/imgPrototipacao.jpeg')} style={{width: '100%', maxWidth: 800}} alt="Foto do CLI em funcionamento" />
            <br/>
        </div>
    </div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

&nbsp; Em resumo, o módulo 1-A unifica o rigor lógico da CLI em Python (tradução espacial e locks) com a execução física no ESP32, garantindo que o operador apenas se preocupe com o valor em centímetros, enquanto o sistema gerencia as conversões cinemáticas, segurança por odometria reversa e persistência de dados.

#### 2.1.9 Vídeo Demonstrativo

&nbsp; Link do [vídeo](https://drive.google.com/file/d/1pTRSiBw9SrRDpV-i9Nd280-Tho2yNlf2/view?usp=drive_link)

---

### 2.2. Módulo 1-B — Leitura de Corrente de Operação

&nbsp; Este módulo consiste no desenvolvimento de um **protótipo de medição de corrente utilizando Arduino e componentes eletrônicos básicos montados em protoboard.** O sistema foi projetado para simular a leitura de corrente elétrica por meio de um circuito simples, permitindo observar diferentes valores de entrada e o comportamento das medições realizadas pelo microcontrolador.

&nbsp; O protótipo foi construído como uma etapa inicial do projeto, com o objetivo de validar o funcionamento do hardware e compreender o processo de aquisição de dados elétricos. A utilização de componentes simples permite **testar o sistema de forma controlada** antes da implementação em um ambiente real.

&nbsp; Em uma **aplicação futura**, o sistema será utilizado no monitoramento da corrente elétrica de uma motobomba empregada em processos de dragagem. A corrente medida poderá ser utilizada como indicador indireto das condições de operação, auxiliando na identificação do **tipo de material sendo sugado** e contribuindo para decisões relacionadas ao posicionamento do equipamento.

#### 2.2.1 Problema Proposto

&nbsp; O objetivo do projeto é realizar a medição de corrente elétrica utilizando Arduino, entretanto não havia disponível um sensor de corrente dedicado, como sensores baseados em **efeito Hall**. Dessa forma, foi necessário desenvolver uma alternativa que permitisse **simular a leitura de corrente elétrica de maneira controlada.**

&nbsp; Foi implementado um método de medição indireta de corrente utilizando **resistor shunt** de 10kΩ e leitura analógica pelo Arduino, simulando o comportamento de um sensor de corrente. O circuito desenvolvido permite variar a corrente elétrica por meio de um **potenciômetro** de 100kΩ e medir a queda de tensão em um resistor conhecido, possibilitando o cálculo da corrente através da **Lei de Ohm.**

#### 2.2.2 Princípio de Funcionamento

&nbsp; O sistema de medição foi baseado na **Lei de Ohm**, que estabelece a relação entre tensão, corrente e resistência:

&nbsp; **I=V/R**

&nbsp; Onde:

- **I** representa a corrente elétrica;
- **V** representa a tensão medida;
- **R** representa a resistência.

&nbsp; No circuito desenvolvido, a corrente elétrica passa por um resistor de 10kΩ, que funciona como resistor shunt. O Arduino realiza a leitura da tensão sobre esse resistor através de uma entrada analógica.

&nbsp; A partir da tensão medida e do valor conhecido da resistência, é possível calcular a corrente elétrica que percorre o circuito.

&nbsp; O potenciômetro de 100kΩ foi utilizado para permitir o ajuste manual da corrente simulada, possibilitando testar diferentes condições de operação.


#### 2.2.3 Lista de Componentes

&nbsp; Os seguintes componentes foram utilizados na montagem do circuito:

| Componente             | Quantidade | Descrição                                                  |
| ---------------------- | ---------- | ---------------------------------------------------------- |
| Arduino Uno            | 1          | Placa microcontroladora para controle do circuito          |
| Protoboard             | 1          | Matriz de contatos para montagem do circuito sem solda     |
| Resistor de 10kΩ       | 1          | Resistor utilizado para limitar ou ajustar corrente/tensão |
| Potenciômetro de 100kΩ | 1          | Resistor variável utilizado para variar a resistência      |
| Jumpers                | Vários     | Fios utilizados para realizar as conexões elétricas        |
| Cabo USB               | 1          | Cabo utilizado para alimentar e programar o Arduino        |


&nbsp; O Arduino foi utilizado como unidade de processamento e aquisição de dados, enquanto a protoboard permitiu a montagem do circuito sem necessidade de soldagem.

#### 2.2.4 Montagem do Circuito

&nbsp; O circuito foi montado em uma protoboard conectada ao Arduino. O potenciômetro foi utilizado como elemento de controle da corrente elétrica, sendo um dos terminais conectado ao 5V do Arduino enquanto o outro foi conectado ao resistor de 10kΩ.

&nbsp; O resistor de 10kΩ foi conectado entre o potenciômetro e o GND do Arduino, formando um circuito em série. A entrada analógica A0 do Arduino foi conectada ao ponto entre o potenciômetro e o resistor, permitindo a medição da tensão sobre o resistor. Essa configuração permite que a corrente seja ajustada através do potenciômetro e medida indiretamente pelo Arduino

&nbsp; A Figura 4 apresenta o diagrama do circuito desenvolvido no Tinkercad.


<p style={{textAlign: 'center'}}>Figura 4 - Simulação do circuito 1-B no Tinkercad</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/tinkercad_modulo_1_b.png").default} style={{width: 800}} alt="Montagem Tinkercad do Circuito 1-B" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

&nbsp; Após a validação do circuito em ambiente de simulação, foi realizada a montagem física em protoboard, permitindo verificar o funcionamento do circuito em condições reais e identificar possíveis diferenças em relação à simulação.

<p style={{textAlign: 'center'}}>Figura 5 - Montagem física do circuito 1-B em protoboard</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/protoboard_modulo_1_b.jpeg").default} style={{width: 800}} alt="Montagem Física do Circuito 1-B" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

#### 2.2.5 Limitações do Protótipo

&nbsp; O protótipo desenvolvido representa uma versão simplificada do sistema final, e os valores de corrente medidos são muito menores que os valores reais esperados na aplicação final, que estarão na ordem de centenas de amperes. Nesta etapa, **o objetivo foi validar o método de medição e o funcionamento geral do sistema.**

&nbsp; Em uma aplicação real, o resistor shunt será substituído por um sensor de corrente apropriado, como sensores baseados em efeito Hall, capazes de medir correntes elevadas com segurança.

#### 2.2.6 Software

&nbsp; Esta seção descreve a implementação de software do Módulo 1-B, composta por dois componentes que atuam em conjunto: o firmware embarcado no **Arduino**, responsável pela aquisição e transmissão dos dados, e o programa **Python** executado no computador, responsável pela comunicação serial, processamento dos valores recebidos e apresentação das informações ao operador por meio de uma interface de linha de comando **(CLI)**.

#### 2.2.7 Código Arduino

&nbsp; O firmware do Arduino foi desenvolvido em C++ utilizando a Arduino IDE. Sua principal responsabilidade é realizar a leitura do sinal analógico gerado pelo divisor de tensão (que simula um sensor Hall), converter esse sinal em valores de corrente elétrica e percentual, e transmiti-los ao computador via comunicação serial, apenas quando solicitado.

**Declaração de variáveis e configuração inicial:**

&nbsp; O pino analógico A0 é declarado como a entrada do sensor. Na função `setup()`, a comunicação serial é inicializada a 9600 bps — a mesma taxa utilizada pelo código Python — para garantir sincronismo na troca de dados.

```cpp
int panalog = A0;   // Pino analógico conectado ao divisor de tensão

void setup() {
  Serial.begin(9600);   // Inicializa comunicação serial a 9600 bps
}
```

**Leitura analógica e conversão de valores:**

&nbsp; A função `loop()` é executada continuamente, porém o Arduino só realiza a leitura quando recebe o caractere `'c'` via serial. Essa abordagem sob demanda evita o envio contínuo de dados desnecessários, tornando a comunicação mais eficiente.

&nbsp; A leitura analógica com `analogRead()` retorna um valor inteiro entre 0 e 1023, correspondente à tensão de 0 V a 5 V na entrada A0. A partir desse valor (ADC), realizam-se três conversões em sequência:

```cpp
void loop() {
  if (Serial.available() > 0) {
    char comando = Serial.read();

    if (comando == 'c') {
      int avalor = analogRead(panalog);              // Leitura ADC: 0–1023

      float tensao = avalor * (5.0 / 1023.0);       // Conversão: ADC → Tensão (V)

      float corrente = tensao / 10000.0;             // Lei de Ohm: I = V / R  (R = 10 kΩ)

      float percentual = (avalor / 1023.0) * 100.0; // Percentual em relação ao fundo de escala

      Serial.print(corrente, 6);    // Envia corrente com 6 casas decimais
      Serial.print(',');
      Serial.println(percentual);   // Envia percentual e finaliza a linha
    }
  }
}
```

- **Conversão ADC → Tensão:** o valor inteiro do ADC é multiplicado pela razão `5,0 / 1023,0`, obtendo a tensão equivalente em Volts medida sobre o resistor shunt de 10 kΩ.

- **Conversão Tensão → Corrente (Lei de Ohm):** a corrente é calculada dividindo a tensão pela resistência do shunt (10.000 Ω), resultando em valores na ordem de microamperes a meio miliampere.

- **Cálculo do Percentual:** o valor do ADC é dividido por 1023 (máximo possível) e multiplicado por 100, expressando a leitura como percentual do fundo de escala. Esse percentual é o parâmetro utilizado pela lógica de classificação no Python.


#### 2.2.8 Código Python

&nbsp; O programa Python é executado no computador e atua como camada de interface entre o Arduino e o operador. Ele estabelece a comunicação serial, envia comandos ao Arduino, recebe e interpreta os dados, aplica a lógica de classificação e exibe o resultado formatado no terminal.

**Configuração da comunicação serial:**

&nbsp; A biblioteca `pyserial` é utilizada para estabelecer a conexão com o Arduino. A porta COM e o baud rate devem coincidir com os configurados no firmware:

```python
import serial

porta = 'COM6'                        # Porta serial do Arduino (ajustar conforme o sistema)
arduino = serial.Serial(porta, 9600)  # Conecta ao Arduino a 9600 bps
```

**Interface de comandos:**

&nbsp; Ao iniciar, o programa exibe um cabeçalho informativo com os comandos disponíveis. O laço principal aguarda a entrada do operador e executa a ação correspondente:

```python
print("Sistema de Monitoramento de Corrente")
print()
print("Digite:")
print("c → Ler corrente")
print("q → Sair")
print()

while True:
    comando = input('> ')

    if comando == 'q':      # Encerra o programa
        break

    if comando == 'c':      # Solicita leitura ao Arduino
        ...
```

**Comunicação, recepção e parsing dos dados:**

&nbsp; Ao receber o comando `'c'`, o programa envia o caractere via serial para o Arduino. O Arduino responde com uma linha no formato `corrente,percentual`, que é lida, decodificada e separada para uso:

```python
arduino.write(b'c')                         # Envia comando 'c' ao Arduino

dado = arduino.readline().decode().strip()  # Lê a linha de resposta e remove espaços

valores = dado.split(',')                   # Separa os valores pelo delimitador vírgula

corrente   = float(valores[0])              # Extrai o valor de corrente em Amperes
percentual = float(valores[1])              # Extrai o percentual
```

**Formatação da saída:**

&nbsp; Os valores recebidos são exibidos de forma estruturada, seguidos do bloco de classificação:

```python
print("=== Leitura ===")
print()
print("Corrente:", corrente, "A")
print("Percentual:", percentual, "%")
print()
```

**Lógica de Classificação de Corrente:**

&nbsp; Com base no percentual calculado pelo Arduino, o Python aplica uma estrutura condicional de três faixas para classificar o estado operacional da motobomba. Essa classificação é fundamentada no comportamento elétrico real do equipamento: a corrente consumida varia conforme o material sugado — líquido puro exige menor esforço do motor, enquanto a presença de sólidos aumenta a carga e, consequentemente, a corrente.

```python
if percentual < 70:
    print("Corrente baixa.")
    print("Predominância de sucção de líquido.")
    print("Sugestão: descer a motobomba.")

elif percentual < 85:
    print("Corrente normal.")
    print("Operação estável.")
    print("Manter posição atual.")

else:
    print("Corrente elevada.")
    print("Alta concentração de sólidos.")
    print("Manter posição.")
```

- **Faixa 0% – 69% (Corrente baixa):** indica que a motobomba está sugando predominantemente líquido, com baixa resistência ao escoamento. O sistema sugere descer a motobomba em busca de maior concentração de material sólido.

- **Faixa 70% – 84% (Corrente normal):** condição de operação estável, com mistura equilibrada entre líquido e sólidos. O sistema recomenda manter a posição atual da motobomba.

- **Faixa 85% – 100% (Corrente elevada):** alta concentração de sólidos (lodo) sendo sugada, próxima à capacidade nominal do equipamento. O sistema recomenda manter a posição e prosseguir com a operação de dragagem.

#### 2.2.9 CLI

&nbsp; A seguir são apresentadas evidências visuais da CLI em operação, cobrindo os três cenários possíveis de classificação. As capturas foram obtidas no terminal integrado do Visual Studio Code durante testes com o potenciômetro ajustado manualmente para cada faixa de corrente.

**Cenário 1 — Corrente Baixa (0% a 69%)**

&nbsp; O potenciômetro foi ajustado para uma posição que resultou em 58,36% da corrente de referência (0,000292 A). O sistema classificou o estado como corrente baixa, indicando predominância de sucção de líquido e sugerindo ao operador descer a motobomba.


<p style={{textAlign: 'center'}}>Figura 6 - CLI Corrente Baixa</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/cli_corrente_baixa.png").default} style={{width: 800}} alt="Protótipo do Sistema de Automação" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>


**Cenário 2 — Corrente Normal (70% a 84%)**

&nbsp; Com o potenciômetro ajustado para 70,28% (0,000351 A), o sistema identificou a condição de operação normal, indicando equilíbrio entre líquido e sólidos e recomendando a manutenção da posição atual.


<p style={{textAlign: 'center'}}>Figura 7 - CLI Corrente Normal</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/cli_corrente_normal.png").default} style={{width: 800}} alt="Protótipo do Sistema de Automação" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>


**Cenário 3 — Corrente Elevada (85% a 100%)**

&nbsp; Com o potenciômetro próximo à posição máxima, a leitura atingiu 90,22% (0,000451 A). O sistema classificou o estado como corrente elevada, sinalizando alta concentração de sólidos e recomendando que a motobomba mantenha sua posição e continue a operação de dragagem.


<p style={{textAlign: 'center'}}>Figura 8 - CLI Corrente Elevada</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/cli_corrente_alta.png").default} style={{width: 800}} alt="Protótipo do Sistema de Automação" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

#### 2.2.10 Vídeo Demonstrativo

&nbsp; O [vídeo](https://drive.google.com/file/d/1wb9S696ZPExv8xya_d-lNqQpMI8oKqUK/view?usp=drive_link) demonstra a integração entre hardware e software no sistema de medição de corrente do módulo 1‑B. Nele, o Arduino é responsável por captar e transmitir os dados do hardware, enquanto no computador o programa em Python recebe essas informações e as executa por meio da CLI (interface de linha de comando). Atualmente, o comando “c” na CLI retorna o valor da corrente com base nas faixas pré‑definidas, como já explicado acima. No futuro, essa interação será realizada diretamente por cliques na aplicação, substituindo a interface de comandos.

---

## 3. Módulo 2 — Movimentação XY

---

### 3.1. Módulo 2-A — Posicionamento da Balsa e Ancoragem

&nbsp; Este módulo simula a movimentação horizontal (eixo X) da balsa de dragagem utilizando uma mini-esteira didática com um motor DC. O controle é realizado através de uma Interface de Linha de Comando (CLI) interativa, comunicando-se via porta Serial com um microcontrolador responsável pela atuação do hardware.

#### 3.1.1 Problema Proposto

&nbsp; A operação da balsa de dragagem exige que o posicionamento sobre a grade de extração seja preciso e controlado remotamente. O problema consiste em garantir que os comandos de direção e frenagem enviados pelo operador (via software) sejam interpretados corretamente pelo hardware embarcado, acionando os propulsores (motores) de forma responsiva para navegar pela superfície do tanque de rejeitos.

#### 3.1.2 Princípio de Funcionamento

&nbsp; O sistema funciona em uma arquitetura de comunicação Mestre-Escravo. O computador do operador (Mestre) roda um script Python interativo que captura as teclas pressionadas em tempo real e envia bytes específicos via cabo USB (Serial). O microcontrolador ESP32 (Escravo) recebe esses bytes e, dependendo do caractere lido (ex: 'a' para esquerda, 'd' para direita, 'p' para parar), aciona as portas lógicas GPIO conectadas a um driver de potência (Ponte H). A Ponte H, por sua vez, inverte a polaridade da energia enviada ao motor DC da esteira, ditando seu sentido de rotação e velocidade.

#### 3.1.3 Lista de Componentes

| Componente | Quantidade | Descrição |
|------------|-----------|-----------|
|    Microcontrolador ESP32        |     1      |     Unidade de processamento para receber comandos seriais e acionar o driver.      |
|       Driver de Motor (Ponte H - L298N)     |    1       |   Módulo de potência para controle de sentido e velocidade do motor via PWM.        |
|      Motor DC (Acoplado à esteira)      |     1      |     Atuador eletromecânico que simula o deslocamento físico da balsa.      |
|      Cabos Jumpers      |     Vários      |      Realização das conexões de sinal e alimentação do circuito.     |
|       Fonte de Alimentação     |      1     |     Fornecimento de energia adequada para o motor e driver de potência.      |



#### 3.1.4 Montagem do Circuito e Funcionamento

&nbsp; A montagem física do circuito integra o microcontrolador ESP32 ao driver de potência (Ponte H L298N) para o controle direto do Motor DC da esteira. O vídeo acima demonstra o funcionamento prático da integração: os comandos inseridos na Interface de Linha de Comando (CLI) em Python são enviados via comunicação Serial, interpretados pelo firmware do ESP32 e convertidos em sinais de tensão na Ponte H, resultando na movimentação física imediata (frente, trás e parada) do protótipo.

&nbsp; Link do [vídeo](https://drive.google.com/file/d/1dlWqnFhzTg_tUYFsMN5LHRY3dEpzKZ9L/view?usp=drive_link)

#### 3.1.5 Limitações do Protótipo

&nbsp; Por se tratar de um modelo de validação em esteira didática, a movimentação atual é restrita a apenas um eixo linear (X), não simulando manobras complexas em Y ou rotações em torno do próprio eixo. Além disso, a comunicação atual depende de uma conexão Serial física (cabo USB simulando a porta COM3 ou ttyUSB), limitando a mobilidade. Em etapas futuras, essa conexão deverá ser substituída por telemetria sem fio (Wi-Fi ou Rádio).

#### 3.1.6 Código Arduino
```cpp
// Trecho destacando a leitura serial e acionamento do motor no firmware balsa.cpp
if (Serial.available() > 0) {
    char comando = Serial.read();
    
    // Mover para Esquerda
    if (comando == 'a') {
        digitalWrite(IN3, HIGH);
        digitalWrite(IN4, LOW);
        analogWrite(ENB, 255); // Velocidade máxima
    }
    // Parar (Freio)
    else if (comando == 'p') {
        digitalWrite(IN3, LOW);
        digitalWrite(IN4, LOW);
        analogWrite(ENB, 0);
    }
}
```

#### 3.1.7 Código Python
```python
# Trecho destacando a captura interativa de teclas e envio serial em esteira_cli.py
import click
import serial

esp = serial.Serial('COM3', 9600) # Alterar porta conforme SO

@click.command()
def controle_balsa():
    while True:
        tecla = click.getchar().lower()
        
        if tecla == 'a':
            esp.write(b'a') # Envia comando de mover para a esquerda
            click.secho("Movendo para a ESQUERDA", fg="green")
            
        elif tecla == ' ':
            esp.write(b'p') # Envia comando de parada
            click.secho("Motor PARADO", fg="red")
```

#### 3.1.8 CLI
```bash
# Comandos para ativar o ambiente virtual, instalar dependências e rodar a interface
python -m venv venv
source venv/Scripts/activate  # ou source venv/bin/activate no Linux/Mac
pip install -r requirements.txt
python esteira_cli.py
```

&nbsp; A implementação deste módulo comprova com sucesso a viabilidade técnica da integração entre o software de controle (CLI) e o hardware de atuação (motor e driver). O protótipo atendeu aos requisitos iniciais de controle direcional e frenagem em tempo real com baixa latência, estabelecendo uma base sólida e funcional para as próximas etapas do projeto, onde a comunicação serial será substituída por telemetria sem fio e integrada ao dashboard visual completo.

---

### 3.2. Módulo 2-B — Inspeção Visual com Câmera

&nbsp; Este submódulo documenta a implementação do sistema de telemetria visual da balsa de dragagem da Itu Bombas, detalhando o hardware, o fluxo de dados e as interfaces de visualização construídas para garantir segurança e monitoramento.

#### 3.2.1 Problema Proposto

&nbsp; Durante a operação de dragagem, a balsa se movimenta em ambientes com alto risco de colisão nas margens. Embora os sensores de proximidade forneçam dados quantitativos de distância, o operador e a equipe de gestão carecem de contexto visual para confirmar a posição exata do maquinário e avaliar falsos positivos. Além disso, a transmissão de vídeo em tempo real a partir de um ambiente remoto impõe desafios de conectividade, especialmente frente aos bloqueios de rede móvel 4G, exigindo uma arquitetura de transmissão eficiente e de baixa latência.

#### 3.2.2 Princípio de Funcionamento

&nbsp; O sistema é ancorado em um microcontrolador ESP32-CAM equipado com um sensor óptico OV2640. O princípio baseia-se na captura contínua de quadros, compressão nativa para o formato JPEG e disponibilização dessas imagens através de um fluxo de dados em rede. Na atual Prova de Conceito, a placa atua como um servidor HTTP local . O fluxo de vídeo é interceptado por uma interface cliente — seja a plataforma web para o gestor ou uma CLI desenvolvida em Python para testes locais —, que decodifica os pacotes e renderiza a imagem em tempo real na tela do operador, oferecendo suporte visual imediato para a tomada de decisão

#### 3.2.3 Lista de Componentes

**ESP32-CAM (AI Thinker)** — 1 unidade
Microcontrolador com Wi-Fi integrado e câmera OV2640, responsável pela captura das imagens e transmissão do stream pela rede.

**Regulador de tensão LM2596** — 1 unidade
Conversor DC-DC utilizado para reduzir a tensão das baterias para 5 V, garantindo alimentação estável para a ESP32-CAM.

**Baterias Li-Ion 18650** — 2 unidades
Fonte de energia do módulo, conectadas ao sistema de alimentação para fornecer energia ao regulador de tensão.

**Chave KCD11-101** — 1 unidade
Interruptor responsável por controlar o fornecimento de energia do sistema.

#### 3.2.4 Montagem do Circuito

&nbsp; Link do [vídeo](https://drive.google.com/file/d/13Kf5-rcqnA2EOAPYFZ2mKDnL_LqshQlY/view?usp=drive_link)

#### 3.2.5 Limitações do Protótipo

&nbsp; O protótipo atual apresenta restrições inerentes ao hardware e à arquitetura local (PoC):

&nbsp; Conexão Única (Gargalo HTTP): O servidor web interno da ESP32-CAM suporta apenas uma conexão de cliente por vez. Se a CLI em Python e o navegador tentarem acessar o IP simultaneamente, a placa recusará a segunda conexão ou sofrerá timeout.

&nbsp; Dependência de Rede Local (LAN): Atualmente, o streaming exige que câmera e cliente estejam sob o mesmo roteador. Para operação real via 4G, será necessária a transição do protocolo para WebSocket com um Cloud Broker.

&nbsp; Visão Noturna: O sensor OV2640 padrão não possui filtro infravermelho (IR) ou iluminação embutida, limitando a eficácia da inspeção visual a operações diurnas ou com a balsa bem iluminada.

#### 3.2.6 Código Arduino

Código fonte da ESP32-CAM disponível em: `backend/src/módulo2-B/firmware.ino`

#### 3.2.7 Código Python
Código Python disponível em: `backend/src/módulo2-B/cli.py`
#### 3.2.8 CLI
```bash
py cli.py abrir-camera
```
&nbsp;A implementação do Módulo 2-B eleva o grau de confiabilidade da solução Itu Bombas. Através desta integração entre hardware de baixo custo, desenvolvimento backend e uma interface visual clara, o sistema deixa de ser "cego" e passa a fornecer os dados sensoriais complementares necessários para que operadores e gestores auditem e reduzam o risco de avarias nas balsas de dragagem.

### 3.3. Módulo 2-C — Alertas de Segurança por Sensores

&nbsp; O submódulo 2-C é dedicado **exclusivamente ao fallback de segurança por sensores de proximidade**, complementando a movimentação horizontal do Módulo 2-A e a inspeção por câmera do Módulo 2-B. Quando a visão da câmera é insuficiente (falha, baixa visibilidade, oclusões ou atraso de rede), o Módulo 2-C assume o papel de “rede de segurança”, monitorando continuamente o entorno da balsa e emitindo alertas visuais ao operador.

#### 3.3.1 Problema Proposto

&nbsp; A movimentação semi-automática da balsa, controlada pelo operador, apoia-se principalmente na visualização de câmera tratada pelo Módulo 2-B. Entretanto, em situações de:

- baixa visibilidade (poeira, neblina, iluminação deficiente);
- perda temporária de vídeo ou latência elevada na transmissão;
- limitações do campo de visão da câmera (pontos cegos);

&nbsp; Existe risco de colisão com as bordas do tanque ou com obstáculos próximos, mesmo que o operador esteja enviando comandos válidos de movimentação XY.  

&nbsp; Assim, o problema central do Módulo 2-C é oferecer um fallback automático de segurança, baseado em sensores de proximidade, capaz de:

- detectar aproximação perigosa da balsa em cada direção (frente, trás, esquerda, direita);
- emitir alertas visuais claros ao operador (pop-ups/laterais na interface);
- registrar os eventos de risco para posterior análise de segurança.

&nbsp; A solução de tais problemáticas estão diretamente correlatas com as user stories US-M2C-01 e US-M2C-02

#### 3.3.2 Princípio de Funcionamento

&nbsp; O protótipo do Módulo 2-C utiliza uma ESP-Wroom-32U, equipada com 4 sensores ultrassônicos HC-SR04, posicionados nas quatro direções em relação à balsa:

- frente;
- trás;
- esquerda;
- direita.

&nbsp; O firmware embarcado (ver Seção 3.3.6) executa o seguinte ciclo contínuo:

**3.3.2.1. Leitura de distância por sensor**  
   &nbsp; Para cada HC-SR04, o microcontrolador gera um pulso de `TRIG` (≈10 µs), mede a duração do sinal de `ECHO` recebido e converte esse tempo em distância (em metros).  
   Distâncias acima de um limite máximo configurável (por exemplo, `3 m`) são interpretadas como “longe/seguro”.

**3.3.2.2. Classificação de risco**  
   &nbsp; A partir da distância medida \(d\), são aplicados limiares globais de risco, definidos em metros:

   - `dist_info`  – limite superior da zona de atenção/informativo;  
   - `dist_alerta` – limite da zona de alerta;  
   - `dist_critico` – limite da zona crítica.

   &nbsp; As regras de classificação são, de forma simplificada:

   - `d > dist_info` → estado `SEGURO`;  
   - `dist_alerta < d ≤ dist_info` → estado `INFORMATIVO`;  
   - `dist_critico < d ≤ dist_alerta` → estado `ALERTA`;  
   - `d ≤ dist_critico` → estado `CRITICO`.

**3.3.2.3. Protocolo de comunicação via Serial**  
   &nbsp; A ESP32 expõe o estado dos sensores por meio de comandos na porta serial (115200 bps), permitindo integração tanto com a CLI (lado PC) quanto com a interface gráfica:

   - `PING` → resposta `OK` (teste rápido de comunicação);  
   - `HELP` → lista de comandos e parâmetros suportados;  
   - `GET_STATUS` → devolve, em uma linha, as distâncias e níveis por direção, por exemplo:  
     `STATUS frente=1.23:ALERTA tras=2.40:SEGURO esquerda=0.55:CRITICO direita=1.80:INFORMATIVO`  
   - `SET_THRESHOLDS <dist_info_m> <dist_alerta_m> <dist_critico_m>` → atualiza, em tempo de execução, os limiares globais de risco, exigindo a condição `0 < dist_critico < dist_alerta < dist_info`.

   &nbsp; Além das respostas a comandos, o firmware pode publicar periodicamente linhas `STATUS` (por exemplo, a cada 1 s), mesmo sem requisição explícita. Isso permite que a interface acompanhe o entorno em “quase tempo real”, construindo barras de proximidade, ícones de perigo ou mensagens de texto sem sobrecarregar o operador com comandos manuais.

**3.3.2.4. Integração futura com a interface e o Módulo 2-A**  
   &nbsp; No front-end, os dados de status são consumidos para:

   - exibir pop-ups/laterais com mensagens do tipo “Cuidado, próximo à borda X”;  
   - ilustrar, nas bordas da visualização da câmera (Módulo 2-B), as leituras dos sensores:  
     - superior: sensor da frente;  
     - inferior: sensor de trás;  
     - esquerda: sensor do lado esquerdo;  
     - direita: sensor do lado direito;
   - aplicar regras de segurança integradas com a movimentação XY (Módulo 2-A), como:  
     - bloqueio total ou parcial de comandos em determinada direção quando o nível for `CRITICO`;  
     - redução da velocidade ou exibição de confirmações adicionais em níveis `ALERTA`.

**3.3.2.5. Tabela para integração futura com o BD**  
   &nbsp; Cada evento relevante de alerta pode ser registrado em uma tabela de banco de dados, por exemplo `alertas_sensores`, para posterior análise:

   | Campo         | Tipo sugerido   | Descrição                                               |
   |---------------|-----------------|---------------------------------------------------------|
   | `id`          | PK (inteiro)    | Identificador único do alerta                           |
   | `timestamp`   | datetime        | Momento exato do alerta                                 |
   | `sensor`      | texto           | Direção do sensor (`frente`, `tras`, `esquerda`, `direita`) |
   | `valor`       | real            | Leitura do sensor (distância em metros, por exemplo)   |
   | `mensagem`    | texto           | Texto exibido ao operador                              |
   | `nivel_risco` | texto           | Nível de risco (`informativo`, `alerta`, `critico`)    |

&nbsp;Essa tabela fornece insumos para relatórios de segurança, auditoria de incidentes e melhoria contínua das políticas operacionais.

#### 3.3.3 Lista de Componentes

| Componente | Quantidade | Descrição |
|------------|-----------|-----------|
| ESP-WROOM-32U (DevKit ESP32) | 1 | Microcontrolador responsável pela leitura dos sensores e lógica de risco |
| Sensor HC-SR04               | 4 | Sensores ultrassônicos de distância (frente, trás, esquerda, direita)    |

#### 3.3.4 Montagem do Circuito

<p style={{textAlign: 'center'}}>Figura 9 - Montagem do Circuito 2-C</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/montagem_2c.png").default} style={{width: 800}} alt="Montagem do Circuito 2-C" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

&nbsp; A montagem física posiciona os quatro sensores HC-SR04 nas laterais da balsa, de forma a cobrir as direções frente, trás, esquerda e direita. Os pinos `TRIG`/`ECHO` de cada sensor são ligados a GPIOs digitais da ESP32, enquanto a alimentação é feita a 5 V, respeitando o aterramento comum entre todos os dispositivos.  

#### 3.3.5 Limitações do Protótipo

&nbsp; Algumas limitações importantes do protótipo do Módulo 2-C são:

- **Alcance e zona cega dos ultrassônicos**: sensores HC-SR04 têm distância mínima de operação (zona morta muito próxima ao transdutor) e alcance máximo limitado, o que pode gerar leituras pouco confiáveis em objetos muito próximos ou muito distantes.  
- **Dependência de geometria e superfície**: superfícies irregulares, muito inclinadas ou absorventes podem refletir menos o feixe ultrassônico, reduzindo a precisão.  
- **Latência inerente à medição**: embora o ciclo de leitura seja rápido, ainda existe um intervalo entre leituras sucessivas e transmissão via serial, o que pode gerar pequeno atraso entre a aproximação real e a visualização do alerta.  
- **Calibração de limiares**: os valores de `dist_info`, `dist_alerta` e `dist_critico` precisam ser ajustados ao ambiente real (geometria da balsa) para evitar falsos positivos ou alertas inadequados.
- **Escopo de fallback**: o módulo não substitui a inspeção visual detalhada (câmera), atuando apenas como camada de segurança adicional para detecção de proximidade.

#### 3.3.6 Código Arduino

&nbsp; O firmware do Módulo 2-C é implementado no arquivo `src/módulo2-C/modulo2-C.ino`. De forma resumida, ele:

- configura os pinos `TRIG`/`ECHO` dos quatro sensores HC-SR04;  
- realiza leituras periódicas de distância em cada direção;  
- classifica o nível de risco (`SEGURO`, `INFORMATIVO`, `ALERTA`, `CRITICO`);  
- expõe um protocolo simples de comandos pela porta serial (`PING`, `HELP`, `GET_STATUS`, `SET_THRESHOLDS`);  
- publica periodicamente linhas `STATUS` com as leituras e níveis atuais.

&nbsp; O fundamental do firmware se dá por:

```cpp
// Esboço simplificado da lógica principal do firmware do módulo 2-C
struct SensorStatus {
  float distancia_m;
  const char* nivel_risco;
};

void loop() {
  SensorStatus frente   = lerSensor(frenteTrigPin, frenteEchoPin);
  SensorStatus tras     = lerSensor(trasTrigPin, trasEchoPin);
  SensorStatus esquerda = lerSensor(esqTrigPin, esqEchoPin);
  SensorStatus direita  = lerSensor(dirTrigPin, dirEchoPin);

  processarComandosSerial(); // Trata PING, HELP, GET_STATUS, SET_THRESHOLDS

  // Exemplo de linha STATUS periódica
  Serial.printf(
    "STATUS frente=%.2f:%s tras=%.2f:%s esquerda=%.2f:%s direita=%.2f:%s\n",
    frente.distancia_m,   frente.nivel_risco,
    tras.distancia_m,     tras.nivel_risco,
    esquerda.distancia_m, esquerda.nivel_risco,
    direita.distancia_m,  direita.nivel_risco
  );

  delay(1000); // período de atualização (ajustável)
}

// Função ilustrativa (implementação detalhada no arquivo .ino do projeto)
SensorStatus lerSensor(int trigPin, int echoPin) {
  // Disparo do pulso TRIG, medição do ECHO, cálculo da distância
  // e mapeamento para o nível de risco correspondente.
}
```

#### 3.3.7 Código Python

&nbsp; O lado PC do Módulo 2-C é implementado em Python, no script `src/módulo2-C/cli.py`, que estabelece comunicação serial com a ESP32 utilizando a biblioteca `pyserial`.  
Em linhas gerais, a CLI:

- abre a porta serial indicada (`--port /dev/ttyUSB0`, por exemplo) a 115200 bps;  
- envia comandos como `PING`, `GET_STATUS` ou `SET_THRESHOLDS`;  
- interpreta as linhas `STATUS` recebidas, apresentando ao operador uma visão formatada (distância + nível de risco por direção);  
- pode operar em modo de monitoramento contínuo, simulando o “dashboard lateral” de alertas de sensores.

&nbsp; O código Python completo pode ser encontrado em `backend/src/módulo2-C/cli.py`.

#### 3.3.8 CLI

&nbsp; A command line interface (CLI) foi desenvolvida para o controle do módulo sem interface visual completa, permitindo comandos diretos e precisos.

&nbsp; Link do [vídeo](https://drive.google.com/file/d/1Kb7BPjwu5Z2OkaLaeOM1HhUXL1-AjuFE/view?usp=drive_link)

**Para utilizar a CLI do módulo:**


&nbsp; O uso típico da CLI do Módulo 2-C segue os seguintes passos (a partir da raiz do projeto, com Python 3.12 e `pyserial` instalados — preferencialmente em um ambiente virtual):

- Garanta que a venv foi criada e está ativada;

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```


&nbsp; Instale o `pyserial`

```Bash
pip install pyserial
```

&nbsp; Na raiz do projeto execute: `cd src/modulo2-C`

- Garanta que a Esp-Wroom-32U está conectada e com o firmware embarcado;

Execute: 
```bash
python3 cli.py --port //Porta referente à Esp32
```

&nbsp; O retorno esperado se da por:

```bash
CLI - Módulo 2-C (fallback sensores)
=====================================

Conectado. Tentando PING inicial...

OK

STATUS ...

Escolha uma opção simples:
1) Ver status atual (GET_STATUS)
2) Monitorar status em tempo real
3) Ajustar limites de risco (SET_THRESHOLDS)
4) Mostrar comandos do módulo (HELP)
0) Sair

Opcao:
```

&nbsp; Em seguida, os principais comandos são:

| Comando (CLI)                                                                 | Descrição                                                                                   | Saída esperada                                                                                   |
|------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| `cli.py --port /dev/ttyUSB0 ping`                      | Testa a comunicação com a ESP32 (`PING`)                                                   | `OK` ou mensagem de erro de porta                                                                |
| `cli.py --port /dev/ttyUSB0 status`                    | Envia um `GET_STATUS` ao firmware e imprime as distâncias/níveis por direção               | Linha bruta `STATUS ...` e visão formatada (Frente/Trás/Esquerda/Direita + risco)               |
| `cli.py --port /dev/ttyUSB0 monitor --interval 1.0`    | Faz leituras contínuas, simulando o “dashboard lateral” de alertas de sensores             | Atualização periódica das quatro direções e respectivos níveis de risco                         |
| `cli.py --port /dev/ttyUSB0 set-thresholds 2.0 1.5 0.8`| Ajusta os limiares globais de risco (INFORMATIVO/ALERTA/CRITICO) usados pelo firmware      | Resposta `OK` em caso de sucesso ou mensagem `ERR ...` em caso de parâmetros inválidos          |

&nbsp; Para validação, recomenda-se utilizar o modo `monitor`, aproximando fisicamente a balsa/borda de cada sensor HC-SR04 e observando:

- a redução da distância medida (em metros) para a direção correspondente;  
- a mudança gradual do nível de risco (`SEGURO → INFORMATIVO → ALERTA → CRITICO`) de acordo com os limites configurados;  
- o eventual registro dos eventos na tabela `alertas_sensores` do banco de dados (quando a camada de persistência estiver integrada) e a exibição de mensagens do tipo “Cuidado, próximo à borda X” na interface do operador.

```bash
# Exemplos (ajustar a porta serial conforme o ambiente)
python3 src/módulo2-C/cli.py --port /dev/ttyUSB0 ping
python3 src/módulo2-C/cli.py --port /dev/ttyUSB0 monitor --interval 1.0
```

<p style={{textAlign: 'center'}}>Figura 10 - CLI 2-C</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/cli_2c.jpeg").default} style={{width: 800}} alt="CLI 2-C" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>


&nbsp; O Módulo 2-C, ao combinar sensores físicos de proximidade, lógica embarcada simples e uma CLI acessível, adiciona uma camada essencial de segurança à movimentação da balsa. Ele reduz a dependência exclusiva da visão por câmera, apoia o operador com alertas objetivos e fornece ao gestor dados concretos para análise de riscos e melhoria contínua do processo.

---

### 4.2. Proposta de Implementação

&nbsp; A proposta de evolução natural do protótipo é transformar as CLIs isoladas em um único utilitário de linha de comando, responsável por orquestrar todos os módulos de automação e centralizar os registros no banco de dados. Em vez de o operador precisar lembrar o script específico de cada parte (CLI Z, CLI XY, CLI câmera, CLI sensores), ele passará a interagir com um único comando raiz (por exemplo, `automacao-cli`) e subcomandos semânticos como `z`, `xy`, `camera` e `sensores`. Cada subcomando delega a lógica para o módulo correspondente (1-A, 1-B, 2-A, 2-B, 2-C), mantendo o encapsulamento técnico, mas oferecendo uma experiência de uso simples consistente, conforme o diagrama abaixo:

<p style={{textAlign: 'center'}}>Figura 11 - Diagrama de Integração das CLIs</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        {<img src={require("/img/diagrama_integração_clis.png").default} style={{width: 800}} alt="Diagrama de Integração das CLIs" />}
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

&nbsp; Do ponto de vista arquitetural, essa CLI unificada funcionará como uma “fachada” entre o operador e o ecossistema da balsa: de um lado, ela traduz os comandos de alto nível do usuário (`balsa-cli z descer 25.5`, `balsa-cli xy mover direita 80`, `balsa-cli camera iniciar`, `balsa-cli sensores monitorar`) para as interfaces já existentes (MQTT, Serial, HTTP); de outro, ela se conecta ao banco de dados PostgreSQL para criar entradas em `Registro_Operacoes` e associar eventuais alertas de risco à tabela `Alertas`. Dessa forma, cada ação executada nos módulos físicos passa a gerar automaticamente um log auditável, com `timestamp`, operador responsável e contexto de segurança, preparando o terreno para a Sprint 3, na qual essa CLI será integrada ao dashboard web do gestor como backend unificado da solução.

---

## 5. Referências


