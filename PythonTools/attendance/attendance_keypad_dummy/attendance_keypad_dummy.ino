#include <Arduino.h>
#include <SSD1306Ascii.h>
#include <SSD1306AsciiAvrI2c.h>

// Setup screen
#define I2C_ADDRESS 0x3C
SSD1306AsciiAvrI2c oled; // Screen object

void setup() {
  // Initialize serial communication
  Serial.begin(9600);

  // Initialize OLED screen
  oled.begin(&Adafruit128x32, I2C_ADDRESS);
  oled.setFont(Adafruit5x7);
  oled.clear();
  oled.set1X();
  oled.println(F("ATTENDANCE"));

  // Seed for random number generation
  randomSeed(analogRead(0));
}

void loop() {
  // Generate a random ID between 100 and 130
  int randomID = random(100, 131); // 131 because upper limit is exclusive

  // Display the ID on the OLED screen
  oled.clear();
  oled.println(F("ID:"));
  oled.println(randomID);

  // Send the ID over serial
  Serial.println(randomID);

  // Initialize variables for handshake waiting
  unsigned long startTime = millis();
  bool handshakeReceived = false;

  // Wait for handshake message with timeout
  while (millis() - startTime < 10000) {  // 10-second timeout
    if (Serial.available()) {
      String handshakeMsg = Serial.readStringUntil('\n');

      // Check if the handshake message is valid
      if (handshakeMsg.startsWith("ACK,")) {
        String studentName = handshakeMsg.substring(4); // Extract name from message
        oled.clear();
        oled.println("ID Accepted:");
        oled.println(studentName);
        handshakeReceived = true;
        break;  // Exit the loop if handshake is received
      }
    }
  }

  // Handle cases where no valid handshake was received
  if (!handshakeReceived) {
    oled.clear();
    oled.println("No response or");
    oled.println("Invalid handshake.");
  }

  // Wait for some time before generating the next ID
  delay(5000); // Delay for 5 seconds
}
