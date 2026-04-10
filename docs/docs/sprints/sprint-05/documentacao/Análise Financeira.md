---
sidebar_label: "Análise Financeira"
sidebar_position: 2
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Análise Financeira do Projeto

## 1. Visão Geral

Esta análise financeira projeta os custos necessários para a implementação real do sistema AutoBombas em escala industrial, considerando um horizonte de **12 meses** desde o início da implantação até a operação assistida.

Os componentes utilizados no protótipo, ESP32, motores de passo de baixo custo, sensores ultrassônicos genéricos e câmeras de desenvolvimento, serviram exclusivamente para **validação de conceito**. Seus custos individuais (na faixa de R$ 15 a R$ 80 por unidade) são praticamente irrelevantes quando comparados aos equivalentes industriais necessários para operação contínua em campo, expostos a umidade, vibração e variações de temperatura. Por esse motivo, a análise a seguir é feita diretamente com os **componentes industriais**, utilizando o protótipo apenas como referência funcional para o mapeamento de requisitos.


## 2. BOM (Bill of Materials)

A BOM está organizada por **subsistema funcional** do produto industrial, e não por módulo de protótipo. No protótipo, o sistema foi dividido em 5 módulos (1-A, 1-B, 2-A, 2-B, 2-C), cada um com uma ESP32 dedicada, por limitação de processamento e memória da plataforma de prototipagem. Em ambiente industrial, essa fragmentação não se aplica: um **CLP de médio porte centraliza toda a lógica de controle** que, no protótipo, exigiu múltiplos microcontroladores. A BOM a seguir reflete essa realidade, agrupando os componentes pela função que desempenham no produto final.

### 2.1 Consolidação: Protótipo para Indústria

A principal diferença estrutural entre o protótipo e o produto industrial é a **consolidação dos controladores**. As 4 ESP32 (módulos 1-A, 1-B, 2-A e 2-C) são substituídas por um único CLP industrial com capacidade de I/O suficiente para todas as funções. As câmeras (ESP32-CAM, módulo 2-B) permanecem como dispositivos distribuídos, por necessidade física de posicionamento nas quatro direções da balsa.

| Componente de Protótipo | Qtd (Prot.) | Equivalente Industrial | Qtd (Ind.) | Valor Unit. (R$) | Valor Total (R$) | Justificativa |
|---|---|---|---|---|---|---|
| ESP32 DevKit (Módulos 1-A, 1-B, 2-A, 2-C) | 4 | CLP Siemens S7-1500 (CPU 1515-2 PN) | 1 | 18.500,00 | 18.500,00 | CLP de alto desempenho com redundância de comunicação, maior capacidade de I/O e suporte a diagnóstico avançado |
| ESP32-CAM (Módulo 2-B) | 1 | Câmera IP industrial PTZ PoE IP67 4K (Axis P5655-E) | 4 | 4.800,00 | 19.200,00 | Câmeras PTZ com resolução 4K e zoom óptico 32× — uma por direção da balsa, com rastreamento automático |
| Motor de passo 28BYJ-48 + ULN2003 | 1 | Servo motor industrial AC + driver Sinamics V20 | 1 | 6.500,00 | 6.500,00 | Servo AC com encoder absoluto para posicionamento preciso do eixo Z sem referenciar após queda de energia |
| Potenciômetro 100kΩ (simulando ACS712) | 1 | Analisador de energia trifásico Janitza UMG 604 | 1 | 2.800,00 | 2.800,00 | Medição completa de qualidade de energia (corrente, tensão, fator de potência, harmônicos) da motobomba |
| Sensores HC-SR04 | 4 | Sensores ultrassônicos industriais IP69K + protocolo HART | 4 | 3.900,00 | 15.600,00 | Sensores com protocolo HART para diagnóstico remoto e proteção IP69K para lavagem de alta pressão |
| Motor DC TT + L298N | 1 | Motor thruster marítimo elétrico 48V + ESC industrial | 2 | 9.800,00 | 19.600,00 | Thrusters 48V com maior torque, vedação IP68 e ESC com proteção contra curto e inversão de polaridade |
| Roteador Wi-Fi doméstico | 1 | Roteador industrial 4G/5G dual-SIM redundante (Robustel R5020) | 1 | 8.200,00 | 8.200,00 | Conectividade redundante com failover automático entre operadoras 4G/5G |
| Notebook local | 1 | IPC industrial fanless certificado ATEX (Advantech MIC-770) | 1 | 22.000,00 | 22.000,00 | Computador industrial certificado para ambientes úmidos, com SSD industrial e fonte redundante |
| **Total** | | | | | **R$ 112.400,00** | |

