---
sidebar_label: "Entendimento do Negócio"
sidebar_position: 1
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Entendimento do Negócio

<!-- Escreva aqui uma breve introdução sobre o entendimento do negócio e os artefatos que serão apresentados nesta seção -->


## 1. Introdução à Matriz de Risco

A **Matriz de Risco** é uma ferramenta de gestão estratégica fundamental que permite a identificação, análise e priorização de incertezas capazes de afetar os objetivos do projeto. Através da correlação direta entre a **Probabilidade** de ocorrência e o **Impacto** gerado, a matriz orienta a alocação eficiente de recursos para a mitigação de ameaças ou a potencialização de oportunidades (PMI, 2017).

No contexto específico do sistema automatizado de dragagem, esta ferramenta torna-se vital para assegurar a integridade do hardware em ambientes subaquáticos hostis e garantir a confiabilidade da navegação autônoma. A análise subsequente prioriza os 10 principais riscos (ameaças) e 9 oportunidades estratégicas, estabelecendo uma conexão direta entre cada item e os requisitos técnicos definidos no **TAPI**.

**Referência:** Project Management Institute (PMI). A Guide to the Project Management Body of Knowledge (PMBOK® Guide). 6th ed. Newtown Square, PA: Project Management Institute, 2017.

## Metodologia de Identificação

A estruturação do levantamento de riscos foi fundamentada em uma estratégia híbrida, organizada através das seguintes frentes:
* **Brainstorming técnico:** Reuniões com o time de engenharia para análise minuciosa de subsistemas como propulsão, içamento, navegação, comunicação e sensoriamento.
* **Consulta ao parceiro:** Alinhamento com especialistas da Itubombas para mapear falhas e incidentes recorrentes em operações manuais de dragagem.
* **Análise de requisitos:** Revisão técnica dos requisitos do TAPI para detecção precoce de possíveis pontos críticos de falha.
* **Ranqueamento por Índice de Risco (IR):** Priorização dos eventos através da fórmula $IR = Probabilidade (\%) \times Impacto (1-5)$.
&nbsp;

Do levantamento inicial de 18 riscos potenciais, foram selecionados os 10 principais que apresentam $IR \geq 0,15$ — o que corresponde a cenários com probabilidade mínima de 30% e impacto classificado como moderado ou superior.

---

<div align="center">
  <sub>Figura 1 - Matriz de Riscos e Oportunidades</sub>
  <img src={useBaseUrl('/img/matrizRiscos.jpg')} alt="Matriz de Riscos e Oportunidades" width="100%" />
  <sup>Fonte: Material produzido pelos autores (2026)</sup>
</div>

---

## 2. Especificação de Riscos (Ameaças)

Os riscos abaixo foram selecionados e ranqueados por ordem de criticidade técnica para o sucesso do protótipo funcional.

### A1 – Desbalanceamento de Peso (Centro de Gravidade)
* **Descrição:** Oscilação pendular da motobomba sob o flutuador deslocando o centro de gravidade.
* **Probabilidade:** 50% | **Justificativa:** O peso da motobomba representa fração significativa do deslocamento; embora as guias limitem o curso lateral, a inércia em manobras é um fator real.
* **Impacto:** Moderado | **Justificativa:** Pode causar adernamento da balsa, comprometendo a horizontalidade dos sensores de nível e precisão do GPS.
* **Requisito Afetado:** R-02 (Estabilidade dinâmica do flutuador).
* **Plano de Mitigação:** Posicionar o sistema de içamento (talha) e a bomba no centro geométrico de flutuação e usar baterias como contrapeso.
* **Indicador de Eficácia:** Inclinação máxima do deck inferior a 5 graus durante operação de içamento.

