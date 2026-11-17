// #include <U8g2lib.h>
// #include <Wire.h>

// U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);

// void setup() {
//   Wire.begin(21, 22);
//   u8g2.begin();
// }

// void loop() {
//   u8g2.clearBuffer();
//   u8g2.setFont(u8g2_font_ncenB10_tr);
//   u8g2.drawStr(10, 25, "ESP32 Buddy");
//   u8g2.drawStr(10, 50, "OLED works!");
//   u8g2.sendBuffer();
//   delay(1000);
// }


#include <ESP_I2S.h>
#include <math.h>

I2SClass i2s;

#define I2S_BCLK 32
#define I2S_WS   25
#define I2S_DIN  33

void setup() {
  Serial.begin(115200);
  i2s.setPins(I2S_BCLK, I2S_WS, -1, I2S_DIN);   // bclk, ws, dout, din

  if (!i2s.begin(I2S_MODE_STD, 16000, I2S_DATA_BIT_WIDTH_32BIT,
                 I2S_SLOT_MODE_MONO, I2S_STD_SLOT_LEFT)) {
    Serial.println("I2S init failed");
    while (1) delay(1000);
  }
}

void loop() {
  int32_t buf[256];
  size_t bytes = i2s.readBytes((char *)buf, sizeof(buf));
  int n = bytes / 4;
  if (n == 0) return;

  int64_t sum = 0;
  for (int i = 0; i < n; i++) sum += (buf[i] >> 8);   // 24-bit signed
  int32_t mean = sum / n;

  int64_t sq = 0;
  for (int i = 0; i < n; i++) {
    int32_t s = (buf[i] >> 8) - mean;
    sq += (int64_t)s * s;
  }

  Serial.printf("rms:%ld\n", (long)sqrt((double)(sq / n)));
}