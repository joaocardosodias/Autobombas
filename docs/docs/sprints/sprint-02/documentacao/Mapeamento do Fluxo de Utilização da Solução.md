---
sidebar_label: "Mapeamento do Fluxo de Utilização da Solução"
sidebar_position: 2
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Mapeamento do Fluxo de Utilização da Solução

---

## 1. User Stories



---

### 1.1 Módulo 1-A — Movimentação Z (Motor de Passo)

| ID | Persona | História | Critério de Aceitação |
|----|---------|----------|-----------------------|
| US-M1A-01 | Operador | Como operador responsável pela dragagem, eu quero comandar a descida e subida da motobomba informando a distância em centímetros via CLI, para que eu possa posicioná-la com precisão na profundidade ideal de extração sem precisar calcular manualmente as rotações do motor. | <ol><li>A CLI deve aceitar os comandos `movZ descer(<cm>)` e `movZ subir(<cm>)`, onde `<cm>` é um valor numérico positivo.</li><li>O sistema deve converter automaticamente a distância em centímetros para o número equivalente de voltas do motor de passo e exibir o resultado da tradução ao operador.</li><li>O sistema deve bloquear novos comandos enquanto o motor estiver em execução, exibindo a mensagem `[ERRO] Motor ocupado. Aguarde o término do movimento.`</li><li>Ao concluir o movimento, o sistema deve exibir a confirmação `[INFO] Movimento CONCLUÍDO`.</li></ol> |
| US-M1A-02 | Gestor | Como gestor, eu quero acessar o histórico completo de movimentações verticais (eixo Z) da motobomba, com data, hora, direção e distância de cada comando executado, para auditar a operação e identificar padrões de uso ou desvios de procedimento. | <ol><li>Cada comando de movimentação Z validado deve gerar um registro persistente no banco de dados, contendo: timestamp, direção (`descer` ou `subir`), distância em centímetros e número de voltas calculadas.</li><li>Os registros não devem ser perdidos ao reiniciar o sistema.</li><li>O gestor deve poder consultar o histórico de dias anteriores por meio da interface de gestão.</li></ol> |

---

### 1.2 Módulo 1-B — Leitura de Corrente de Operação

| ID | Persona | História | Critério de Aceitação |
|----|---------|----------|-----------------------|
| US-M1B-01 | Operador | Como um operador responsável pela dragagem, eu quero visualizar a corrente elétrica da motobomba em tempo real para entender o desempenho da sucção e tomar decisões sobre o posicionamento da motobomba. | <ol><li>O sistema deve exibir a leitura de corrente em tempo real por meio da interface CLI quando solicitado pelo operador.</li><li>O sistema deve apresentar a corrente também em formato percentual em relação ao valor máximo de medição.</li><li>O sistema deve atualizar os valores de corrente sempre que uma nova leitura for solicitada.</li></ol> |
| US-M1B-02 | Gestor | Como gestor de operações de dragagem, eu quero visualizar o histórico de leituras de corrente elétrica da motobomba com classificação automática do estado operacional em cada operação, para analisar padrões de uso e desempenho das motobombas, obter insights sobre eficiência e manutenção, e tomar decisões fundamentadas sobre posicionamento e alocação do equipamento em operações futuras. | **CA-01 — Registro histórico das leituras por operação**<br /><br />O sistema deve registrar cada leitura de corrente realizada, associando-a a um timestamp (data e hora) e ao identificador da operação em curso. O histórico deve persistir entre sessões. Cada entrada deve conter timestamp, valor de corrente em Amperes, percentual (%) e classificação automática.<br /><br />**CA-02 — Visualização consolidada do histórico**<br /><br />O sistema deve permitir a visualização do histórico de leituras em ordem cronológica. O formato das entradas deve ser padronizado e legível, por exemplo: [2026-02-25 14:32:10] \| Corrente: 0.000451 A \| Percentual: 90.22% \| Classificação: Corrente elevada. O histórico deve ser acessível sem necessidade de ferramentas externas.<br /><br />**CA-03 — Classificação automática consistente**<br /><br />O sistema deve aplicar a mesma lógica de classificação utilizada na exibição em tempo real. As faixas devem seguir:<br />- 0% – 69% → Corrente baixa (Predominância de sucção de líquido)<br />- 70% – 84% → Corrente normal (Operação estável)<br />- 85% – 100% → Corrente elevada (Alta concentração de sólidos). A classificação deve ser automática e nenhuma entrada deve ser registrada sem classificação.<br /><br />**CA-04 — Suporte à análise de padrões**<br /><br />O histórico deve permitir identificar padrões de operação ao longo do tempo. O sistema deve permitir filtrar ou segmentar o histórico por operação. As informações registradas devem ser suficientes para embasar decisões de manutenção e análise operacional.<br /><br />**CA-05 — Acesso ao histórico**<br /><br />O sistema deve permitir que o usuário acesse o histórico de leituras de forma clara e rápida por meio da interface disponível. ||

