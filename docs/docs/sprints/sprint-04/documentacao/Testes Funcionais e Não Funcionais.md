---
sidebar_label: "Testes Funcionais e Não Funcionais"
sidebar_position: 1
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Documentação dos testes funcionais e não funcionais

---

## 1. Visão Geral

Este documento apresenta a documentação dos testes funcionais e não funcionais realizados para demonstrar que os requisitos do sistema estão sendo atendidos. Os registros completos dos testes estão disponíveis na planilha a seguir:

[Planilha de Registros de Testes](https://docs.google.com/spreadsheets/d/1aDvr1urazaIDQAINt3JYcrPZst3YYCE91nwBn6bdL5Q/edit?gid=1692673611#gid=1692673611)

### Estrutura dos casos de teste

Cada caso de teste é documentado com as seguintes informações:

| Campo | Descrição |
|---|---|
| **ID** | Número que identifica o caso de teste |
| **Caso de Teste** | Breve descrição do cenário de teste |
| **Tipo de Teste** | Funcional ou Não Funcional |
| **Passo-a-passo** *(opcional)* | Sequência detalhada de tarefas para executar o teste, podendo incluir dados de teste |
| **Resultado Esperado** | Descrição do resultado que se pretende obter |
| **Resultado Obtido** | Descrição do resultado após executar o teste; erros e melhorias devem ser reportados com detalhe |
| **Estado** | Passou / Falhou / Pendente / Sem efeito |
| **Última Atualização** | Data de quando o teste foi executado |
| **Comentários** *(opcional)* | Informações adicionais sobre o teste |

### Legenda de estados

| Estado | Descrição |
|---|---|
| ✅ Passou | O resultado obtido corresponde ao resultado esperado |
| ❌ Falhou | O resultado obtido não corresponde ao resultado esperado |
| ⏳ Pendente | O teste está bloqueado e não pôde ser executado |
| — Sem efeito | O teste não era aplicável ao cenário |

---

## 2. Testes Funcionais

Os testes funcionais têm como objetivo verificar se as funcionalidades do sistema se comportam conforme os requisitos especificados, garantindo que cada funcionalidade entregue o resultado esperado para os usuários finais.

Diferentemente dos testes não funcionais, que avaliam como o sistema se comporta, os testes funcionais verificam o que o sistema faz, validando entradas, saídas e fluxos de interação da aplicação.

---

### 2.1 Objetivo dos Testes

Os testes funcionais foram definidos com base nos requisitos funcionais (RFs) do sistema e possuem os seguintes objetivos:

* Verificar o funcionamento correto dos controles de movimentação da balsa (eixos XY e Z)
* Validar o monitoramento de corrente elétrica em tempo real e sua exibição no dashboard
* Verificar a visualização e os alertas dos sensores de proximidade por direção
* Validar os intertravamentos de segurança (bloqueio e parada de emergência automática)
* Garantir a visualização adequada do histórico de eventos no dashboard

---

### 2.2 Escopo dos Testes

Os testes funcionais abrangem os seguintes componentes do sistema:

* Interface do dashboard utilizada pelo operador e pelo gestor
* Controles de movimentação da balsa (eixos X, Y e Z)
* Componente de monitoramento de corrente elétrica (Amperímetro)
* Painel de sensores de proximidade e lógica de intertravamento
* Sistema de visualização do histórico e logs de eventos

Os testes de autenticação (login, cadastro e recuperação de senha) não foram incluídos neste escopo, pois não representam funcionalidades críticas para o objetivo principal do sistema. A priorização foi direcionada aos fluxos diretamente relacionados à operação, monitoramento e segurança da bomba, considerando que o processo de autenticação não impacta diretamente esses cenários.

Os testes são realizados, prioritariamente, em ambiente de simulação e protótipo, podendo ser posteriormente estendidos para validação em campo real.

---

### 2.3 Estratégia de Teste

A estratégia de testes foi definida a partir do mapeamento direto entre os requisitos funcionais e os fluxos de interação do sistema:

* Testes de controle de movimentação da balsa nos eixos XY e Z
* Testes de monitoramento de corrente elétrica em tempo real
* Testes de visualização e status dos sensores de proximidade
* Testes de intertravamento de segurança (bloqueio e parada de emergência)
* Testes de visualização e acesso ao histórico de eventos

Os resultados dos testes serão posteriormente registrados na planilha de acompanhamento indicada neste documento.

---

### 2.4 Casos de Teste

| ID | Caso de Teste | Persona | Passo-a-passo | Resultado Esperado | Resultado Obtido | Estado | Última Atualização | Comentários |
|---|---|---|---|---|---|---|---|---|
| TF-01 | Abrir modal de Movimentação XY | Operador | No Dashboard, no cartão da Bomba Submersível, clicar no botão "Movimentação XY". | O modal "Controlar Direção" é exibido na tela, contendo as setas direcionais e o botão "Iniciar". | *(a preencher)* | *(a preencher)* | *(a preencher)* | *(a preencher)* |
| TF-02 | Enviar comando de Movimentação XY | Operador | Com o modal XY aberto, selecionar uma direção (ex: seta para cima) e clicar em "Iniciar". | O sistema envia o comando para a balsa e exibe um feedback visual de sucesso na interface. | *(a preencher)* | *(a preencher)* | *(a preencher)* | *(a preencher)* |
| TF-03 | Abrir modal de Motor Z | Operador | No Dashboard, no cartão da Bomba Submersível, clicar no botão "Motor Z". | O modal "Controlar Motor Z" é exibido com os botões "Subir"/"Descer" e o campo de distância (cm). | *(a preencher)* | *(a preencher)* | *(a preencher)* | *(a preencher)* |
| TF-04 | Enviar comando de Movimentação Z | Operador | Com o modal Z aberto, selecionar "Subir", digitar "10" no campo de centímetros e confirmar. | O sistema envia o comando de elevação, fecha o modal e mostra uma mensagem de sucesso. | *(a preencher)* | *(a preencher)* | *(a preencher)* | *(a preencher)* |
| TF-05 | Acessar o histórico da bomba | Gestor | No Dashboard principal, clicar na opção "Ver histórico". | O sistema redireciona o utilizador para a tela (ou abre um modal) contendo a tabela de logs e eventos da bomba. | *(a preencher)* | *(a preencher)* | *(a preencher)* | *(a preencher)* |
| TF-06 | Visualizar leitura de corrente em tempo real | Operador | No Dashboard, observar o componente de Amperímetro após o carregamento. Verificar se o valor de corrente (em A) e o percentual são exibidos na tela. | O componente exibe a leitura de corrente atual da bomba em Ampères e em formato percentual, atualizando automaticamente a cada ciclo de leitura. | *(a preencher)* | *(a preencher)* | *(a preencher)* | *(a preencher)* |
| TF-07 | Bloqueio de movimentação XY com bomba fora da origem | Operador | (1) Enviar um comando Z para descer a bomba alguns centímetros. (2) Sem recolher a bomba, tentar acionar um comando de movimentação XY (ex: seta para frente). | O sistema bloqueia o comando XY e exibe uma mensagem informando que a balsa não pode se mover enquanto a bomba não estiver na posição de origem (Z = 0 cm). | *(a preencher)* | *(a preencher)* | *(a preencher)* | *(a preencher)* |
| TF-08 | Visualizar status dos sensores de proximidade no painel | Operador | No Dashboard, clicar no ícone ou botão de "Sensores" para abrir o painel de sensores. | O painel exibe o status de cada sensor de proximidade (frente, trás, esquerda, direita) com a respectiva classificação de risco (SEGURO, INFORMATIVO, ALERTA ou CRÍTICO). | *(a preencher)* | *(a preencher)* | *(a preencher)* | *(a preencher)* |
| TF-09 | Parada de emergência automática por sensor crítico | Operador | (1) Iniciar uma movimentação XY da balsa. (2) Aproximar a balsa de um obstáculo até que o sensor detecte distância ≤ 0,5 m (nível CRÍTICO). | O sistema interrompe automaticamente a movimentação da balsa e exibe um alerta de proximidade crítica, sem que o operador precise acionar o comando de parada manualmente. | *(a preencher)* | *(a preencher)* | *(a preencher)* | *(a preencher)* |
| TF-10 | Gestor consulta histórico com dados temporais | Gestor | Executar algumas ações no sistema (movimentações e leituras de corrente). Em seguida, acessar o histórico de eventos da bomba pelo Dashboard. | O histórico exibe os eventos registrados com data e hora, identificação do tipo de evento e informações suficientes para entender o que ocorreu em cada momento. | *(a preencher)* | *(a preencher)* | *(a preencher)* | *(a preencher)* |
---

### 2.5 Considerações

Os testes definidos nesta seção estabelecem uma base estruturada para validação dos requisitos funcionais do sistema. A execução desses testes permitirá identificar possíveis divergências entre o comportamento implementado e o comportamento esperado, contribuindo para o aprimoramento da qualidade e da confiabilidade da solução proposta.

Os resultados obtidos serão utilizados como insumo para correção de defeitos e ajustes na interface do sistema, garantindo maior aderência às necessidades do parceiro e às condições reais de operação.


---

## 3. Testes Não Funcionais

&nbsp; Os testes não funcionais têm como objetivo validar atributos de qualidade do sistema, como confiabilidade, desempenho, segurança, robustez e usabilidade, garantindo que a solução seja adequada para operação em ambiente real de campo.

&nbsp; Diferentemente dos testes funcionais, que verificam o que o sistema faz, os testes não funcionais avaliam como o sistema se comporta sob diferentes condições de uso, incluindo cenários de falha, operação contínua e interação com o usuário.

---

### 3.1 Objetivo dos Testes

&nbsp; Os testes não funcionais foram definidos com base nos requisitos não funcionais (RNFs) do sistema e possuem os seguintes objetivos:

* Validar a confiabilidade do sistema embarcado durante operação contínua
* Verificar a robustez do sistema em cenários prolongados sem intervenção manual
* Avaliar o desempenho da atualização de dados entre a balsa e o dashboard
* Garantir que o sistema priorize condições seguras em situações críticas
* Verificar a integridade dos dados frente a ruídos e inconsistências de sinais
* Validar o registro adequado de eventos relevantes para análise posterior
* Avaliar a clareza e interpretação das informações exibidas ao operador
* Verificar a simplicidade de uso do dashboard nas ações principais
* Garantir a possibilidade de configuração de parâmetros operacionais sem alteração de código

---

### 3.2 Escopo dos Testes

&nbsp; Os testes não funcionais abrangem os seguintes componentes do sistema:

* Módulo embarcado responsável pelo controle da bomba
* Comunicação entre a balsa e o dashboard
* Interface do dashboard utilizada pelo operador
* Sistema de registro de eventos (logs)

&nbsp; Os testes são realizados, prioritariamente, em ambiente de simulação e protótipo, podendo ser posteriormente estendidos para validação em campo real.

---

### 3.3 Estratégia de Teste

&nbsp; A estratégia de testes foi definida a partir do mapeamento direto entre os requisitos não funcionais e os tipos de validação necessários:

* Testes de execução contínua para avaliar confiabilidade e robustez (RNF01, RNF03)
* Testes de latência e atualização de dados (RNF02)
* Testes de segurança operacional e validação de regras (RNF04)
* Testes de integridade e tratamento de sinais (RNF05)
* Testes de registro e rastreabilidade de eventos (RNF06)
* Testes de usabilidade e clareza da interface (RNF07, RNF08)
* Testes de configurabilidade de parâmetros (RNF09)

&nbsp; Os valores quantitativos adotados nos testes (como tempo de atualização e duração de execução contínua) foram definidos com base em critérios de validação de protótipo, considerando limitações do ambiente de teste e a necessidade de simular condições reais de operação.

&nbsp; O tempo máximo de 2 segundos para atualização foi considerado adequado para não comprometer a tomada de decisão do operador. O período de operação contínua adotado nos testes é definido conforme as condições disponíveis no momento da execução.

&nbsp; Esses valores servem como referência inicial e podem ser ajustados em fases futuras de validação em campo.

&nbsp; Os resultados dos testes serão posteriormente registrados na planilha de acompanhamento indicada neste documento.

---

### 3.4 Casos de Teste

| ID     | Caso de Teste                                            | Persona           | RNF Relacionado | Passo-a-passo                                                                                                                                                          | Resultado Esperado                                                                                                                                              | Resultado Obtido | Estado          | Última Atualização | Comentários     |
| ------ | -------------------------------------------------------- | ----------------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | --------------- | ------------------ | --------------- |
| TNF-01 | Execução contínua do sistema embarcado por período definido | Operador e Gestor | RNF01, RNF03    | Manter o sistema em operação contínua por 30 minutos, acompanhando pelo dashboard a atualização dos dados de corrente, status dos sensores e estado da balsa, verificando a responsividade da interface durante todo o período. | O sistema permanece estável durante os 30 minutos de execução, sem travamentos, sem necessidade de reinicialização manual e sem interrupções na atualização dos dados exibidos no dashboard. | *(a preencher)*  | *(a preencher)* | *(a preencher)*    | *(a preencher)* |
| TNF-02 | Tempo de atualização de dados no dashboard               | Operador          | RNF02           | Alterar o estado da bomba (ligar/desligar) pelo dashboard e medir o tempo até a atualização visual da informação                                                       | O dashboard reflete a mudança em até 3 segundos após a ação do operador                                                                                         | *(a preencher)*  | *(a preencher)* | *(a preencher)*    | *(a preencher)* |
| TNF-03 | Bloqueio e parada em condição insegura                   | Operador          | RNF04           | (1) Tentar movimentar a balsa em uma condição que deveria ser bloqueada; (2) iniciar um movimento permitido e observar o comportamento ao ocorrer uma situação crítica | (1) O sistema impede a ação e informa claramente o motivo; (2) o sistema interrompe automaticamente o movimento e informa o ocorrido ao operador                | *(a preencher)*  | *(a preencher)* | *(a preencher)*    | *(a preencher)* |
| TNF-04 | Registro de eventos críticos no sistema                  | Gestor            | RNF06           | Executar ações relevantes no sistema (movimentação, bloqueios, ativação de modo automático) e posteriormente consultar os registros disponíveis                        | Os eventos realizados podem ser consultados posteriormente, com identificação temporal e informações suficientes para entendimento do ocorrido                  | *(a preencher)*  | *(a preencher)* | *(a preencher)*    | *(a preencher)* |
| TNF-05 | Clareza do estado de segurança no dashboard              | Operador          | RNF07           | Observar o dashboard em diferentes estados do sistema (liberado e bloqueado) durante a operação                                                                        | O dashboard apresenta de forma clara e inequívoca se a operação está permitida ou bloqueada, evitando interpretações ambíguas                                   | *(a preencher)*  | *(a preencher)* | *(a preencher)*    | *(a preencher)* |
| TNF-06 | Configuração de parâmetros operacionais                  | Gestor            | RNF09           | Alterar parâmetros operacionais (ex: limite de corrente) pela interface e verificar o comportamento do sistema após a alteração                                        | O sistema aplica os novos parâmetros corretamente e seu comportamento reflete a configuração realizada, sem necessidade de alteração de código                  | *(a preencher)*  | *(a preencher)* | *(a preencher)*    | *(a preencher)* |


---

### 3.5 Considerações

&nbsp; Os testes definidos nesta seção estabelecem uma base estruturada para validação dos requisitos não funcionais do sistema. A execução desses testes permitirá identificar possíveis limitações relacionadas à operação em ambiente real, contribuindo para o aprimoramento da confiabilidade, segurança e usabilidade da solução proposta.

&nbsp; Os resultados obtidos serão utilizados como insumo para ajustes na arquitetura, na lógica de controle e na interface do sistema, garantindo maior aderência às necessidades do parceiro e às condições reais de operação.


---

## 4. Problemas Reportados

&nbsp; Lista consolidada de erros e melhorias identificados durante os testes.

| ID do Problema | Caso de Teste Relacionado | Descrição | Severidade | Status |
|---|---|---|---|---|
| *(a preencher)* | *(a preencher)* | *(a preencher)* | *(a preencher)* | *(a preencher)* |

---

## 5. Referências

- [Como documentar testes funcionais? — Mosaico](https://guias.mosaico.gov.pt/guias-praticos/como-documentar-testes-funcionais)
- [Requisitos funcionais e não funcionais — GeeksforGeeks](https://www.geeksforgeeks.org/software-engineering/functional-vs-non-functional-requirements/)
