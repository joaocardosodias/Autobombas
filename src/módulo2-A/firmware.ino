#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// === Pinos do motor DC (L298N/L293D) ===
#define ENB 32
#define IN3 25
#define IN4 33

// === Configuracao ===
const int BOMBA_ID = 1;

const char* ssid     = "iPhone de Schmidt";
const char* password = "Schmidtt";

const char* mqtt_server = "172.20.10.12";

const int PWM_FREQ      = 1000;
const int PWM_RESOLUCAO = 8;
const int VELOCIDADE    = 200;   // 0-255

// Topicos MQTT
char topic_comando[40];
char topic_status[40];
char topic_heartbeat[50];
char topic_heartbeat_ack[50];

WiFiClient   espClient;
PubSubClient client(espClient);

bool sistema_ligado = false;
String direcao_atual = "PARADO";

// === Watchdog: tempo do ultimo PONG recebido do backend ===
unsigned long ultimoPongRecebido = 0;
const unsigned long PONG_TIMEOUT_MS = 2500; // 2.5s sem PONG => parar motor

// === Controle do motor ===

void motor_esquerda() {
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  ledcWrite(ENB, VELOCIDADE);
  direcao_atual = "ESQUERDA";
}

void motor_direita() {
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  ledcWrite(ENB, VELOCIDADE);
  direcao_atual = "DIREITA";
}

void motor_parar() {
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  ledcWrite(ENB, 0);
  direcao_atual = "PARADO";
}

// === MQTT Callback ===

void callbackMQTT(char* topic, byte* payload, unsigned int length) {
  String mensagem = "";
  for (int i = 0; i < length; i++) {
    mensagem += (char)payload[i];
  }

  Serial.print("[MQTT] Recebido: ");
  Serial.println(mensagem);

  // Parse JSON: {"acao": "esquerda", "operador_id": 2}
  StaticJsonDocument<128> doc;
  DeserializationError err = deserializeJson(doc, mensagem);

  String acao = "";
  if (!err && doc.containsKey("acao")) {
    acao = doc["acao"].as<String>();
  } else {
    // Fallback: payload simples (compatibilidade)
    acao = mensagem;
  }

  // Heartbeat ACK do backend
  if (String(topic) == String(topic_heartbeat_ack)) {
    if (mensagem == "PONG") {
      ultimoPongRecebido = millis();
      Serial.println("[HB] Backend ativo (PONG recebido)");
    }
    return;
  }

  acao.toLowerCase();

  if (acao == "ligar") {
    sistema_ligado = true;
    client.publish(topic_status, "LIGADO");
    Serial.println("[CMD] Sistema LIGADO");

  } else if (acao == "desligar") {
    motor_parar();
    sistema_ligado = false;
    client.publish(topic_status, "DESLIGADO");
    Serial.println("[CMD] Sistema DESLIGADO");

  } else if (!sistema_ligado) {
    Serial.println("[AVISO] Sistema desligado, comando ignorado.");
    return;

  } else if (acao == "esquerda" || acao == "tras") {
    motor_esquerda();
    String status_msg = (acao == "tras") ? "TRAS" : "ESQUERDA";
    char buf[16];
    status_msg.toCharArray(buf, 16);
    client.publish(topic_status, buf);
    Serial.print("[CMD] Motor -> ");
    Serial.println(status_msg);

  } else if (acao == "direita" || acao == "frente") {
    motor_direita();
    String status_msg = (acao == "frente") ? "FRENTE" : "DIREITA";
    char buf[16];
    status_msg.toCharArray(buf, 16);
    client.publish(topic_status, buf);
    Serial.print("[CMD] Motor -> ");
    Serial.println(status_msg);

  } else if (acao == "parar") {
    motor_parar();
    client.publish(topic_status, "PARADO");
    Serial.println("[CMD] Motor -> PARADO");

  } else {
    Serial.print("[AVISO] Acao desconhecida: ");
    Serial.println(acao);
  }
}

// === WiFi ===

void conectarWiFi() {
  Serial.print("Conectando WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado!");
}

// === MQTT Reconexao ===

void reconectarMQTT() {
  while (!client.connected()) {
    Serial.print("Conectando MQTT...");
    if (client.connect("ESP32Balsa")) {
      Serial.println("OK!");
      Serial.print("Inscrito em: ");
      Serial.println(topic_comando);
      client.subscribe(topic_comando);
      client.subscribe(topic_heartbeat_ack);
      client.publish(topic_status, "ONLINE");
      ultimoPongRecebido = millis(); // reset watchdog ao (re)conectar
    } else {
      Serial.print("Falha (rc=");
      Serial.print(client.state());
      Serial.println("). Tentando em 2s...");
      delay(2000);
    }
  }
}

// === Setup ===

void setup() {
  Serial.begin(115200);

  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  ledcAttach(ENB, PWM_FREQ, PWM_RESOLUCAO);

  motor_parar();

  // Monta topicos com bomba_id
  sprintf(topic_comando, "balsa/%d/comando", BOMBA_ID);
  sprintf(topic_status,  "balsa/%d/status",  BOMBA_ID);
  sprintf(topic_heartbeat, "balsa/%d/heartbeat", BOMBA_ID);
  sprintf(topic_heartbeat_ack, "balsa/%d/heartbeat/ack", BOMBA_ID);

  conectarWiFi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callbackMQTT);
}

// === Loop ===

void loop() {
  if (!client.connected()) {
    reconectarMQTT();
  }
  client.loop();

  // === Watchdog: parar motor se backend offline durante movimento ===
  if (sistema_ligado && direcao_atual != "PARADO" && ultimoPongRecebido > 0) {
    if (millis() - ultimoPongRecebido >= PONG_TIMEOUT_MS) {
      motor_parar();
      client.publish(topic_status, "PARADO");
      Serial.println("[WDG] Backend offline! Motor parado automaticamente.");
      ultimoPongRecebido = 0; // evita loop de stops
    }
  }

  // === Heartbeat: envia PING a cada 1s ===
  static unsigned long ultimoHeartbeat = 0;
  if (millis() - ultimoHeartbeat >= 1000) {
    ultimoHeartbeat = millis();
    client.publish(topic_heartbeat, "PING");
  }
}