### 1.3 Módulo 2-A — Posicionamento da Balsa e Ancoragem

| ID | Persona | História | Critério de Aceitação |
|----|---------|----------|-----------------------|
| US-M2A-01 | Operador | Como Operador, eu quero utilizar botões direcionais intuitivos (Frente, Trás, Esquerda, Direita) no dashboard para movimentar a balsa pela superfície do tanque, garantindo que eu consiga levá-la exatamente até o próximo ponto de dragagem da grade. | <ol><li>O dashboard deve possuir botões direcionais claros.</li><li>Ao acionar um comando, o sistema deve enviar o sinal correspondente ao hardware.</li><li>O motor deve responder na direção correta.</li></ol> |
| US-M2A-02 | Operador | Como Operador, eu quero um controle de nível de potência (ex: slider de 0% a 100%) no dashboard para ajustar a velocidade dos propulsores, para que eu possa fazer manobras mais finas e precisas quando estiver chegando perto do ponto ideal. | <ol><li>O painel deve ter um controle de nível (slider) de 0 a 100%.</li><li>A alteração nesse controle deve ajustar o sinal PWM do motor proporcionalmente em tempo real.</li></ol> |
| US-M2A-03 | Operador | Como Operador, eu quero um botão de "Parar Motores" bem visível no painel de movimentação para cortar o acionamento dos propulsores imediatamente, permitindo que a balsa estabilize no ponto escolhido para iniciar a dragagem. | <ol><li>Deve existir um botão de Parada/Freio em destaque.</li><li>O clique neste botão deve sobrepor qualquer outro comando e cortar a energia dos motores (PWM = 0) instantaneamente.</li></ol> |
| US-M2A-04 | Operador | Como Operador, eu quero que o painel destaque visualmente qual direção está sendo acionada no momento, para que eu tenha certeza de que o sistema registrou o meu comando corretamente. | <ol><li>O botão pressionado deve mudar de estado visual (ex: acender) na interface.</li><li>O feedback visual deve voltar ao normal quando o comando de parada for acionado.</li></ol> |
| US-M2A-05 | Gestor | Como Gestor, eu quero acessar uma tabela no dashboard contendo o registro de todos os comandos de movimentação executados pelo operador (Ex: "Mover Frente", "Parar"), acompanhados de seus respectivos *timestamps* (Data e Hora exatas), para auditar as ações. | <ol><li>O dashboard deve exibir uma tabela de logs de operação.</li><li>Cada acionamento de motor ou parada deve gerar uma linha com o nome do comando e o horário exato.</li></ol> |
| US-M2A-06 | Gestor | Como Gestor, eu quero que essa tabela de *timestamps* seja salva de forma persistente (banco de dados), para que eu possa consultar o histórico de dias anteriores caso haja alguma divergência na produtividade relatada. | <ol><li>Cada comando validado na CLI/Dashboard deve realizar um `INSERT` no banco de dados relacional.</li><li>Os dados salvos não devem ser perdidos ao desligar o sistema.</li><li>Deve ser possível visualizar registros passados.</li></ol> |