### 2.2 Controle Central

O subsistema de controle central é responsável pelo processamento de toda a lógica de automação do sistema AutoBombas. Em ambiente industrial, um CLP de alto desempenho substitui os múltiplos microcontroladores utilizados no protótipo, garantindo robustez, escalabilidade de I/O e alimentação redundante.

| Componente | Função | Qtd | Valor Unit. (R$) | Valor Total (R$) |
|---|---|---|---|---|
| CLP Siemens S7-1500 (CPU 1515-2 PN) | Controlador central de alto desempenho — substitui as 4 ESP32 do protótipo | 1 | 18.500,00 | 18.500,00 |
| Módulo de expansão digital/analógico ET 200SP | Ampliação de I/O digital e analógico com diagnóstico por canal | 2 | 4.200,00 | 8.400,00 |
| Fonte de alimentação redundante 24V 20A (SITOP PSU8600) | Alimentação redundante com diagnóstico de falha e comutação automática | 1 | 4.800,00 | 4.800,00 |
| Painel elétrico IP66 em aço inox (800×600×300mm) | Proteção dos componentes eletrônicos com pintura marinha anticorrosiva | 1 | 6.500,00 | 6.500,00 |
| **Subtotal** | | | | **R$ 38.200,00** |

### 2.3 Atuação

O subsistema de atuação engloba os motores e controladores responsáveis pela movimentação física da balsa (eixo XY) e pelo posicionamento vertical da motobomba (eixo Z). Os componentes industriais oferecem maior torque, vedação adequada ao ambiente marítimo e proteções elétricas avançadas.

| Componente | Função | Qtd | Valor Unit. (R$) | Valor Total (R$) |
|---|---|---|---|---|
| Servo motor industrial AC + driver Sinamics V20 | Controle de profundidade da motobomba (eixo Z) com encoder absoluto — substitui 28BYJ-48 | 1 | 6.500,00 | 6.500,00 |
| Motor thruster marítimo elétrico 48V | Propulsão horizontal da balsa (eixo XY) com maior torque e vedação IP68 — substitui motor TT | 2 | 8.500,00 | 17.000,00 |
| Controlador ESC marítimo industrial 48V | Controle de velocidade e direção com proteção contra inversão e regeneração de energia | 2 | 2.200,00 | 4.400,00 |
| **Subtotal** | | | | **R$ 27.900,00** |

### 2.4 Sensoriamento

O subsistema de sensoriamento reúne os dispositivos responsáveis pela coleta de dados do ambiente e do estado operacional do equipamento. Inclui sensores de distância para geofencing, medição de energia da motobomba, posicionamento absoluto do eixo vertical e monitoramento de estabilidade da balsa.

| Componente | Função | Qtd | Valor Unit. (R$) | Valor Total (R$) |
|---|---|---|---|---|
| Analisador de energia trifásico Janitza UMG 604 | Medição completa de qualidade de energia da motobomba — substitui potenciômetro simulador | 1 | 2.800,00 | 2.800,00 |
| Sensor ultrassônico industrial IP69K com protocolo HART | Detecção de bordas e geofencing com diagnóstico remoto — substitui HC-SR04 | 4 | 3.900,00 | 15.600,00 |
| Encoder absoluto multivolta IP67 (Heidenhain ECN 413) | Medição de posição vertical absoluta da bomba sem necessidade de referenciar após queda de energia | 1 | 4.200,00 | 4.200,00 |
| Sensor de inclinação / IMU industrial (Bosch BMI088) | Monitoramento de estabilidade e inclinação da balsa em tempo real | 1 | 1.800,00 | 1.800,00 |
| **Subtotal** | | | | **R$ 24.400,00** |

### 2.5 Monitoramento Visual

O subsistema de monitoramento visual permite a visualização remota em tempo real do ambiente ao redor da balsa. As câmeras industriais com resolução 4K e zoom óptico cobrem as quatro direções da embarcação, conectadas por um switch PoE gerenciável com redundância de rede.

