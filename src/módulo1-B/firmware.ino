#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// === Pino do sensor de corrente ===
#define PINO_SENSOR 34    // GPIO34 (ADC1) - pino analogico

// === Configuracao ===
const int BOMBA_ID = 1;

const char* ssid     = "Guilherme";
const char* password = "guigu123a";

const char* mqtt_server = "172.20.10.2";

// Topicos MQTT
char topic_comando[40];
char topic_status[40];
char topic_heartbeat[50];
char topic_heartbeat_ack[50];

WiFiClient   espClient;
PubSubClient client(espClient);

int operador_id_atual = 1; // atualizado via comando MQTT

// Fator multiplicador da corrente lida (ajusta para simulação com potenciômetro)
// Para sensor real de corrente: ajuste conforme a escala do transdutor
const float MULTIPLICADOR_CORRENTE = 300000.0;

// Intervalo para envio continuo de STATUS via MQTT (ms)
const unsigned long STATUS_INTERVAL_MS = 500;
unsigned long lastStatusSent = 0;

// === MQTT Callback ===

void callbackMQTT(char* topic, byte* payload, unsigned int length) {
  String mensagem = "";
  for (int i = 0; i < length; i++) {
    mensagem += (char)payload[i];
  }

  // Heartbeat ACK do backend
  if (String(topic) == String(topic_heartbeat_ack)) {
    if (mensagem == "PONG") {
      Serial.println("[HB] Backend ativo (PONG recebido)");
    }
    return;
  }

  Serial.print("[MQTT] Recebido: ");
  Serial.println(mensagem);

  StaticJsonDocument<64> doc;
  DeserializationError err = deserializeJson(doc, mensagem);

  String acao = "";
  if (!err && doc.containsKey("acao")) {
    acao = doc["acao"].as<String>();
  } else {
    acao = mensagem;
  }

  if (doc.containsKey("operador_id")) {
    operador_id_atual = doc["operador_id"].as<int>();
  }

  acao.toLowerCase();

  if (acao == "ler") {
    realizar_leitura();
  } else {
    Serial.print("[AVISO] Acao desconhecida: ");
    Serial.println(acao);
  }
}

// === Leitura do sensor ===

void realizar_leitura() {
  int avalor = analogRead(PINO_SENSOR);

  // ESP32 ADC: 12 bits (0-4095), 3.3V
  float tensao = avalor * (3.3 / 4095.0);
  float corrente_bruta = tensao / 10000.0;
  float corrente = corrente_bruta * MULTIPLICADOR_CORRENTE;

  Serial.print("[SENSOR] Corrente bruta: ");
  Serial.print(corrente_bruta, 6);
  Serial.print(" A  |  Escalada: ");
  Serial.print(corrente, 6);
  Serial.println(" A");

  // Publica resultado como JSON
  StaticJsonDocument<128> doc;
  doc["corrente_a"] = corrente;
  doc["operador_id"] = operador_id_atual;

  char buffer[128];
  serializeJson(doc, buffer);
  client.publish(topic_status, buffer);

  Serial.println("[SENSOR] Leitura publicada via MQTT");
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
    if (client.connect("ESP32Sensor")) {
      Serial.println("OK!");
      Serial.print("Inscrito em: ");
      Serial.println(topic_comando);
      client.subscribe(topic_comando);
      client.subscribe(topic_heartbeat_ack);
      client.publish(topic_status, "{\"status\": \"ONLINE\"}");
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

  // Monta topicos com bomba_id
  sprintf(topic_comando, "corrente/%d/comando", BOMBA_ID);
  sprintf(topic_status,  "corrente/%d/status",  BOMBA_ID);
  sprintf(topic_heartbeat, "corrente/%d/heartbeat", BOMBA_ID);
  sprintf(topic_heartbeat_ack, "corrente/%d/heartbeat/ack", BOMBA_ID);

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

  unsigned long agora = millis();
  if (agora - lastStatusSent >= STATUS_INTERVAL_MS) {
    lastStatusSent = agora;
    realizar_leitura();
  }

  // === Heartbeat: envia PING a cada 1s ===
  static unsigned long ultimoHeartbeat = 0;
  if (agora - ultimoHeartbeat >= 1000) {
    ultimoHeartbeat = agora;
    client.publish(topic_heartbeat, "PING");
  }
}