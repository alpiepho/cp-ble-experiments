// SPDX-FileCopyrightText: 2021 Phil Burgess for Adafruit Industries
//
// SPDX-License-Identifier: MIT

/*
BLUETOOTH SCROLLING MESSAGE for Adafruit EyeLights (LED Glasses + Driver).
Use BLUEFRUIT CONNECT app on iOS or Android to connect to LED glasses.
Use the app's UART input to enter a new message.
Use the app's Color Picker (under "Controller") to change text color.
This is based on the glassesdemo-3-smooth example from the
Adafruit_IS31FL3741 library, with Bluetooth additions on top. If this
code all seems a bit too much, you can start with that example (or the two
that precede it) to gain an understanding of the LED glasses basics, then
return here to see what the extra Bluetooth layers do.
*/

#include <Adafruit_IS31FL3741.h> // For LED driver
#include <bluefruit.h>           // For Bluetooth communication
#include <EyeLightsCanvasFont.h> // Smooth scrolly font for glasses

// These items are over in the packetParser.cpp tab:
extern uint8_t packetbuffer[];
extern uint8_t readPacket(BLEUart *ble, uint16_t timeout);
extern int8_t packetType(uint8_t *buf, uint8_t len);
extern float parsefloat(uint8_t *buffer);
extern void printHex(const uint8_t * data, const uint32_t numBytes);

// GLOBAL VARIABLES -------

// 'Buffered' glasses for buttery animation,
// 'true' to allocate a drawing canvas for smooth graphics:
Adafruit_EyeLights_buffered glasses(true);
GFXcanvas16 *canvas; // Pointer to glasses' canvas object
// Because 'canvas' is a pointer, always use -> when calling
// drawing functions there. 'glasses' is an object in itself,
// so . is used when calling its functions.

char message[51] = "HELLO WORLD!"; // Scrolling message
int16_t text_x;   // Message position on canvas
int16_t text_min; // Leftmost position before restarting scroll

// CLI_MODIFICATIONS
bool text_pause = false;
float text_level = 1.0;
int32_t text_color = 0x00303030;
int16_t text_count = 0;
int16_t text_delay = 2;
char msg[40];
uint8_t r;
uint8_t g;
uint8_t b;

BLEUart bleuart;  // Bluetooth low energy UART

int8_t last_packet_type = 99; // Last BLE packet type, init to nonsense value

// ONE-TIME SETUP ---------

void setup() { // Runs once at program start...

  Serial.begin(115200);
  //while(!Serial);

  // Configure and start the BLE UART service
  Bluefruit.begin();
  Bluefruit.setTxPower(4);
  bleuart.begin();
  startAdv(); // Set up and start advertising

  if (!glasses.begin()) err("IS3741 not found", 2);

  canvas = glasses.getCanvas();
  if (!canvas) err("Can't allocate canvas", 5);

  // Configure glasses for full brightness and enable output
  glasses.setLEDscaling(0xFF);
  glasses.setGlobalCurrent(0xFF);
  glasses.enable(true);

  // Set up for scrolling text, initialize color and position
  canvas->setFont(&EyeLightsCanvasFont);
  canvas->setTextWrap(false); // Allow text to extend off edges
  canvas->setTextColor(glasses.color565(0x303030)); // Dim white to start
  reposition_text(); // Sets up initial position & scroll limit
}

// Crude error handler, prints message to Serial console, flashes LED
void err(char *str, uint8_t hz) {
  Serial.println(str);
  pinMode(LED_BUILTIN, OUTPUT);
  for (;;) digitalWrite(LED_BUILTIN, (millis() * hz / 500) & 1);
}

// Set up, start BLE advertising
void startAdv(void) {
  // Advertising packet
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();
  
  // Include the BLE UART (AKA 'NUS') 128-bit UUID
  Bluefruit.Advertising.addService(bleuart);

  // Secondary Scan Response packet (optional)
  // Since there is no room for 'Name' in Advertising packet
  Bluefruit.ScanResponse.addName();

  // Start Advertising
  // - Enable auto advertising if disconnected
  // - Interval:  fast mode = 20 ms, slow mode = 152.5 ms
  // - Timeout for fast mode is 30 seconds
  // - Start(timeout) with timeout = 0 will advertise forever (until connected)
  // 
  // For recommended advertising interval
  // https://developer.apple.com/library/content/qa/qa1931/_index.html   
  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.setInterval(32, 244); // in unit of 0.625 ms
  Bluefruit.Advertising.setFastTimeout(30);   // number of seconds in fast mode
  Bluefruit.Advertising.start(0);             // 0 = Don't stop advertising after n seconds  
}