| Componente | Função | Qtd | Valor Unit. (R$) | Valor Total (R$) |
|---|---|---|---|---|
| Câmera IP PTZ industrial PoE IP67 4K (Axis P5655-E) | Visualização em tempo real com zoom óptico 32× — uma por direção da balsa | 4 | 4.800,00 | 19.200,00 |
| Switch PoE industrial gerenciável 16 portas (Moxa EDS-G512E) | Gerenciamento centralizado, PoE+ e redundância de rede (RSTP) | 1 | 7.500,00 | 7.500,00 |
| **Subtotal** | | | | **R$ 26.700,00** |

### 2.6 Comunicação e Rede

O subsistema de comunicação e rede garante a conectividade entre a balsa e a central de controle remoto. Utiliza um roteador industrial com failover entre operadoras 4G/5G, além de cabeamento blindado e conectores vedados adequados ao ambiente marítimo.

| Componente | Função | Qtd | Valor Unit. (R$) | Valor Total (R$) |
|---|---|---|---|---|
| Roteador industrial 4G/5G dual-SIM (Robustel R5020) | Conectividade redundante com failover automático entre operadoras para áreas remotas | 1 | 8.200,00 | 8.200,00 |
| Cabo Ethernet CAT6A blindado outdoor armado | Conexão blindada com proteção mecânica contra roedores e abrasão | 100 m | 28,00/m | 2.800,00 |
| Conectores M12 industriais 8 pinos e acessórios | Conexões vedadas IP67 para equipamentos de rede de alta velocidade | 12 | 120,00 | 1.440,00 |
| **Subtotal** | | | | **R$ 12.440,00** |

### 2.7 Infraestrutura Geral

O subsistema de infraestrutura geral abrange os componentes de suporte necessários ao funcionamento contínuo de toda a plataforma. Inclui o computador industrial que executa o backend e o frontend, proteções físicas para sensores e atuadores, cabeamento de potência naval e proteção contra quedas de energia.

| Componente | Função | Qtd | Valor Unit. (R$) | Valor Total (R$) |
|---|---|---|---|---|
| IPC industrial fanless certificado ATEX (Advantech MIC-770) | Execução do backend Flask e frontend React com certificação para ambiente úmido | 1 | 22.000,00 | 22.000,00 |
| Invólucros e conectores IP68 (kit industrial completo) | Proteção de sensores e atuadores submersos ou expostos a alta umidade | 1 | 6.500,00 | 6.500,00 |
| Cabeamento de potência naval + terminais industriais | Alimentação de motores, bomba e painel com cabo náutico homologado (50 m) | 50 m | 75,00/m | 3.750,00 |
| Nobreak industrial 48V redundante (Schneider Galaxy VS) | Proteção contra quedas de energia com autonomia de 2h e monitoramento SNMP | 1 | 9.500,00 | 9.500,00 |
| **Subtotal** | | | | **R$ 41.750,00** |

### 2.8 Resumo da BOM

A tabela a seguir consolida os custos de todos os subsistemas da BOM industrial, permitindo uma visão geral do investimento necessário em componentes físicos para a montagem de uma unidade completa do sistema AutoBombas.

| Subsistema | Custo Total (R$) |
|---|---|
| Controle Central | R$ 38.200,00 |
| Atuação | R$ 27.900,00 |
| Sensoriamento | R$ 24.400,00 |
| Monitoramento Visual | R$ 26.700,00 |
| Comunicação e Rede | R$ 12.440,00 |
| Infraestrutura Geral | R$ 41.750,00 |
| **Total da BOM (componentes industriais)** | **R$ 171.390,00** |

## 3. Custos de Implementação

Além dos componentes físicos detalhados na BOM, a implementação em escala industrial envolve custos recorrentes de software e infraestrutura em nuvem, mão de obra especializada para desenvolvimento e instalação, e investimento em treinamento dos operadores. Todos os valores são projetados para um período de **12 meses**, correspondente ao ciclo completo de desenvolvimento, instalação, comissionamento e operação assistida.

### 3.1 Software e Serviços

Esta subseção detalha os custos recorrentes com plataformas de software e serviços em nuvem necessários para a operação do sistema, incluindo banco de dados, servidor de aplicação, broker de mensagens, domínio e licenciamento de supervisório industrial.