### A2 – Pontos Cegos de Comunicação (Shadowing)
* **Descrição:** Obstrução de sinal RF por barreiras físicas como taludes ou vegetação.
* **Probabilidade:** 10% | **Justificativa:** Áreas de dragagem frequentemente possuem margens elevadas que bloqueiam a linha de visada direta (LoS).
* **Impacto:** Alto | **Justificativa:** Perda de telemetria pode causar colisão ou perda de controle manual em situações de emergência.
* **Requisito Afetado:** R-08 (Continuidade da comunicação de dados).
* **Plano de Mitigação:** Configurar rotinas de segurança (failsafe) para retorno automático ("Return to Home") se o heartbeat falhar por > 5s.
* **Indicador de Eficácia:** Ativação do protocolo de segurança em 100% das simulações de perda de sinal.

### A3 – Saturação dos Motores contra Correnteza
* **Descrição:** Força da correnteza superando a potência nominal dos propulsores.
* **Probabilidade:** 50% | **Justificativa:** Canais de dragagem podem apresentar fluxos laminares rápidos, especialmente em períodos de chuva.
* **Impacto:** Muito Alto | **Justificativa:** Deriva da embarcação e possível colisão catastrófica ou perda do protótipo.
* **Requisito Afetado:** R-01 (Navegação autônoma em ambiente hidrodinâmico).
* **Plano de Mitigação:** Superdimensionar a potência dos motores em 20% e implementar sensoriamento de corrente elétrica.
* **Indicador de Eficácia:** Manutenção da posição estática (erro < 1m) em correnteza de até 1.5 m/s.

### A4 – Interferência Magnética na Bússola (Magnetômetro)
* **Descrição:** Campo eletromagnético da bomba e cabos distorcendo as leituras de direção.
* **Probabilidade:** 70% | **Justificativa:** A alta corrente necessária para a bomba de dragagem gera campos magnéticos que interferem em sensores digitais próximos.
* **Impacto:** Alto | **Justificativa:** Erro de orientação impede a execução de trajetórias retas e o mapeamento correto.
* **Requisito Afetado:** R-04 (Precisão de orientação e azimute).
* **Plano de Mitigação:** Isolar o módulo bússola/GPS em estrutura elevada e realizar calibração de compensação magnética (hard iron).
* **Indicador de Eficácia:** Desvio de orientação inferior a 3 graus medido contra bússola analógica de referência.

### A5 – Cavitação das Hélices em Águas Agitadas
* **Descrição:** Aeração das hélices devido à oscilação vertical da balsa.
* **Probabilidade:** 70% | **Justificativa:** O movimento de arfagem (pitch) em águas turbulentas pode aproximar os propulsores da superfície.
* **Impacto:** Moderado | **Justificativa:** Perda momentânea de tração e vibração excessiva no sistema propulsor.
* **Requisito Afetado:** R-10 (Operação em águas com agitação superficial).
* **Plano de Mitigação:** Projetar suportes de motor com profundidade ajustável.
* **Indicador de Eficácia:** Manutenção do empuxo constante em condições de ondulação de até 20cm.

### A6 – Superaquecimento dos Drivers de Motor
* **Descrição:** Operação contínua de "station keeping" elevando a temperatura da eletrônica.
* **Probabilidade:** 50% | **Justificativa:** O esforço constante dos motores para manter posição contra correnteza gera calor residual nos controladores de potência.
* **Impacto:** Alto | **Justificativa:** Desligamento térmico dos motores, resultando em perda de manobrabilidade.
* **Requisito Afetado:** R-12 (Confiabilidade do sistema eletrônico de potência).
* **Plano de Mitigação:** Utilizar drivers com capacidade superior à nominal e ventilação forçada.
* **Indicador de Eficácia:** Temperatura estável dos drivers abaixo de 70°C em operação contínua.

### A7 – Efeito Ventosa (Suction Effect)
* **Descrição:** Resistência do lodo excedendo a capacidade de carga da talha no início da subida.
* **Probabilidade:** 90% | **Justificativa:** Superfícies planas da bomba em contato com sedimentos finos criam vácuo hidráulico; relatado como ocorrência padrão em operações da Itubombas.
* **Impacto:** Muito Alto | **Justificativa:** Sobrecarga mecânica do cabo de aço ou queima do motor de içamento.
* **Requisito Afetado:** R-03 (Sistema de içamento e remoção de bomba).
* **Plano de Mitigação:** Algoritmos de içamento pulsado e monitoramento de corrente do motor da talha.
* **Indicador de Eficácia:** Identificação de sobrecarga e redução de velocidade em < 0.5s.

