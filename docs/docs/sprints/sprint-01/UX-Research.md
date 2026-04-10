---
sidebar_label: "UX Research"
sidebar_position: 3
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# UX Research

&nbsp; A pesquisa de UX é fundamental para garantir que as decisões de design e desenvolvimento estejam fundamentadas em evidências reais sobre as necessidades, comportamentos e expectativas dos usuários, evitando que o produto seja direcionado por suposições não validadas ou vieses da equipe de projeto. Neste projeto, a pesquisa de UX foi conduzida por meio de três técnicas complementares que permitiram uma compreensão abrangente do problema e do contexto operacional: a técnica de imersão, a pesquisa preliminar e a pesquisa desk.

&nbsp; A técnica de imersão consiste na aproximação da equipe com a realidade operacional do problema, permitindo compreender o contexto de uso do sistema antes do processo de proposição de soluções. Essa abordagem é essencial para reduzir vieses de projeto e evitar decisões baseadas em suposições não validadas sobre o comportamento e as necessidades dos usuários, garantindo que a solução desenvolvida esteja alinhada com a prática real de campo.

&nbsp; A pesquisa preliminar corresponde à fase inicial de contato direto com especialistas e stakeholders, realizada por meio de atividades como kick-offs técnicos e entrevistas. Essa técnica permite confrontar o escopo inicialmente proposto com a realidade observada junto aos parceiros, possibilitando a identificação precisa de dores operacionais, restrições técnicas e expectativas reais dos usuários e gestores envolvidos na operação.

&nbsp; A pesquisa desk, por sua vez, consiste na investigação documental que consolida referências técnicas, normativas e tecnológicas relacionadas ao domínio do problema. Essa técnica fornece embasamento teórico e normativo para as decisões adotadas durante a fase de imersão, complementando os dados obtidos junto aos parceiros com fundamentação científica e regulatória.

&nbsp; A combinação dessas três técnicas permitiu uma compreensão multidimensional do problema de automação de dragagem, fundamentando a definição das personas, a modelagem da jornada do usuário e as decisões de arquitetura e design do sistema proposto. Os resultados dessa pesquisa são apresentados nas seções seguintes deste documento.

## Imersão Preliminar

### 1. Introdução e Metodologia

