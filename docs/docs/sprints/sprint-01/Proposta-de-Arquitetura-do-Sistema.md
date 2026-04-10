---
sidebar_label: "Proposta de Arquitetura"
sidebar_position: 2
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Proposta de Arquitetura do Sistema

&nbsp;Um diagrama de blocos é uma representação gráfica simplificada de um sistema que identifica suas principais funções e as interconexões entre essas funções, sem a necessidade de mostrar uma implementação detalhada. Segundo Sinclair (2011), os elementos visualizados em um diagrama de blocos são blocos retangulares que mostram sinais de entrada e sinais de saída para uma porção de um circuito, juntamente com um nome para o bloco. Todas as fontes de alimentação são ignoradas, assim como componentes individuais. O propósito de um diagrama de blocos é compreender rapidamente como um dispositivo funciona em termos de processamento de sinais, utilizando poucos tipos de símbolos e permitindo uma visão geral do sistema.

&nbsp;Este tipo de representação é particularmente útil para comunicar conceitos de sistemas a audiências diversas, incluindo stakeholders técnicos e não-técnicos, e para ilustrar documentos como planos de projeto e descrições de processos em fases iniciais de desenvolvimento.

---

## Visão Geral da Arquitetura

&nbsp;No contexto da proposta de solução para o sistema automatizado de dragagem com bomba submersível da Itubombas, este diagrama de blocos representa a concepção inicial da arquitetura funcional do sistema. O objetivo desta primeira versão é apresentar de forma clara e objetiva como a solução proposta se organiza para resolver o desafio operacional de movimentação automatizada do equipamento durante o processo de dragagem.

&nbsp;Atualmente, a Itubombas enfrenta dificuldades na operação de bombas submersíveis devido à falta de visibilidade do que ocorre abaixo do flutuador, exigindo intervenção manual frequente para reposicionar o equipamento conforme o acúmulo de sólidos ou a queda do nível do fluido. A solução proposta decompõe o sistema em quatro módulos principais que trabalham de forma integrada, permitindo visualizar o fluxo de informações desde a interface com o operador até a execução física da dragagem.

&nbsp;Esta representação em alto nível serve como base para discussões com a equipe da Itubombas sobre viabilidade, requisitos e próximos passos de desenvolvimento, sem ainda especificar tecnologias ou detalhes de implementação que serão definidos nas fases subsequentes do projeto.

&nbsp;

<div align="center">
  <sub>Figura 1 - Diagrama da Arquitetura do Sistema</sub>
  <img src={useBaseUrl('/img/diagrama-blocos-sprint1.drawio.png')} alt="Arquitetura do Sistema" width="100%" />
  <sup>Fonte: Material produzido pelos autores (2026)</sup>
</div>

&nbsp;

&nbsp;O diagrama apresenta quatro módulos principais que compõem a arquitetura proposta e seus fluxos de informação:

&nbsp;**Interface do Operador** é o ponto de contato entre o operador de campo e o sistema automatizado. Permite ao operador visualizar o estado da operação através de um dashboard, configurar parâmetros da área de dragagem e manter controle manual em situações de emergência, garantindo que a automação não elimine a capacidade de intervenção humana quando necessário.

&nbsp;**Controle e Processamento Central** atua como o núcleo de inteligência do sistema, responsável por planejar automaticamente as rotas de dragagem, gerenciar os diferentes estados da operação, analisar continuamente os dados dos sensores para tomada de decisão, implementar sistemas de segurança e manter registro das atividades para análise posterior.

&nbsp;**Navegação** é o módulo responsável pelo posicionamento e movimentação horizontal da balsa no reservatório, controlando propulsores para mover o equipamento entre os pontos de dragagem e garantindo que a operação respeite os limites geográficos definidos (geofencing).

&nbsp;**Dragagem** representa o módulo de execução do bombeamento, controlando o guincho e a bomba submersível. Utiliza sensores para monitorar profundidade e densidade do material bombeado, ajustando automaticamente a altura da bomba para manter eficiência operacional.

