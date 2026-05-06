#include <Servo.h>

#define LED_PIN 3
#define SERVO_PIN 6

Servo myServo;

String input = "";
String gesture = "";
float confidence = 0.0;

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  myServo.attach(SERVO_PIN);

  Serial.println("AI System Ready...");
}

void loop() {

  if (Serial.available()) {

    input = Serial.readStringUntil('\n');
    input.trim();

    // ===== PARSE MESSAGE =====
    int commaIndex = input.indexOf(',');

    if (commaIndex != -1) {
      gesture = input.substring(0, commaIndex);
      confidence = input.substring(commaIndex + 1).toFloat();
    }

    Serial.print("Gesture: ");
    Serial.print(gesture);
    Serial.print(" | Confidence: ");
    Serial.println(confidence);

    // ===== CONFIDENCE FILTER =====
    if (confidence < 0.5) {
      return; // ignore weak predictions
    }

    // ===== ACTION SYSTEM =====

    if (gesture == "CLOSE") {
      digitalWrite(LED_PIN, HIGH);
      myServo.write(0);
    }

    else if (gesture == "FAR") {
      digitalWrite(LED_PIN, LOW);
      myServo.write(180);
    }

    else if (gesture == "LEFT") {
      myServo.write(45);
    }

    else if (gesture == "RIGHT") {
      myServo.write(135);
    }

    else if (gesture == "SWIPE") {
      digitalWrite(LED_PIN, HIGH);
      delay(80);
      digitalWrite(LED_PIN, LOW);
    }
  }
}
