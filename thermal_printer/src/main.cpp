
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include "secrets.h"
// Wi-Fi credentials


const char* ssid = SSID;
const char* password = PASSWORD;

void setup() {
    Serial.print(SSID);
    Serial.print(password);
    Serial.begin(115200);
    delay(1000);

    Serial.println();
    Serial.println("=== ESP8266 WiFi test ===");

    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    delay(100);

    Serial.print("SSID: ");
    Serial.println(ssid);

    Serial.println("Scanning...");
    int n = WiFi.scanNetworks();

    Serial.printf("Found %d networks\n", n);

    for (int i = 0; i < n; i++) {
        Serial.printf(
            "%2d: %s  RSSI=%d  channel=%d  encryption=%d\n",
            i,
            WiFi.SSID(i).c_str(),
            WiFi.RSSI(i),
            WiFi.channel(i),
            WiFi.encryptionType(i)
        );
    }

    Serial.println();
    Serial.println("Starting connection...");

    WiFi.onStationModeConnected([](const WiFiEventStationModeConnected& event) {
        Serial.println("EVENT: Connected to AP");
    });

    WiFi.onStationModeDisconnected([](const WiFiEventStationModeDisconnected& event) {
        Serial.printf("EVENT: Disconnected, reason=%d\n", event.reason);
    });

    WiFi.onStationModeGotIP([](const WiFiEventStationModeGotIP& event) {
        Serial.println("EVENT: Got IP");
    });

    WiFi.onStationModeDisconnected(
        [](const WiFiEventStationModeDisconnected& event) {
            Serial.printf("DISCONNECTED: reason=%d\n", event.reason);
        }
    );

    WiFi.begin(ssid, password);

    unsigned long start = millis();

    while (WiFi.status() != WL_CONNECTED &&
           millis() - start < 30000) {

        Serial.printf(
            "status=%d  RSSI=%d  elapsed=%lus\n",
            WiFi.status(),
            WiFi.RSSI(),
            (millis() - start) / 1000
        );

        delay(1000);
    }

    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("CONNECTED!");
        Serial.print("IP: ");
        Serial.println(WiFi.localIP());
        Serial.print("Gateway: ");
        Serial.println(WiFi.gatewayIP());
        Serial.print("DNS: ");
        Serial.println(WiFi.dnsIP());
    } else {
        Serial.printf(
            "FAILED. Final WiFi.status() = %d\n",
            WiFi.status()
        );
    }
    WiFiClient client;
    HTTPClient http;

    String url = "http://192.168.1.206:8000/output.txt";

    if (http.begin(client, url)) {
        int httpCode = http.GET();

        if (httpCode > 0) {
            Serial.printf("HTTP response: %d\n", httpCode);

            String payload = http.getString();
            Serial.println(payload);
        } else {
            Serial.printf("HTTP request failed: %s\n",
                          http.errorToString(httpCode).c_str());
        }

        http.end();
    }
}

void loop() {
}


