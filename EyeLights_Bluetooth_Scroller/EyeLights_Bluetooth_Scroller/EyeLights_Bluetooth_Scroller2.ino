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

#include <Adafruit_LIS3DH.h>     // For accelerometer
#include <Adafruit_Sensor.h>     // For m/s^2 accel units


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

char message[51] = "HELLO!"; // Scrolling message
int16_t text_x;   // Message position on canvas
int16_t text_delta = -1; // Message position on canvas
int16_t text_min; // Leftmost position before restarting scroll
int16_t text_max; // Rightmost position before restarting scroll

// General variables
char msg1[40];
char msg2[40];
uint8_t r;
uint8_t g;
uint8_t b;

// Scrolling text
bool text_pause = false;
int32_t text_color = 0x00303030;
int16_t text_count = 0;
int16_t text_delay = 2;

// Fixed number text
bool number_enabled = false;
char number_value_1[3] = "00";      // left number
char number_value_2[3] = "00";      // right number
uint8_t number_color_pending = 0;   // 1-shot for setting left/right colors
int32_t number_color1 = 0x00303030;
int32_t number_color2 = 0x00303030;

uint8_t button_pending = 0;

// Tilt and tap
float    filtered_y;        // De-noised accelerometer reading
bool     looking_down;      // Set true when glasses are oriented downward
sensors_event_t event;      // For accelerometer conversion
uint32_t last_tap_time = 0; // For accelerometer tap de-noising
Adafruit_LIS3DH accel;

// Bluetooth
BLEUart bleuart;  // Bluetooth low energy UART
int8_t last_packet_type = 99; // Last BLE packet type, init to nonsense value

// ONE-TIME SETUP ---------

