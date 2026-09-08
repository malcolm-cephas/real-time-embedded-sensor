import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# Locate project files
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = PROJECT_ROOT / "data" / "sensor_data.csv"

OUTPUT_DIR = PROJECT_ROOT / "data" / "plots"
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================
# Load data
# ============================================================

df = pd.read_csv(DATA_FILE)

print("\n=== MULTI-SENSOR DATA ANALYSIS ===")

print(f"Total samples: {len(df)}")

# ============================================================
# ADC ANALYSIS
# ============================================================

print("\n=== ADC Analysis ===")

print(f"Minimum raw value: {df['raw_value'].min()}")
print(f"Maximum raw value: {df['raw_value'].max()}")
print(f"Average raw value: {df['raw_value'].mean():.2f}")

print(f"Minimum filtered value: {df['filtered_value'].min()}")
print(f"Maximum filtered value: {df['filtered_value'].max()}")
print(f"Average filtered value: {df['filtered_value'].mean():.2f}")

# ============================================================
# FILTERING ANALYSIS
# ============================================================

df["filter_difference"] = (
    df["raw_value"] - df["filtered_value"]
)

df["absolute_difference"] = (
    df["filter_difference"].abs()
)

mean_absolute_difference = (
    df["absolute_difference"].mean()
)

maximum_difference = (
    df["absolute_difference"].max()
)

difference_std = (
    df["filter_difference"].std()
)

raw_std = df["raw_value"].std()
filtered_std = df["filtered_value"].std()

if raw_std != 0:
    variation_reduction = (
        (raw_std - filtered_std) / raw_std
    ) * 100
else:
    variation_reduction = 0

print("\n=== Filtering Analysis ===")

print(
    f"Mean absolute raw-filtered difference: "
    f"{mean_absolute_difference:.2f}"
)

print(
    f"Maximum absolute raw-filtered difference: "
    f"{maximum_difference:.2f}"
)

print(
    f"Standard deviation of filtering difference: "
    f"{difference_std:.2f}"
)

print(
    f"Raw standard deviation: "
    f"{raw_std:.2f}"
)

print(
    f"Filtered standard deviation: "
    f"{filtered_std:.2f}"
)

print(
    f"Variation reduction: "
    f"{variation_reduction:.2f}%"
)

# ============================================================
# TEMPERATURE ANALYSIS
# ============================================================

print("\n=== Temperature Analysis ===")

temperature_data = pd.to_numeric(
    df["temperature"],
    errors="coerce"
).dropna()

if len(temperature_data) > 0:

    print(
        f"Minimum temperature: "
        f"{temperature_data.min():.1f} °C"
    )

    print(
        f"Maximum temperature: "
        f"{temperature_data.max():.1f} °C"
    )

    print(
        f"Average temperature: "
        f"{temperature_data.mean():.2f} °C"
    )

else:

    print("No valid temperature data available.")

# ============================================================
# HUMIDITY ANALYSIS
# ============================================================

print("\n=== Humidity Analysis ===")

humidity_data = pd.to_numeric(
    df["humidity"],
    errors="coerce"
).dropna()

if len(humidity_data) > 0:

    print(
        f"Minimum humidity: "
        f"{humidity_data.min():.1f} %"
    )

    print(
        f"Maximum humidity: "
        f"{humidity_data.max():.1f} %"
    )

    print(
        f"Average humidity: "
        f"{humidity_data.mean():.2f} %"
    )

else:

    print("No valid humidity data available.")

# ============================================================
# DISTANCE ANALYSIS
# ============================================================

print("\n=== Distance Analysis ===")

distance_data = pd.to_numeric(
    df["distance"],
    errors="coerce"
).dropna()

if len(distance_data) > 0:

    print(
        f"Minimum distance: "
        f"{distance_data.min():.1f} cm"
    )

    print(
        f"Maximum distance: "
        f"{distance_data.max():.1f} cm"
    )

    print(
        f"Average distance: "
        f"{distance_data.mean():.2f} cm"
    )

else:

    print("No valid distance data available.")

# ============================================================
# WARNING ANALYSIS
# ============================================================

warning_count = (
    df["status"] == "WARNING"
).sum()

warning_percentage = (
    warning_count / len(df)
) * 100

print("\n=== Warning Analysis ===")

print(f"Warning samples: {warning_count}")
print(f"Warning percentage: {warning_percentage:.2f}%")

# ============================================================
# Plot 1 — Raw vs Filtered ADC
# ============================================================

plt.figure(figsize=(10, 5))

plt.plot(
    df["sequence"],
    df["raw_value"],
    label="Raw ADC"
)

plt.plot(
    df["sequence"],
    df["filtered_value"],
    label="Filtered ADC"
)

plt.axhline(
    y=800,
    linestyle="--",
    label="Warning Threshold"
)

plt.xlabel("Sequence Number")
plt.ylabel("ADC Value")

plt.title(
    "ADC Sensor Data: Raw vs Filtered"
)

plt.legend()
plt.grid(True)
plt.tight_layout()

adc_plot = OUTPUT_DIR / "adc_raw_vs_filtered.png"

plt.savefig(
    adc_plot,
    dpi=150
)

plt.close()

# ============================================================
# Plot 2 — Temperature
# ============================================================

if len(temperature_data) > 0:

    plt.figure(figsize=(10, 5))

    plt.plot(
        df["sequence"],
        pd.to_numeric(
            df["temperature"],
            errors="coerce"
        ),
        label="Temperature"
    )

    plt.xlabel("Sequence Number")
    plt.ylabel("Temperature (°C)")

    plt.title(
        "DHT22 Temperature"
    )

    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    temperature_plot = (
        OUTPUT_DIR / "temperature.png"
    )

    plt.savefig(
        temperature_plot,
        dpi=150
    )

    plt.close()

# ============================================================
# Plot 3 — Humidity
# ============================================================

if len(humidity_data) > 0:

    plt.figure(figsize=(10, 5))

    plt.plot(
        df["sequence"],
        pd.to_numeric(
            df["humidity"],
            errors="coerce"
        ),
        label="Humidity"
    )

    plt.xlabel("Sequence Number")
    plt.ylabel("Humidity (%)")

    plt.title(
        "DHT22 Humidity"
    )

    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    humidity_plot = (
        OUTPUT_DIR / "humidity.png"
    )

    plt.savefig(
        humidity_plot,
        dpi=150
    )

    plt.close()

# ============================================================
# Plot 4 — Distance
# ============================================================

if len(distance_data) > 0:

    plt.figure(figsize=(10, 5))

    plt.plot(
        df["sequence"],
        pd.to_numeric(
            df["distance"],
            errors="coerce"
        ),
        label="Distance"
    )

    plt.axhline(
        y=10,
        linestyle="--",
        label="Warning Threshold"
    )

    plt.xlabel("Sequence Number")
    plt.ylabel("Distance (cm)")

    plt.title(
        "HC-SR04 Distance"
    )

    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    distance_plot = (
        OUTPUT_DIR / "distance.png"
    )

    plt.savefig(
        distance_plot,
        dpi=150
    )

    plt.close()

# ============================================================
# Completion
# ============================================================

print("\n=== Analysis Complete ===")

print(f"Plots saved to: {OUTPUT_DIR}")