| Item | Descrição | Valor Mensal (R$) | Valor 12 meses (R$) |
|---|---|---|---|
| Banco de dados PostgreSQL gerenciado | Supabase Pro com réplica de leitura e backups diários — armazenamento de leituras, movimentações e logs | 380,00 | 4.560,00 |
| Servidor cloud (VPS) | VPS 8 vCPU / 32 GB RAM com alta disponibilidade para backend Flask e dashboard React | 980,00 | 11.760,00 |
| Broker MQTT com alta disponibilidade | HiveMQ Enterprise — comunicação em tempo real com clustering e persistência de mensagens | 620,00 | 7.440,00 |
| Domínio, certificado SSL e CDN | Domínio do dashboard, HTTPS e CDN global para acesso de baixa latência | 180,00 | 2.160,00 |
| Licença SCADA/supervisório industrial | WinCC Unified para supervisão avançada integrada ao CLP Siemens | 1.200,00 | 14.400,00 |
| **Subtotal** | | **3.360,00** | **R$ 40.320,00** |

### 3.2 Mão de Obra

A equipe de implementação é composta por profissionais especializados com atuação em fases distintas do projeto. A alocação foi dimensionada conforme a complexidade de cada etapa, desde o desenvolvimento de software até a instalação física na balsa.

| Perfil | Quantidade | Valor Mensal (R$) | Meses | Valor Total (R$) |
|---|---|---|---|---|
| Engenheiro de Software Sênior | 1 | 18.000,00 | 12 | 216.000,00 |
| Engenheiro de Automação Pleno | 1 | 11.000,00 | 6 | 66.000,00 |
| Engenheiro Eletricista Industrial | 1 | 14.000,00 | 4 | 56.000,00 |
| Técnico de Campo Sênior | 1 | 8.500,00 | 4 | 34.000,00 |
| **Subtotal** | | | | **R$ 372.000,00** |

O **engenheiro de software sênior** atua durante todo o ciclo (12 meses), sendo responsável pela arquitetura do sistema, adaptação do backend/frontend, integração com o CLP via OPC-UA/MQTT, testes de carga e manutenção. O **engenheiro de automação pleno** atua nos 6 primeiros meses, cobrindo a especificação elétrica, programação do CLP S7-1500, integração PROFINET e comissionamento. O **engenheiro eletricista industrial** atua nos 4 meses intermediários, responsável pelo projeto e homologação do painel elétrico. O **técnico de campo sênior** atua nos 4 meses finais, realizando a instalação física, cabeamento náutico e testes operacionais na balsa.

### 3.3 Treinamento e Implantação

Esta subseção contempla os custos pontuais associados à capacitação dos operadores e à instalação física do sistema na balsa, incluindo montagem, comissionamento e elaboração da documentação técnica obrigatória.

| Item | Descrição | Valor (R$) |
|---|---|---|
| Treinamento de operadores | Capacitação prática (80h) no uso do dashboard, SCADA, interpretação de telemetria e procedimentos de emergência | 18.000,00 |
| Instalação mecânica e elétrica em campo | Montagem do painel, fixação de sensores, cabeamento náutico certificado e conexão dos thrusters na balsa | 38.000,00 |
| Comissionamento e testes | Validação funcional completa do sistema integrado em ambiente real, com ajuste de parâmetros e testes de falha | 24.000,00 |
| Documentação técnica | Manuais de operação, manutenção preventiva, diagramas elétricos, FMEA e documentação de segurança (NR-10/NR-12) | 12.000,00 |
| **Subtotal** | | **R$ 92.000,00** |

### 3.4 Resumo de Custos

A tabela a seguir consolida todas as categorias de custo do projeto, somando componentes físicos, software, mão de obra e implantação, para apresentar o investimento total necessário para a primeira unidade do sistema AutoBombas.

| Categoria | Valor (R$) |
|---|---|
| BOM (componentes industriais) | R$ 171.390,00 |
| Software e Serviços (12 meses) | R$ 40.320,00 |
| Mão de Obra (12 meses) | R$ 372.000,00 |
| Treinamento e Implantação | R$ 92.000,00 |
| **Custo Total de Implementação** | **R$ 675.710,00** |

## 4. Análise de Viabilidade

