import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Locate project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "sensor_data.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "sensor_analysis.png"

# Load data
df = pd.read_csv(DATA_FILE)

print("\n=== Sensor Data Analysis ===")

# Basic statistics
print(f"Total samples: {len(df)}")

print(f"Minimum raw value: {df['raw_value'].min()}")
print(f"Maximum raw value: {df['raw_value'].max()}")
print(f"Average raw value: {df['raw_value'].mean():.2f}")

print(f"Minimum filtered value: {df['filtered_value'].min()}")
print(f"Maximum filtered value: {df['filtered_value'].max()}")
print(f"Average filtered value: {df['filtered_value'].mean():.2f}")

# -------------------------------------------------
# Filtering analysis
# -------------------------------------------------

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

print("\n=== Filtering Analysis ===")

print(
    f"Mean absolute raw-filtered difference: "
    f"{mean_absolute_difference:.2f}"
)

print(
    f"Maximum absolute raw-filtered difference: "
    f"{maximum_difference}"
)

print(
    f"Standard deviation of filtering difference: "
    f"{difference_std:.2f}"
)

# -------------------------------------------------
# Warning analysis
# -------------------------------------------------

warning_count = (
    df["status"] == "WARNING"
).sum()

warning_percentage = (
    warning_count / len(df)
) * 100

print("\n=== Warning Analysis ===")

print(f"Warning samples: {warning_count}")
print(f"Warning percentage: {warning_percentage:.2f}%")

# -------------------------------------------------
# Plot raw vs filtered
# -------------------------------------------------

plt.figure(figsize=(10, 5))

plt.plot(
    df["sequence"],
    df["raw_value"],
    label="Raw"
)

plt.plot(
    df["sequence"],
    df["filtered_value"],
    label="Filtered"
)

plt.axhline(
    y=800,
    linestyle="--",
    label="Warning Threshold"
)

plt.xlabel("Sequence Number")
plt.ylabel("ADC Value")
plt.title("Embedded Sensor Data: Raw vs Filtered")

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    OUTPUT_FILE,
    dpi=150
)

print(
    f"\nGraph saved to: {OUTPUT_FILE}"
)

plt.show()