&nbsp;As setas bidirecionais entre os módulos representam a troca de informações necessária para operação coordenada: comandos fluem do topo para a base (operador → controle → atuadores), enquanto dados dos sensores retornam no sentido oposto (atuadores → controle → operador). A conexão lateral entre Navegação e Dragagem indica a necessidade de coordenação entre movimentos horizontais e verticais para operação segura.

&nbsp;Esta arquitetura em quatro módulos demonstra claramente como o sistema proposto atende aos objetivos principais do projeto: aumentar a autonomia operacional através do núcleo de Controle e Processamento Central, reduzir a necessidade de intervenção manual através dos módulos de Navegação e Dragagem automatizados, e manter a segurança operacional através do sistema de monitoramento e da possibilidade de controle manual via Interface do Operador. A representação modular facilita a identificação de pontos críticos que exigirão maior atenção no desenvolvimento, como a coordenação entre subsistemas, a confiabilidade do sistema de análise de sensores e a robustez dos mecanismos de segurança.

---

## Requisitos Funcionais

Os Requisitos Funcionais (RF) descrevem o comportamento esperado do sistema, ou seja, especificam **o que** o sistema deve fazer para atender às necessidades operacionais. Eles definem as entradas, os processamentos e as saídas necessárias para que a balsa realize a dragagem com eficiência e segurança.

No contexto deste projeto, os requisitos foram estruturados para cobrir três pilares principais: a **navegação assistida** (controle do operador com proteções de software), a **automação do processo de dragagem** (controle inteligente do guincho baseado na carga de lodo) e a **segurança operacional** (intertravamentos que impedem erros humanos e falhas mecânicas). A lista a seguir detalha cada uma dessas funções.
&nbsp;

| **ID** | **Requisito** | **Descrição** |
| --- | --- | --- |
| RF-01 | Planejamento de Rota | O sistema deve calcular automaticamente uma rota de varredura em grade (ziguezague) baseada nas dimensões da área inseridas. |
| RF-02 | Controle Remoto de Navegação | O sistema deve permitir o controle direto dos propulsores pelo operador. |
| RF-03 | Geofencing | O sistema deve impedir via software que a balsa ultrapasse os limites geográficos do tanque. |
| RF-04 | Posicionamento Inicial | O sistema deve descer a bomba até detectar proximidade do fundo/água para iniciar a operação. |
| RF-05 | Leitura de Carga | O sistema deve ler a corrente elétrica da bomba para inferir a densidade do material (água vs. lodo). |
| RF-06 | Controle Adaptativo de Guincho | Ajustar a altura da bomba baseado na corrente: descer se baixa (água), parar se alta (lodo), subir se crítica. |
| RF-07 | Critério de Ponto Limpo | Determinar o fim da dragagem no ponto quando atingir profundidade máxima com corrente baixa. |
| RF-08 | Ciclo de Transição | Ao limpar o ponto, desligar bomba, recolher guincho e mover para o próximo alvo automaticamente. |
| RF-09 | Intertravamento de Movimento | Bloquear acionamento dos propulsores se a bomba não estiver desligada e recolhida. |
| RF-10 | Dashboard Operacional | Exibir mapa, profundidade, corrente e status em tempo real para o operador. |

&nbsp;


A definição destes requisitos estabelece um escopo claro para o desenvolvimento do firmware e da eletrônica embarcada. Ao priorizar a automação do eixo vertical (profundidade e carga da bomba) e manter a navegação sob controle manual do operador, o sistema garante a máxima eficiência na remoção de sedimentos sem abrir mão da flexibilidade de manobra.

O cumprimento integral destes itens assegura que o equipamento não apenas remova o lodo de forma otimizada (evitando o bombeamento excessivo de água), mas também proteja a integridade física da bomba e da balsa através dos mecanismos de intertravamento e geofencing.

---

## Requisitos Não Funcionais

