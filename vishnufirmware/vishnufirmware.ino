#define LED_PIN 13  // Onboard LED

unsigned long lastBlink = 0;
const unsigned long interval = 1000; // 1 second
bool ledState = false;

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);

  delay(1000);  // Give time for USB to stabilize

  // Print firmware info on boot
  Serial.println("=== VishnuFirm ===");
  Serial.println("Version: 1.0.0");
  Serial.println("==================");
}

void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - lastBlink >= interval) {
    lastBlink = currentMillis;

    // Toggle LED
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState);

    // Print LED state
    if (ledState)
      Serial.println("LED ON");
    else
      Serial.println("LED OFF");
  }
}