---

### 1.4 Módulo 2-B — Inspeção Visual com Câmera

| ID | Persona | História | Critério de Aceitação |
|----|---------|----------|-----------------------|
| US-M2B-01 | Operador | Como Operador, eu quero visualizar o vídeo em tempo real das câmeras (ESP32-CAM) através de um ícone na plataforma, para que eu possa verificar com precisão a posição da balsa e a distância das bordas com os sensores laterais. | <ol><li>O ícone de câmera deve estar visível no menu lateral esquerdo da plataforma.</li><li>Ao clicar, o sistema deve exibir opções para escolher qual ESP32-CAM visualizar.</li><li>A imagem deve abrir em uma janela flutuante (modal HTML) sem sair da página atual.</li><li>O modal deve conter um botão "X" que encerra o vídeo e fecha a janela imediatamente.</li></ol> |
| US-M2B-02 | Gestor | Como Gestor, eu quero que o sistema registre um histórico automático de acessos às câmeras, para que eu possa auditar quando a balsa foi inspecionada visualmente pela equipe. | <ol><li>Toda vez que o operador abrir a visualização de uma câmera, o sistema deve salvar um log no banco de dados.</li><li>O log deve registrar obrigatoriamente qual câmera foi acessada e o carimbo de data e hora exato do acionamento.</li><li>O banco de dados não deve salvar o fluxo de vídeo em si.</li><li>O evento deve ser registrado no momento exato em que o input `abrir-camera` for acionado pelo botão da interface.</li></ol> |

### 1.5 Módulo 2-C — Alertas de Segurança por Sensores

| ID | Persona | História | Critério de Aceitação |
|----|---------|----------|-----------------------|
| US-M1C-01 | Operador | Como operador, quero receber alertas visuais claros quando a balsa estiver próxima das bordas, para evitar colisões e aumentar a segurança da operação. | O sistema exibe avisos visuais destacados sempre que a distância medida pelos sensores atingir zonas de risco pré-definidas, permitindo ao operador interromper ou ajustar a movimentação antes de uma colisão. |
| US-M1C-02 | Gestor | Como gestor, quero ter registro dos alertas de sensores, para analisar incidentes e melhorar as políticas de segurança. | Cada alerta gerado é registrado com data/hora, direção do sensor, nível de risco e mensagem associada, possibilitando consultas posteriores e geração de relatórios de segurança. |


---



---

## 2. User Flow

&nbsp;O mapeamento do fluxo de utilização do usuário (*user flow*) é a representação visual dos passos ou telas que um usuário percorre para realizar uma ação ou atingir um objetivo dentro de um produto ou serviço digital. Segundo Sinclair (2011), essa representação identifica as principais funções e interconexões de um sistema, permitindo uma visão geral do processamento de sinais e tomada de decisão. No contexto da Itubombas, o fluxo detalha a integração entre a operação manual da balsa e a automação do sistema de bombeamento submersível.

---

### 2.1 User Flow — Operador

&nbsp;O fluxo do operador é centrado na **operação assistida**, onde a navegação horizontal (XY) permanece sob controle humano, enquanto a operação vertical (Z) e a proteção do motor da bomba são geridas pelo sistema de controle. Este fluxo visa otimizar a extração de sedimentos e garantir a integridade do hardware.


<p style={{textAlign: 'center'}}>Figura 1 - User Flow Operador</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/UserFlowOperador.png").default} style={{width: 800}} alt="User Flow Operador" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>



**Contextualização do Fluxo:**

