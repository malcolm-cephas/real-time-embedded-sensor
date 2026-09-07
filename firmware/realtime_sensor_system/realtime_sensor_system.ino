const int STATUS_LED = LED_BUILTIN;

// -------------------------
// Timing configuration
// -------------------------
unsigned long previousMillis = 0;
const unsigned long sampleInterval = 100;

unsigned long previousSerialMillis = 0;
const unsigned long serialInterval = 500;

// -------------------------
// Packet sequence
// -------------------------
unsigned long sequenceNumber = 0;

// -------------------------
// LED state
// -------------------------
bool ledState = false;

// -------------------------
// Moving-average filter
// -------------------------
const int FILTER_SIZE = 5;

int samples[FILTER_SIZE];
int sampleIndex = 0;

bool filterInitialized = false;

// -------------------------
// Calculate moving average
// -------------------------
int calculateAverage()
{
    long total = 0;

    for (int i = 0; i < FILTER_SIZE; i++)
    {
        total += samples[i];
    }

    return total / FILTER_SIZE;
}

// -------------------------
// Setup
// -------------------------
void setup()
{
    pinMode(STATUS_LED, OUTPUT);

    Serial.begin(9600);

    // Seed random number generator
    randomSeed(analogRead(A0));

    // Firmware identification
    Serial.println("FIRMWARE: FILTER_INIT_V2");

    // Initialize filter buffer
    for (int i = 0; i < FILTER_SIZE; i++)
    {
        samples[i] = 0;
    }
}

// -------------------------
// Main loop
// -------------------------
void loop()
{
    unsigned long currentMillis = millis();

    // -------------------------
    // Sample every 100 ms
    // -------------------------
    if (currentMillis - previousMillis >= sampleInterval)
    {
        previousMillis = currentMillis;

        // -------------------------
        // Generate realistic test signal
        // Base signal:
        // 500 +/- 400
        // -------------------------
        int baseValue = 500 + 400 * sin(millis() / 2000.0);

        // Add random noise
        int noise = random(-30, 31);

        int rawValue = baseValue + noise;

        // Keep ADC value within 10-bit ADC range
        rawValue = constrain(rawValue, 0, 1023);

        // -------------------------
        // Initialize filter using
        // first valid measurement
        // -------------------------
        if (!filterInitialized)
        {
            for (int i = 0; i < FILTER_SIZE; i++)
            {
                samples[i] = rawValue;
            }

            filterInitialized = true;
        }
        else
        {
            // Add new sample to circular buffer
            samples[sampleIndex] = rawValue;

            sampleIndex++;

            if (sampleIndex >= FILTER_SIZE)
            {
                sampleIndex = 0;
            }
        }

        // -------------------------
        // Calculate filtered value
        // -------------------------
        int filteredValue = calculateAverage();

        // -------------------------
        // Threshold detection
        // -------------------------
        bool warning = filteredValue > 800;

        // LED indicates warning state
        digitalWrite(STATUS_LED, warning ? HIGH : LOW);

        // -------------------------
        // Send telemetry every 500 ms
        // -------------------------
        if (currentMillis - previousSerialMillis >= serialInterval)
        {
            previousSerialMillis = currentMillis;

            Serial.print("DATA,");
            Serial.print(sequenceNumber);
            Serial.print(",");
            Serial.print(rawValue);
            Serial.print(",");
            Serial.print(filteredValue);
            Serial.print(",");

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