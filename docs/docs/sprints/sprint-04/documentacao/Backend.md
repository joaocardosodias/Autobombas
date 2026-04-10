---
sidebar_label: "Backend"
sidebar_position: 3
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Documentação do Backend 
--- 

## 1. Visão Geral do Backend

&nbsp; O backend da solução é a camada central que interliga o sistema de automação (hardware embarcado nos ESPs), o banco de dados relacional (PostgreSQL/Supabase) e a interface do usuário (frontend React client-side). Nesta sprint, a principal evolução foi a implementação do modo automático e do intertravamento entre módulos: o Módulo 2-A (movimentação da balsa) passou a ser controlado não apenas pelo estado da motobomba (Módulo 1-A), mas também pelas leituras dos sensores de proximidade (Módulo 2-C), garantindo uma camada de segurança operacional completa.

&nbsp; A comunicação entre backend e hardware é feita via protocolo MQTT (broker Mosquitto), enquanto o frontend consome a API REST com autenticação JWT. Todas as operações são persistidas no banco de dados, permitindo rastreabilidade e auditoria das ações dos operadores.

&nbsp; O sistema segue um fluxo integrado onde o frontend envia requisições ao backend, que processa regras de negócio e se comunica com os dispositivos via MQTT. As respostas dos dispositivos são persistidas no banco de dados e disponibilizadas novamente para a interface do usuário.

--- 
## 2. Arquitetura da Aplicação e Integrações 

&nbsp; O backend é implementado em Flask (Python) e se conecta a três camadas distintas:

- **Hardware (ESPs)**: comunicação bidirecional via MQTT. O backend publica comandos nos tópicos `motor/<bomba_id>/comando`, `balsa/<bomba_id>/comando` e `sensor/<bomba_id>/comando`, e recebe respostas nos tópicos `motor/+/status`, `sensor/+/status`, `corrente/+/status` e `sensor/+/distancias`. Um listener MQTT dedicado roda em thread separada com reconexão automática. Além disso, o sistema de heartbeat monitora a conectividade dos ESPs via tópicos `+/+/heartbeat` (PING/PONG).

- **Banco de Dados (PostgreSQL — Supabase)**: conexão via pool de conexões `psycopg2`, com padrão repository para cada entidade. Todas as operações de movimentação, leituras de sensores e logs são gravados automaticamente.

- **Frontend (React — client-side)**: o frontend consome a API REST diretamente via requisições HTTP autenticadas com JWT no header `Authorization: Bearer <token>`. O backend fornece CORS habilitado e documentação Swagger automática.

--- 

## 3. Tecnologias Utilizadas

Essa sessão destaca as principais tecnologias utilizadas no backend da aplicação.

| Tecnologia | Finalidade |
|------------|-----------|
| Python 3.12 | Linguagem principal do backend |
| Flask | Framework web para a API REST |
| Flask-JWT-Extended | Autenticação via tokens JWT |
| Flasgger (Swagger) | Documentação automática dos endpoints |
| psycopg2 | Driver PostgreSQL com pool de conexões |
| paho-mqtt | Cliente MQTT para comunicação com os ESPs |
| PostgreSQL (Supabase) | Banco de dados relacional em nuvem |
| bcrypt | Hash seguro de senhas |

--- 

## 4. Funcionalidades Implementadas

&nbsp; Os principais avanços desta sprint foram: (1) o sistema de heartbeat para monitorar a conectividade dos módulos ESP em tempo real, (2) o modo automático de descida/subida da motobomba baseado na corrente de operação, e (3) os sistemas de intertravamento (interlocks) entre sensores e balsa.

### 4.1 Sistema de Heartbeat

&nbsp; Para garantir que os comandos enviados pelo backend alcancem os módulos físicos, foi implementado um sistema de heartbeat bidirecional via MQTT. Cada ESP envia periodicamente uma mensagem `PING` no tópico `<tipo>/<id>/heartbeat`, e o backend responde com `PONG` no tópico `<tipo>/<id>/heartbeat/ack`.

&nbsp; O estado de cada módulo é mantido em memória no serviço `mqtt_service.py`:

```python
HEARTBEAT_TIMEOUT_S = 5  # segundos sem PING = considerado offline

def registrar_heartbeat(tipo: str, modulo_id: int):
    chave = f"{tipo}/{modulo_id}"
    with _heartbeat_lock:
        _heartbeat_state[chave] = datetime.now()

    topico_ack = f"{tipo}/{modulo_id}/heartbeat/ack"
    client = _get_client()
    if client:
        client.publish(topico_ack, "PONG")
```

&nbsp; O backend também mantém uma thread daemon que envia `PONG` periódico a cada 1 segundo para todos os módulos conhecidos, garantindo que os ESPs saibam que o backend está ativo. A lista de módulos monitorados é:

| Módulo | Tópico heartbeat | Descrição |
|--------|-----------------|-----------|
| `motor/1` | `motor/1/heartbeat` | ESP do motor Z (Módulo 1-A) |
| `corrente/1` | `corrente/1/heartbeat` | ESP do sensor de corrente (Módulo 1-B) |
| `sensor/1` | `sensor/1/heartbeat` | ESP dos sensores de distância (Módulo 2-C) |
| `balsa/1` | `balsa/1/heartbeat` | ESP da balsa XY (Módulo 2-A) |

&nbsp; O estado de conectividade é consultável via API:

- `GET /sistema/heartbeat` — lista todos os módulos com status online/offline
- `GET /sistema/heartbeat/<tipo>/<id>` — status de um módulo específico
- `GET /sistema/heartbeat/debug` — estado bruto para diagnóstico (todos os PINGs recebidos, módulos sem PING e PINGs de módulos desconhecidos)

&nbsp; Esse sistema é utilizado como pré-condição em funcionalidades críticas: o modo automático só é ativado se os ESPs de motor e corrente estiverem online, e a solicitação de leitura de corrente (`POST /leituras-corrente/solicitar/<bomba_id>`) retorna HTTP 503 se o ESP estiver offline.

### 4.2 Modo Automático de Descida/Subida

&nbsp; O modo automático (`auto_mode_service.py`) permite que a motobomba ajuste sua posição vertical automaticamente com base na corrente de operação, sem intervenção contínua do operador. O sistema utiliza dois limiares de corrente configuráveis por bomba:

| Parâmetro | Descrição |
|-----------|-----------|
| `limite_inferior` | Corrente mínima de dragagem — abaixo desse valor, a motobomba deve **descer** |
| `limite_superior` | Corrente máxima de proteção — acima desse valor, a motobomba deve **subir** (emergencial) |
| `passo_auto_cm` | Incremento de descida por ciclo (padrão: 2.0 cm) |

&nbsp; Os limiares são configurados via `PATCH /bombas/<bomba_id>/config`:

```python
class BombaConfigUpdate(BaseModel):
    diametro_carretel_cm: Optional[Decimal] = None
    comprimento_corda_cm: Optional[Decimal] = None
    limite_inferior: Optional[Decimal] = None
    limite_superior: Optional[Decimal] = None
    passo_auto_cm: Optional[Decimal] = None
```

&nbsp; O ciclo de controle roda em uma thread dedicada a cada 2 segundos e segue a seguinte lógica:

```python
def _ciclo(bomba_id, st):
    # 1. Verifica heartbeat do motor e do sensor de corrente
    if not motor_online:
        st["fase"] = "MOTOR_OFFLINE"
        return
    if not sensor_online:
        st["fase"] = "SENSOR_OFFLINE"
        return

    # 2. Lê a corrente mais recente do banco
    corrente = float(leitura["corrente_a"])

    # 3. Decide a ação
    if corrente > limite_sup:
        # EMERGÊNCIA: sobe até a origem (posição 0 cm)
        delta_cm = -posicao_atual
    elif corrente < limite_inf and tem_espaco:
        # Abaixo do mínimo: desce um passo
        delta_cm = passo_auto_cm
    else:
        st["fase"] = "ESTAVEL"
        return

    # 4. Publica comando MQTT e registra no banco
    mqtt_service.publicar(f"motor/{bomba_id}/comando", {"voltas": voltas})
    movimentacao_z_repo.criar(...)
```

