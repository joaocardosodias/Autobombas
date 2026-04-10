#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>


// ----------------- Configuração HTTP/MQTT e Identificação -----------------
const int BOMBA_ID = 1; 
const char* ssid = "Joao";
const char* password = "fazol123";
const char* mqtt_server = "10.89.165.89";

char topic_distancias[50];
char topic_comando[50];
char topic_heartbeat[50];
char topic_heartbeat_ack[50];

WiFiClient espClient;
PubSubClient client(espClient);

// ----------------- Configuração de hardware -----------------

// Pinos dos sensores ultrassônicos HC-SR04
const int TRIG_FRENTE   = 4;
const int ECHO_FRENTE   = 32;

const int TRIG_TRAS     = 5;
const int ECHO_TRAS     = 33;

const int TRIG_ESQUERDA = 18;
const int ECHO_ESQUERDA = 34;

const int TRIG_DIREITA  = 19;
const int ECHO_DIREITA  = 35;

// Distância máxima considerada (em metros) para o mapeamento simples
const float DIST_MAX_M = 3.0f;

// Intervalo para envio espontâneo de STATUS via MQTT (ms)
const unsigned long STATUS_INTERVAL_MS = 500;
unsigned long lastStatusSent = 0;

// ----------------- Funções auxiliares de WiFi/MQTT -----------------

void conectarWiFi() {
  Serial.print("Conectando WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado!");
}

void reconectarMQTT() {
  while (!client.connected()) {
    Serial.print("Conectando MQTT...");
    if (client.connect("ESP32_Sensor2C")) {
      Serial.println("conectado!");
      client.subscribe(topic_comando);
      client.subscribe(topic_heartbeat_ack);
      Serial.print("Inscrito em: ");
      Serial.println(topic_comando);
    } else {
      Serial.print("falhou, rc=");
      Serial.print(client.state());
      Serial.println(" tentando novamente em 2s");
      delay(2000);
    }
  }
}

// ----------------- Funções Sensores -----------------

float medirDistanciaHC(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  unsigned long dur = pulseIn(echoPin, HIGH, 30000);
  if (dur == 0) return DIST_MAX_M;

  float dist = dur * 0.0001715f;
  if (dist > DIST_MAX_M) dist = DIST_MAX_M;
  if (dist < 0.0f) dist = 0.0f;
  return dist;
}

// ----------------- Publicar Leitura MQTT -----------------

void enviarDistanciasMQTT() {
  float frente   = medirDistanciaHC(TRIG_FRENTE,   ECHO_FRENTE);
  float tras     = medirDistanciaHC(TRIG_TRAS,     ECHO_TRAS);
  float esquerda = medirDistanciaHC(TRIG_ESQUERDA, ECHO_ESQUERDA);
  float direita  = medirDistanciaHC(TRIG_DIREITA,  ECHO_DIREITA);

  // Buffer JSON
  StaticJsonDocument<128> doc;
  doc["frente_m"] = round(frente * 100) / 100.0;
  doc["tras_m"] = round(tras * 100) / 100.0;
  doc["esq_m"] = round(esquerda * 100) / 100.0;
  doc["dir_m"] = round(direita * 100) / 100.0;

  char payload[128];
  serializeJson(doc, payload);

  client.publish(topic_distancias, payload);
  Serial.println(payload);
}

// ----------------- Callback Comandos MQTT -----------------

void callbackMQTT(char* topic, byte* payload, unsigned int length) {
  String msg = "";
  for (unsigned int i = 0; i < length; i++) {
    msg += (char)payload[i];
  }

  // Heartbeat ACK do backend — verifica antes do parse JSON
  if (String(topic) == String(topic_heartbeat_ack)) {
    if (msg == "PONG") {
      Serial.println("[HB] Backend ativo (PONG recebido)");
    }
    return;
  }

  Serial.print("Comando recebido: ");
  Serial.println(msg);

  StaticJsonDocument<128> doc;
  DeserializationError error = deserializeJson(doc, msg);
  if (error) {
    Serial.print("Erro parse JSON: ");
    Serial.println(error.c_str());
    return;
  }

  const char* acao = doc["acao"];
  if (acao && String(acao) == "ler_distancia") {
    enviarDistanciasMQTT();
  }
}

// ----------------- Setup / Loop -----------------

void setup() {
  pinMode(TRIG_FRENTE, OUTPUT);
  pinMode(ECHO_FRENTE, INPUT);

  pinMode(TRIG_TRAS, OUTPUT);
  pinMode(ECHO_TRAS, INPUT);

  pinMode(TRIG_ESQUERDA, OUTPUT);
  pinMode(ECHO_ESQUERDA, INPUT);

  pinMode(TRIG_DIREITA, OUTPUT);
  pinMode(ECHO_DIREITA, INPUT);

  Serial.begin(115200);
  delay(100);

  sprintf(topic_distancias, "sensor/%d/distancias", BOMBA_ID);
  sprintf(topic_comando, "sensor/%d/comando", BOMBA_ID);
  sprintf(topic_heartbeat, "sensor/%d/heartbeat", BOMBA_ID);
  sprintf(topic_heartbeat_ack, "sensor/%d/heartbeat/ack", BOMBA_ID);

  conectarWiFi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callbackMQTT);

  Serial.println("Modulo 2-C (WiFi/MQTT) Pronto");
}

void loop() {
  if (!client.connected()) {
    reconectarMQTT();
  }
  client.loop();

  unsigned long agora = millis();
  if (agora - lastStatusSent >= STATUS_INTERVAL_MS) {
    lastStatusSent = agora;
    enviarDistanciasMQTT();
  }

  // === Heartbeat: envia PING a cada 1s ===
  static unsigned long ultimoHeartbeat = 0;
  if (agora - ultimoHeartbeat >= 1000) {
    ultimoHeartbeat = agora;
    client.publish(topic_heartbeat, "PING");
  }
}

