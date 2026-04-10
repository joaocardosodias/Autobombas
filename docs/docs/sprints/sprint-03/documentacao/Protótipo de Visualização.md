---
sidebar_label: "Protótipo de Visualização"
sidebar_position: 2
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Documentação do Protótipo de Alta Fidelidade — AutoBombas
---

## 1. Visão Geral

O presente protótipo de alta fidelidade representa a evolução da interface do sistema **AutoBombas** de uma interação baseada em linha de comando (CLI) para uma Interface Gráfica do Usuário (GUI) completa e orientada à operação industrial.

Anteriormente, o controle das bombas de dragagem e a leitura dos dados de telemetria — como profundidade, amperagem, temperatura e movimentação — eram realizados de forma direta via terminais de comando ou acesso bruto a painéis físicos, sem visualização consolidada ou registro estruturado das sessões. Isso impunha alta carga cognitiva ao operador em campo e dificultava a supervisão remota por parte do gestor de operações.

Para solucionar essas limitações, foi desenvolvido um **Mockup de Alta Fidelidade** no Figma com os seguintes objetivos:

- **Validar a usabilidade** dos fluxos de controle antes da codificação, evitando retrabalho de desenvolvimento;
- **Abstrair a complexidade técnica** dos módulos de hardware em componentes visuais intuitivos (medidores, botões direcionais, indicadores de câmera);
- **Reduzir a carga cognitiva** do operador em campo, centralizando câmeras ao vivo, controles de profundidade, amperagem e direção em uma única tela;
- **Separar responsabilidades** entre dois perfis distintos — Operador (controle em tempo real) e Gestor (supervisão e análise histórica) — com interfaces dedicadas a cada função;
- **Simular o comportamento dinâmico** dos dados de telemetria (atualização em tempo real via WebSocket) por meio de estados visuais e valores representativos nos componentes do protótipo.

Os dados de telemetria e controle foram abstraídos da seguinte forma na interface visual:

| Dado de Hardware | Abstração Visual na GUI |
|---|---|
| Leitura do sensor de pressão | Indicador de profundidade com barra vertical e valor em metros |
| Consumo de corrente elétrica (A) | Medidor analógico semicircular com zonas de cor (verde/amarelo/vermelho) |
| Feed das câmeras embarcadas | Cards de câmera com status REC/ONLINE e visualização ao vivo |
| Comandos de movimentação XY | Grid de botões direcionais com parada central |
| Status dos sensores e componentes | Painel lateral deslizante com badges coloridos por dispositivo |
| Registro de alertas por sessão | Histórico cronológico com nível de severidade (Normal/Atenção/Crítico) |

---

## 2. Decisões de Projeto (UX/UI)

### 2.1 Identidade Visual

A identidade visual da plataforma foi construída sobre uma paleta que equilibra **legibilidade em ambientes industriais** com a identidade de marca da Itubombas:

- **Verde Escuro (#1A4731):** Cor primária da marca, usada na sidebar, botões de ação principal e cabeçalhos de tabela. Transmite solidez e confiança — fundamental em contextos de operação crítica.
- **Âmbar (#F59E0B):** Reservado exclusivamente para estados de **atenção** — alertas intermediários, profundidade em nível médio, botão de pausa. A escolha do âmbar (e não do amarelo puro) melhora o contraste em telas com luz solar direta.
- **Vermelho (#EF4444):** Usado apenas para **estados críticos** — alertas de sobrecarga elétrica e falhas de sensor. A escassez do vermelho na interface garante que sua aparição seja imediatamente percebida pelo operador.
- **Verde Operacional (#16A34A):** Diferenciado do verde primário, indica estados positivos: sensor "Operante", câmera "Ativo", sistema "Conectado". A distinção entre os dois verdes é perceptível tanto em telas calibradas quanto em ambientes externos.
- **Cinza Claro (#F3F4F6):** Fundo das telas principais, reduz o cansaço visual em operações prolongadas.

A tipografia adota **Arial** em toda a interface — uma escolha pragmática que prioriza legibilidade universal, carregamento rápido e ausência de dependência de fontes externas em ambientes com conectividade limitada.

### 2.2 Hierarquia da Informação

A hierarquia visual foi desenhada para que o operador capture o estado crítico do sistema em menos de 3 segundos:

1. **Nível 1 — Status Global:** Badge "Conectado / Sistema" no canto superior direito e "Sistema Operacional / 12 sensores ativos" no rodapé da sidebar — visíveis em qualquer tela.
2. **Nível 2 — Dados Operacionais Ativos:** Câmeras ao vivo (maior área da tela) e os três painéis de controle (profundidade, amperagem, direção) ocupam a maior parte do viewport do operador.
3. **Nível 3 — Dados de Contexto:** Informações de sessão (data, operador, duração) em cards menores no topo da tela do gestor.
4. **Nível 4 — Histórico e Auditoria:** Tabelas de sessão e alertas, acessíveis por navegação secundária.

### 2.3 Componentização

O design system foi construído com componentes consistentes e reutilizáveis:

- **Cards de sensor:** Padrão uniforme com ícone de tipo, nome, categoria, badge de status e valor — aplicado tanto no modal do operador quanto na tela do gestor.
- **Badges de status:** Componente único com variantes de cor (verde/âmbar/vermelho) e texto parametrizável — elimina ambiguidade de interpretação.
- **Botões de controle circular:** Usados nos controles de profundidade e direção com estados normal, ativo (âmbar) e desabilitado — feedback tátil simulado visualmente.
- **Medidor analógico:** Componente de amperagem com ponteiro, escala numérica e gradiente de cor — mais intuitivo que um número isolado para operadores sem formação técnica formal.
- **Linha do tempo de fases:** Componente exclusivo da tela do gestor que representa graficamente a distribuição temporal das fases operacionais de cada sessão.

### 2.4 Comportamento Dinâmico e Tempo Real

O protótipo simula o comportamento de dados em tempo real (via WebSocket na implementação final) por meio das seguintes decisões de design:

- **Timestamp atualizado no cabeçalho:** Hora e data visíveis em todas as telas reforçam a expectativa de atualização contínua.
- **Badge "REC" na Câmera 1:** Indica gravação ativa, sinalizando ao operador que os dados estão sendo capturados em tempo real.
- **"Última atualização: agora"** no rodapé do painel de sensores: Comunica a latência esperada da sincronização de dados.
- **Valores representativos nos controles:** Profundidade em 6.0m, amperagem em 12.5A de 30A máximo — valores que contextualizam a escala real do equipamento para validação com stakeholders.
- **Estado "Em Andamento"** na tabela de sessões: Demonstra o comportamento de sessões ativas sendo exibidas ao lado de sessões históricas, validando o modelo de dados em tempo real do gestor.

---

## 3. Telas e Funcionalidades do Protótipo

### 3.1 Tela de Login

A tela de autenticação é o ponto de entrada único da plataforma, compartilhada pelos dois perfis de usuário (Operador e Gestor). O redirecionamento pós-login ocorre com base no perfil associado às credenciais.

**Estrutura da tela:**

- **Painel esquerdo (~60%):** Foto da fachada da empresa Itubombas com overlay verde escuro. Exibe o headline da plataforma, três propostas de valor em bullets e métricas institucionais. Link "Saiba mais sobre a plataforma →" para informações adicionais.
- **Painel direito (~40%):** Fundo verde escuro sólido com logotipo animado do AutoBombas (ícone de bomba com seta de crescimento e moedas), saudação "Bem-vindo de volta" e formulário de acesso.

**Componentes do formulário:**

| Campo | Tipo | Detalhe |
|---|---|---|
| E-mail | Input text | Placeholder: `seu@email.com`, ícone de envelope |
| Senha | Input password | Placeholder: `Digite sua senha`, ícone de cadeado, toggle de visibilidade |
| Entrar na plataforma | Button primário | Verde sólido, largura total, ícone de entrada |

**Métricas institucionais no rodapé esquerdo:**

- `+500` Empresas atendidas
- `99.9%` Disponibilidade
- `24/7` Suporte dedicado

<p style={{textAlign: 'center'}}>Figura 1 - Tela de Login</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={useBaseUrl('/img/LOGIN.png')} style={{width: '100%', maxWidth: 800}} alt="Tela de Login" />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

---

### 3.2 Tela Principal — Dashboard de Controle (Perfil Operador)

A tela principal do operador é o núcleo operacional da plataforma. Foi desenhada para centralizar em uma única tela todas as informações e controles necessários para operar a bomba de dragagem em campo, eliminando a necessidade de alternar entre terminais ou painéis físicos.

**Relação dos elementos com o hardware:**

| Elemento na GUI | Módulo de Hardware Correspondente |
|---|---|
| Cards de câmera (Câmera 1–4) | Câmeras embarcadas na bomba: Visão Frontal, Lateral Esq., Lateral Dir. e Inferior |
| Controle de Profundidade (0–20m) | Sensor de pressão hidrostática + atuador de descida/subida da bomba |
| Medidor de Amperagem (0–30A) | Sensor de corrente elétrica do motor principal (ITB-DRG-2024-001) |
| Botões direcionais (↑←⏹→↓) | Módulo de movimentação XY da bomba (controle horizontal) |
| Botão de pausa central (⏸) | Parada de emergência do sistema de movimentação |
| Indicador "Sistema Operacional / 12 sensores ativos" | Agregação do status de todos os dispositivos IoT conectados |

**Seção 1 — Monitoramento de Câmeras:**

Grid de 4 câmeras em tempo real. A Câmera 1 (Visão Frontal) exibe badge "REC" em vermelho, indicando gravação ativa. As demais exibem "ONLINE" em verde. Cada card tem botão de expansão (↗) para visualização em tela cheia. Indicador global "4 câmeras ativas" no canto superior direito da seção.

**Seção 2 — Painel de Controle (3 cards lado a lado):**

- **Controle de Profundidade:** Barra vertical de escala 0–20m com marcador amarelo na posição atual (6.0m). Botões ▲/⏸/▼ para ajuste fino. Status "Profundidade atual — Médio" indica zona operacional intermediária.
- **Amperagem:** Medidor analógico semicircular com gradiente verde → âmbar → vermelho. Ponteiro em 12.5A (de 30A máximo) — zona verde. Status "Normal" exibido abaixo.
- **Controle Direcional:** Grid 3×3 de botões com ícones de seta e botão de parada central (⏹) destacado em âmbar. Label "Pressione para mover" orienta a interação.

**Gatilhos visuais de alerta:**

- Amperagem acima de 24A (80%): medidor entra na zona âmbar
- Amperagem acima de 28.5A (95%): medidor entra na zona vermelha
- Profundidade acima de 18m: indicador deve mudar para status "Alto"
- Câmera offline: badge passa de "ONLINE" para "OFFLINE" em vermelho

<p style={{textAlign: 'center'}}>Figura 2 - Dashboard de Controle (Perfil Operador)</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={useBaseUrl('/img/OperadorDash.png')} style={{width: '100%', maxWidth: 800}} alt="Dashboard do Operador" />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

---

### 3.3 Painel de Sensores — Modal Deslizante (Perfil Operador)

Acessado pelo menu lateral ("Sensores →"), o painel de sensores é um **modal deslizante lateral** que aparece sobreposto ao dashboard sem interromper o contexto visual da tela principal (fundo com blur sutil). Lista todos os 12 dispositivos monitorados com status individual em tempo real.

**Relação com o hardware:**

| Sensor / Componente | Tipo de Medição | Hardware Real |
|---|---|---|
| Sensor de Profundidade | Pressão hidrostática | 6.2m atual |
| Sensor de Temperatura | Térmica (motor) | 28°C atual |
| Câmera Frontal | Vídeo | 1080p — Operante |
| Câmera Lateral Esq. | Vídeo | 1080p — Operante |
| Câmera Lateral Dir. | Vídeo | 720p — **Atenção** (degradação de qualidade) |
| Câmera Inferior | Vídeo | 1080p — Operante |
| + 6 sensores adicionais | — | Status variado |

O único componente em estado "Atenção" é a **Câmera Lateral Dir.**, operando em resolução reduzida (720p vs. 1080p esperado) — o que exemplifica como degradações sutis de hardware são comunicadas visualmente ao operador sem interromper a operação.

**Resumo de status (topo do modal):**

- `11` Online (verde)
- `1` Atenção (âmbar)
- `0` Offline (vermelho)

<p style={{textAlign: 'center'}}>Figura 3 - Painel de Sensores e Componentes (Modal Lateral)</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={useBaseUrl('/img/OperadorSensores.png')} style={{width: '100%', maxWidth: 800}} alt="Tela de Sensores(Operador)" />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

---

### 3.4 Sobre o Sistema (Perfil Operador)

Tela de referência técnica e tutorial inline. Serve como **manual integrado** à plataforma, eliminando a necessidade de documentos externos em campo. Estruturada em quatro blocos sequenciais:

**Bloco 1 — Identificação do Equipamento:**
Dados técnicos do equipamento associado à sessão atual:

- ID: `ITB-DRG-2024-001` | Status: **Operacional**
- Modelo: Itubombas DRG-500X | Firmware: v3.2.1
- Capacidade: 500 m³/h | Profundidade máx.: 20m | Potência: 75 kW / 380V / 60Hz

**Bloco 2 — Funcionalidades do Sistema:**
Grid de 6 cards descrevendo as capacidades da plataforma: Monitoramento em Tempo Real, Controle de Profundidade, Movimentação Direcional, Monitoramento Elétrico, Sensores Térmicos e Sensor de Vazão.

**Bloco 3 — Tutoriais de Utilização:**
Accordions expansíveis com passo a passo para as funções principais:
- *Controles de Movimentação* (3 passos)
- *Painel de Sensores* (3 passos)
- *Medidor de Amperagem* (3 passos)

**Bloco 4 — Avisos de Segurança:**
Card com fundo âmbar claro listando 4 regras críticas de operação segura. Destaque visual garante que o operador veja antes de iniciar.

<p style={{textAlign: 'center'}}>Figura 4 - Tela Sobre o Sistema (Perfil Operador)</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={useBaseUrl('/img/OperadorTutorial.png')} style={{width: '100%', maxWidth: 800}} alt="Tela de Tutorial(Operador)" />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

---

### 3.5 Tela Secundária — Gestão de Sessões / Dashboard do Gestor

A tela principal do gestor é voltada à **supervisão e auditoria** das operações. Diferente do dashboard do operador — que é reativo e em tempo real — esta tela é analítica e orientada a histórico.

**Funcionalidades:**

- **Filtros em linha:** 3 dropdowns para filtrar por data, operador e status da sessão.
- **Tabela de sessões:** Listagem paginada com colunas Sessão, Início, Fim, Operador, Status e botão "Detalhar".
- **Paginação:** Exibindo 1–5 de 8 sessões | Controles Anterior / 1 / 2 / Próximo.

**Estados de sessão e seus significados:**

| Status | Cor | Situação |
|---|---|---|
| Finalizada | Cinza neutro | Operação concluída normalmente |
| Em Andamento | Âmbar | Sessão ativa no momento da consulta |
| Alerta | Vermelho claro | Sessão com ocorrências críticas registradas |

A coexistência de sessões "Em Andamento" e históricas na mesma tabela valida o modelo de dados híbrido (tempo real + histórico) da plataforma.

<p style={{textAlign: 'center'}}>Figura 5 - Dashboard de Gestão de Sessões (Perfil Gestor)</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={useBaseUrl('/img/GestorDash.png')} style={{width: '100%', maxWidth: 800}} alt="Dashboard do Gestor" />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

---

### 3.6 Detalhes da Sessão — Histórico e Logs (Perfil Gestor)

Acessada pelo botão "Detalhar" em cada linha da tabela, esta tela é o módulo de **auditoria detalhada** de uma sessão específica. Corresponde à tela de "Históricos e Logs" do modelo de documentação.

**Metadados da sessão (cards no topo):**

| Data | Operador | Duração | Status |
|---|---|---|---|
| 09/03/2026 | Carlos Silva | 4h 30min | Finalizada |

**Histórico de Alertas (log de eventos):**

Tabela cronológica com todos os alertas disparados durante a sessão, funcionando como **log de auditoria** da operação:

| Horário | Sensor | Valor | Nível de Alerta |
|---|---|---|---|
| 08:12 | Movimento XY | 80% | Atenção |
| 08:18 | Corrente | 92% | **Crítico** |
| 09:45 | Profundidade | 75% | Normal |
| 10:30 | Temperatura | 88% | Atenção |

O botão "Filtrar" permite ao gestor segmentar os alertas por nível de severidade — útil para relatórios de manutenção e análise de incidentes.

**Fases da Operação (análise de produtividade):**

Visualização gráfica da distribuição de tempo entre as fases da operação — dado estratégico para o gestor avaliar eficiência operacional:

| Fase | % do Tempo | Interpretação |
|---|---|---|
| Buscando | 25% | Posicionamento da bomba |
| Intermediário | 45% | Maior parte — ajustes e transições |
| Dragando | 30% | Extração efetiva de sedimentos |

A **Linha do Tempo Completa** (barra horizontal colorida de 08:00 às 12:30) permite identificar visualmente a sequência e duração de cada fase — recurso não disponível em sistemas CLI.

<p style={{textAlign: 'center'}}>Figura 6 - Detalhes da Sessão #001 — Histórico de Alertas e Fases</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={useBaseUrl('/img/GestorporBomba.png')} style={{width: '100%', maxWidth: 800}} alt="Tela por Sessão de uso da Bomba(Gestor)" />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

---

## 4. Como Acessar o Protótipo no Figma

**Link de acesso:**
```
https://www.figma.com/design/obUKpTUhd06KLBr3F0Ggfq/ItuBombas?node-id=0-1&p=f&t=Bq2XRhbvRW8i6hFs-0
```

**Principais fluxos interativos disponíveis:**

| Ação no Protótipo | Destino |
|---|---|
| Preencher e-mail/senha + clicar "Entrar na plataforma" | Dashboard do Operador ou Gestor (conforme perfil) |
| Clicar em "Sensores →" no menu lateral (Operador) | Abre o modal deslizante de Sensores e Componentes |
| Clicar em "Sobre o Sistema" no menu lateral | Tela de Identificação do Equipamento e Tutoriais |
| Clicar em "Detalhar" em qualquer sessão (Gestor) | Tela de Detalhes da Sessão com histórico de alertas |
| Clicar em "← Voltar para Gestão" (Gestor) | Retorna ao Dashboard de Gestão de Sessões |
| Clicar em "Sensores →" no menu lateral (Gestor) | Painel de Sensores por Bomba |


---