### A8 – Encavalamento do Cabo de Aço
* **Descrição:** Enrolamento desordenado no carretel devido à baixa tensão ou balanço.
* **Probabilidade:** 50% | **Justificativa:** O empuxo reduz o peso aparente da bomba na subida, facilitando folgas no cabo.
* **Impacto:** Alto | **Justificativa:** Travamento do mecanismo, exigindo intervenção manual externa.
* **Requisito Afetado:** R-15 (Mecanismo de gerenciamento de cabo).
* **Plano de Mitigação:** Implementar guias mecânicas e manter peso constante para tração do cabo.
* **Indicador de Eficácia:** Execução de 50 ciclos de subida/descida sem sobreposição de espiras.

### A9 – Leitura Falsa de Profundidade
* **Descrição:** Sonar interpretando lodo fluido (nuvem de sedimento) como fundo sólido.
* **Probabilidade:** 70% | **Justificativa:** Sinais ultrassônicos sofrem reflexão em meios de densidades variadas antes do solo firme.
* **Impacto:** Moderado | **Justificativa:** Interrupção prematura da descida da bomba, reduzindo a produção.
* **Requisito Afetado:** R-06 (Mapeamento de profundidade e batimetria).
* **Plano de Mitigação:** Sensor de carga na talha para confirmar toque físico (redução de tração).
* **Indicador de Eficácia:** Correlação superior a 95% entre leitura do sonar e sensor de peso.

### A10 – Oscilação Pendular na Subida
* **Descrição:** Colisão da bomba contra os flutuadores durante o recolhimento.
* **Probabilidade:** 50% | **Justificativa:** Velocidade de içamento combinada com correntes laterais induz movimento de pêndulo na carga suspensa.
* **Impacto:** Moderado | **Justificativa:** Danos aos cascos dos flutuadores ou desalinhamento de sensores de base.
* **Requisito Afetado:** R-11 (Integridade estrutural do sistema de acoplamento).
* **Plano de Mitigação:** Limitar velocidade via software (PWM) e instalar estruturas de guia ("berço").
* **Indicador de Eficácia:** Zero colisões registradas durante testes de recolhimento em carga máxima.

---

## 3. Especificação de Riscos (Oportunidades)

As oportunidades representam o potencial de exceder os requisitos do TAPI e gerar diferenciais competitivos (Green Tech e eficiência).

### O1 – Otimização Energética
* **Descrição:** Redução do consumo de energia durante manobras operacionais.
* **Probabilidade:** Alta | **Justificativa:** Algoritmos PID reduzem o consumo em manobras em até 15%.
* **Impacto:** Alto (Redução de OPEX) | **Justificativa:** Diminuição direta nos custos operacionais e aumento da autonomia das baterias.
* **Requisito Afetado:** R-Eficiência (Gerenciamento de Energia).
* **Plano de Potencialização:** Implementar logs de consumo para validar autonomia.
* **Indicador de Eficácia:** Relatórios de log demonstrando redução de ≥15% no consumo médio por manobra.

### O2 – Redução de Desgaste
* **Descrição:** Preservação do equipamento contra danos físicos operacionais.
* **Probabilidade:** Alta | **Justificativa:** Sensores evitam cavitação e operação a seco.
* **Impacto:** Alto (Manutenibilidade) | **Justificativa:** Aumento da vida útil dos componentes e menor tempo de inatividade (downtime).
* **Requisito Afetado:** R-Confiabilidade (Saúde do Equipamento).
* **Plano de Potencialização:** Criar relatórios de saúde do equipamento para o cliente.
* **Indicador de Eficácia:** Feedback positivo do cliente baseado nos relatórios de manutenção preditiva gerados.