&nbsp; As fases do modo automático são:

| Fase | Descrição |
|------|-----------|
| `INICIANDO` | Modo recém-ativado, aguardando primeiro ciclo |
| `DESCENDO` | Motobomba descendo por passo (corrente abaixo do limite inferior) |
| `SUBINDO` | Motobomba subindo até a origem (corrente acima do limite superior) |
| `ESTAVEL` | Corrente dentro da faixa operacional — nenhuma ação necessária |
| `MOTOR_OFFLINE` | ESP do motor não responde ao heartbeat — ciclo pausado |
| `SENSOR_OFFLINE` | ESP do sensor de corrente não responde — ciclo pausado |
| `LIMITE_MINIMO` | Motobomba já está na posição 0 cm — não pode subir mais |
| `SEM_LEITURA` | Nenhuma leitura de corrente disponível no banco |
| `ERRO` | Exceção no ciclo de controle |
| `PARADO` | Modo automático desligado |

&nbsp; Na subida emergencial (corrente acima do limite superior), o sistema monitora a corrente a cada segundo durante o recolhimento. Quando a corrente cai para um valor seguro, envia o comando `EMERGENCIA` via MQTT para parar o motor imediatamente, evitando subir mais do que o necessário. Ao encerrar o modo automático, a posição final é gravada no banco como um registro do tipo `SNAPSHOT`, garantindo que o `/z status` reflita a posição real.

&nbsp; Os endpoints do modo automático são:

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/auto/<bomba_id>/ligar` | Ativa o modo automático (exige motor e corrente online) |
| `POST` | `/auto/<bomba_id>/desligar` | Desativa (motor conclui o passo atual antes de parar) |
| `GET` | `/auto/<bomba_id>/status` | Retorna fase, posição, ciclos executados e último erro |

Vídeo demonstrativo do modo automático: [Link](https://drive.google.com/file/d/1OAEmNPNHAivgTqhQ1FNIb9QrrNZzYblo/view?usp=sharing)

### 4.3 Intertravamento Motobomba x Balsa

&nbsp; A balsa (Módulo 2-A) só pode ser movimentada quando a motobomba (Módulo 1-A) estiver no ponto de origem (posição Z = 0 cm, sem movimento em andamento).

&nbsp; Quando a motobomba está fora da origem, a interface do sistema (CLI e frontend) exibe a mensagem de bloqueio ao operador:

<p style={{textAlign: 'center'}}>Figura 1 - Mensagem de intertravamento Motobomba x Balsa</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/intertravamento-Motobomba-Balsa.png" ).default} style={{width: 800}} alt="Mensagem de intertravamento Motobomba x Balsa" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>


&nbsp;Essa regra é implementada no serviço via `validador_balsa.py`:

```python
def motobomba_esta_na_origem(bomba_id: int) -> tuple[bool, str]:
    # 1. Verificar se há movimento Z em andamento
    em_andamento = movimentacao_z_repo.tem_movimento_em_andamento(bomba_id)
    if em_andamento:
        return (False, "Motobomba em movimento (eixo Z). Aguarde a conclusão antes de movimentar a balsa.")

    # 2. Verificar posição atual
    posicao = movimentacao_z_repo.recuperar_posicao(bomba_id)
    if posicao is None:
        return True, "ok"

    posicao_cm = float(posicao.get("posicao_final_cm", 0) or 0)
    if posicao_cm > TOLERANCIA_ORIGEM_CM:
        return (False, f"Motobomba fora do ponto de origem (posição atual: {posicao_cm:.1f} cm).")

    return True, "ok"
