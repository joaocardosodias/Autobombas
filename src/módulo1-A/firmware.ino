#include <WiFi.h>
#include <PubSubClient.h>

#define IN1 14
#define IN2 27
#define IN3 26
#define IN4 25

// === CONFIGURACAO ===
const int BOMBA_ID = 1;

const char* ssid = "Joao";
const char* password = "fazol123";
const char* mqtt_server = "10.211.123.89";

// Topicos MQTT dinamicos baseados no BOMBA_ID
char topic_comando[40];
char topic_status[40];
char topic_heartbeat[50];
char topic_heartbeat_ack[50];

WiFiClient espClient;
PubSubClient client(espClient);

int passo = 0;
long passosRestantes = 0;
long passosTotaisMovimento = 0;

const int minIntervalo = 800;
const int maxIntervalo = 2500;
const int passosRampa = 800;
int intervaloAtual = maxIntervalo;
unsigned long ultimoPasso = 0;

float voltasGlobais = 0.0;
const int passosPorVolta = 4096;

// === Watchdog: tempo do ultimo PONG recebido do backend ===
unsigned long ultimoPongRecebido = 0;
const unsigned long PONG_TIMEOUT_MS = 2500; // 2.5s sem PONG => abortar

// === Abort pendente: reenvia ao backend assim que MQTT reconectar ===
bool pendingAbort = false;
char pendingAbortMsg[50] = "";

void setup() {
  Serial.begin(115200);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Monta topicos com bomba_id
  sprintf(topic_comando, "motor/%d/comando", BOMBA_ID);
  sprintf(topic_status, "motor/%d/status", BOMBA_ID);
  sprintf(topic_heartbeat, "motor/%d/heartbeat", BOMBA_ID);
  sprintf(topic_heartbeat_ack, "motor/%d/heartbeat/ack", BOMBA_ID);

  conectarWiFi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callbackMQTT);
}

void loop() {
  if (!client.connected()) {
    reconectarMQTT();
  }

  client.loop();

  // === Heartbeat: envia PING a cada 1s ===
  static unsigned long ultimoHeartbeat = 0;
  if (millis() - ultimoHeartbeat >= 1000) {
    ultimoHeartbeat = millis();
    client.publish(topic_heartbeat, "PING");
  }

  // === Watchdog: abortar movimento se backend offline ===
  if (passosRestantes != 0 && ultimoPongRecebido > 0) {
    if (millis() - ultimoPongRecebido >= PONG_TIMEOUT_MS) {
      long passosFeitos = passosTotaisMovimento - abs(passosRestantes);
      float voltasFeitas = (float)passosFeitos / (float)passosPorVolta;
      if (voltasGlobais < 0) voltasFeitas = -voltasFeitas;

      String msgAborto = "ABORTADO:" + String(voltasFeitas, 4);
      passosRestantes = 0;
      passosTotaisMovimento = 0;
      ativar(0, 0, 0, 0);

      // Tenta publicar imediatamente; se falhar, salva para reenviar na reconexao
      msgAborto.toCharArray(pendingAbortMsg, 50);
      if (client.publish(topic_status, pendingAbortMsg)) {
        pendingAbort = false;
        Serial.println("[WDG] ABORTADO publicado com sucesso.");
      } else {
        pendingAbort = true;
        Serial.println("[WDG] Broker offline — ABORTADO salvo para reenvio.");
      }

      Serial.println("[WDG] Backend offline! Movimento abortado automaticamente.");
      ultimoPongRecebido = 0; // evita loop de aborts
    }
  }

  if (passosRestantes != 0) {
    long passosFeitos = passosTotaisMovimento - abs(passosRestantes);
    long passosFaltando = abs(passosRestantes);

    if (passosTotaisMovimento > passosRampa * 2) {
      if (passosFeitos < passosRampa) {
        intervaloAtual = maxIntervalo - ((maxIntervalo - minIntervalo) * passosFeitos / passosRampa);
      } else if (passosFaltando < passosRampa) {
        intervaloAtual = minIntervalo + ((maxIntervalo - minIntervalo) * (passosRampa - passosFaltando) / passosRampa);
      } else {
        intervaloAtual = minIntervalo;
      }
    } else {
      intervaloAtual = maxIntervalo;
    }

    unsigned long agora = micros();

    if (agora - ultimoPasso >= intervaloAtual) {
      ultimoPasso = agora;

      if (passosRestantes > 0) {
        girarHorario();
        passosRestantes--;
      } else {
        girarAntiHorario();
        passosRestantes++;
        
      }

      if (passosRestantes == 0) {
        passosTotaisMovimento = 0;
        ativar(0,0,0,0);
        client.publish(topic_status, "LIVRE");
        Serial.println("Movimento concluido! Enviado estado 'LIVRE' ao broker.");
      }
    }
  }
}