void setup() { // Runs once at program start...

  Serial.begin(115200);
  //while(!Serial);

  // Configure accelerometer and get initial state
  if (! accel.begin())   err("LIS3DH not found", 5);
  accel.setClick(1, 100); // Set threshold for single tap
  accel.getEvent(&event); // Current accel in m/s^2
  // Check accelerometer to see if we've started in the looking-down state,
  // set the target color (what we're aiming for) appropriately. Only the
  // Y axis is needed for this.
  filtered_y = event.acceleration.y;
  looking_down = (filtered_y > 5.0);
  Serial.println(filtered_y);

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
  if (text_count % 1000) {
    // The look-down detection only needs the accelerometer's Y axis.
    // This works with the Glasses Driver mounted on either temple,
    // with the glasses arms "open" (as when worn).
    accel.getEvent(&event);
    // Smooth the accelerometer reading the same way RGB colors are
    // interpolated. This avoids false triggers from jostling around.
    filtered_y = filtered_y * 0.97 + event.acceleration.y * 0.03;
    //Serial.println(filtered_y);


    // The threshold between "looking down" and "looking up" depends
    // on which of those states we're currently in. This is an example
    // of hysteresis in software...a change of direction requires a
    // little extra push before it takes, which avoids oscillating if
    // there was just a single threshold both ways.
    if (looking_down) {       // Currently in the looking-down state...
      (void)accel.getClick(); // Discard any taps while looking down
      if (filtered_y < 3.5) { // Have we crossed the look-up threshold?
        //target_color = colors[color_index]; // Back to list color
        looking_down = false;               // We're looking up now!
        Serial.println("looking_down 1 -> 0");
      }
    } else {                  // Currently in the looking-up state...
      if (filtered_y > 5.0) { // Crossed the look-down threshold?
        //target_color = looking_down_color; // Aim for white
        looking_down = true;               // We're looking down now!
        Serial.println("looking_down 0 -> 1");
      } else if (accel.getClick()) {
        // No look up/down change, but the accelerometer registered
        // a tap. Compare this against the last time we sensed one,
        // and only do things if it's been more than half a second.
        // This avoids spurious double-taps that can occur no matter
        // how carefully the tap threshold was set.
        uint32_t now = millis();
        uint32_t elapsed = now - last_tap_time;
        if (elapsed > 500) {
          // A good tap was detected. Cycle to the next color in
          // the list and note the time of this tap.
          //color_index = (color_index + 1) % NUM_COLORS;
          //target_color = colors[color_index];
          Serial.println("tap");
          last_tap_time = now;
        }
      }
    }
  }

  
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
    //  case 0: // Accelerometer
    //   Serial.println("Accel");
    //   break;
    //  case 1: // Gyro:
    //   Serial.println("Gyro");
    //   break;
    //  case 2: // Magnetometer
    //   Serial.println("Mag");
    //   break;
    //  case 3: // Quaternion
    //   Serial.println("Quat");
    //   break;
     case 4: // Button
      {
        Serial.println("Button");
        char btn = packetbuffer[2];
        char on = packetbuffer[3];
        switch (btn) {
          case '1': 
            number_color_pending = 1;
            break;
          case '2': 
            number_color_pending = 2;
            break;
          case '3': 
            break;
          case '4': 
            break;
          case '5': // up
            if (button_pending == 1) {
              int val = atoi(number_value_1);
              val += 1;
              if (val > 99) val = 99;
              sprintf(number_value_1, "%2d");
            }
            if (button_pending == 2) {
              int val = atoi(number_value_2);
              val += 1;
              if (val > 99) val = 99;
              sprintf(number_value_2, "%2d");
            }
            button_pending = 0;
            break;
          case '6': // down
            if (button_pending == 1) {
              int val = atoi(number_value_1);
              val -= 1;
              if (val < 0) val = 0;
              sprintf(number_value_1, "%2d");
            }
            if (button_pending == 2) {
              int val = atoi(number_value_2);
              val -= 1;
              if (val < 0) val = 0;
              sprintf(number_value_2, "%2d");
            }
            button_pending = 0;
            break;
          case '7': // left
            button_pending = 1;
            break;
          case '8': // right
            button_pending = 2;
            break;
        }
      }
      break;
     case 5: // Color
      {
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
        long int ltemp = 0;
        ltemp = (packetbuffer[2] << 16) | (packetbuffer[3] << 8) | (packetbuffer[4] << 0);
        rgb_apply_level(ltemp);
        switch (number_color_pending) {
          case 1:
            number_color1 = ltemp;
            break;
          case 2:
            number_color2 = ltemp;
            break;
          default:
            text_color = ltemp;
            canvas->setTextColor(glasses.color565(glasses.Color(r, g, b)));
        }
        number_color_pending = 0;
      }
      break;
     case 6: // Location
      Serial.println("Location");
      break;
     default: // -1
      // CLI_MODIFICATIONS
      handle_cli(&bleuart);
    }
    last_packet_type = type; // Save packet type for next pass
  } else {
    last_packet_type = 99; // BLE read timeout, reset last type to nonsense
  }

  clear_text();
  clear_numbers();

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
    text_x += text_delta;
    if (text_x < text_min) {  // If text scrolls off left edge,
      text_x = canvas->width(); // reset position off right edge
    }
    if (text_x > text_max) {  // If text scrolls off right edge,
      text_x = -12 * strlen(message); // estimate reset position off left edge
    }
  }
  

  //DEBUG
  //number_enabled = true;
  //sprintf(msg2, "%04d", text_count);
  //Serial.println(msg2);
  //number_value_1[0] = msg2[0];
  //number_value_1[1] = msg2[1];
  //number_value_2[0] = msg2[2];
  //number_value_2[1] = msg2[3];

  if (!looking_down) {
    if (number_enabled) {
      show_numbers();
    }
    else {
      show_text();
    }
  }
  
  glasses.show();  // MUST call 0x00ffffff() to update matrix
}

// When new message text is assigned, call this to reset its position
// off the right edge and calculate column where scrolling resets.
void reposition_text() {
  uint16_t w, h, ignore;
  canvas->getTextBounds(message, 0, 0, (int16_t *)&ignore, (int16_t *)&ignore, &w, &ignore);
  if (text_delta < 0)
    text_x = canvas->width();
  else
    text_x = -12 * strlen(message);
  text_min = -w; // Off left edge this many pixels
  text_max = 12 * strlen(message); // estimate Off right edge this many pixels
}

// CLI_MODIFICATIONS
void ble_print__(BLEUart *ble, char *text) {
  sprintf(msg1, text);
  ble->write(msg1, strlen(msg1));
}

void ble_print_s(BLEUart *ble, char *text, char *value) {
  sprintf(msg1, text, value);
  ble->write(msg1, strlen(msg1));
}

void ble_print_i(BLEUart *ble, char *text, int value) {
  sprintf(msg1, text, value);
  ble->write(msg1, strlen(msg1));
}

void ble_print_f(BLEUart *ble, char *text, float value) {
  sprintf(msg1, text, value);
  ble->write(msg1, strlen(msg1));
}