```
### 4.4 Intertravamento Sensores x Balsa

&nbsp; O Módulo 2-C (sensores de proximidade HC-SR04) monitora continuamente as 4 direções da balsa (frente, trás, esquerda, direita). Com base na distância medida, o backend classifica cada direção em um dos 4 níveis de risco e aplica restrições à movimentação:

| Condição | Nível | Efeito na balsa |
|----------|-------|-----------------|
| d &gt; dist_info | **SEGURO** | Movimento normal |
| dist_alerta &lt; d ≤ dist_info | **INFORMATIVO** | Movimento normal |
| dist_critico &lt; d ≤ dist_alerta | **ALERTA** | Movimento permitido com velocidade reduzida |
| d ≤ dist_critico | **CRÍTICO** | Movimento **bloqueado** naquela direção |

&nbsp; Os limiares padrão são `dist_info = 2.0 m`, `dist_alerta = 1.0 m` e `dist_critico = 0.5 m`, e podem ser ajustados em tempo real via API (`PUT /leituras-distancia/limiares`) ou pela CLI (`/sensor limiares <info> <alerta> <critico>`), respeitando a regra `0 < critico < alerta < info`.

&nbsp; A classificação é feita no serviço `validador_sensores.py`:

```python
def classificar_distancia(distancia_m: float) -> str:
    lim = get_limiares()
    if distancia_m <= lim["dist_critico_m"]:
        return NIVEL_CRITICO
    if distancia_m <= lim["dist_alerta_m"]:
        return NIVEL_ALERTA
    if distancia_m <= lim["dist_info_m"]:
        return NIVEL_INFORMATIVO
    return NIVEL_SEGURO
```

&nbsp; Antes de executar qualquer comando de movimentação XY, a rota `POST /movimentacao-xy/` executa duas validações em cadeia:

```python
# Validação 1: motobomba no ponto de origem
permitido, msg = motobomba_esta_na_origem(dados.bomba_id)
if not permitido:
    return jsonify({"detail": msg}), 403

# Validação 2: intertravamento com sensores de proximidade (módulo 2-C)
sensor_ok, sensor_msg, sensor_detalhes = verificar_movimento_permitido(
    dados.bomba_id, dados.direcao
)
if not sensor_ok:
    return jsonify({"detail": sensor_msg, "sensores": sensor_detalhes}), 403
```

&nbsp; Quando o sensor na direção solicitada está em nível CRÍTICO, o comando é bloqueado:

<p style={{textAlign: 'center'}}>Figura 2 - Mensagem de intertravamento Sensores x Balsa</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/intertravamento-Sensores-Balsa-01.png" ).default} style={{width: 800}} alt="Mensagem de intertravamento Sensores x Balsa" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

&nbsp; O operador pode consultar o status de todos os sensores em tempo real via comando `/sensor status`, que exibe a distância, o nível de risco por direção e as direções bloqueadas ou em alerta:

<p style={{textAlign: 'center'}}>Figura 3 - Tabela de Status dos sensores</p>
<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("/img/intertravamento-Sensores-Balsa-02.png" ).default} style={{width: 800}} alt="Tabela de Status dos sensores" />
        <br />
    </div>
</div>
<p style={{textAlign: 'center'}}>Fonte: Material produzido pelos autores (2026)</p>

### 4.5 Parada de Emergência Automática

&nbsp; Além do bloqueio preventivo nos comandos, o backend implementa uma **parada de emergência reativa**: quando uma nova leitura de distância chega via MQTT (`sensor/+/distancias`) e algum sensor está em nível CRÍTICO, o backend automaticamente:

1. Publica um comando `parar` no tópico `balsa/<bomba_id>/comando` via MQTT;
2. Encerra todas as movimentações XY em andamento no banco de dados.

```python
def _verificar_parada_emergencia(bomba_id, leitura):
    criticos = verificar_proximidade_critica(leitura)
    if not criticos:
        return

    # Envia parada imediata para o ESP da balsa
    topico = f"balsa/{bomba_id}/comando"
    mqtt_service.publicar(topico, {
        "acao": "parar",
        "motivo": "parada_emergencia_sensores",
        "direcoes_criticas": ", ".join(c["direcao"] for c in criticos),
    })

    # Fecha movimentações XY em andamento no banco
    ids_fechados = movimentacao_xy_repo.fechar_orfaos(bomba_id)
