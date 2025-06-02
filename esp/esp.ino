void setup() {
  Serial.begin(115200);      // Gửi ra PC
  Serial2.begin(9600, SERIAL_8N1, 16, 17); // RX = GPIO16, TX = GPIO17
  // Lưu ý: nối TX Uno → RX ESP32 (GPIO16)
  // RX Uno → TX ESP32 (GPIO17)
  // GND → GND
}

void loop() {
  if (Serial2.available()) {
    String data = Serial2.readStringUntil('\n');  // Đọc từng dòng
    Serial.print("📡 Du_Lieu_Nhan_Duoc: ");
    Serial.println(data);
    
    // Có thể tách giá trị nêuSS cần
    // ví dụ: temp, hum, lux, soil, flow
    int idx = 0;
    float values[5];
    while (data.length() > 0 && idx < 5) {
      int commaIndex = data.indexOf(',');
      String token = data.substring(0, commaIndex);
      values[idx++] = token.toFloat();
      data = data.substring(commaIndex + 1);
    }

    // In từng giá trị
    Serial.print("Nhiet_Do: "); Serial.print(values[0]); Serial.println(" °C");
    Serial.print("Do_Am_Khong_Khi: "); Serial.print(values[1]); Serial.println(" %");
    Serial.print("Anh_Sang: "); Serial.print(values[2]); Serial.println(" lux");
    Serial.print("Do_Am_Dat: "); Serial.print(values[3]); Serial.println(" %");
    Serial.print("Luu_Luong_Nuoc: "); Serial.print(values[4]); Serial.println(" L/phút");
    Serial.println("-----------------------------");
  }

  delay(500);
}