void help(BLEUart *ble) {
  // NOTE: try to favor letters over numbers, 
  //       and extra options instead of parameters,
  //       those are easier from Bluefruit Connect app

  // ble->write only transfers 23 chars, so split up writes
  ble_print__(ble, "h - help\n");
  ble_print__(ble, "i - info\n");
  ble_print__(ble, "t - scroll <text>\n");
    ble_print__(ble, " (16 char max)\n");
  ble_print__(ble, "p - pause/start");
    ble_print_i(ble, " (current %d)\n", text_pause);
  ble_print__(ble, "r - rate <int>");
    ble_print_i(ble, " (current %d)\n", text_delay);
  ble_print__(ble, "d - toggle direction");
    ble_print_i(ble, " (current %d)\n", text_delta);
  ble_print__(ble, "c - color <hex>");
    ble_print_i(ble, " (current 0x%08x)\n", text_color);
  ble_print__(ble, "n - numbers ie. 01 05 or _1 _3");
    sprintf(msg2, " (current %s %s)", number_value_1, number_value_2);
    ble_print_s(ble, " %s\n", msg2);
  ble_print__(ble, "1 - set color 1\n");
  ble_print__(ble, "2 - set color 2\n");
}

void info(BLEUart *ble) {
  ble_print__(ble, "text:          ");    
    ble_print_s(ble, "%s\n", message);
  ble_print__(ble, "text_pause:    ");
    ble_print_i(ble, "%d\n", text_pause);
  ble_print__(ble, "text_rate:     ");
    ble_print_i(ble, "%d\n", text_delay);
  ble_print__(ble, "text_color:    ");
    ble_print_i(ble, "0x%08x\n", text_color);
  ble_print__(ble, "numbers:       ");    
    sprintf(msg2, " (current %s %s)", number_value_1, number_value_2);
    ble_print_s(ble, " %s\n", msg2);
  ble_print__(ble, "number_color1: ");
    ble_print_i(ble, "0x%08x\n", number_color1);
  ble_print__(ble, "number_color2: ");
    ble_print_i(ble, "0x%08x\n", number_color2);
}

void rgb_apply_level(int32_t given_color) {
  r = ((given_color & 0x00ff0000) >> 16);
  g = ((given_color & 0x0000ff00) >> 8);
  b = ((given_color & 0x000000ff) >> 0);
}