1.  **Inicialização e Diagnóstico**: O operador acessa a interface e o sistema executa um auto-teste nos sensores dos módulos de navegação e dragagem.
2.  **Navegação Manual Assistida (Módulos 02-A, 02-B e 02-C)**:
    * O operador utiliza o controle remoto para acionar a movimentação XY (**02-A**).
    * O feedback visual é fornecido pela câmera embarcada (**02-B**).
    * Sensores de proximidade (**02-C**) monitoram as bordas do local, enviando alertas em tempo real para evitar colisões durante o deslocamento manual.
3.  **Configuração e Bloqueio de Segurança**: Ao atingir o ponto de dragagem, o operador inicia o ciclo Z. O sistema ativa um intertravamento que bloqueia a movimentação XY (**02-A**) para evitar danos mecânicos com a bomba submersa.
4.  **Dragagem Automatizada (Módulos 01-A e 01-B)**:
    * O guincho (**01-A**) desce a bomba até detectar o material.
    * A medição da corrente (**01-B**) determina o comportamento do guincho: descer em baixa carga, manter em carga ideal e subir em caso de sobrecarga crítica.
5.  **Finalização do Ponto**: Após a limpeza do ponto, a bomba é recolhida totalmente (**01-A**), liberando os motores de navegação para um novo deslocamento.

&nbsp;  O fluxo do operador reduz a carga cognitiva ao automatizar a gestão de profundidade, garantindo que o foco humano seja mantido na segurança da navegação e no posicionamento estratégico da balsa.

---

### 2.2 User Flow — Gestor

&nbsp;O fluxo do gestor ou supervisor foca na auditoria técnica e produtividade. Ele utiliza dados históricos gerados pelos módulos da balsa para validar a conformidade e eficiência das sessões de campo.

<p style={{textAlign: 'center'}}>Figura 2 - User Flow Gestor</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/UsereFlowGestor.png").default} style={{width: 800}} alt="User Flow Gestor" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>


**Contextualização do Fluxo:**

1.  **Acesso e Triagem**: O supervisor acessa a plataforma de gestão e visualiza a lista de sessões recentes, filtrando por data, cliente ou bomba específica.
2.  **Análise de Eventos (Módulos 02-C e 01-B)**:
    * Na tela de detalhes, o supervisor audita o histórico de alertas.
    * Alertas de proximidade indicam se o operador ignorou os limites de segurança do módulo **02-C**.
    * Alertas de corrente crítica indicam se a bomba submersível foi levada a condições extremas de esforço (**01-B**).
3.  **Avaliação de Eficiência (Módulo 01-A)**:
    * O supervisor analisa o gráfico de estados da bomba (Buscando, Intermediário, Dragando).
    * Isso permite identificar o tempo efetivo de dragagem em relação ao tempo total de operação.
4.  **Conclusão da Auditoria**: Com base nos logs e gráficos, o gestor valida a sessão ou identifica necessidades de manutenção preventiva ou re-treinamento de pessoal.

&nbsp; O fluxo do gestor transforma telemetria de hardware em inteligência operacional, permitindo uma supervisão baseada em dados reais de esforço mecânico e segurança lateral.

---



## 3. Wireframes

&nbsp;Wireframes são esboços simples de telas de produtos digitais, como sites e aplicativos, cujo intuito é estruturar e validar ideias sem a presença de detalhes como cores, fontes, ícones e imagens. Dessa forma, os wireframes conseguem demonstrar de forma direta a ideia de arquitetura final de uma interface, posicionando os elementos de forma simples e organizada, refletindo apenas o necessário da proposta de uma interface digital (GUIMARÃES, 2021).

