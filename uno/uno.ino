#include <Wire.h>
#include <BH1750.h>
#include <DHT.h>

#define DHTPIN 4
#define DHTTYPE DHT11
#define SOIL_PIN A0
#define RELAY_PIN 7
#define FLOW_SENSOR 2

DHT dht(DHTPIN, DHTTYPE);
BH1750 lightMeter;

volatile int flowCount = 0;
float flowRate = 0;
unsigned long lastFlowTime = 0;

void flowISR() {
  flowCount++;
}

void setup() {
  Serial.begin(9600);  // UART giao tiếp với ESP32
  Wire.begin();
  dht.begin();
  lightMeter.begin();

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  pinMode(FLOW_SENSOR, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR), flowISR, RISING);
}

void loop() {
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  float lux = lightMeter.readLightLevel();
  int soilRaw = analogRead(SOIL_PIN);
  float soilPercent = map(soilRaw, 0, 1023, 100, 0);

  unsigned long now = millis();
  if (now - lastFlowTime >= 1000) {
    flowRate = flowCount / 7.5;
    flowCount = 0;
    lastFlowTime = now;
  }

  // Gửi dữ liệu qua Serial UART cho ESP32
  Serial.print(temp); Serial.print(",");
  Serial.print(hum); Serial.print(",");
  Serial.print(lux); Serial.print(",");
  Serial.print(soilPercent); Serial.print(",");
  Serial.println(flowRate);  // dòng cuối kèm newline

  // Điều khiển bơm
  if (soilPercent < 40) digitalWrite(RELAY_PIN, HIGH);
  else digitalWrite(RELAY_PIN, LOW);

  delay(2000);
}