// MAIN LOOP --------------

void loop() { // Repeat forever...
  uint8_t text_on = 0;
  // The packet read timeout (9 ms here) also determines the text
  // scrolling speed -- if no data is received over BLE in that time,
  // the function exits and returns here with len=0.
  uint8_t len = readPacket(&bleuart, 9);
  if (len) {
    int8_t type =  packetType(packetbuffer, len);
    // The Bluefruit Connect app can return a variety of data from
    // a phone's sensors. To keep this example relatively simple,
    // we'll only look at color and text, but here's where others
    // would go if we were to extend this. See Bluefruit library
    // examples for the packet data formats. packetParser.cpp
    // has a couple functions not used in this code but that may be
    // helpful in interpreting these other packet types.
    switch(type) {
     case 0: // Accelerometer
      Serial.println("Accel");
      break;
     case 1: // Gyro:
      Serial.println("Gyro");
      break;
     case 2: // Magnetometer
      Serial.println("Mag");
      break;
     case 3: // Quaternion
      Serial.println("Quat");
      break;
     case 4: // Button
      Serial.println("Button");
      break;
     case 5: // Color
      Serial.println("Color");
      // packetbuffer[2] through [4] contain R, G, B byte values.
      // Because the drawing canvas uses lower-precision '565' color,
      // and because glasses.scale() applies gamma correction and may
      // quantize the dimmest colors to 0, set a brightness floor here
      // so text isn't invisible.
      for (uint8_t i=2; i<=4; i++) {
        if (packetbuffer[i] < 0x20) packetbuffer[i] = 0x20;
      }
      // CLI_MODIFICATIONS - save color
      text_color = (packetbuffer[2] << 16) | (packetbuffer[3] << 8) | (packetbuffer[4] << 0);
      r = packetbuffer[2];
      g = packetbuffer[3];
      b = packetbuffer[4];
      r = (uint8_t)(text_level * r);
      g = (uint8_t)(text_level * g);
      b = (uint8_t)(text_level * b);
      canvas->setTextColor(glasses.color565(glasses.Color(r, g, b)));
      break;
     case 6: // Location
      Serial.println("Location");
      break;
     default: // -1
      // CLI_MODIFICATIONS
#if 1
      handle_cli(&bleuart);
#else
      // Packet is not one of the Bluefruit Connect types. Most programs
      // will ignore/reject it as not valud, but in this case we accept
      // it as a freeform string for the scrolling message.
      if (last_packet_type != -1) {
        // If prior data was a packet, this is a new freeform string,
        // initialize the message string with it...
        strncpy(message, (char *)packetbuffer, 20);
      } else {
        // If prior data was also a freeform string, concatenate this onto
        // the message (up to the max message length). BLE packets can only
        // be so large, so long strings are broken into multiple packets.
        uint8_t message_len = strlen(message);
        uint8_t max_append = sizeof message - 1 - message_len;
        strncpy(&message[message_len], (char *)packetbuffer, max_append);
        len = message_len + max_append;
      }
      message[len] = 0; // End of string NUL char
      Serial.println(message);
      reposition_text(); // Reset text off right edge of canvas
#endif
    }
    last_packet_type = type; // Save packet type for next pass
  } else {
    last_packet_type = 99; // BLE read timeout, reset last type to nonsense
  }

  canvas->fillScreen(0); // Clear the whole drawing canvas

  // CLI_MODIFICATIONS
  text_on = !text_pause;
  if (text_on) {
    if ((text_count % text_delay) != 0) {
      text_on = 0; // delay
    }
  }
  text_count++;

  if (text_on) {
    // Update text to new position, and draw on canvas
    if (--text_x < text_min) {  // If text scrolls off left edge,
      text_x = canvas->width(); // reset position off right edge
    }
  }
  
  canvas->setCursor(text_x, canvas->height());
  canvas->print(message);
  glasses.scale(); // 1:3 downsample canvas to LED matrix
  glasses.show();  // MUST call show() to update matrix
}

// When new message text is assigned, call this to reset its position
// off the right edge and calculate column where scrolling resets.
void reposition_text() {
  uint16_t w, h, ignore;
  canvas->getTextBounds(message, 0, 0, (int16_t *)&ignore, (int16_t *)&ignore, &w, &ignore);
  text_x = 0; //canvas->width();
  text_min = -w; // Off left edge this many pixels
}