```

&nbsp; Esse mecanismo garante que, mesmo que o operador tenha iniciado um movimento antes de o sensor detectar a proximidade, a balsa será parada automaticamente assim que a leitura atualizada chegar ao backend.

### 4.6 Listener MQTT e persistência automática

&nbsp; O backend mantém um subscriber MQTT em thread dedicada que escuta os tópicos dos ESPs e persiste as informações automaticamente no banco de dados:

```python
def on_connect(client, userdata, flags, rc, properties):
    client.subscribe("motor/+/status")
    client.subscribe("balsa/+/status")
    client.subscribe("sensor/+/status")
    client.subscribe("sensor/+/distancias")
    client.subscribe("corrente/+/status")
    client.subscribe("+/+/heartbeat")
```

&nbsp; Cada tipo de mensagem recebida é tratado por uma função especializada:

| Tópico MQTT | Função | Ação |
|------------|--------|------|
| `motor/+/status` | `tratar_status_motor` | Atualiza `movimentacao_z` (CONCLUIDO ou ABORTADO) |
| `sensor/+/status` ou `corrente/+/status` | `tratar_leitura_sensor` | Salva leitura de corrente em `leituras_corrente` |
| `sensor/+/distancias` | `tratar_leitura_distancias` | Salva leitura de distância em `leituras_distancia` + verifica parada de emergência |
| `+/+/heartbeat` | `registrar_heartbeat` | Atualiza timestamp do módulo e responde com PONG |

--- 

## 5. Endpoints e Fluxos de Comunicação

&nbsp; Os endpoints documentados na sprint 3 ("Protótipo Finalizado do Sistema de Automação") permanecem funcionais. As principais adições e modificações nesta sprint foram:

| Método | Rota | Descrição | Status |
|--------|------|-----------|--------|
| `GET` | `/sistema/heartbeat` | Lista todos os módulos ESP com status online/offline | Novo |
| `GET` | `/sistema/heartbeat/<tipo>/<id>` | Status de heartbeat de um módulo específico | Novo |
| `GET` | `/sistema/heartbeat/debug` | Estado bruto de todos os PINGs recebidos (diagnóstico) | Novo |
| `POST` | `/auto/<bomba_id>/ligar` | Ativa o modo automático de descida/subida | Novo |
| `POST` | `/auto/<bomba_id>/desligar` | Desativa o modo automático | Novo |
| `GET` | `/auto/<bomba_id>/status` | Estado atual do loop de controle automático | Novo |
| `PATCH` | `/bombas/<bomba_id>/config` | Atualiza configurações da bomba (limiares de corrente, passo auto) | Novo |
| `GET` | `/movimentacao-z/posicao/<bomba_id>` | Agora retorna o campo `em_andamento` (booleano) | Modificado |
| `GET` | `/movimentacao-xy/pode-mover/<bomba_id>` | Agora inclui status completo dos sensores de proximidade | Modificado |
| `GET` | `/leituras-distancia/bomba/<bomba_id>/status-proximidade` | Classificação de risco por direção, direções bloqueadas/alerta e limiares | Novo |
| `GET` | `/leituras-distancia/limiares` | Consulta os limiares de risco atuais | Novo |
| `PUT` | `/leituras-distancia/limiares` | Atualiza os limiares de risco em tempo real | Novo |

&nbsp; A rota `POST /movimentacao-xy/` e `POST /movimentacao-xy/comando/<bomba_id>` passaram a executar duas validações em cadeia (motobomba na origem + sensores de proximidade) antes de publicar o comando MQTT, retornando HTTP 403 quando bloqueado. A rota `POST /leituras-corrente/solicitar/<bomba_id>` agora verifica o heartbeat do ESP de corrente antes de enviar o comando, retornando HTTP 503 se estiver offline.

### 5.1 Exemplo de Fluxo de Execução (Movimentação da Balsa)

1. O usuário solicita a movimentação pelo frontend;
2. O frontend envia uma requisição `POST /movimentacao-xy/` para o backend;
3. O backend valida os intertravamentos (posição da motobomba e sensores de proximidade);
4. Se permitido, publica o comando via MQTT no tópico `balsa/<bomba_id>/comando`;
5. O ESP executa o movimento e envia status de volta pelo tópico `balsa/<bomba_id>/status`;
6. O backend persiste o resultado no banco de dados;
7. O frontend pode consultar o estado atualizado via API.

--- 

## 6. Persistência de Dados e Logs

&nbsp; O banco de dados PostgreSQL (Supabase) mantém 6 tabelas principais, todas com chaves estrangeiras para `bombas` e `usuarios`:

| Tabela | Módulo | Descrição |
|--------|--------|-----------|
| `usuarios` | Geral | Credenciais e roles dos operadores |
| `bombas` | Geral | Configurações da bomba: diâmetro do carretel, comprimento da corda, `limite_inferior` e `limite_superior` de corrente, `passo_auto_cm` |
| `movimentacao_z` | 1-A | Registros de deslocamento vertical com posição inicial/final, voltas e status (incluindo `SNAPSHOT` do modo auto) |
| `movimentacao_xy` | 2-A | Registros de movimentação horizontal com direção, duração e status |
| `leituras_corrente` | 1-B | Medições de corrente em Amperes com timestamp |
| `leituras_distancia` | 2-C | Leituras dos 4 sensores ultrassônicos (frente, trás, esquerda, direita) em metros |

&nbsp; Nesta sprint, a tabela `bombas` foi ampliada com os campos `limite_inferior`, `limite_superior` e `passo_auto_cm` para suportar o modo automático. A tabela `movimentacao_z` passou a aceitar `operador_id` nulo (para registros criados automaticamente) e o status `SNAPSHOT` (para gravar a posição final quando o modo automático é desligado). A tabela `leituras_corrente` foi simplificada, removendo os campos de classificação e sugestão — agora armazena apenas a corrente bruta em Amperes.

&nbsp; A gravação ocorre de três formas: por ação direta do operador (via API REST), automaticamente pelo listener MQTT quando os ESPs reportam dados, ou pelo loop de controle do modo automático. Os logs de operação podem ser consultados via `GET /logs`.

&nbsp; Exemplo de registro de log gerado pelo sistema:

```json
{
  "timestamp": "2026-03-20T14:32:10Z",
  "bomba_id": 1,
  "acao": "movimentacao_xy",
  "direcao": "frente",
  "status": "concluido",
  "origem": "usuario"
}
```

&nbsp; Esses logs permitem rastrear todas as ações realizadas no sistema, sejam iniciadas por operadores ou automaticamente pelo backend (como no modo automático ou paradas de emergência), garantindo auditabilidade completa.

--- 

## 7. Limitações Atuais e Próximos Passos

&nbsp; Limitações identificadas nesta sprint:

- **Heartbeat para bomba_id=1 apenas**: a lista de módulos conhecidos (`_MODULOS_CONHECIDOS`) está fixa com `modulo_id=1` para cada tipo de ESP. Para suportar múltiplas bombas, essa lista precisaria ser dinâmica, carregada a partir do banco de dados.

- **Limiares de proximidade em memória**: os valores de `dist_info`, `dist_alerta` e `dist_critico` são armazenados em memória. Se o backend reiniciar, retornam aos valores padrão (2.0 / 1.0 / 0.5 m). Os limiares de corrente do modo automático, por outro lado, já são persistidos no banco (tabela `bombas`).

- **Velocidade reduzida depende do firmware**: quando o nível é ALERTA, o backend envia `velocidade_reduzida: true` no payload MQTT, mas a efetiva redução de velocidade depende do firmware do ESP interpretar esse campo e ajustar o PWM do motor.

- **Modo automático e estimativa de posição**: na subida emergencial, se o motor não confirmar a parada a tempo, a posição é estimada com base no tempo decorrido. Essa estimativa é grosseira e pode divergir da posição real do hardware.

- **Dependência de leitura recente**: tanto o intertravamento de sensores quanto o modo automático utilizam a última leitura disponível no banco. Se os sensores pararem de enviar dados, o sistema continuará usando a última leitura conhecida, que pode estar desatualizada. O heartbeat mitiga parcialmente esse problema ao detectar ESPs offline.

&nbsp; Essas limitações não impedem o funcionamento do sistema nesta sprint, mas indicam pontos de evolução para torná-lo mais escalável e aderente a cenários reais de operação.