&nbsp; Segundo Susan Farrell, do Nielsen Norman Group, a etapa de imersão é fundamental para reduzir vieses de projeto e evitar decisões baseadas em suposições não validadas sobre o comportamento e as necessidades dos usuários <sup>[1](#c1)</sup>. Essa fase tem como objetivo aproximar a equipe da realidade operacional do problema, permitindo compreender o contexto de uso do sistema antes do processo de proposição de soluções.

&nbsp; Neste projeto, a Imersão Preliminar foi conduzida a partir de duas frentes complementares:
- **(i)** o **kick-off** técnico realizado com os especialistas Bruno Yokoya e Caio Sevilha, colaboradores da Itubombas, no dia 04 de fevereiro de 2026 <sup>[3](#c1)</sup>; e
- **(ii)** uma **Pesquisa Desk**, responsável por consolidar referências técnicas, normativas e tecnológicas relacionadas à automação de processos de dragagem.

&nbsp; Essa abordagem permitiu confrontar o escopo inicialmente apresentado no TAPI com a realidade observada junto ao parceiro, possibilitando uma compreensão mais precisa das dores operacionais, das restrições técnicas e das expectativas reais dos usuários e gestores envolvidos na operação <sup>[3](#c1)</sup>.

### 2. Cenário do Problema e Principais Insights do Parceiro

&nbsp; O contato direto com o parceiro revelou diferenças relevantes em relação às premissas iniciais do projeto, especialmente no que se refere ao nível de automação, ao uso de sensores e à natureza do problema enfrentado na operação <sup>[3](#c1)</sup>. Esses achados evidenciam a necessidade de reavaliação das premissas do escopo inicialmente proposto, a partir da realidade operacional observada em campo.

#### 2.1 Segmentação da Dor Operacional: Dragagem e Drenagem

&nbsp; Durante a imersão, foi identificada uma distinção clara entre os processos de dragagem e drenagem, o que impacta diretamente o tipo de solução necessária <sup>[3](#c1)</sup>.

**Dragagem:**
&nbsp;A principal dor está associada à movimentação da balsa, e não ao mapeamento do fundo. As dimensões do ambiente de operação (largura, comprimento e profundidade) geralmente já são conhecidas, assim como a altura do fundo, permitindo trajetórias planejadas com poucas passagens <sup>[3](#c1)</sup>.

**Drenagem:**
&nbsp; Nesse cenário, além da movimentação da balsa, existe a necessidade de mapeamento contínuo do fundo, pois o nível do fluido e a topografia submersa podem variar ao longo do processo <sup>[3](#c1)</sup>.
&nbsp; Essa diferenciação foi essencial para delimitar corretamente o escopo do projeto, direcionando o foco para a **automação da movimentação na dragagem**, evitando soluções superdimensionadas para contextos operacionais mais simples <sup>[3](#c1)</sup>.

#### 2.2 Experiência Atual do Operador em Campo

&nbsp; A imersão junto ao parceiro revelou que, na prática, a movimentação da balsa ainda depende fortemente do trabalho manual do operador, que precisa empurrar, puxar ou arrastar o equipamento repetidamente para posicioná-lo durante a dragagem. Esse processo é fisicamente desgastante, exige esforço contínuo e expõe o profissional a riscos operacionais, especialmente em ambientes instáveis ou com visibilidade limitada <sup>[3](#c1)</sup>.
&nbsp; Além disso, como o operador não tem visão direta do fundo, ele frequentemente precisa agir por tentativa e erro para posicionar a bomba, o que aumenta o tempo de operação, gera incerteza sobre a eficiência do processo e pode levar a retrabalho desnecessário <sup>[3](#c1)</sup>.
&nbsp; Esse cenário reforça a necessidade de uma solução que reduza o esforço físico do operador, aumente sua segurança e forneça apoio técnico para decisões de movimentação, sem eliminar completamente seu papel de controle sobre a operação — alinhado às boas práticas de design centrado no usuário defendidas por Farrell <sup>[1](#c1)</sup>.

#### 2.3 Impactos Operacionais para a Gestão

&nbsp; Do ponto de vista gerencial, a necessidade de movimentação manual frequente da balsa resulta em paradas operacionais, maior demanda por mão de obra e risco de atrasos na execução do serviço.
&nbsp; O gestor de operações enfrenta o desafio de equilibrar produtividade, segurança e custo, especialmente em projetos de dragagem de maior escala <sup>[3](#c1)</sup>.
&nbsp; Durante a imersão, ficou evidente que uma solução de movimentação automatizada assistida poderia reduzir esses impactos, aumentando a previsibilidade da operação, diminuindo retrabalho e reduzindo a necessidade de intervenções manuais frequentes no local <sup>[3](#c1)</sup>.

#### 2.4 Uso da Telemetria Elétrica como Fonte de Informação (“Sensorless”)

&nbsp; Um dos principais insights obtidos durante a imersão foi a constatação de que não há sensores dedicados instalados na balsa para distinguir a sucção de água da sucção de lodo. Contudo, essa diferenciação já é realizada de forma indireta por meio da leitura da corrente elétrica do motor da bomba <sup>[3](#c1)</sup>.

&nbsp; Na prática, observou-se que:
- valores **mais baixos de corrente** indicam a sucção predominante de água;
- valores **mais elevados de corrente** indicam maior concentração de lodo ou sólidos, em função do aumento do torque exigido pelo motor <sup>[3](#c1)</sup>.

&nbsp; A literatura técnica confirma que o aumento da viscosidade do fluido bombeado implica maior torque no eixo do motor e maior consumo de corrente elétrica, permitindo inferir a presença de lodo sem sensores dedicados — viabilizando estratégias sensorless mais simples e econômicas <sup>[4](#c1)</sup>.

#### 2.5 Regras de Segurança e Intertravamento

&nbsp; Durante o kick-off, foi estabelecida uma regra de negócio considerada crítica e inegociável pelo parceiro: a balsa não pode se movimentar enquanto a bomba estiver submersa <sup>[3](#c1)</sup>. Essa restrição visa evitar danos estruturais, colisões subaquáticas e falhas operacionais graves.
&nbsp; Dessa forma, qualquer lógica de automação deve garantir que a bomba tenha sido completamente suspensa antes da liberação do sistema de propulsão. Esse tipo de intertravamento está alinhado às diretrizes da NR-12, que exige mecanismos automáticos para impedir movimentos perigosos em sistemas automatizados <sup>[3](#c1)</sup>.

#### 2.6 Infraestrutura Existente e Comunicação

&nbsp; Apesar da ausência de sensores adicionais, identificou-se que a comunicação entre os dispositivos já é funcional, sendo realizada por meio de rádio transmissor e receptor <sup>[3](#c1)</sup>. 
&nbsp; Assim, a conectividade não representa uma dor técnica para o parceiro, permitindo que o projeto concentre esforços na lógica de controle e na automação do deslocamento da balsa.

#### 2.7 Proposta de Valor Reavaliada

&nbsp; A partir dos insights obtidos na imersão, a proposta de valor do sistema foi refinada. Em vez de uma autonomia total, o parceiro demonstrou maior interesse em uma solução de movimentação automática assistida, na qual o operador permanece responsável pela tomada de decisão, enquanto o sistema executa o deslocamento de forma precisa e segura <sup>[3](#c1)</sup>.

&nbsp; Essa abordagem atende simultaneamente a duas necessidades identificadas na imersão:
- Para o operador: reduz esforço físico, risco e incerteza no campo;
- Para o gestor: melhora eficiência operacional, reduz custos e diminui paradas desnecessárias <sup>[3](#c1)</sup>.

&nbsp; Essa visão também dialoga com práticas de inovação industrial e eficiência operacional associadas ao ODS 9 – Indústria, Inovação e Infraestrutura <sup>[5](#c1)</sup>.

### 3. Pesquisa Desk: Fundamentação Técnica

&nbsp; A Pesquisa Desk complementou os dados obtidos junto ao parceiro, fornecendo embasamento técnico e normativo para as decisões adotadas durante a fase de imersão.

#### 3.1 Monitoramento de Carga via Telemetria

&nbsp; Estudos técnicos indicam que o aumento da viscosidade do fluido bombeado implica maior torque no eixo do motor e maior consumo de corrente elétrica, permitindo inferir a presença de lodo sem sensores dedicados <sup>[4](#c1)</sup>.

#### 3.2 Intertravamento e Segurança em Sistemas Automatizados

&nbsp; Em sistemas automatizados, a implementação de intertravamentos é uma prática consolidada para mitigação de riscos. A NR-12 reforça a necessidade de bloqueio automático da movimentação em condições perigosas, como quando a bomba está submersa <sup>[2](#c1)</sup>.

#### 3.3 Navegação em Ambientes de Dimensões Conhecidas

&nbsp; Quando o ambiente de operação possui dimensões previamente conhecidas, a literatura recomenda o uso de trajetórias pré definidas e padrões sistemáticos de varredura, o que pode aumentar a eficiência operacional e reduzir consumo energético — alinhado ao ODS 9 <sup>[5](#c1)</sup>.

### 4. Conexão da Imersão com as Futuras Personas

&nbsp; Os achados da Imersão Preliminar fundamentam a definição de duas personas principais para o projeto:
- **Operador de Dragagem**, diretamente impactado pelo esforço físico, riscos operacionais e incertezas do processo atual <sup>[3](#c1)</sup>;
- **Gestor de Operações**, preocupado com eficiência, segurança, custos e continuidade do serviço <sup>[3](#c1)</sup>.

&nbsp; Essas perspectivas orientarão as próximas etapas do projeto, incluindo a construção das personas e a modelagem da jornada do usuário.







---

## Definição das Personas

&nbsp; Personas são arquétipos que representam padrões de comportamento e expectativas, fictícios porém fundamentados em **dados empíricos**, sintetizando **perfis reais** de usuários de um sistema. Seu propósito é orientar decisões de estratégia, experiência do usuário e desenvolvimento, garantindo que a solução projetada esteja centrada nas pessoas que de fato operam e gerenciam o processo <sup>[6](#c1)</sup>.

&nbsp; Neste projeto, as personas foram elaboradas como **protopersonas**, ou seja, representações iniciais e hipotéticas de perfis de usuários construídas a partir de evidências preliminares, suposições validadas com stakeholders e dados iniciais de pesquisa, utilizadas para orientar o direcionamento do projeto nas fases iniciais de desenvolvimento <sup>[7](#c1)</sup>. Essas protopersonas foram construídas com base nos achados da **Imersão Preliminar**, especialmente nas entrevistas realizadas no **kick-off técnico** com a Itubombas e na análise desk complementar. A partir dessa base, foram identificados dois perfis-chave para a operação de dragagem: o **Operador de Dragagem (Carlos)** e o **Gestor de Operações (Bruno)**, representando perspectivas complementares da mesma operação.

### Persona 1

&nbsp; **Carlos** representa o profissional responsável pela execução direta da dragagem, vivenciando no campo as limitações operacionais, os riscos físicos e os desafios associados à baixa visibilidade do processo.

<div align="center">
  <sub>Figura 1 - Descrição da persona Carlos</sub>
  <img src={useBaseUrl('/img/persona_carlos.png')} alt="Persona Carlos" width="100%" />
  <sup>Fonte: Material produzido pelos autores(2026)</sup>
</div>

&nbsp; Atuando diretamente no reservatório, ele depende de sua experiência prática, do comportamento da bomba e da leitura de corrente elétrica para avaliar a eficiência da dragagem, o que muitas vezes o obriga a se deslocar para reposicionar manualmente a balsa. Essa condição gera frustração, pois pode ser responsabilizado por falhas causadas por fatores que não consegue enxergar ou controlar. No seu cotidiano, acompanha a operação presencialmente e valoriza soluções que mantenham seu controle final sobre o processo, mas que ofereçam apoio à decisão e reduzam sua exposição ao risco e às intervenções emergenciais.

&nbsp; Assim, Carlos sintetiza as principais dores operacionais do campo, evidenciando a necessidade de maior previsibilidade, segurança e suporte à decisão durante a execução da dragagem.

### Persona 2

&nbsp; **Bruno** simboliza a perspectiva gerencial da operação, concentrando as demandas relacionadas ao acompanhamento remoto, à segurança e à tomada de decisão estratégica.

<div align="center">
  <sub>Figura 2 - Descrição da persona Bruno </sub>
  <img src={useBaseUrl('/img/persona_bruno.png')} alt="Persona Bruno" width="100%" />
  <sup>Fonte: Material produzido pelos autores (2026)</sup>
</div>

&nbsp; Como **gestor de operações**, ele não atua diretamente em campo, mas é responsável pela eficiência da dragagem, pela segurança dos equipamentos e pela relação com o cliente. Acompanha múltiplas operações simultaneamente, muitas vezes à distância, dependendo principalmente de relatos dos operadores, telefonemas e informações fragmentadas, o que gera insegurança e dificulta identificar em tempo hábil o uso inadequado dos equipamentos ou situações de risco. No seu cotidiano, sente falta de uma visão consolidada e em tempo real da operação, desejando um meio de monitorar status, regras de segurança e histórico de eventos, anomalias e movimentações da operação para apoiar decisões técnicas, orientar o operador e alinhar expectativas com o cliente quando surgem anomalias.

&nbsp; Dessa forma, a persona Bruno evidencia as demandas por monitoramento estruturado, maior confiabilidade das informações e suporte à tomada de decisão, aspectos também identificados como críticos durante a Imersão Preliminar.

&nbsp; Assim, as personas Carlos e Bruno derivam diretamente dos achados da **Imersão Preliminar**. No kick-off, identificou-se que a principal dor da dragagem está na movimentação manual da balsa, que gera esforço físico, riscos e incerteza operacional, fundamentando a construção de Carlos como operador diretamente impactado pelo processo. Da mesma forma, os impactos gerenciais observados, como paradas frequentes, baixa previsibilidade e dependência de comunicação informal, sustentam a definição de Bruno como representante da visão estratégica da operação.

&nbsp; Além disso, regras críticas estabelecidas com o parceiro, como o **intertravamento** que impede a movimentação com a bomba submersa, e o uso da **corrente elétrica** como fonte de informação para inferência operacional, reforçam que as personas são resultado de evidências concretas levantadas na imersão. 

&nbsp; Portanto, o projeto e as personas mantêm alinhamento entre **tecnologia, prática de campo e gestão**, assegurando que a solução responda às necessidades reais identificadas junto à Itubombas.

---

## Jornada do Usuário

&nbsp; Um mapa da jornada do usuário é uma representação estruturada que descreve as etapas, experiências, percepções e pontos de interação pelos quais uma pessoa passa ao utilizar um sistema, produto ou serviço. Ele permite compreender não apenas o fluxo de ações, mas também expectativas, emoções, dores e decisões ao longo do processo. Essa ferramenta é fundamental para alinhar o design da solução às necessidades reais dos usuários, identificar oportunidades de melhoria e garantir que a tecnologia desenvolvida realmente apoie suas atividades cotidianas de forma segura, eficiente e significativa <sup>[8](#c1)</sup>.

&nbsp; No contexto deste projeto, foram elaborados **dois mapas de jornada do usuário**, correspondentes às personas **Carlos**, operador de dragagem, e **Bruno**, gestor de operações. Ambas as jornadas consideram o cenário com a solução em funcionamento, mas a partir de perspectivas diferentes e complementares: Carlos vivencia a operação em campo, enquanto Bruno acompanha e gerencia o processo de forma remota. Assim, as jornadas permitem compreender como o mesmo sistema impacta simultaneamente a **execução técnica da dragagem e sua gestão operacional**.

### Jornada do Usuário - Persona 1

&nbsp; Conforme identificado na Imersão Preliminar, operadores como Carlos enfrentam desafios relacionados à necessidade de monitorar múltiplos parâmetros simultaneamente, interpretar sinais técnicos em tempo real e reagir rapidamente a variações de desempenho durante a dragagem <sup>[3](#c1)</sup>. A jornada apresentada na Figura X evidencia como o sistema proposto foi estruturado para apoiar sua atuação em campo, reduzindo incertezas operacionais e aumentando a segurança na execução das atividades.

<div align="center">
  <sub>Figura 3 - Jornada do Usuário Carlos</sub>
  <img src={useBaseUrl('/img/jornada_do_usuario_carlos.png')} alt="Jornada do Usuário Carlos" width="100%" />
  <sup>Fonte: Material produzido pelos autores (2026)</sup>
</div>

&nbsp; A jornada de **Carlos** descreve sua experiência direta durante a dragagem. Ele interage com o sistema para configurar o ambiente, acompanhar o desempenho da motobomba e responder a alertas de queda de eficiência baseados na leitura de corrente elétrica e profundidade. Quando necessário, valida a movimentação automática da balsa dentro do plano virtual do reservatório, sempre respeitando intertravamentos de segurança. Ao final, retoma a dragagem e avalia se o desempenho foi restabelecido. Sob a perspectiva da arquitetura proposta, Carlos interage com a **Interface do Operador**, enquanto o **Controle e Processamento Central** coordena os módulos de **Navegação e Dragagem** para executar a movimentação horizontal e vertical de forma integrada e segura.

&nbsp; Dessa forma, o mapeamento dessa experiência revela que a integração entre interface, processamento e módulos físicos não substitui o operador, mas potencializa sua capacidade de decisão ao reduzir desgastes físicos, aumentar a segurança operacional e garantir maior eficiência na execução da dragagem.

### Jornada do Usuário - Persona 2

&nbsp; Conforme identificado na Imersão Preliminar, gestores como Bruno enfrentam desafios relacionados à fragmentação das informações operacionais e à dificuldade de acompanhar, à distância, situações críticas em tempo hábil <sup>[3](#c1)</sup>. A jornada apresentada na Figura 4 evidencia como o sistema proposto foi concebido para mitigar essas dores no contexto real de uso.

<div align="center">
  <sub>Figura 4 - Jornada do Usuário Bruno</sub>
  <img src={useBaseUrl('/img/jornada_do_usuario_bruno.png')} alt="Jornada do Usuário Bruno" width="100%"  />
  <sup>Fonte: Material produzido pelos autores (2026)</sup>
</div>

&nbsp; A jornada de **Bruno** retrata o uso do sistema sob uma ótica gerencial e remota. Ele consulta o status geral da operação por meio de um dashboard de monitoramento, recurso identificado como necessidade crítica durante o kick-off técnico <sup>[3](#c1)</sup>, verifica estados críticos de segurança e acompanha indicadores simplificados para avaliar se tudo está sob controle. Em caso de alerta, analisa a situação pelo sistema e decide como agir, seja orientando o operador, acionando manutenção ou alinhando expectativas com o cliente. Na arquitetura proposta, sua interação ocorre principalmente por meio da **Interface do Operador**, que apresenta informações consolidadas pelo **Controle e Processamento Central**, incluindo telemetria de corrente elétrica proveniente do módulo de **Dragagem** e dados de posicionamento oriundos do módulo de **Navegação**.

&nbsp; Dessa forma, Bruno não atua diretamente sobre os módulos físicos do sistema, mas toma decisões fundamentadas a partir do fluxo estruturado de dados que percorre toda a arquitetura funcional. Essa integração entre interface, processamento e execução operacional, fundamentada nos achados da Imersão Preliminar <sup>[3](#c1)</sup>, reduz a dependência de comunicação ad hoc, melhora a rastreabilidade das decisões tomadas e permite que o gestor atue proativamente sobre anomalias sem necessidade de presença física no campo, garantindo que a gestão remota esteja alinhada à realidade operacional, reduzindo incertezas, fortalecendo a segurança e assegurando maior previsibilidade à operação de dragagem.

&nbsp; Conclui-se que as duas jornadas, como identificado na **imersão preliminar**, se complementam de forma estruturada dentro do mesmo ecossistema operacional. Enquanto **Carlos** configura o ambiente de dragagem, acompanha a corrente elétrica como indicador de eficiência, valida o reposicionamento da balsa e executa a operação com apoio dos intertravamentos de segurança, **Bruno** monitora remotamente os estados da balsa e da bomba, interpreta alertas operacionais e toma decisões estratégicas com base nos dados consolidados pelo sistema. Dessa interação, é possível garantir que a movimentação automática ocorra com segurança, que quedas de desempenho sejam tratadas rapidamente e que a operação mantenha continuidade sem depender exclusivamente de percepção empírica ou comunicação informal. Assim, o sistema **conecta a execução em campo à gestão remota**, tornando a dragagem mais previsível, segura, rastreável e alinhada às necessidades operacionais da Itubombas.

---

## Referências

[1] FARRELL, Susan. *UX Research Cheat Sheet*. Nielsen Norman Group, 2017. Disponível em: https://www.nngroup.com/articles/ux-research-cheat-sheet/. Acesso em: 4 fev. 2026.

[2] BRASIL. Ministério do Trabalho e Emprego. *NR-12: Segurança no Trabalho em Máquinas e Equipamentos*. Brasília, DF: MTE, 2022. Disponível em: https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/comissao-tripartite-partitaria-permanente/normas-regulamentadora/normas-regulamentadoras-vigentes/norma-regulamentadora-no-12-nr-12. Acesso em: 4 fev. 2026.

[3] ITUBOMBAS. *Relatório de Kick-off: requisitos e regras de negócio para automação*. Itu, SP, fev. 2026. Anotações de reunião. Participantes: Bruno Yokoya, Caio Sevilha e Sara Farencena.

[4] PUMP SCHOOL. *Understanding Slurry Pump Performance and Motor Amperage*. [S. l.], 2024. Disponível em: https://pumpschool.com. Acesso em: 4 fev. 2026.

[5] NAÇÕES UNIDAS BRASIL. *Objetivo de Desenvolvimento Sustentável 9: indústria, inovação e infraestrutura*. Brasília, DF, 2023. Disponível em: https://brasil.un.org/pt-br/sdgs/9. Acesso em: 4 fev. 2026.

[6] HARLEY, Aurora. *Personas: Heras Why and How You Should Use Them*. [S. l.]: Nielsen Norman Group, 16 jul. 2017. Disponível em: https://www.nngroup.com/articles/personas-study-guide/. Acesso em: 12 fev. 2026.

[7] GOTHELF, Jeff; SEIDEN, Josh. *Lean UX: Applying Lean Principles to Improve User Experience*. Sebastopol: O'Reilly Media, 2013.

[8] KAPLAN, Kate. *When and how to create customer journey maps*. [S. l.]: Nielsen Norman Group, 15 jan. 2016. Disponível em: https://www.nngroup.com/articles/customer-journey-mapping-101/. Acesso em: 12 fev. 2026.