&emsp;Esta seção descreve os requisitos não funcionais do sistema. Diferentemente dos requisitos funcionais, que definem o que o sistema deve fazer, os não funcionais
estabelecem como sistema deve se comportar em termos de confiabilidade, segurança, robustez, usabilidade e operação.
O objetivo é garantir que a solução proposta não seja apenas funcional, mas também segura e adequada ao uso em ambiente de campo, atendendo as expectativas do parceiro.

&nbsp;

| ID | Requisito | Descrição | Como será atendido pela arquitetura |
|----|-----------|-----------|-------------------------------------|
| RNF01 |Confiabilidade | O sistema não deve apresentar travamentos ou falhas de software durante um ciclo completo de teste, desde que usado conforme especificado| Lógica de controle implementada em módulo embarcado dedicado com tratamento de erros básicos|
| RNF02 |Desempenho de atualização | Os dados exibidos no dashboard (estado da bomba, posição, corrente…) devem ser atualizados em intervalos regulares, com um atraso mínimo entre o evento de campo e visualização| Comunicação periódica entre da balsa e dashboard, com envio de pacotes em intervalo fixo e atualização imediata na interface|
| RNF03 | Robustez | O sistema deve conseguir permanecer em operação contínua em testes de campo sem necessidade reinicialização manual| Execução contínua do software embarcado em loop estável, com uma reinicialização apenas para o módulo de controle em caso de falha|
| RNF04 | Segurança| Em qualquer conflito entre comandos do operador e regras de segurança, o sistema deve sempre priorizar a condição segura| Regras de segurança e intertravamento implementadas no controlador local, que valida condições antes de obedecer qualquer comando do operador|
| RNF05 |Integridade de dados |O sistema deve garantir que sinais críticos (ex:estado da bomba) não sejam alterados por ruídos, utilizando uma validação básica de sinais | Aplicação de filtros e validações de consistência nos sinais críticos antes de usá-los na lógica de controle ou exibi-los no dashboard|
| RNF06 |Registro de eventos | O sistema deve registrar eventos relevantes (comandos de movimento, erros) marcados pelo tempo em que ocorreu, para análise posterior da equipe de operação| Módulo de log no software que grava eventos importantes em memória local ou arquivo, incluindo timestamp e tipo de evento|
| RNF07 |Clareza de interface  | O dashboard deve apresentar de forma clara se a balsa está “Liberada para mover” ou “Bloqueada por segurança”, evitando má ou ambíguas interpretações pelo operador| Comunicação periódica entre da balsa e dashboard, com envio de pacotes em intervalo fixo e atualização imediata na interDashboard com elementos visuais dedicados (ex: indicador grande de Liberada/Bloqueada) e cores/ícones padronizados para estados de segurança, em uma linguagem simples e intuitiva para o operador|
| RNF08 | Simplicidade Operacional  | As funcionalidades essenciais do sistema no dashboard, devem ser acessíveis em poucos passos, sem exigir navegação complexa| Organização das telas do dashboard priorizando as ações principais em uma tela inicial, com poucos botões e navegação rasa|
| RNF09 | Configurabilidade| Parâmetros operacionais básicos (limites de área, limites de corrente, profundidade máxima) devem ser configuráveis sem necessidade de alterar o código fonte| Tela ou arquivo de configuração onde limites de área, corrente e profundidade são parametrizados e lidos pelo sistema via interface|
| RNF10 |Documentação|Produção de um documento completo (disponível pelo Docssauros) descrevendo estados, fluxos principais e telas, mantido junto ao repositório do projeto|

&nbsp;

&emsp;Os requisitos não funcionais servirão como referência durante o desenho da arquitetura, implementação e testes, garantindo que o protótipo desenvolvido se adeque ao contexto real de uso da Itubombas.

---

## Referências

<!-- Liste aqui as fontes e referências utilizadas na elaboração deste documento -->

SINCLAIR, I. Electronics Simplified. 3rd ed. Oxford: Newnes, 2011. Disponível em: https://www.sciencedirect.com/book/9780080970639/electronics-simplified. Acesso em: 10 fev. 2026.

