import serial
import csv
from datetime import datetime
from pathlib import Path

# Arduino serial configuration
PORT = "COM5"
BAUD_RATE = 9600

# Project data directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_FILE = DATA_DIR / "sensor_data.csv"
last_sequence = None

# Create data directory if it doesn't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Connect to Arduino
ser = serial.Serial(PORT, BAUD_RATE, timeout=1)

print("Connected to Arduino Nano")
print("Waiting for data...")

# Open CSV file
with open(DATA_FILE, "a", newline="") as file:

    writer = csv.writer(file)

    # Add header if the file is empty
    if DATA_FILE.stat().st_size == 0:
        writer.writerow([
            "timestamp",
            "sequence",
            "raw_value",
            "filtered_value",
            "status"
        ])

    while True:

        line = ser.readline().decode("utf-8").strip()

        if not line:
            continue

        print(line)

        parts = line.split(",")

        # Expected:
        # DATA,sequence,raw,filtered,status
        if len(parts) != 5:
            print("Invalid packet:", line)
            continue

        packet_type = parts[0]

        if packet_type != "DATA":
            print("Unknown packet type:", line)
            continue

        try:
            sequence = int(parts[1])
            raw_value = int(parts[2])
            filtered_value = int(parts[3])
            status = parts[4]
        except ValueError:
            print("Invalid numeric data:", line)
            continue

        if last_sequence is not None:

            expected_sequence = last_sequence + 1

            if sequence != expected_sequence:

                if sequence > expected_sequence:
                    print(
                        f"WARNING: Missing packet(s) "
                        f"{expected_sequence} to {sequence - 1}"
                    )

                elif sequence <= last_sequence:
                    print(
                        f"WARNING: Unexpected sequence number {sequence}"
                    )

        last_sequence = sequence
        # Validate measurement ranges
        if not (0 <= raw_value <= 1023):
            print(f"Invalid raw ADC value: {raw_value}")
            continue

        if not (0 <= filtered_value <= 1023):
            print(f"Invalid filtered ADC value: {filtered_value}")
            continue

        # Validate status
        if status not in ("NORMAL", "WARNING"):
            print(f"Invalid status: {status}")
            continue
            
        timestamp = datetime.now().isoformat()

        writer.writerow([
            timestamp,
            sequence,
            raw_value,
            filtered_value,
            status
        ])

        file.flush()