void handle_cli(BLEUart *ble) {
  char option = packetbuffer[0]; // ie. "s this is message"  or "p"
  char *ptr;
  int itemp = 0;
  long int ltemp = 0;
  float ftemp = 0;

  ptr = (char *)packetbuffer;
  ptr[strcspn(ptr, "\n")] = 0;
  switch (option) {
    case 'i':
      info(ble);
      break;
    case 't':
      number_enabled = false;
      ptr++;
      if (*ptr == ' ') {
        ptr++;
      if (*ptr) {
        strncpy(message, ptr, 50);
        ptr = message;
        while (*ptr) {
          *ptr = toupper((unsigned char) *ptr);
          ptr++;
        }
      }
      button_pending = 0;
      break;
    case 'p':
      text_pause = !text_pause;
      break;
    case 'r':
      itemp = atoi(ptr);
      if (itemp >= 1 && itemp <= 100) text_delay = itemp;
     break;
    case 'd':
      text_delta = -1 * text_delta;
     break;
    case 'c':
      ptr++;
      if (*ptr == ' ') {
        ptr++;
        if (*ptr) {
          ltemp = strtol(ptr, NULL, 16);
          switch (number_color_pending) {
            case 1:
              number_color1 = ltemp;
              break;
            case 2:
              number_color2 = ltemp;
              break;
            default:
              text_color = ltemp;
          }
        }
      }
      number_color_pending = 0;
      break;
    case 'n':
      // ie. n 01 02 or _1 _4
      // TODO: should expand parsing numbers
      number_value_1[0] = *ptr;
      ptr++;
      number_value_1[1] = *ptr;
      ptr++;
      ptr++;
      number_value_2[0] = *ptr;
      ptr++;
      number_value_2[1] = *ptr;
      ptr++;
      number_enabled = true;
      button_pending = 0;
      break;
    case '1':
      number_color_pending = 1;
      break;
    case '2':
      number_color_pending = 2;
      break;
    default:
      help(ble);
      break;
  }

  sprintf(msg1, "\noption > ");  ble->write(msg1, strlen(msg1));
}

void clear_text() {
  canvas->fillScreen(0); // Clear the whole drawing canvas
}

void show_text() {
  rgb_apply_level(text_color);
  canvas->setTextColor(glasses.color565(glasses.Color(r, g, b)));
  canvas->setCursor(text_x, canvas->height());
  canvas->print(message);
  glasses.scale(); // 1:3 downsample canvas to LED matrix
}

void clear_numbers() {
  glasses.left_ring.fill(0);
  glasses.right_ring.fill(0);

  digit(' ', 1, 0x00000000);
  digit(' ', 2, 0x00000000);
  digit(' ', 3, 0x00000000);
  digit(' ', 4, 0x00000000);
}

void show_numbers() {
  //glasses.left_ring.fill(0);
  //glasses.right_ring.fill(0);

  rgb_apply_level(number_color1);
  digit(number_value_1[0], 1, glasses.color565(glasses.Color(r, g, b)));
  digit(number_value_1[1], 2, glasses.color565(glasses.Color(r, g, b)));
  rgb_apply_level(number_color2);
  digit(number_value_2[0], 3, glasses.color565(glasses.Color(r, g, b)));
  digit(number_value_2[1], 4, glasses.color565(glasses.Color(r, g, b)));

  // possible left ring side
  //glasses.left_ring.setPixelColor(18, number_color1);
  //glasses.left_ring.setPixelColor(19, number_color1);

  // possible right ring side
  //glasses.right_ring.setPixelColor(5, number_color2);
  //glasses.right_ring.setPixelColor(6, number_color2);

  // possible middle dash
  //glasses.drawPixel(8, 2, number_color1);
  //glasses.drawPixel(9, 2, number_color2);

}


int pixels[11][5][3] = {
    {
      {1, 1, 1}, 
      {1, 0, 1}, 
      {1, 0, 1}, 
      {1, 0, 1}, 
      {1, 1, 1}
    },
    {
      {0, 0, 1}, 
      {0, 0, 1}, 
      {0, 0, 1}, 
      {0, 0, 1}, 
      {0, 0, 1}
    },
    {
      {1, 1, 1}, 
      {0, 0, 1}, 
      {1, 1, 1}, 
      {1, 0, 0}, 
      {1, 1, 1}
    },
    {
      {1, 1, 1}, 
      {0, 0, 1}, 
      {1, 1, 1}, 
      {0, 0, 1}, 
      {1, 1, 1}
    },
    {
      {1, 0, 1}, 
      {1, 0, 1}, 
      {1, 1, 1}, 
      {0, 0, 1}, 
      {0, 0, 1}
    },
    {
      {1, 1, 1}, 
      {1, 0, 0}, 
      {1, 1, 1}, 
      {0, 0, 1}, 
      {1, 1, 1}
    },
    {
      {1, 0, 0}, 
      {1, 0, 0}, 
      {1, 1, 1}, 
      {1, 0, 1}, 
      {1, 1, 1}
    },
    {
      {1, 1, 1}, 
      {0, 0, 1}, 
      {0, 0, 1}, 
      {0, 0, 1}, 
      {0, 0, 1}
    },
    {
      {1, 1, 1}, 
      {1, 0, 1}, 
      {1, 1, 1}, 
      {1, 0, 1}, 
      {1, 1, 1}
    },
    {
      {1, 1, 1}, 
      {1, 0, 1}, 
      {1, 1, 1}, 
      {0, 0, 1}, 
      {0, 0, 1}
    },
    {
      {0, 0, 0}, 
      {0, 0, 0}, 
      {0, 0, 0}, 
      {0, 0, 0}, 
      {0, 0, 0}
    }
  };

void digit(char value, int slot, int32_t pixel_color) {
  int x, y;
  int x_offset = 0;
  int index = 10;
  switch (slot) {
    case 1: x_offset = 1; break;
    case 2: x_offset = 5; break;
    case 3: x_offset = 10; break;
    case 4: x_offset = 14; break;
    default: break;
  }
  if (value >= '0' && value <= '9') {
    index = value - '0';
  }
  for (y = 0; y < 5; y++) {
    for (x = 0; x < 3; x++) {
      if (pixels[index][y][x]) {
        glasses.drawPixel(x_offset+x, y, pixel_color);
      }
      else {
         glasses.drawPixel(x_offset+x, y, 0x00000000);       
      }
    }
  }
}



// TODO mark possession

// reset
// battery
// TODO refactor cli as library file
