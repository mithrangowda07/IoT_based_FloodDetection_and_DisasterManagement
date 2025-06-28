#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>

const char* ssid = "DisasterManagement";  // More descriptive network name
const char* password = "123456789"; // Simple password for emergency use
const byte DNS_PORT = 53;
IPAddress apIP(192, 168, 4, 1);  // ESP32 IP Address

DNSServer dnsServer;
WebServer webServer(80);

void setup() {
  Serial.begin(115200);
  
  // Set up as Access Point with a static IP
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));
  WiFi.softAP(ssid, password);
  
  // Start DNS Server
  dnsServer.start(DNS_PORT, "*", apIP);
  
  Serial.println("Access Point Started");
  Serial.print("Network Name: ");
  Serial.println(ssid);
  Serial.print("Password: ");
  Serial.println(password);
  Serial.print("AP IP address: ");
  Serial.println(WiFi.softAPIP());
  
  // Setup web server
  webServer.onNotFound([]() {
    String message = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'>";
    message += "<style>body{font-family:Arial,sans-serif;margin:20px;text-align:center;}</style></head>";
    message += "<body><h1>Disaster Management System</h1>";
    message += "<p>Server Status: Online</p>";
    message += "<p>To access the system, please connect to:</p>";
    message += "<p><strong>Network: " + String(ssid) + "</strong></p>";
    message += "<p><strong>Password: " + String(password) + "</strong></p>";
    message += "<p>Then open your browser and go to: <strong>http://192.168.4.1</strong></p>";
    message += "</body></html>";
    webServer.send(200, "text/html", message);
  });
  
  webServer.begin();
  Serial.println("HTTP server started");
}

void loop() {
  dnsServer.processNextRequest();
  webServer.handleClient();
}