### O3 – Negócio Sustentável
* **Descrição:** Operação ecologicamente correta e redução da pegada de carbono.
* **Probabilidade:** Muito Alta | **Justificativa:** Automação elimina a necessidade de motores auxiliares a diesel.
* **Impacto:** Alto (Imagem Corporativa/ESG) | **Justificativa:** Alinhamento com normas ambientais rigorosas e apelo comercial "verde".
* **Requisito Afetado:** R-Sustentabilidade (Emissões Zero).
* **Plano de Potencialização:** Calculadora de CO2 evitado integrada à interface.
* **Indicador de Eficácia:** Exibição em tempo real da métrica "Kg de CO2 Evitado" no painel de controle.

### O4 – Propriedade Intelectual
* **Descrição:** Criação de ativos intangíveis e diferenciação tecnológica.
* **Probabilidade:** Média/Alta | **Justificativa:** Integração inédita de navegação com lógica de dragagem.
* **Impacto:** Muito Alto (Estratégico) | **Justificativa:** Proteção de mercado e valorização da valuation da empresa.
* **Requisito Afetado:** R-Inovação (Diferencial Competitivo).
* **Plano de Potencialização:** Documentar algoritmos para fins de patenteamento.
* **Indicador de Eficácia:** Pedido de patente depositado e aceito para análise.

### O5 – Diagnóstico do Fundo
* **Descrição:** Capacidade de análise geológica em tempo real.
* **Probabilidade:** Média | **Justificativa:** Processamento de sinal para classificar sedimentos.
* **Impacto:** Médio (Operacional) | **Justificativa:** Permite ajustes finos na operação dependendo do tipo de material (lodo vs detritos).
* **Requisito Afetado:** R-Operação (Inteligência de Sondagem).
* **Plano de Potencialização:** Treinar algoritmo para diferenciar lodo de detritos.
* **Indicador de Eficácia:** Taxa de acerto superior a 90% na classificação automática de sedimentos durante testes.

### O6 – Segurança do Trabalho
* **Descrição:** Eliminação do risco humano direto na operação de dragagem.
* **Probabilidade:** Certeza (100%) | **Justificativa:** Remoção completa do operador de áreas de risco.
* **Impacto:** Crítico (Segurança Humana) | **Justificativa:** Zera a probabilidade de acidentes de trabalho in loco com operadores.
* **Requisito Afetado:** R-Segurança (NR-12 / Operação Remota).
* **Plano de Potencialização:** Enfatizar segurança remota no material comercial.
* **Indicador de Eficácia:** Aceitação do produto por equipes de SMS (Saúde, Meio Ambiente e Segurança) dos clientes.

### O7 – Gamificação de Treino
* **Descrição:** Uso de simulação para capacitação de operadores.
* **Probabilidade:** Alta | **Justificativa:** Interface digital permite simulação HIL (Hardware-in-the-loop).
* **Impacto:** Médio (Treinamento) | **Justificativa:** Reduz a curva de aprendizado e evita riscos de treino em equipamento real.
* **Requisito Afetado:** R-Usabilidade (Treinamento de Usuário).
* **Plano de Potencialização:** Criar Modo Simulação com dados reais gravados.
* **Indicador de Eficácia:** Operadores aptos a operar o sistema real após X horas no Modo Simulação.

### O8 – Precisão Volumétrica
* **Descrição:** Controle exato da quantidade e local do material dragado.
* **Probabilidade:** Alta | **Justificativa:** Controle milimétrico da profundidade de dragagem.
* **Impacto:** Alto (Qualidade Técnica) | **Justificativa:** Evita sobredragagem (custo extra) ou subdragagem (não atendimento do escopo).
* **Requisito Afetado:** R-Performance (Precisão de Dragagem).
* **Plano de Potencialização:** Integrar talha com mapa batimétrico alvo dinâmico.
* **Indicador de Eficácia:** Divergência menor que 10mm entre o mapa alvo e o fundo dragado real.

