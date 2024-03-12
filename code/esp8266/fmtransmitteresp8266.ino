#include <SoftwareSerial.h>
#include <PubSubClient.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <EEPROM.h>
#include <DNSServer.h>
#include <WiFiManager.h>
#include <ESP8266mDNS.h>


#define WIFI_STA_NAME ""
#define WIFI_STA_PASS  ""
#define MQTT_SERVER   ""
#define MQTT_PORT     
#define MQTT_USERNAME ""
#define MQTT_PASSWORD ""
#define MQTT_NAME     "fmtx"

char mqttServer[40];
char mqttPort[6];
char mqttUsername[40];
char mqttPassword[40];

SoftwareSerial uart(D2, D3); // RX, TX
WiFiClient client;
PubSubClient mqtt(client);
//ESP8266WebServer server(80);

void saveConfigCallback() {
    Serial.println("Configuration saved.");
}

void configureWiFiManager() {
  WiFiManager wifiManager;

  WiFi.hostname("ThaiSDR THS-FTX1");

  if (!MDNS.begin("ThaiSDR THS-FTX1")) {
    Serial.println("Error setting up MDNS responder!");
  }

  // Parameters to be configured
  WiFiManagerParameter custom_mqtt_server("server", "MQTT Server", mqttServer, 40);
  WiFiManagerParameter custom_mqtt_port("port", "MQTT Port", mqttPort, 6);
  WiFiManagerParameter custom_mqtt_username("username", "MQTT Username", mqttUsername, 40);
  WiFiManagerParameter custom_mqtt_password("password", "MQTT Password", mqttPassword, 40);
  
  wifiManager.setTitle("ThaiSDR THS-FTX1 config");

  wifiManager.addParameter(&custom_mqtt_server);
  wifiManager.addParameter(&custom_mqtt_port);
  wifiManager.addParameter(&custom_mqtt_username);
  wifiManager.addParameter(&custom_mqtt_password);

  wifiManager.autoConnect("ThaiSDR THS-FTX1");

  //wifiManager.startConfigPortal();

  //wifiManager.setConfigPortalBlocking(false);

  // Save the custom parameters to EEPROM
  strcpy(mqttServer, custom_mqtt_server.getValue());
  strcpy(mqttPort, custom_mqtt_port.getValue());
  strcpy(mqttUsername, custom_mqtt_username.getValue());
  strcpy(mqttPassword, custom_mqtt_password.getValue());

}


void setup() {
  pinMode(BUILTIN_LED, OUTPUT); 

  Serial.begin(115200);
  uart.begin(11520); // Set baudrate to match Raspberry Pi Pico

  //WiFi.mode(WIFI_STA);

  configureWiFiManager();

  Serial.println("MQTT Connecting");
  mqtt.setServer(MQTT_SERVER, MQTT_PORT);
  mqtt.setCallback(callback);

  if (mqtt.connect(MQTT_NAME, mqttUsername, mqttPassword)) {
    // MQTT connected successfully
    Serial.println("MQTT connected");
  } else {
    // MQTT connection failed
    Serial.println("MQTT connection failed");
    // Handle the failure here, such as retrying or going into a deep sleep mode.
  }

  mqtt.subscribe("fmtx/transmitter/si4713/txpower");
  mqtt.subscribe("fmtx/transmitter/si4713/txfreq");
  mqtt.subscribe("fmtx/transmitter/si4713/rds/station");
  mqtt.subscribe("fmtx/transmitter/si4713/rds/buffer");
  mqtt.subscribe("fmtx/transmitter/si4713/txcompo");
  mqtt.subscribe("fmtx/transmitter/si4713/rds/pty");
  mqtt.subscribe("fmtx/transmitter/si4713/audiochannel");
  mqtt.subscribe("fmtx/transmitter/si4713/rds/enable");
  mqtt.subscribe("fmtx/transmitter/si4713/power");
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
    Serial.println("[RP2040] "+command);
    String id = input.substring(index1 + 1, index2);
    String message = input.substring(index2 + 1);

    if (id == "INLE") {
      mqtt.publish("fmtx/status/INLE", message.c_str());
    } else if (id == "ASQ") {
      mqtt.publish("fmtx/status/ASQ", message.c_str());
    } else if (id == "AudioL") {
      mqtt.publish("fmtx/status/audioinput/L", message.c_str());
    } else if (id == "AudioR") {
      mqtt.publish("fmtx/status/audioinput/R", message.c_str());
    }

  }
  mqtt.loop();
}

void sendcommand(String command, String receivedMessage) {
  uart.print(command + " " + receivedMessage + "|");
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
    sendcommand("setrdstation", receivedMessage);
    //uart.print("<<<!setrdstation "+receivedMessage+"|");
  } else if (strcmp(topic, "fmtx/transmitter/si4713/rds/buffer") == 0) {
    sendcommand("setrdsbuffer", receivedMessage);
    //uart.print("<<<!setrdsbuffer "+receivedMessage+"|");
  } else if (strcmp(topic, "fmtx/transmitter/si4713/txfreq") == 0) {
    sendcommand("settxfreq", receivedMessage);
    //uart.print("<<<!settxfreq "+receivedMessage+"|");
  } else if (strcmp(topic, "fmtx/transmitter/si4713/txpower") == 0) {
    sendcommand("setgentxpower", receivedMessage);
    //uart.print("<<<!setgentxpower "+receivedMessage+"|");
  } else if (strcmp(topic, "fmtx/transmitter/si4713/rds/pty") == 0) {
    sendcommand("setrdspty", receivedMessage);
    //uart.print("<<<!setrdspty "+receivedMessage+"|");
  } else if (strcmp(topic, "fmtx/transmitter/si4713/audiochannel") == 0) {
    sendcommand("setaudiochannel", receivedMessage);
    //uart.print("<<<!setaudiochannel "+receivedMessage+"|");
  } else if (strcmp(topic, "fmtx/transmitter/si4713/rds/enable") == 0) {
    sendcommand("setrds", receivedMessage);
    //uart.print("<<<!setrds "+receivedMessage+"|");
  } else if (strcmp(topic, "fmtx/transmitter/si4713/power") == 0) {
    if (receivedMessage == "on") {
      sendcommand("powerup", "NO");
      //uart.print("<<<!powerup|");
    } else if (receivedMessage == "off") {
      sendcommand("powerdown", "NO");
      //uart.print("<<<!powerdown|");
    }
  }

  Serial.println(receivedMessage);

  receivedMessage = "";
}