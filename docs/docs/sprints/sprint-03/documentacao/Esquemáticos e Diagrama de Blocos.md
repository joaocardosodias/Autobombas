---
sidebar_label: "Esquemáticos e Diagrama de Blocos"
sidebar_position: 2
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Esquemáticos e Diagrama de Blocos dos Periféricos

---

## 1. Visão Geral

O diagrama de blocos e os esquemáticos elétricos tem por funcionalidade garantir a reprodução em escala dos sistemas físicos produzidos na POC (Prova de Conceito). Enquanto o diagrama de blocos evidencia como os periféricos, módulos e o backend se comunicam, os esquemáticos elétricos descrevem, para cada protótipo, as conexões físicas de alimentação, sinal e periféricos, assegurando a correta remontagem do hardware. 

As ferramentas utilizadas foram o Draw.io para o diagrama de blocos e, para o esquemático elétrico, o QElectroTech com componentes personalizados produzidos pela equipe.       

Todos os componentes foram disponibilizados pelo maker inteli, mas nenhuma PCB (Placa de Circuito Impresso) dedicada foi usinada. A montagem física fora realizada majoritariamente em protoboards.

---

## 2. Diagrama de Blocos de Periféricos

O diagrama de blocos de periféricos abaixo representa visualmente todos os componentes do sistema e suas interações, evidenciando o fluxo de energia, de dados e de controle entre os módulos. O sistema é composto por seis módulos: os Módulos 1-A e 1-B, que controlam a movimentação vertical (eixo Z) e simulam a leitura de corrente, respectivamente, os Módulos 2-A, 2-B e 2-C, responsáveis pela movimentação horizontal (eixo XY), captura de imagem via câmera e detecção de proximidade por sensores ultrassônicos, e o Módulo 3, responsável pela alimentação de todos os anteriores (conforme pode ser visto pelas setas do diagrama). Cada módulo de operação conta com um ESP32 dedicado, que publica os dados coletados em um broker, via MQTT (Módulos 1-A, 1-B, 2-A e 2-C) ou HTTP (Módulo 2-B), o qual os repassa ao backend, tanto para armazenamento no banco de dados, quanto para exibição na interface (CLI/Frontend).

<p style={{textAlign: 'center'}}>Figura 1 - Diagrama de Blocos de Periféricos</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/diagrama-perifericos-att-sprint3.drawio.png").default} style={{width: 800}} alt="Montagem Física do Circuito 1-B" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

Com isso, é possível compreender de forma clara como cada periférico contribui para o funcionamento do sistema: o módulo de alimentação garante o fornecimento de energia de forma centralizada, enquanto os módulos de operação coletam e transmitem dados de forma autônoma e paralela, e o backend consolida essas informações, tornando-as acessíveis para monitoramento e tomada de decisão. Essa arquitetura modular facilita tanto a identificação de falhas quanto a evolução incremental do sistema.

O software de desenvolvimento utilizado foi o draw.io e o arquivo editável se encontra em: ``docs/static/img/diagrama-perifericos-att-sprint3.drawio``


## 3. Esquemáticos Elétricos por Módulo

Os esquemáticos a seguir documentam, por módulo, as interligações elétricas (alimentação, terra, sinais e interfaces) e os componentes empregados, servindo como referência para montagem, depuração e replicação do sistema.

O software de desenvolvimento utilizado foi o QElectroTech e o arquivo editável se encontra em: ``docs/static/img/esquema_eletrico/EsquemaElétrico-AutoBombas.qet``

---

### 3.1 Módulo 1-A — Motor de Passo (Eixo Z)

No Módulo 1‑A, dedicado à movimentação vertical da motobomba (eixo Z), o esquemático elétrico apresenta o microcontrolador ESP-WROOM-32U interligado ao driver ULN2003AN, que por sua vez realiza o acionamento do motor de passo 28BYJ-48, evidenciando as trilhas de sinal, alimentação e controle necessárias para o funcionamento do conjunto.

