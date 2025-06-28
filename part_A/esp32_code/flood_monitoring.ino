#include <Arduino.h>

// Sensor pins
#define trigPin 5
#define echoPin 18
#define FLOW_SENSOR_PIN 27

// Variables for distance measurement
long duration;
float distance;
volatile int flow_frequency = 0; // Measures flow sensor pulses
float flow_rate; // Calculated litres/minute
unsigned long currentTime;
unsigned long cloopTime;

void setup() {
  Serial.begin(115200); // Serial communication with PC or other device

  // Initialize ultrasonic sensor pins
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // Initialize water flow sensor pin
  pinMode(FLOW_SENSOR_PIN, INPUT);
  digitalWrite(FLOW_SENSOR_PIN, HIGH); // Optional internal pull-up

  // Attach Interrupt for Water Flow Sensor
  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN), flow, RISING); // Setup Interrupt
  sei(); // Enable interrupts

  // Initialize timer
  currentTime = millis();
  cloopTime = currentTime;

  Serial.println("Serial Communication Started");
}

void loop() {
  // Measure distance
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2; // Calculate distance in cm

  // Water flow reading every 1 second
  currentTime = millis();
  if (currentTime >= (cloopTime + 1000)) {
    cloopTime = currentTime;

    // Calculate flowrate in litres/minute
    flow_rate = (flow_frequency * 60.0 / 7.5) / 60.0; // Convert L/hour to L/min
    flow_frequency = 0; // Reset for next interval

    // Send data in CSV format: distance,flow_rate
    Serial.print(distance);
    Serial.print(",");
    Serial.println(flow_rate);
  }

  delay(100);
}

void flow() {
  flow_frequency++;
} 