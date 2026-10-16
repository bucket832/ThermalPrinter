
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include "secrets.h"
#include <string>
// Wi-Fi credentials


const char* ssid = SSID;
const char* password = PASSWORD;
String url = URL;

void setupWifi() {
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
    // Serial.println("Starting connection...");

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
}


void setup() {
    Serial.begin(115200);
    Serial1.begin(9600);
    delay(1000);

    setupWifi();
    WiFiClient client;
    HTTPClient http;

    const char* target_header = "Next-Checkin";    
    const char* headerKeys[] = {target_header};
    if (http.begin(client, url)) {
        http.collectHeaders(headerKeys, 1);
        int httpCode = http.GET();

        if (httpCode > 0) {
            Serial.printf("HTTP response: %d\n", httpCode);
            if (http.hasHeader(target_header)) {
                String nextCheckinVal = http.header(target_header);
                Serial.printf("Next-Checkin value: %s\n", nextCheckinVal.c_str());
                int numVal = atoi(nextCheckinVal.c_str());
                if (numVal != 0) {
                    Serial.printf("It Worked !! %d !\n", numVal);
                } else {
                    Serial.printf("Cast Failed\n");
                }
            } else {
                Serial.println("Header not found!");
            }
            String payload = http.getString();
            Serial.println(payload);
            Serial1.print("\n----------------------------\n\n");
            Serial1.print(payload);
            Serial1.print("\n\n\n");
        } else {
            Serial.printf("HTTP request failed: %s\n",
                          http.errorToString(httpCode).c_str());
        }

        http.end();
    }
}


void loop() {
}