### O9 – Flexibilidade Logística
* **Descrição:** Facilidade de mobilização e desmobilização do equipamento.
* **Probabilidade:** Alta | **Justificativa:** Sistema modular facilita transporte para locais remotos.
* **Impacto:** Médio (Logística) | **Justificativa:** Permite atender obras em locais de difícil acesso com menor custo de frete.
* **Requisito Afetado:** R-Portabilidade (Mobilidade do Sistema).
* **Plano de Potencialização:** Design Plug & Play para montagem rápida.
* **Indicador de Eficácia:** Tempo total de montagem e setup em campo inferior a 4 horas.

---

## 4. Conclusão

O processo de identificação e ranqueamento de riscos demonstra que, embora o projeto apresente alta complexidade técnica, as ameaças são mitigáveis. A transição dos requisitos do TAPI para planos de mitigação com indicadores claros garante que o protótipo não seja apenas funcional, mas seguro e confiável para operação real. A gestão contínua desses fatores será o pilar para o cumprimento dos prazos e metas operacionais estipulados junto à **Itubombas**.

&nbsp;

## Canvas Proposta de Valor

<div align="center">
  <sub>Figura 2 - Canvas Proposta de Valor</sub>
  <img src={useBaseUrl('/img/value_proposition_canvas.jpg')} alt="Matriz de Risco" width="100%" />
  <sup>Fonte: Material produzido pelos autores (2026)</sup>
</div>

#### 1. Introdução Conceitual

&nbsp; O Canvas de Proposta de Valor, desenvolvido por Osterwalder e Pigneur, tem como objetivo estruturar de forma clara a relação entre as necessidades reais do cliente, suas principais dores e ganhos esperados, e os produtos e serviços oferecidos para atendê-los. Trata-se de uma ferramenta que desloca o foco da tecnologia ou do produto em si para a criação efetiva de valor percebido pelo cliente.

&nbsp; No contexto deste projeto, o Canvas é utilizado para analisar como a automação do processo de dragagem pode gerar ganhos operacionais concretos para o cliente final, ao mesmo tempo em que fortalece a posição estratégica da Itubombas como líder em soluções de bombeamento e dragagem.


#### 2. Perfil do Cliente

***2.1 Customer Jobs***

&nbsp; As principais tarefas do cliente são:

- Realizar operações de dragagem de forma contínua, eficiente e segura.

- Garantir que a bomba foi retirada totalmente antes de deslocar a balsa.

- Assegurar a movimentação da balsa nos locais corretos.

&nbsp; É importante ressaltar que atividades como movimentar a bomba ou a balsa não constituem objetivos finais do cliente, mas ainda sim são meios necessários para a realização desse trabalho principal.

***2.2 Dores*** 

&nbsp; As principais dores associadas à execução desse job são o risco de operação a seco, decorrente da falta de visibilidade sobre o nível do fluido e o avanço da dragagem e o processo 100% manual, altamente dependente da experiência do operador e sujeito a falhas humanas, levando a posicionamentos ineficientes e perda de produtividade. Dessa forma, essas dores impactam diretamente a segurança, os custos e a confiabilidade da operação.

***2.3 Ganhos Esperados***

&nbsp; Os principais ganhos esperados pelo cliente incluem:

- Redução de custos operacionais, por meio da diminuição de paradas improdutivas e danos ao equipamento.

- Maior autonomia operacional, com menor dependência de intervenção humana contínua.

- Precisão no posicionamento da balsa, assegurando que a dragagem ocorra de forma mais eficiente.

#### 3. Proposta de Valor

***3.1 Produtos e Serviços***

&nbsp; A solução proposta consiste em um sistema integrado de automação e monitoramento para operações de dragagem, composto por alguns elementos principais, como a automação da movimentação da bomba e da balsa, com lógica de intertravamento que impede o deslocamento do flutuador enquanto a bomba não estiver em posição segura e o dispositivo de mapeamento do fundo, que permite a identificação da topografia subaquática e possíveis obstáculos. 

