---
sidebar_label: "ReadMe"
sidebar_position: 1
---

# Sprint 2 – Protótipo de Automação e Documentação

&nbsp;Este documento funciona como um índice da Sprint 2, indicando onde estão os principais artefatos (protótipo de automação, user flow, wireframes e modelagem de BD) e como cada membro da equipe deve utilizá-los e complementá-los.

## Índice

- [1. Visão geral da Sprint 2](#1-visao-geral-da-sprint-2)
- [2. Artefatos da Sprint 2](#2-artefatos-da-sprint-2)
- [3. Estrutura por módulo (onde cada responsável deve editar)](#3-estrutura-por-modulo-onde-cada-responsavel-deve-editar)
- [4. Artefatos gerais](#4-artefatos-gerais)
- [5. Como executar as CLIs por módulo](#5-como-executar-as-clis-por-modulo)

## 1. Visão geral da Sprint 2

Esta página resume os artefatos de documentação da Sprint 2 e indica, de forma organizada, onde cada membro da equipe deve registrar as informações de seu módulo.

- **Protótipo do Sistema de Automação (por módulo)**: descrição de hardware, CLI, user stories e instruções de execução de cada módulo (`1-A`, `1-B`, `2-A`, `2-B`, `2-C`).
- **Mapeamento do Fluxo de Utilização da Solução (user flow + wireframes)**: fluxos de uso da solução, relacionando usuário, módulos, banco de dados e telas principais.

## 2. Artefatos da Sprint 2

- **Protótipo do Sistema de Automação**  
  Descreve o sistema microcontrolado, a CLI e a modelagem de banco de dados, estruturados por módulo.  
  Arquivo: `Protótipo do Sistema de Automação.md`

- **Mapeamento do Fluxo de Utilização da Solução**  
  Define os user flows, relaciona-os às user stories e indica onde entram os principais wireframes.  
  Arquivo: `Mapeamento do Fluxo de Utilização da Solução.md`

## 3. Estrutura por módulo (onde cada responsável deve editar)

Cada módulo da solução é documentado em seções específicas dentro de `Protótipo do Sistema de Automação.md`:

- **Módulo 1-A – Movimentação Z (Motor de Passo)**  
  - Protótipo de automação + hardware (circuito, microcontrolador, driver/motor de passo).  
  - CLI específica (ex.: `movZ descer(X)`), comandos e retornos.  
  - User stories do Operador e do Gestor focadas em movimentação Z.  
  - Instruções de execução da parte do projeto relacionada ao Módulo 1-A.

- **Módulo 1-B – Leitura de corrente de operação**  
  - Descrição do sensor simulado (potenciômetro + divisor de tensão) e conversão para corrente.  
  - Lógica de decisão (DRAGANDO x BUSCANDO) e mapeamento para o banco de dados.  
  - User stories relacionadas à interpretação de corrente pelo operador e decisões de dragagem.  
  - Instruções de execução para rodar a leitura de corrente via CLI.

- **Módulo 2-A – Movimentação XY**  
  - Descrição do dashboard/controles (botões ou teclas, slider de potência, botão de ancoragem).  
  - Definição dos comandos CLI ou inputs de interface que disparam a movimentação XY.  
  - User stories de posicionamento da balsa na grade.  
  - Instruções de execução específicas do Módulo 2-A.

- **Módulo 2-B – Visualização da câmera**  
  - Descrição do protótipo de captura/streaming de vídeo.  
  - Elementos principais da interface de visualização (janela de vídeo, controles).  
  - User stories de inspeção visual pelo operador e acompanhamento pelo gestor.  
  - Instruções de execução da visualização da câmera.

- **Módulo 2-C – Fallback Sensores**  
  - Descrição dos sensores de proximidade e da lógica de alerta.  
  - Integração visual com a interface (pop-ups, laterais da visualização, etc.).  
  - User stories de segurança/alertas para operador e gestor.  
  - Instruções de execução da leitura dos sensores/fallback.

## 4. Artefatos gerais

Os artefatos gerais da Sprint 2 também estão organizados nos documentos desta pasta:

- **Modelagem de Banco de Dados (Geral)**  
  Seção centralizada em `Protótipo do Sistema de Automação.md`, com tabelas sugeridas para:  
  - leituras de corrente (Módulo 1-B);  
  - movimentações XY (Módulo 2-A);  
  - alertas de sensores (Módulo 2-C);  
  - outras tabelas de apoio (operadores, sessões, etc.).

- **User Flow da solução**  
  Seções em `Mapeamento do Fluxo de Utilização da Solução.md`, detalhando cenários que envolvem os módulos (dragagem, movimentação XY, visualização de câmera, alertas de sensores).

- **Wireframes das principais telas**  
  Espaços reservados em `Mapeamento do Fluxo de Utilização da Solução.md` para inserir/relacionar imagens de wireframes (dashboard, tela de leitura de corrente, tela da câmera com sensores, etc.).

## 5. Como executar as CLIs por módulo

&nbsp;Os comandos abaixo servem como **modelo de execução das CLIs** de cada módulo. Cada responsável deve **ajustar o comando real** conforme a implementação no diretório `src` e garantir que o passo a passo completo também esteja descrito em `src/README.md`.

### 5.1 Módulo 1-A – Movimentação Z (Motor de Passo)

- **Objetivo**: controlar a movimentação da motobomba no eixo Z (subir/descer).  
- **Exemplo de execução da CLI** (ajustar conforme o nome real do módulo/comando):

```bash
# Entrar na pasta do módulo no backend
cd backend/src/módulo1-A

# Iniciar a CLI (requer broker MQTT rodando)
python cli.py

# Exemplos de comandos dentro da CLI:
# >> movZ descer(25.5)   → Solta 25,5 cm de corda
# >> movZ subir(10)      → Puxa 10 cm de corda
# >> movZ status         → Ver posição atual
# >> movZ reset          → Recolher toda a corda
# >> sair                → Encerrar
```

### 5.2 Módulo 1-B – Leitura de corrente de operação

- **Objetivo**: ler a corrente da motobomba (A e %) e decidir entre DRAGANDO / BUSCANDO.  
- **Exemplo de execução da CLI**:

```bash
# Entrar na pasta do módulo no backend
cd backend/src/módulo1-B

# Iniciar a CLI (requer Arduino conectado via serial)
python cli.py

# Comandos dentro da CLI:
# c → Solicitar leitura de corrente
# q → Sair
```

### 5.3 Módulo 2-A – Movimentação XY

- **Objetivo**: controlar a movimentação horizontal da balsa (Cima/Baixo/Esquerda/Direita) e potência (50/80/100%).  
- **Exemplo de execução da CLI**:

```bash
# Entrar na pasta do módulo no backend
cd backend/src/módulo2-A

# Instalar dependências e iniciar a CLI (requer ESP32 conectado via serial)
pip install -r requirements.txt
python esteira_cli.py

# Teclas de controle dentro da CLI:
# a         → Mover para a esquerda
# d         → Mover para a direita
# Espaço    → Parar motor
```

### 5.4 Módulo 2-B – Visualização da câmera

- **Objetivo**: iniciar a captura/visualização da câmera para inspeção da área de dragagem.  
- **Exemplo de execução da CLI**:

```bash
# Entrar na pasta do módulo no backend
cd backend/src/módulo2-B

# Instalar dependências
pip install typer opencv-python requests numpy

# Iniciar visualização da câmera (requer ESP32-CAM na mesma rede)
python cli.py abrir-camera
```

### 5.5 Módulo 2-C – Fallback Sensores

- **Objetivo**: monitorar sensores de proximidade e gerar alertas (ex.: “Cuidado, próximo à borda X”).  
- **Exemplo de execução da CLI**:

```bash
# Entrar na pasta do módulo no backend
cd backend/src/módulo2-C

# Instalar dependências
pip install pyserial

# Iniciar a CLI (requer ESP32 conectado via serial)
python cli.py --port /dev/ttyUSB0

# Outros exemplos:
python cli.py --port /dev/ttyACM0
python cli.py --port COM3          # Windows
```
