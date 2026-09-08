#include <DHT.h>

// ============================================================
// REAL-TIME MULTI-SENSOR MONITORING SYSTEM
// Arduino Nano
//
// Sensors:
//   - Analog sensor / ADC input
//   - DHT22 temperature and humidity sensor
//   - HC-SR04 ultrasonic distance sensor
//
// Processing:
//   - 5-sample moving-average filter
//   - Threshold-based warning detection
//   - UART serial telemetry
// ============================================================


// ============================================================
// PIN CONFIGURATION
// ============================================================

const int ADC_PIN = A0;

const int STATUS_LED = LED_BUILTIN;

#define DHT_PIN 2
#define DHT_TYPE DHT22

const int TRIG_PIN = 7;
const int ECHO_PIN = 8;


// ============================================================
// DHT22 CONFIGURATION
// ============================================================

DHT dht(DHT_PIN, DHT_TYPE);

float temperature = 0.0;
float humidity = 0.0;

bool dhtValid = false;

unsigned long previousDHTMillis = 0;

const unsigned long DHT_INTERVAL = 2000;


// ============================================================
// HC-SR04 CONFIGURATION
// ============================================================

float distance = 0.0;

bool distanceValid = false;


// ============================================================
// SAMPLING / SERIAL TIMING
// ============================================================

unsigned long previousSampleMillis = 0;
unsigned long previousSerialMillis = 0;

const unsigned long SAMPLE_INTERVAL = 100;
const unsigned long SERIAL_INTERVAL = 500;

unsigned long sequenceNumber = 0;


// ============================================================
// ADC MOVING-AVERAGE FILTER
// ============================================================

const int FILTER_SIZE = 5;

int samples[FILTER_SIZE];

int sampleIndex = 0;

bool filterInitialized = false;


// ------------------------------------------------------------
// Calculate moving average
// ------------------------------------------------------------

int calculateAverage()
{
    long total = 0;

    for (int i = 0; i < FILTER_SIZE; i++)
    {
        total += samples[i];
    }

    return total / FILTER_SIZE;
}


// ============================================================
// HC-SR04 DISTANCE MEASUREMENT
// ============================================================

float readDistance()
{
    // Generate ultrasonic trigger pulse

    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);

    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);

    digitalWrite(TRIG_PIN, LOW);


    // Measure echo pulse duration

    unsigned long duration = pulseIn(
        ECHO_PIN,
        HIGH,
        30000
    );


    // No echo received

    if (duration == 0)
    {
        return -1.0;
    }


    // Convert time to distance

    float measuredDistance =
        duration * 0.0343 / 2.0;


    // Validate measurement

    if (
        measuredDistance < 2.0 ||
        measuredDistance > 300.0
    )
    {
        return -1.0;
    }


    return measuredDistance;
}


// ============================================================
// SETUP
// ============================================================

void setup()
{
    // LED

    pinMode(STATUS_LED, OUTPUT);


    // HC-SR04

    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);

    digitalWrite(TRIG_PIN, LOW);


    // UART

    Serial.begin(9600);


    // DHT22

    dht.begin();


    // Initialize moving-average buffer

    for (int i = 0; i < FILTER_SIZE; i++)
    {
        samples[i] = 0;
    }


    // Firmware identification

    Serial.println("FIRMWARE: MULTI_SENSOR_V2");


    // Allow sensors to stabilize

    delay(2000);
}


// ============================================================
// MAIN LOOP
// ============================================================

void loop()
{
    unsigned long currentMillis = millis();


    // ========================================================
    // SENSOR SAMPLING
    // ========================================================

    if (
        currentMillis - previousSampleMillis
        >= SAMPLE_INTERVAL
    )
    {
        previousSampleMillis = currentMillis;


        // ====================================================
        // ADC ACQUISITION
        // ====================================================

        int rawValue = analogRead(ADC_PIN);


        // ====================================================
        // MOVING-AVERAGE FILTER
        // ====================================================

        if (!filterInitialized)
        {
            // Initialize every filter position
            // with the first measured value.

            for (int i = 0; i < FILTER_SIZE; i++)
            {
                samples[i] = rawValue;
            }

            filterInitialized = true;
        }
        else
        {
            samples[sampleIndex] = rawValue;

            sampleIndex++;

            if (sampleIndex >= FILTER_SIZE)
            {
                sampleIndex = 0;
            }
        }


        int filteredValue = calculateAverage();


        // ====================================================
        // DHT22 ACQUISITION
        // ====================================================

        if (
            currentMillis - previousDHTMillis
            >= DHT_INTERVAL
        )
        {
            previousDHTMillis = currentMillis;


            float newHumidity =
                dht.readHumidity();

            float newTemperature =
                dht.readTemperature();


            if (
                !isnan(newHumidity) &&
                !isnan(newTemperature)
            )
            {
                humidity = newHumidity;
                temperature = newTemperature;

                dhtValid = true;
            }
            else
            {
                dhtValid = false;
            }
        }


        // ====================================================
        // HC-SR04 ACQUISITION
        // ====================================================

        float newDistance = readDistance();


        if (newDistance >= 0)
        {
            distance = newDistance;

            distanceValid = true;
        }
        else
        {
            distanceValid = false;
        }


        // ====================================================
        // THRESHOLD / WARNING DETECTION
        // ====================================================

        bool adcWarning = false;
        bool temperatureWarning = false;
        bool humidityWarning = false;
        bool distanceWarning = false;


        // ADC warning threshold

        if (filteredValue > 900)
        {
            adcWarning = true;
        }


        // Temperature warning threshold

        if (
            dhtValid &&
            temperature > 35.0
        )
        {
            temperatureWarning = true;
        }


        // Humidity warning threshold

        if (
            dhtValid &&
            humidity > 80.0
        )
        {
            humidityWarning = true;
        }


        // Proximity warning threshold

        if (
            distanceValid &&
            distance < 10.0
        )
        {
            distanceWarning = true;
        }


        // Combine all warning conditions

        bool warning =
            adcWarning ||
            temperatureWarning ||
            humidityWarning ||
            distanceWarning;


        // ====================================================
        // STATUS LED
        // ====================================================

        digitalWrite(
            STATUS_LED,
            warning ? HIGH : LOW
        );


        // ====================================================
        // UART TELEMETRY
        // ====================================================

        if (
            currentMillis - previousSerialMillis
            >= SERIAL_INTERVAL
        )
        {
            previousSerialMillis = currentMillis;


            Serial.print("DATA,");

            // Sequence number

            Serial.print(sequenceNumber);
            Serial.print(",");


            // Raw ADC

            Serial.print(rawValue);
            Serial.print(",");


            // Filtered ADC

            Serial.print(filteredValue);
            Serial.print(",");


            // Temperature

            if (dhtValid)
            {
                Serial.print(temperature, 1);
            }
            else
            {
                Serial.print("ERROR");
            }

            Serial.print(",");


            // Humidity

            if (dhtValid)
            {
                Serial.print(humidity, 1);
            }
            else
            {
                Serial.print("ERROR");
            }

            Serial.print(",");


            // Distance

            if (distanceValid)
            {
                Serial.print(distance, 1);
            }
            else
            {
                Serial.print("ERROR");
            }

            Serial.print(",");


            // System status

            if (warning)
            {
                Serial.println("WARNING");
            }
            else
            {
                Serial.println("NORMAL");
            }


            sequenceNumber++;
        }
    }
}