#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <Stepper.h>

// WiFi Credentials
const char* ssid = "Redmi A3";
const char* password = "Anoop@689102";

ESP8266WebServer server(80);

#define iny1 14
#define iny2 12
#define iny3 13
#define iny4 15

#define inx1 16
#define inx2 5
#define inx3 4
#define inx4 2
#define pumppin 3

int steps=2048, i;
bool one_roty=false;
Stepper ymotor(steps,iny1,iny3,iny2,iny4);
Stepper xmotor(steps,inx1,inx3,inx2,inx4);
int motspeed=10;

// Function to handle the Web Request for the pump
void handlePump() {
  server.send(200, "text/plain", "Pump Activated");
  pump();
}

void setup() {
  Serial.begin(115200); // Higher baud rate for WiFi debugging
  
  // WiFi Connection
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.println(WiFi.localIP()); // Look at Serial Monitor once to get the IP

  // Web Server Routes
  server.on("/pump", handlePump); 
  server.begin();

  ymotor.setSpeed(motspeed);
  xmotor.setSpeed(motspeed);

  pinMode(iny1,OUTPUT); pinMode(iny2,OUTPUT); pinMode(iny3,OUTPUT); pinMode(iny4,OUTPUT);
  pinMode(inx1,OUTPUT); pinMode(inx2,OUTPUT); pinMode(inx3,OUTPUT); pinMode(inx4,OUTPUT);
  pinMode(pumppin,OUTPUT);

  motorstop();
}

void loop() {
  server.handleClient(); // Checks for WiFi commands

  for(i=0; i<=200; i+=5){
    ymotor.step(-i);
    xmotor.step(-i);
    delay(500);
    server.handleClient(); // Keep checking WiFi during the long motor loops
  }

  one_roty=true;
  delay(3000);

  if(one_roty==true){
    for(i=0; i<=200; i+=5){
      ymotor.step(i);
      xmotor.step(i);
      delay(500);
      server.handleClient(); 
    }
  }
}

void motorstop(){
  digitalWrite(iny1,LOW); digitalWrite(iny2,LOW); digitalWrite(iny3,LOW); digitalWrite(iny4,LOW);
  digitalWrite(inx1,LOW); digitalWrite(inx2,LOW); digitalWrite(inx3,LOW); digitalWrite(inx4,LOW);
}

void pump(){
  digitalWrite(pumppin, HIGH);
  delay(500);
  digitalWrite(pumppin, LOW);
}