void callbackMQTT(char* topic, byte* payload, unsigned int length) {
  String mensagem = "";

  for (int i = 0; i < length; i++) {
    mensagem += (char)payload[i];
  }

  // Heartbeat ACK do backend
  if (String(topic) == String(topic_heartbeat_ack)) {
    if (mensagem == "PONG") {
      ultimoPongRecebido = millis();
      Serial.println("[HB] Backend ativo (PONG recebido)");
    }
    return;
  }

  if (mensagem == "EMERGENCIA") {
    long passosFeitos = passosTotaisMovimento - abs(passosRestantes);
    float voltasFeitas = (float)passosFeitos / (float)passosPorVolta;

    if (voltasGlobais < 0) {
        voltasFeitas = -voltasFeitas;
    }

    String mensagemAborto = "ABORTADO:" + String(voltasFeitas, 4);

    passosRestantes = 0;
    passosTotaisMovimento = 0;
    ativar(0,0,0,0);

    char msgCharArray[50];
    mensagemAborto.toCharArray(msgCharArray, 50);
    client.publish(topic_status, msgCharArray);

    Serial.println("\n[!!!] EMERGENCIA! Parada forcada recebida!");
    Serial.print("Motor completou ");
    Serial.print(voltasFeitas);
    Serial.println(" voltas antes de abortar.");
    return;
  }

  // Extrai o campo "voltas" do JSON: {"voltas": 7.47, ...}
  int idx = mensagem.indexOf("\"voltas\":");
  if (idx >= 0) {
    String valorStr = mensagem.substring(idx + 9);
    int endIdx = valorStr.indexOf(",");
    if (endIdx < 0) endIdx = valorStr.indexOf("}");
    valorStr = valorStr.substring(0, endIdx);
    valorStr.trim();

    float voltas = valorStr.toFloat();
    voltasGlobais = voltas;

    if (voltas != 0) {
      passosRestantes = voltas * passosPorVolta;
      passosTotaisMovimento = abs(passosRestantes);
      client.publish(topic_status, "OCUPADO");

      Serial.println("\nNova instrucao recebida:");
      Serial.print("Voltas: ");
      Serial.println(voltas);
      Serial.print("Passos calculados: ");
      Serial.println(passosRestantes);
    }
  }
}

void conectarWiFi() {
  Serial.println("Conectando WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi conectado!");
}

void reconectarMQTT() {
  while (!client.connected()) {
    Serial.println("Conectando MQTT...");
    if (client.connect("ESP32Motor")) {
      Serial.println("MQTT conectado!");
      Serial.print("Inscrito em: ");
      Serial.println(topic_comando);
      client.subscribe(topic_comando);
      client.subscribe(topic_heartbeat_ack);
      ultimoPongRecebido = millis(); // reset watchdog ao (re)conectar

      // Reenvia ABORTADO pendente ao backend (caso broker estava offline)
      if (pendingAbort && strlen(pendingAbortMsg) > 0) {
        client.publish(topic_status, pendingAbortMsg);
        Serial.print("[WDG] ABORTADO pendente reenviado: ");
        Serial.println(pendingAbortMsg);
        pendingAbort = false;
        pendingAbortMsg[0] = '\0';
      }
    } else {
      delay(2000);
    }
  }
}

void girarHorario() {
  switch(passo) {
    case 0: ativar(1,0,0,0); break;
    case 1: ativar(1,1,0,0); break;
    case 2: ativar(0,1,0,0); break;
    case 3: ativar(0,1,1,0); break;
    case 4: ativar(0,0,1,0); break;
    case 5: ativar(0,0,1,1); break;
    case 6: ativar(0,0,0,1); break;
    case 7: ativar(1,0,0,1); break;
  }

  passo++;
  if(passo > 7) passo = 0;
}

void girarAntiHorario() {
  passo--;
  if(passo < 0) passo = 7;

  switch(passo) {
    case 0: ativar(1,0,0,0); break;
    case 1: ativar(1,1,0,0); break;
    case 2: ativar(0,1,0,0); break;
    case 3: ativar(0,1,1,0); break;
    case 4: ativar(0,0,1,0); break;
    case 5: ativar(0,0,1,1); break;
    case 6: ativar(0,0,0,1); break;
    case 7: ativar(1,0,0,1); break;
  }
}

void ativar(int a, int b, int c, int d) {
  digitalWrite(IN1, a);
  digitalWrite(IN2, b);
  digitalWrite(IN3, c);
  digitalWrite(IN4, d);
}