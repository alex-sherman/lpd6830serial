#include <FastSPI_LED.h>

uint8_t NUM_LEDS  = 150;

// Sometimes chipsets wire in a backwards sort of way
struct Color { unsigned char g; unsigned char r; unsigned char b; };
//struct CRGB { unsigned char r; unsigned char g; unsigned char b; };
struct Color *leds;

#define PIN 4

#define SETRANGE 0x1
#define LERPRANGE 0x2
#define SETVALUES 0x3

void setup()
{
  Serial.begin(115200);
  while(Serial.available() == 0) {
    delay(10);
  }
  NUM_LEDS = Serial.read();
  while(Serial.available() > 0) Serial.read();
  Serial.print("Starting with ");
  Serial.print(NUM_LEDS, DEC);
  Serial.println(" LEDS");
  
  FastSPI_LED.setLeds(NUM_LEDS);
  FastSPI_LED.setChipset(CFastSPI_LED::SPI_LPD6803);
  
  FastSPI_LED.init();
  FastSPI_LED.start();

  leds = (struct Color*)FastSPI_LED.getRGBData();
  memset(leds, 0, NUM_LEDS * 3);
  FastSPI_LED.show();
}

void readInto(char *dest, int size) {
  for(int i = 0; i < size; i++) {
    dest[i] = readSync();
  }
}

void SetValues() {
  readInto((char *)leds, NUM_LEDS * 3);
  FastSPI_LED.show();
}

void SetRange() {
  uint8_t i_start;
  uint8_t i_end;
  struct Color color;
  readInto((char *)&color, sizeof(color));
  i_start = readSync();
  i_end = readSync();
  
  for(int i = i_start; i <= i_end; i++) {
    leds[i].r = color.r;
    leds[i].g = color.g;
    leds[i].b = color.b;
  }
  FastSPI_LED.show();
}

void LerpRange() {
  struct Color color;
  uint8_t i_start;
  uint8_t i_end;
  uint8_t steps;
  uint8_t t_delay;
  readInto((char *)&color, sizeof(color));
  i_start = readSync();
  i_end = readSync();
  steps = readSync();
  t_delay = readSync();
  Color past[i_end - i_start + 1];
  memcpy(past, &leds[i_start], sizeof(past));
  for(int i = 0; i < steps - 1; i++) {
    for(int j = 0; j <= i_end - i_start; j++) {
      leds[j + i_start].r = (color.r - past[j].r) * i / steps + past[j].r;
      leds[j + i_start].g = (color.g - past[j].g) * i / steps + past[j].g;
      leds[j + i_start].b = (color.b - past[j].b) * i / steps + past[j].b;
    }
    FastSPI_LED.show();
    delay(t_delay);
  }
  for(int i = i_start; i <= i_end; i++) {
    leds[i].r = color.r;
    leds[i].g = color.g;
    leds[i].b = color.b;
  }
  FastSPI_LED.show();
}

uint8_t readSync() {
  while(Serial.available() == 0) { }
  return Serial.read();
}

void loop() {
  uint8_t msg_type;
  if(Serial.available() > 0) {
    msg_type = Serial.read();
    
    switch(msg_type) {
      case(SETVALUES):
        SetValues();
        Serial.write(SETVALUES);
        break;
      case(SETRANGE):
        SetRange();
        Serial.write(SETRANGE);
        break;
      case(LERPRANGE):
        LerpRange();
        Serial.write(LERPRANGE);
        break;
      default:
        //Serial.write(255);
        Serial.flush();
        break;
    }
  }
  //else { delay(1); }
}