<p style={{textAlign: 'center'}}>Figura 2 - Esquemático do Módulo 1-A</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={useBaseUrl('/img/esquema_eletrico/EsquemaEletrico_M1A.jpg')} style={{width: '100%', maxWidth: 800}} alt="Foto do Protótipo de movimentação em Z" />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

---

### 3.2 Módulo 1-B — Sensor de Corrente

O módulo 1-B é dedicado à aferição da corrente de operação da motobomba. Na POC desenvolvido pela equipe, essa corrente é simulada por meio de um potenciômetro que regula o fluxo de corrente da própria ESP-WROOM-32U para um resistor de 10 kΩ. Esse arranjo de circuito permite gerar um intervalo controlado de valores de corrente, que pode ser posteriormente normalizado em relação à corrente real de operação da motobomba, viabilizando a simulação e os testes de funcionamento do sistema de monitoramento. Em escala tal simulação deve ser substituida por um sensor de corrente dedicado.

<p style={{textAlign: 'center'}}>Figura 3 - Esquemático do Módulo 1-B</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={useBaseUrl('/img/esquema_eletrico/EsquemaEletrico_M1B.jpg')} style={{width: '100%', maxWidth: 800}} alt="Foto do Protótipo de movimentação em Z" />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

---

### 3.3 Módulo 2-A — Controle de Movimentação XY

O módulo 2-A é responsável pelo controle da movimentação cartesiana da balsa nos eixos X e Y. Ele é composto por uma ESP-WROOM-32U, um módulo ponte H L298N e um motor TT DC com redução, que em conjunto simulam o deslocamento da estrutura em um sistema análogo a uma esteira transportadora.

<p style={{textAlign: 'center'}}>Figura 4 - Esquemático do Módulo 2-A</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={useBaseUrl('/img/esquema_eletrico/EsquemaEletrico_M2A.jpg')} style={{width: '100%', maxWidth: 800}} alt="Foto do Protótipo de movimentação em Z" />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

---

### 3.4 Módulo 2-B — Câmera ESP32-CAM

A folha de esquema elétrico do módulo 2-B conta apenas com a ESP32-CAM e sua devida alimentação, visto que o core do módulo é o código embarcado, e não o circuito físico que, no caso, já é fornecido integralmente pela própria placa.

<p style={{textAlign: 'center'}}>Figura 5 - Esquemático do Módulo 2-B</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={useBaseUrl('/img/esquema_eletrico/EsquemaEletrico_M2B.jpg')} style={{width: '100%', maxWidth: 800}} alt="Foto do Protótipo de movimentação em Z" />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

---

### 3.5 Módulo 2-C — Sensores de Proximidade (HC-SR04)

O Módulo 2-C é responsável pela função de fallback de sensoriamento de proximidade. Foram utilizados quatro sensores ultrassônicos HC‑SR04, todos gerenciados por uma ESP‑WROOM‑32U dedicada, de forma a garantir a detecção de obstáculos e a redundância na medição de distância em torno da balsa.

<p style={{textAlign: 'center'}}>Figura 6 - Esquemático do Módulo 2-C</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={useBaseUrl('/img/esquema_eletrico/EsquemaEletrico_M2C.jpg')} style={{width: '100%', maxWidth: 800}} alt="Foto do Protótipo de movimentação em Z" />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

### 3.5 Módulo 3 — Alimentação

O Módulo 3 é referente à alimentação de todos os módulos anteriores. Foi adotado um conversor step-down LM2596 para garantir que qualquer tensão de entrada entre 4 V e 35 V seja regulada para uma saída estável e contínua de 5 V, capaz de suprir de forma confiável a operação de todos os módulos do sistema. Também foi adicionado um  de dois estados KCD11-101 para poder ligar ou desligar todo os sitema. 

<p style={{textAlign: 'center'}}>Figura 6 - Esquemático do Módulo 2-C</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={useBaseUrl('/img/esquema_eletrico/EsquemaEletrico_M3.jpg')} style={{width: '100%', maxWidth: 800}} alt="Foto do Protótipo de movimentação em Z" />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>