#include <SoftwareSerial.h>
#include <PubSubClient.h>
#include <ESP8266WiFi.h>

#define WIFI_STA_NAME "NEW"
#define WIFI_STA_PASS  "0981789654"
#define MQTT_SERVER   "0.tcp.ap.ngrok.io"
#define MQTT_PORT     11755
#define MQTT_USERNAME ""
#define MQTT_PASSWORD ""
#define MQTT_NAME     "fmtx"

SoftwareSerial uart(D2, D3); // RX, TX
WiFiClient client;
PubSubClient mqtt(client);

void setup() {
  pinMode(BUILTIN_LED, OUTPUT); 

  Serial.begin(115200);
  uart.begin(9600); // Set baudrate to match Raspberry Pi Pico

  WiFi.mode(WIFI_STA); 
  WiFi.begin(WIFI_STA_NAME, WIFI_STA_PASS);
  Serial.println("WIFI Connecting");
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
    Serial.print(".");
    digitalWrite(LED_BUILTIN, LOW);
  }
  digitalWrite(LED_BUILTIN, LOW);
  WiFi.hostname("fm transmitter");
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  Serial.println("MQTT Connecting");
  mqtt.setServer(MQTT_SERVER, MQTT_PORT);
  mqtt.setCallback(callback);

  mqtt.connect(MQTT_NAME, MQTT_USERNAME, MQTT_PASSWORD);

  Serial.print("testing Publish message: ");
  if (mqtt.publish("TEST/MQTT","Arduino Test MQTT") == true) { 
    Serial.println("Success sending");
  } else {
    Serial.println("Fail sending");
  }

  mqtt.subscribe("fmtx/transmitter/si4713/txpower");
  mqtt.subscribe("fmtx/transmitter/si4713/txfreq");
  mqtt.subscribe("fmtx/transmitter/si4713/rds/station");
  mqtt.subscribe("fmtx/transmitter/si4713/rds/buffer");
  //mqtt.subscribe("fmtx/transmitter/si4713/rds/picode");
  digitalWrite(BUILTIN_LED, HIGH);
}

void loop() {
  if (uart.available()) {
    String input = uart.readStringUntil('\n'); // read the incoming string until a newline character is received
    input.trim(); // remove any leading or trailing white space

    // split the input string based on the colon and space characters
    int index1 = input.indexOf(':');
    int index2 = input.indexOf(' ');
    String command = input.substring(0, index1);
    String id = input.substring(index1 + 1, index2);
    String message = input.substring(index2 + 1);

    if (id == "INLE") {
      mqtt.publish("fmtx/status/INLE", message.c_str());
    } else if (id == "ASQ") {
      mqtt.publish("fmtx/status/ASQ", message.c_str());
    } else if (id == "ASQW") {
      mqtt.publish("fmtx/status/ASQW", message.c_str());
    }

  }
  mqtt.loop();
}

void callback(char* topic, byte* payload, unsigned int length) {
  String receivedMessage = "";

  Serial.print("Message received in topic: ");
  Serial.print(topic);
  Serial.print("   length is:");
  Serial.println(length);

  Serial.print("Data Received From Broker:");
  for (int i = 0; i < length; i++) {
    receivedMessage += (char)payload[i];
  }

  if (strcmp(topic, "fmtx/transmitter/si4713/rds/station") == 0) {
    uart.print("!setrdstation "+receivedMessage+"|");
  } else if (strcmp(topic, "fmtx/transmitter/si4713/rds/buffer") == 0) {
    uart.print("!setrdsbuffer "+receivedMessage+"|");
  } else if (strcmp(topic, "fmtx/transmitter/si4713/txfreq") == 0) {
    uart.print("!settxfreq "+receivedMessage+"|");
  } else if (strcmp(topic, "fmtx/transmitter/si4713/txpower") == 0) {
    uart.print("!setgentxpower "+receivedMessage+"|");
  }

  Serial.println(receivedMessage);

  receivedMessage = "";
}
