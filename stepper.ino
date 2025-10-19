#include<Stepper.h>
#define iny1 14
#define iny2 12
#define iny3 13
#define iny4 15

#define inx1 16
#define inx2 5
#define inx3 4
#define inx4 2
int steps=2048,i;
bool one_roty=false,one_rotx=false,stepsize=5;
Stepper ymotor(steps,iny1,iny3,iny2,iny4);
Stepper xmotor(steps,inx1,inx3,inx2,inx4);
int motspeed=10;
void setup() {
  Serial.begin(9600);
  ymotor.setSpeed(motspeed);
  xmotor.setSpeed(motspeed);
  pinMode(iny1,OUTPUT);
  pinMode(iny2,OUTPUT);
  pinMode(iny3,OUTPUT);
  pinMode(iny4,OUTPUT);

  pinMode(inx1,OUTPUT);
  pinMode(inx2,OUTPUT);
  pinMode(inx3,OUTPUT);
  pinMode(inx4,OUTPUT);
  motorstop();
  
  
}

void loop() {
  for(i=0;i<=200;i+=5){
    ymotor.step(-i);
    xmotor.step(-i);
    Serial.print("ccw steps:");
    Serial.println(i);
    delay(500);
  }
  one_roty=true;
  delay(3000);
  if(one_roty==true){
 Serial.println("complete one rot");
 for(i=0;i<=220;i+=5){
    ymotor.step(i);
    xmotor.step(i);
    Serial.print("cw steps:");
    Serial.println(i);
    delay(500);
  }

  }

  //motorstop();

  Serial.println("finish");  
}
void motorstop(){
  digitalWrite(iny1,LOW);
  digitalWrite(iny2,LOW);
  digitalWrite(iny3,LOW);
  digitalWrite(iny4,LOW);

  digitalWrite(inx1,LOW);
  digitalWrite(inx2,LOW);
  digitalWrite(inx3,LOW);
  digitalWrite(inx4,LOW);
}

  