&nbsp; Além disso, também inclui-se um dashboard de monitoramento e controle, fornecendo ao operador informações em tempo real sobre o estado da bomba, liberação para movimentação e condições operacionais.
Esses produtos e serviços atuam de forma integrada para transformar a operação em um processo assistido por tecnologia, reduzindo a dependência de ações manuais e decisões baseadas exclusivamente na experiência do operador.

***3.2 Criadores de Ganho***

&nbsp; Os criadores de ganho representam como a solução potencializa os resultados desejados pelo cliente durante a execução da dragagem, que vão além do essencial e do que é esperado na solução:

- Processo operacional simplificado, reduzindo a complexidade da operação e a necessidade de acompanhamento constante do operador.

- Redução do tempo de resposta operacional, ao eliminar paradas improdutivas para reposicionamento manual da balsa e verificação empírica das condições do fundo.

- Operação baseada em dados, permitindo decisões mais assertivas a partir de informações objetivas sobre profundidade, estado da bomba e condições do processo.

&nbsp; Esses ganhos contribuem para uma operação mais previsível, contínua e eficiente, alinhada às expectativas do cliente por maior produtividade e menor risco.

***3.3 Aliviadores de Dor***

&nbsp; Por fim, os aliviadores de dor atuam diretamente sobre os principais pontos críticos, normalmente relacionados com as dores citadas. Nesse sentido, o sistema fail-safe, que bloqueia automaticamente a movimentação da balsa caso a bomba não esteja em posição segura, sana o perigo da operação ocorrer a seco. Por último, o controle remoto do processo, diminui a porcentagem do processo que ocorre de forma manual. Assim, esses mecanismos mitigam falhas operacionais que podem gerar danos ao equipamento, aumento de custos e riscos à segurança.


#### 4. Geração de Valor para a Itubombas a partir da Proposta de Valor ao Cliente

&nbsp; Embora o Canvas seja estruturado a partir da perspectiva do cliente, a criação de valor sustentável ocorre quando a proposta também fortalece o modelo de negócios da empresa provedora da solução. Nesse sentido, a automação da dragagem gera valor estratégico direto para a Itubombas.

&nbsp; Ao resolver dores críticas do cliente, a solução eleva o valor percebido da locação, deslocando o foco do equipamento isolado para uma solução tecnológica integrada. Isso reduz a sensibilidade ao preço, fortalece a diferenciação competitiva e consolida a posição da Itubombas como fornecedora de soluções completas, e não apenas de ativos físicos.

&nbsp; Além disso, a mitigação de falhas operacionais reduz o desgaste dos equipamentos locados, impactando positivamente a vida útil dos ativos, os custos de manutenção e a disponibilidade do parque de locação, elementos centrais para a rentabilidade do negócio. A automação também permite à Itubombas escalar conhecimento operacional, reduzindo a dependência da experiência individual de operadores, inclusive quando a operação é realizada por equipes do cliente. Isso aumenta a confiabilidade das operações e cria barreiras competitivas difíceis de serem replicadas por concorrentes.

&nbsp; Por fim, a incorporação de inteligência, dados e automação ao portfólio reforça o posicionamento da Itubombas como líder de mercado orientado à inovação, ampliando seu range de atuação e abrindo espaço para novos modelos de serviço e parcerias tecnológicas estratégicas.

#### 5. Considerações Finais

&nbsp; Concluindo, a proposta de valor apresentada transforma a operação de dragagem de um processo manual e empírico em uma atividade orientada por dados, com maior previsibilidade, segurança e eficiência. Ao alinhar as necessidades do cliente com uma solução tecnológica integrada, o projeto não apenas resolve problemas operacionais, mas fortalece a posição estratégica da Itubombas, demonstrando como a criação de valor para o cliente e para a empresa ocorre de forma interdependente e sustentável.


## Referências

Osterwalder, A.; Pigneur, Y.; Bernarda, G.; Smith, A. Value Proposition Design: How to Create Products and Services Customers Want. Wiley, 2014.