Esta seção avalia a viabilidade econômica do projeto AutoBombas, comparando os custos operacionais do cenário manual atual com os do sistema automatizado. A partir dessa comparação, são calculados o retorno sobre o investimento (ROI), os ganhos indiretos e as perspectivas de escala para múltiplas unidades.

### 4.1 Custo Operacional Atual (cenário manual)

No cenário atual, a operação de dragagem com reposicionamento manual da bomba submersível demanda uma equipe de **2 a 3 operadores em campo** por balsa, com custo médio de R$ 4.000,00/mês por operador (incluindo encargos). Considerando a operação contínua de uma balsa durante 12 meses:

| Item | Valor Mensal (R$) | Valor Anual (R$) |
|---|---|---|
| Operadores em campo (3 pessoas) | 12.000,00 | 144.000,00 |
| Manutenção corretiva frequente (desgaste por operação inadequada) | 3.500,00 | 42.000,00 |
| Combustível para motores auxiliares a diesel | 2.000,00 | 24.000,00 |
| Paradas não planejadas (perda de produtividade estimada) | 4.000,00 | 48.000,00 |
| **Total operacional anual (manual)** | **21.500,00** | **R$ 258.000,00** |

### 4.2 Custo Operacional com o Sistema AutoBombas

Com o sistema automatizado, a operação passa a exigir **1 operador remoto** monitorando o dashboard, com intervenções pontuais de manutenção preventiva:

| Item | Valor Mensal (R$) | Valor Anual (R$) |
|---|---|---|
| Operador remoto (1 pessoa) | 5.000,00 | 60.000,00 |
| Manutenção preventiva programada | 1.500,00 | 18.000,00 |
| Software e serviços em nuvem | 3.360,00 | 40.320,00 |
| Energia elétrica adicional (thrusters e CLP) | 800,00 | 9.600,00 |
| **Total operacional anual (automatizado)** | **10.660,00** | **R$ 127.920,00** |

### 4.3 Retorno sobre o Investimento (ROI)

A **economia operacional anual** estimada com a adoção do sistema é de:

> **R$ 258.000,00 − R$ 127.920,00 = R$ 130.080,00/ano**

Considerando o investimento total de implementação de **R$ 675.710,00**, o payback estimado é de:

> **R$ 675.710,00 ÷ R$ 130.080,00 ≈ 5,2 anos (≈ 62 meses)**

Ou seja, o investimento se paga em aproximadamente **5 anos de operação**, passando a gerar economia líquida a partir do sexto ano.

### 4.4 Ganhos Indiretos

Além da redução direta de custos operacionais, a implementação do sistema traz benefícios que não são facilmente quantificáveis, mas que impactam significativamente a viabilidade do projeto:

- **Redução de riscos operacionais:** a eliminação da operação manual em campo reduz a exposição dos trabalhadores a condições insalubres e riscos de acidentes próximos a corpos d'água e equipamentos pesados.
- **Eliminação do risco de operação a seco:** o controle automático de profundidade (eixo Z) baseado na leitura de corrente da motobomba previne a operação sem carga, que é a principal causa de danos ao equipamento.
- **Redução de paradas não planejadas:** com monitoramento contínuo de telemetria e geofencing, situações anômalas são detectadas antes de causarem falhas.
- **Aumento de eficiência produtiva:** o reposicionamento automatizado permite ciclos de dragagem mais curtos e consistentes, aumentando o volume de material processado por turno.
- **Sustentabilidade:** a substituição de motores auxiliares a diesel por thrusters elétricos reduz emissões e ruído no ambiente de operação.

### 4.5 Considerações sobre Escala

O custo de implementação da **primeira unidade** (R$ 675.710,00) inclui todo o desenvolvimento de software, que é um custo não recorrente. Para unidades adicionais, o custo marginal se limita à BOM, instalação e treinamento:

| Item | Custo por unidade adicional (R$) |
|---|---|
| BOM (componentes industriais) | 171.390,00 |
| Instalação em campo | 38.000,00 |
| Comissionamento | 24.000,00 |
| Treinamento de operador | 8.000,00 |
| **Total por balsa adicional** | **R$ 241.390,00** |

Com isso, o payback de cada balsa adicional cai para aproximadamente **20 meses**, tornando a expansão para múltiplas unidades financeiramente atrativa a partir da segunda balsa equipada.