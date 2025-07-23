String inputString = "";
bool stringComplete = false;

void setup() {
  Serial.begin(9600);
  for (int i = 2; i <= 13; i++) pinMode(i, OUTPUT);
  for (int i = A0; i <= A5; i++) pinMode(i, OUTPUT);
}

void loop() {
  if (stringComplete) {
    Serial.println("Received: " + inputString);
    int pin = inputString.substring(0, inputString.indexOf(":")).toInt();
    String action = inputString.substring(inputString.indexOf(":")+1);

    if (action == "ON") digitalWrite(pin, HIGH);
    else if (action == "OFF") digitalWrite(pin, LOW);

    inputString = "";
    stringComplete = false;
  }
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') stringComplete = true;
    else inputString += inChar;
  }
}
