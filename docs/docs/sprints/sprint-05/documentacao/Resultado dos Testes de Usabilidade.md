---
sidebar_label: "Resultado dos Testes de Usabilidade"
sidebar_position: 4
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Resultados dos Testes de Usabilidade

---

## 1. Contexto Geral

Na Sprint 4, foi definida a estratégia de testes funcionais e não funcionais, incluindo a elaboração dos casos de teste e o planejamento da execução.

Os participantes foram selecionados para validar fluxos de interação em ambiente controlado, sem exigência de correspondência às personas reais do sistema — abordagem adequada para identificar problemas de interface antes do acesso ao público final.

Os registros completos dos testes podem ser acessados na planilha:

[Planilha de Registros de Testes](https://docs.google.com/spreadsheets/d/1aDvr1urazaIDQAINt3JYcrPZst3YYCE91nwBn6bdL5Q/edit?usp=sharing)

---

## 2. Preparação do Ambiente de Testes

Para a execução dos testes de usabilidade, o ambiente foi organizado de forma a simular a operação real do sistema.

Foram utilizados três notebooks, distribuídos da seguinte forma:

- Notebook 1: módulos **1A e 1B** com **dashboard do operador**
- Notebook 2: módulos **2A, 2B e 2C** com **dashboard do operador**
- Notebook 3: **dashboard do gestor**

A equipe foi dividida em papéis fixos durante toda a execução, garantindo padronização na coleta:

- Um integrante responsável por **contextualizar o projeto** para o usuário, sempre com o mesmo roteiro para não influenciar o comportamento dos participantes
- Um integrante responsável por **oferecer dicas padronizadas**, apenas quando necessário
- Um integrante responsável por **registrar fotos** do processo
- Quatro integrantes responsáveis por **anotar resultados e comportamentos observados** na planilha
---

## 3. Execução dos Testes

Os testes foram realizados em duas rodadas, separadas por um ciclo de implementação, com grupos de participantes distintos em cada etapa.

### 3.1 Primeira rodada de testes

Realizada em **01/04/2026** com 3 usuárias: Júlia Sales, Beatriz Queiroz e Raissa Guimarães.

Os fluxos principais do operador (abertura dos modais de Movimentação XY e Motor Z, envio de comandos e leitura de corrente) foram executados com sucesso, ainda que com dificuldades pontuais de navegação e ausência de feedback visual após os comandos

Os seguintes testes não puderam ser executados por funcionalidades ainda não disponíveis:

- **Teste 06** – Bloqueio de movimentação XY com bomba fora da origem
- **Teste 08** – Parada de emergência automática por sensor crítico
- **Teste 09** – Tempo de atualização de dados no dashboard
- **Teste 10** – Bloqueio e parada em condição insegura

### 3.2 Evolução do sistema

Entre as duas rodadas foram implementadas as funcionalidades pendentes: bloqueio de movimentação XY com bomba fora da origem **(Teste 06)**, parada automática por sensor crítico **(Teste 08)**, atualização de dados em tempo real **(Teste 09)** e bloqueio em condição insegura **(Teste 10)**. Foram realizados também ajustes pontuais de layout e nomenclatura.


### 3.3 Segunda rodada de testes

Realizada em **08/04/2026** com 3 novos usuários: Rafael Gomes, Rafael Klippel e Guilherme Hassen. Com as funcionalidades de segurança implementadas, todos os testes puderam ser executados.

Os fluxos do operador que já haviam passado na primeira rodada se mantiveram estáveis: Testes 01, 02, 03 e 05 foram concluídos com sucesso pela maioria dos participantes. Os Testes 06, 08 e 10 (que haviam falhado integralmente na primeira rodada por estarem pendentes de implementação) passaram para todos os 3 usuários da segunda rodada, representando a evolução mais significativa entre os ciclos. O Teste 09, também antes pendente, passou para dois dos três usuários dentro do critério de 3 segundos, com comportamento ainda inconsistente para um deles.

## 4. Registros dos Testes

Abaixo estão alguns registros do processo de execução dos testes:

<p style={{textAlign: 'center'}}>Figura 1 - Usuária Julia</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/usuaria_julia.jpeg").default} style={{width: 800}} alt="Usuária Julia" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>


<p style={{textAlign: 'center'}}>Figura 2 - Usuária Beatriz</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/usuaria_beatriz.jpeg").default} style={{width: 800}} alt="Usuária Beatriz" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>


<p style={{textAlign: 'center'}}>Figura 3 - Usuária Raissa</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/usuaria_raissa.jpeg").default} style={{width: 800}} alt="Usuária Raissa" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

---

## 5. Síntese dos Resultados

De forma geral, o sistema evoluiu significativamente entre as rodadas. As funcionalidades de segurança implementadas entre os ciclos (Testes 06, 08 e 10) foram todas validadas com sucesso na segunda rodada. Os problemas que persistem concentram-se em ajustes de interface que afetam a clareza da operação cotidiana e a rastreabilidade de eventos para o gestor.
 
#### Ausência de feedback após comandos — Testes 02 e 04
Nas duas rodadas, após enviar um comando de movimentação XY ou Z, a interface não exibiu nenhuma confirmação visual. Os usuários não sabiam se o comando havia sido recebido ou executado — nas duas rodadas, todos os participantes que comentaram sobre esses testes apontaram a ausência de retorno. No Teste 04, Beatriz Queiroz (rodada 1) não conseguiu concluir a tarefa por não receber mensagem de sucesso; Rafael Klippel (rodada 2) tentou subir 20 cm sem ter descido nada e o sistema não bloqueou a ação.
 
#### Nomenclatura "Motor Z" pouco reconhecível — Teste 03
Na primeira rodada, Júlia Sales não sabia o que era o eixo Z e Beatriz Queiroz apontou que o texto estava escrito muito pequeno. Na segunda rodada, Rafael Klippel relatou demora no carregamento dos botões internos do modal, embora Guilherme Hassen tenha achado o ícone e o texto claros. A legibilidade melhorou para parte dos usuários, mas o problema não foi eliminado completamente.
 
#### Painel de sensores fora do fluxo esperado — Teste 07
Em ambas as rodadas, parte dos usuários procurou o painel de sensores dentro do card da bomba. Na segunda rodada, Rafael Gomes e Guilherme Hassen relataram explicitamente que só encontraram o painel depois de procurar no menu lateral. A separação entre o card da bomba e o painel de sensores não é percebida de forma intuitiva.
 
#### Estado de segurança ambíguo no dashboard — Teste 11
Na primeira rodada, 2 usuários falharam ou não obtiveram efeito. Na segunda rodada, Rafael Gomes conseguiu identificar o estado pelo indicador, mas Rafael Klippel e Guilherme Hassen acharam ambíguo distinguir se o sistema estava travado ou apenas lento. O problema persiste para a maioria dos participantes.
 
#### Rótulo "Detalhar" no lugar de "Histórico" — Teste 01 do Gestor
Na primeira rodada, Júlia Sales não conseguiu concluir a tarefa pela divergência de nomenclatura. Na segunda rodada, Rafael Klippel não conseguiu por procurar por "Logs" ou "Histórico", e Rafael Gomes e Guilherme Hassen conseguiram apenas com dificuldade, demorando a associar "Detalhar" ao histórico. O problema afetou 5 dos 6 participantes.
 
#### Logs sem descrição suficiente para associação temporal — Teste 02 do Gestor
Nenhum dos 6 participantes — nas duas rodadas — conseguiu identificar qual log correspondia a qual ação executada. Na segunda rodada, os comentários foram explícitos: "Gerou dúvida sobre qual ação correspondia a qual log" (Rafael Klippel e Guilherme Hassen). O teste falhou para todos os 6 usuários.

---

## 6. Análise com gráficos

### Gráfico 1 — Evolução geral entre rodadas

<p style={{textAlign: 'center'}}>Figura 4 - Gráfico 1</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/grafico1.png").default} style={{width: 800}} alt="Gráfico 1" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

 
O gráfico apresenta a distribuição de resultados por teste nas duas rodadas. A proporção de sucessos mais que dobrou entre os ciclos — de 30% para 61% — reflexo direto da implementação das funcionalidades de segurança, que transformaram testes que antes falhavam integralmente em aprovações unânimes na segunda rodada.


### Gráfico 2 — Testes de segurança: antes e depois das correções

<p style={{textAlign: 'center'}}>Figura 5 - Gráfico 2</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/grafico2.png").default} style={{width: 800}} alt="Gráfico 2" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>


O gráfico detalha os quatro testes que estavam pendentes de implementação na primeira rodada. Em T06, T08 e T10, a mudança foi total: de falha unânime a aprovação por todos os participantes. T09 apresentou melhora significativa, mas com resultado heterogêneo — dois usuários dentro do critério de 3 segundos e um acima de 5 s, indicando que a correção funcionou mas ainda não é estável.

---

## 7.  Problemas Priorizados para Correção

#### Prioridade alta

**Testes 02 e 04 – Ausência de feedback de confirmação**
O operador executa um comando e a interface não retorna nenhuma informação sobre o que aconteceu. Em um contexto de operação remota de equipamento físico, isso pode levar a duplos comandos acidentais ou à suposição incorreta de que o sistema travou. O problema foi apontado nas duas rodadas, por todos os usuários que comentaram sobre esses testes. No Teste 04, a ausência de feedback impediu que um usuário concluísse a tarefa na primeira rodada.

**Teste 11 – Estado de segurança ambíguo**
Quando o sistema está em bloqueio, o operador precisa saber disso de forma inequívoca. A confusão entre "sistema travado" e "sistema lento" foi identificada em 2 dos 3 participantes da segunda rodada, indicando que o indicador atual ainda não é suficiente.

**Teste 02 do Gestor – Logs ilegíveis para auditoria**
O histórico existe, mas nenhum dos 6 gestores conseguiu associar cada entrada a uma ação específica. Sem essa associação, o registro perde o valor de rastreabilidade para o qual foi construído. É o único problema que afetou 6 de 6 participantes sem nenhuma variação entre as rodadas.

#### Prioridade média

**Teste 09 – Latência de atualização parcialmente resolvida**
A atualização passou a ocorrer dentro do critério de 3 s para a maioria dos casos, mas o comportamento ainda é inconsistente — Rafael Klippel registrou tempo acima de 5 s na mesma sessão em que os outros dois não tiveram problema. Vale notar que os diferentes dados do dashboard possuem intervalos de polling distintos: leituras de corrente e heartbeat atualizam a cada 3 s, enquanto os sensores de proximidade atualizam a cada 5 s, o que pode explicar a variação observada.

#### Prioridade baixa

**Teste 01 do Gestor – Rótulo "Detalhar"**
Renomear para "Histórico" ou "Ver logs" resolve o problema sem custo de desenvolvimento relevante. Afetou 5 dos 6 participantes.

**Teste 03 – Visibilidade do botão "Motor Z"**
Aumento de tamanho e contraste do texto resolve a dificuldade de leitura apontada nas duas rodadas.

**Teste 07 – Localização do painel de sensores**
Mover ou replicar o acesso dentro do card da bomba, onde os usuários naturalmente procuram.

---

## 8. Conclusão

A evolução entre as rodadas foi expressiva. As três funcionalidades de segurança que estavam pendentes na primeira rodada (bloqueio de movimentação XY com bomba fora da origem, parada automática por sensor crítico e bloqueio em condição insegura) foram implementadas e validadas com sucesso por todos os participantes da segunda rodada. O Teste 09 também passou para a maioria dos usuários dentro do critério de 3 segundos, com apenas um caso fora do esperado.
 
Os problemas que persistem ao final das duas rodadas são de natureza diferente: ausência de feedback visual após comandos, ambiguidade no estado de segurança do dashboard e dificuldade do gestor em interpretar e navegar os logs. São problemas de interface e usabilidade, não de segurança operacional, e representam o foco de melhoria para planos futuros.
 
Os testes de usabilidade realizados nas duas rodadas cumpriram seu papel: os fluxos principais do operador foram validados e funcionaram de forma consistente, e os problemas identificados foram documentados e priorizados para orientar os próximos passos do projeto.