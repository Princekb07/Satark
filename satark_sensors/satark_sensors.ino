#include <Arduino.h>
#include <Arduino_LED_Matrix.h>
#include <DHT.h>
#include "heart_frames.h"

// ================= SATARK SENSOR FIRMWARE =================

// MQ
#define MQ_ANALOG A0
#define MQ_DIGITAL 3

// DHT11
#define DHT_PIN 2
#define DHT_TYPE DHT11

// Ultrasonic
#define FRONT_TRIG 4
#define FRONT_ECHO 5

#define BACK_TRIG 6
#define BACK_ECHO 7

#define LEFT_TRIG 8
#define LEFT_ECHO 9

#define RIGHT_TRIG 10
#define RIGHT_ECHO 11

// External RED LED
#define RED_LED 12

DHT dht(DHT_PIN, DHT_TYPE);
ArduinoLEDMatrix matrix;

unsigned long lastSensor = 0;
unsigned long lastBlink = 0;

bool headDown = false;
bool ledState = false;


// ================= ULTRASONIC =================

long distanceCM(int trig, int echo)
{
  digitalWrite(trig, LOW);
  delayMicroseconds(2);

  digitalWrite(trig, HIGH);
  delayMicroseconds(10);

  digitalWrite(trig, LOW);

  long duration = pulseIn(echo, HIGH, 30000);

  if (duration == 0)
    return -1;

  return duration / 58;
}


// ================= PYTHON COMMAND =================

void readPythonCommand()
{
  while (Serial.available())
  {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "HEAD_DOWN")
    {
      headDown = true;
      Serial.println("HEAD_DOWN: RED LED ACTIVE");
    }

    else if (command == "HEAD_UP")
    {
      headDown = false;
      ledState = false;
      digitalWrite(RED_LED, LOW);

      Serial.println("HEAD_UP: RED LED OFF");
    }
  }
}


// ================= SETUP =================

void setup()
{
  Serial.begin(115200);
  delay(1000);

  // MQ
  pinMode(MQ_ANALOG, INPUT);
  pinMode(MQ_DIGITAL, INPUT);

  // DHT
  dht.begin();

  // Ultrasonic
  pinMode(FRONT_TRIG, OUTPUT);
  pinMode(FRONT_ECHO, INPUT);

  pinMode(BACK_TRIG, OUTPUT);
  pinMode(BACK_ECHO, INPUT);

  pinMode(LEFT_TRIG, OUTPUT);
  pinMode(LEFT_ECHO, INPUT);

  pinMode(RIGHT_TRIG, OUTPUT);
  pinMode(RIGHT_ECHO, INPUT);

  // RED LED
  pinMode(RED_LED, OUTPUT);
  digitalWrite(RED_LED, LOW);

  // Heart matrix
  matrix.begin();
  matrix.clear();

  // ORIGINAL HEART
  matrix.loadFrame(HeartStatic);

  Serial.println();
  Serial.println("================================");
  Serial.println("       SATARK SYSTEM");
  Serial.println("================================");
  Serial.println("MQ       : A0 / D3");
  Serial.println("DHT11    : D2");
  Serial.println("FRONT    : D4 / D5");
  Serial.println("BACK     : D6 / D7");
  Serial.println("LEFT     : D8 / D9");
  Serial.println("RIGHT    : D10 / D11");
  Serial.println("RED LED  : D12");
  Serial.println("BMP180   : REMOVED");
  Serial.println("RELAY    : REMOVED");
  Serial.println("HEART    : ACTIVE");
  Serial.println("HEAD     : PYTHON CONTROL");
  Serial.println("================================");
}


// ================= LOOP =================

void loop()
{
  unsigned long now = millis();

  // Read commands from Python
  readPythonCommand();

  // RED LED ONLY WHEN HEAD DOWN
  if (headDown)
  {
    if (now - lastBlink >= 500)
    {
      lastBlink = now;

      ledState = !ledState;
      digitalWrite(RED_LED, ledState);
    }
  }
  else
  {
    ledState = false;
    digitalWrite(RED_LED, LOW);
  }

  // Sensor reading every 1 second
  if (now - lastSensor >= 1000)
  {
    lastSensor = now;

    int mqA = analogRead(MQ_ANALOG);
    int mqD = digitalRead(MQ_DIGITAL);

    float dhtTemp = dht.readTemperature();
    float humidity = dht.readHumidity();

    long front = distanceCM(FRONT_TRIG, FRONT_ECHO);
    long back  = distanceCM(BACK_TRIG, BACK_ECHO);
    long left  = distanceCM(LEFT_TRIG, LEFT_ECHO);
    long right = distanceCM(RIGHT_TRIG, RIGHT_ECHO);

    Serial.println();
    Serial.println("========== SATARK DATA ==========");

    Serial.print("MQ Analog : ");
    Serial.println(mqA);

    Serial.print("MQ Digital: ");
    Serial.println(mqD);

    Serial.print("DHT Temp  : ");

    if (isnan(dhtTemp))
      Serial.println("ERROR");
    else
    {
      Serial.print(dhtTemp, 2);
      Serial.println(" C");
    }

    Serial.print("Humidity  : ");

    if (isnan(humidity))
      Serial.println("ERROR");
    else
    {
      Serial.print(humidity, 2);
      Serial.println(" %");
    }

    Serial.print("FRONT     : ");
    if (front < 0)
      Serial.println("NO ECHO");
    else
    {
      Serial.print(front);
      Serial.println(" cm");
    }

    Serial.print("BACK      : ");
    if (back < 0)
      Serial.println("NO ECHO");
    else
    {
      Serial.print(back);
      Serial.println(" cm");
    }

    Serial.print("LEFT      : ");
    if (left < 0)
      Serial.println("NO ECHO");
    else
    {
      Serial.print(left);
      Serial.println(" cm");
    }

    Serial.print("RIGHT     : ");
    if (right < 0)
      Serial.println("NO ECHO");
    else
    {
      Serial.print(right);
      Serial.println(" cm");
    }

    Serial.print("HEAD      : ");
    Serial.println(headDown ? "DOWN" : "UP");

    Serial.println("=================================");
  }
}