// CLI_MODIFICATIONS
void help(BLEUart *ble) {
  // NOTE: try to favor letters over numbers, 
  //       and extra options instead of parameters,
  //       those are easier from Bluefruit Connect app

  // ble->write only transfers 23 chars, so split up writes
  sprintf(msg, "h - help\n");                           ble->write(msg, strlen(msg));
  sprintf(msg, "i - info\n");                           ble->write(msg, strlen(msg));
  sprintf(msg, "s - scroll <text>\n");                  ble->write(msg, strlen(msg));
    sprintf(msg, " (16 char max)\n");                   ble->write(msg, strlen(msg));
  sprintf(msg, "p - pause/start");                      ble->write(msg, strlen(msg));
    sprintf(msg, " (current %d)\n", text_pause);        ble->write(msg, strlen(msg));
  sprintf(msg, "r - rate <int>");                       ble->write(msg, strlen(msg));
    sprintf(msg, " (current %d)\n", text_delay);        ble->write(msg, strlen(msg));
  sprintf(msg, "b - brighness <float>");                ble->write(msg, strlen(msg));
    sprintf(msg, " (current %.2f)\n", text_level);      ble->write(msg, strlen(msg));
  sprintf(msg, "c - color <hex>");                      ble->write(msg, strlen(msg));
    sprintf(msg, " (current 0x%08x)\n", text_color);    ble->write(msg, strlen(msg));
}

void info(BLEUart *ble) {
  sprintf(msg, "text_x:        ");        ble->write(msg, strlen(msg));
    sprintf(msg, "%d\n", text_x);         ble->write(msg, strlen(msg));
  sprintf(msg, "text_min:      ");        ble->write(msg, strlen(msg));
    sprintf(msg, "%d\n", text_min);       ble->write(msg, strlen(msg));
  sprintf(msg, "text_pause:    ");        ble->write(msg, strlen(msg));
    sprintf(msg, "%d\n", text_pause);     ble->write(msg, strlen(msg));
  sprintf(msg, "text_rate:     ");        ble->write(msg, strlen(msg));
    sprintf(msg, "%d\n", text_delay);     ble->write(msg, strlen(msg));
  sprintf(msg, "text_level:    ");        ble->write(msg, strlen(msg));
    sprintf(msg, "%.2f\n", text_level);   ble->write(msg, strlen(msg));
  sprintf(msg, "text_color:    ");        ble->write(msg, strlen(msg));
    sprintf(msg, "0x%08x\n", text_color); ble->write(msg, strlen(msg));
}

void handle_cli(BLEUart *ble) {
  char option = packetbuffer[0]; // ie. "s this is message"  or "p"
  char *ptr;
  int itemp = 0;
  long int ltemp = 0;
  float ftemp = 0;

  ptr = (char *)packetbuffer+2;
  switch (option) {
    case 'i':
      info(ble);
      break;
    case 'p':
      text_pause = !text_pause;
      break;
    case 'b':
      ftemp = atof(ptr);
      if (ftemp > 0 && ftemp <= 1.0) text_level = ftemp;
      r = ((text_color & 0x00ff0000) >> 16);
      g = ((text_color & 0x0000ff00) >> 8);
      b = ((text_color & 0x000000ff) >> 0);
      r = (uint8_t)(text_level * r);
      g = (uint8_t)(text_level * g);
      b = (uint8_t)(text_level * b);
      canvas->setTextColor(glasses.color565(glasses.Color(r, g, b)));
      break;
    case 'r':
      itemp = atoi(ptr);
      if (itemp >= 1 && itemp <= 100) text_delay = itemp;
     break;
    case 's':
      strncpy(message, ptr, 50);
      break;
    case 'c':
      ltemp = strtol(ptr, NULL, 16);
      text_color = ltemp;
      r = ((text_color & 0x00ff0000) >> 16);
      g = ((text_color & 0x0000ff00) >> 8);
      b = ((text_color & 0x000000ff) >> 0);
      r = (uint8_t)(text_level * r);
      g = (uint8_t)(text_level * g);
      b = (uint8_t)(text_level * b);
      canvas->setTextColor(glasses.color565(glasses.Color(r, g, b)));
      break;
    default:
      help(ble);
      break;
  }
  sprintf(msg, "\noption > ");  ble->write(msg, strlen(msg));
}

// TODO fixed letters points
// TODO color zones/regions
// TODO refactor color setting
// TODO refactor ble write