&nbsp;No contexto deste projeto para a Itubombas, os wireframes cumprem o papel de materializar visualmente as decisões tomadas durante a etapa de user flow, traduzindo os cenários de uso do operador e do gestor em estruturas concretas de interface. Os wireframes apresentados a seguir são de **baixa fidelidade**, desenhados à mão, sem texto, cores ou especificações visuais definitivas, o que é intencional para esta fase, pois o objetivo é vapenas validar o que aparece em cada tela e como o usuário navega entre elas, não como os elementos serão estilizados. As telas estão organizadas por persona, refletindo a diferença fundamental de uso já identificada no user flow: o operador Carlos interage com o sistema em tempo real durante a operação de dragagem, enquanto o gestor Bruno acessa exclusivamente histórico consolidado para análise e tomada de decisão gerencial.

### 3.1 Wireframe — Operador

&nbsp;Conforme identificado no UX Research, o operador Carlos atua diretamente em campo, em condições que exigem respostas rápidas e seguras. Sua interação com o sistema ocorre durante a execução da dragagem, quando precisa monitorar múltiplos parâmetros simultaneamente, interpretar sinais técnicos em tempo real e reagir a variações de desempenho sem margem para navegação complexa entre telas. Essa realidade operacional orientou a principal decisão de interface desta persona: consolidar toda a interação em uma única tela, garantindo que todas as informações relevantes e todos os controles necessários estejam sempre visíveis, sem que o operador precise navegar para encontrá-los, assim como representado na seguinte imagem:

#### Tela O-1 — Tela Principal do Operador

<p style={{textAlign: 'center'}}>Figura 3 - Wireframe Operador</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/wireframe-operador-tela1.jpeg").default} style={{width: 800}} alt="Mapeamento de Fluxo de Utilização da Solução" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

- **Ponto no user flow:** cobre cenários de interação da Persona Operador — é a única tela de interação do operador com o sistema durante toda a operação de dragagem.
- **Elementos:**
  - **Cabeçalho:** identificação do sistema e do operador em sessão, com ícone e informações textuais de contexto, permitindo rastreabilidade básica sem exigir navegação
  - **Área de visualização da câmera** (placeholder grande com X): feed da câmera em tempo real, correspondente ao Módulo 2-B. Posicionado em destaque e com maior área da tela por ser o principal recurso de percepção espacial do operador durante a operação — é por meio dele que o operador monitora a proximidade da balsa com as bordas, complementado pelos alertas do Módulo 2-C
  - **Barra de leitura de corrente** (placeholder horizontal): exibição das informações do Módulo 1-B — valor de corrente atual, percentual e estado inferido pelo sistema (BUSCANDO / INTERMEDIÁRIO / DRAGANDO), com a ação recomendada correspondente. Posicionada abaixo da câmera para que o operador possa cruzar visualmente o que vê no feed com o estado operacional da motobomba
  - **Botão de joystick** (primeiro círculo, à esquerda): controle de movimentação XY da balsa, correspondente ao Módulo 2-A. Representado como botão circular por remeter visualmente à metáfora de joystick, tornando o comando intuitivo mesmo sem legenda
  - **Botão Parar / Atracar** (segundo círculo, ao centro): acionamento de parada imediata dos propulsores e registro do evento de ancoragem no banco de dados, correspondente ao encerramento do ciclo de movimentação do Módulo 2-A. Posicionado ao centro dos controles por ser a ação de maior criticidade — deve ser acessível rapidamente em qualquer situação
  - **Botões de Movimentação Z** (quadrado, à direita): par de botões de subir e descer para controle vertical da motobomba, correspondente ao Módulo 1-A. Representado como um único elemento quadrado contendo dois controles sobrepostos (▲ subir / ▼ descer), mantendo a área de toque compacta sem sacrificar a distinção entre as duas ações


### 3.2 Wireframe — Gestor

&nbsp;Conforme identificado no UX Research, o gestor Bruno acompanha e gerencia o processo de dragagem de forma remota, sem atuar diretamente sobre os módulos físicos do sistema. Suas necessidades estão centradas em rastreabilidade, análise de produtividade e tomada de decisões gerenciais baseadas em dados consolidados das operações. Diferentemente do operador, que precisa de acesso imediato e centralizado durante a execução, o gestor percorre um fluxo de consulta progressivo — primeiro localizando a operação de interesse, depois aprofundando a análise. Essa distinção fundamenta a estrutura de duas telas sequenciais adotada para esta persona, apresentadas a seguir:

#### Tela G-1 — Visão Geral e Filtragem

<p style={{textAlign: 'center'}}>Figura 4 - Tela 1 Wireframe Gestor</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/wireframe-gestor-tela1.jpeg").default} style={{width: 800}} alt="Mapeamento de Fluxo de Utilização da Solução" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

- **Ponto no user flow:** o gestor acessa o sistema e filtra progressivamente para localizar a operação que deseja consultar.
- **Elementos:**
  - **Cabeçalho:** identificação do sistema com ícone e informações textuais de contexto em duas colunas, sendo a primeira referente à identificação do sistema e a segunda a informações de sessão ou navegação atual
  - **Linha de filtragem** (ícone + três placeholders horizontais): mecanismo de seleção progressiva que permite ao gestor afunilar a consulta em etapas — o primeiro placeholder representa a seleção do locatário, o segundo a seleção do equipamento (bomba) associado a esse locatário, e o terceiro a seleção da operação ou período desejado dentro desse equipamento. Essa progressão evita que o gestor seja imediatamente confrontado com um volume grande de dados sem contexto
  - **Tabela de resultados** (quatro colunas, múltiplas linhas): listagem das operações correspondentes aos filtros aplicados. Cada coluna representa um atributo relevante de cada registro — como data, duração, operador responsável e status da operação. Cada linha da tabela é selecionável e direciona o gestor para o detalhamento completo da operação na Tela G-2


#### Tela G-2 — Visão Detalhada da Operação

<p style={{textAlign: 'center'}}>Figura 5 - Tela 2 Wireframe Gestor</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/wireframe-gestor-tela2.jpeg").default} style={{width: 800}} alt="Mapeamento de Fluxo de Utilização da Solução" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

- **Ponto no user flow:** etapa de análise detalhada, acessada após o gestor selecionar uma operação específica na Tela G-1.
- **Elementos:**
  - **Cabeçalho duplo** (duas linhas com ícone + campos de texto): identificação completa da operação selecionada, organizada em duas linhas para comportar todos os atributos sem comprimir a legibilidade. A primeira linha traz informações de identificação de nível mais alto (ex.: locatário e equipamento) e a segunda traz informações específicas da operação (ex.: data, operador responsável)
  - **Bloco de histórico** (placeholder lateral + tabela de texto): estrutura combinada que apresenta o histórico completo da operação de duas formas complementares. O placeholder lateral representa uma visualização temporal ou gráfica da sessão — como a linha do tempo de eventos ou o gráfico de corrente × tempo do Módulo 1-B — oferecendo ao gestor uma leitura rápida do comportamento da operação como um todo. A tabela ao lado detalha textualmente cada evento registrado ao longo da sessão em múltiplas colunas, cobrindo os registros dos Módulos 1-A, 1-B, 2-A e 2-C — movimentações Z, leituras de corrente, movimentos XY e alertas de sensor, respectivamente
  - **Galeria de frames** (dois placeholders horizontais na parte inferior): exibição dos registros visuais capturados pelo Módulo 2-B durante a operação, apresentados lado a lado com timestamp associado a cada frame. Posicionada na parte inferior da tela por ser um complemento ao histórico textual — o gestor consulta primeiro os dados estruturados e depois, se necessário, as evidências visuais da operação


## Referências

GUIMARÃES, Felipe; EQUIPE AELA. Wireframe: O Que É e Como Criar Um Para Seus Projetos De UX Design? *Aela School*, 15 abr. 2021. Disponível em: https://www.aela.io/pt-br/blog/conteudos/wireframe-o-que-e-como-desenhar. Acesso em: 26 fev. 2026.
