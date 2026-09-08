import serial
import csv
import os
from datetime import datetime

# =========================
# Serial Configuration
# =========================

PORT = "COM5"
BAUD_RATE = 9600

# =========================
# Correct project paths
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "sensor_data.csv")

# Create data folder if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

print("Data file:", DATA_FILE)

# =========================
# Connect to Arduino
# =========================

ser = serial.Serial(PORT, BAUD_RATE, timeout=1)

print("Connected to Arduino Nano")
print("Waiting for data...")

# =========================
# Create/open CSV
# =========================

file_exists = os.path.exists(DATA_FILE)

with open(DATA_FILE, "a", newline="") as file:

    writer = csv.writer(file)

    # Create header if file is new
    if not file_exists or os.path.getsize(DATA_FILE) == 0:

        writer.writerow([
            "timestamp",
            "sequence",
            "raw_value",
            "filtered_value",
            "temperature",
            "humidity",
            "distance",
            "status"
        ])

        file.flush()

        print("Created CSV file.")

    # =========================
    # Receive data
    # =========================

    while True:

        line = ser.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()

        if not line:
            continue

        print(line)

        # Ignore firmware messages
        if not line.startswith("DATA,"):
            continue

        parts = line.split(",")

        # Expected:
        #
        # DATA,
        # sequence,
        # raw,
        # filtered,
        # temperature,
        # humidity,
        # distance,
        # status

        if len(parts) != 8:
            print("Invalid packet:", line)
            continue

        try:

            sequence = int(parts[1])
            raw_value = int(parts[2])
            filtered_value = int(parts[3])

            # Sensor values may occasionally be ERROR
            if parts[4] == "ERROR":
                temperature = ""
            else:
                temperature = float(parts[4])

            if parts[5] == "ERROR":
                humidity = ""
            else:
                humidity = float(parts[5])

            if parts[6] == "ERROR":
                distance = ""
            else:
                distance = float(parts[6])

            status = parts[7]

            timestamp = datetime.now().isoformat()

            writer.writerow([
                timestamp,
                sequence,
                raw_value,
                filtered_value,
                temperature,
                humidity,
                distance,
                status
            ])

            file.flush()

        except ValueError:

            print("Invalid data:", line)