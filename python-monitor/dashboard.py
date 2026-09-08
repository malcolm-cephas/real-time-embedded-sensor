import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pathlib import Path

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "sensor_data.csv"

# ============================================================
# SETTINGS
# ============================================================

REFRESH_INTERVAL = 1000
DISPLAY_SAMPLES = 100

# ============================================================
# DASHBOARD
# ============================================================

fig = plt.figure(figsize=(15, 9))

try:
    fig.canvas.manager.set_window_title(
        "Real-Time Multi-Sensor Monitoring System"
    )
except Exception:
    pass


def update_dashboard(frame):

    # --------------------------------------------------------
    # Load CSV
    # --------------------------------------------------------

    try:
        df = pd.read_csv(DATA_FILE)

    except (FileNotFoundError, pd.errors.EmptyDataError):

        fig.clear()

        ax = fig.add_subplot(111)
        ax.axis("off")

        ax.text(
            0.5,
            0.5,
            "Waiting for sensor data...",
            ha="center",
            va="center",
            fontsize=20
        )

        return

    if len(df) == 0:
        return

    # --------------------------------------------------------
    # Convert numeric columns
    # --------------------------------------------------------

    numeric_columns = [
        "sequence",
        "raw_value",
        "filtered_value",
        "temperature",
        "humidity",
        "distance"
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    df = df.dropna(
        subset=[
            "sequence",
            "raw_value",
            "filtered_value",
            "temperature",
            "humidity",
            "distance"
        ]
    )

    if len(df) == 0:
        return

    # --------------------------------------------------------
    # Latest reading
    # --------------------------------------------------------

    latest = df.iloc[-1]

    temperature = latest["temperature"]
    humidity = latest["humidity"]
    distance = latest["distance"]
    raw_value = latest["raw_value"]
    filtered_value = latest["filtered_value"]

    status = str(latest["status"]).upper()

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    total_samples = len(df)

    warning_count = (
        df["status"]
        .astype(str)
        .str.upper()
        .eq("WARNING")
        .sum()
    )

    warning_percentage = (
        warning_count / total_samples * 100
    )

    # --------------------------------------------------------
    # Determine warning reason
    # --------------------------------------------------------

    warning_reason = "NONE"

    if status == "WARNING":

        if distance < 10:
            warning_reason = "PROXIMITY"

        elif filtered_value > 800:
            warning_reason = "HIGH ADC"

        else:
            warning_reason = "THRESHOLD"

    # --------------------------------------------------------
    # Sensor health
    # --------------------------------------------------------

    dht_online = (
        pd.notna(temperature)
        and pd.notna(humidity)
    )

    ultrasonic_online = pd.notna(distance)

    adc_online = (
        pd.notna(raw_value)
        and pd.notna(filtered_value)
    )

    data_link_online = len(df) > 0

    # --------------------------------------------------------
    # Recent data
    # --------------------------------------------------------

    recent = df.tail(DISPLAY_SAMPLES)

    # --------------------------------------------------------
    # Clear dashboard
    # --------------------------------------------------------

    fig.clear()

    fig.suptitle(
        "REAL-TIME MULTI-SENSOR MONITORING SYSTEM",
        fontsize=20,
        fontweight="bold"
    )

    # ========================================================
    # TOP CARDS
    # ========================================================

    ax_temp = fig.add_axes(
        [0.03, 0.79, 0.21, 0.12]
    )

    ax_humidity = fig.add_axes(
        [0.27, 0.79, 0.21, 0.12]
    )

    ax_distance = fig.add_axes(
        [0.51, 0.79, 0.21, 0.12]
    )

    ax_status = fig.add_axes(
        [0.75, 0.79, 0.22, 0.12]
    )

    def setup_card(ax, title, value):

        ax.set_xticks([])
        ax.set_yticks([])

        for spine in ax.spines.values():
            spine.set_linewidth(1.5)

        ax.text(
            0.5,
            0.72,
            title,
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold"
        )

        ax.text(
            0.5,
            0.30,
            value,
            ha="center",
            va="center",
            fontsize=19
        )

    setup_card(
        ax_temp,
        "TEMPERATURE",
        f"{temperature:.1f} °C"
    )

    setup_card(
        ax_humidity,
        "HUMIDITY",
        f"{humidity:.1f} %"
    )

    setup_card(
        ax_distance,
        "DISTANCE",
        f"{distance:.1f} cm"
    )

    # ========================================================
    # STATUS CARD
    # ========================================================

    ax_status.set_xticks([])
    ax_status.set_yticks([])

    for spine in ax_status.spines.values():
        spine.set_linewidth(2)

    ax_status.text(
        0.5,
        0.72,
        "SYSTEM STATUS",
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold"
    )

    ax_status.text(
        0.5,
        0.39,
        status,
        ha="center",
        va="center",
        fontsize=20,
        fontweight="bold"
    )

    if status == "WARNING":

        ax_status.text(
            0.5,
            0.12,
            warning_reason,
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold"
        )

    # ========================================================
    # ADC GRAPH
    # ========================================================

    ax_adc = fig.add_axes(
        [0.06, 0.47, 0.42, 0.25]
    )

    ax_adc.plot(
        recent["sequence"],
        recent["raw_value"],
        label="Raw ADC"
    )

    ax_adc.plot(
        recent["sequence"],
        recent["filtered_value"],
        label="Filtered ADC"
    )

    ax_adc.axhline(
        800,
        linestyle="--",
        label="Warning Threshold"
    )

    ax_adc.set_title(
        "ADC Signal: Raw vs Filtered",
        fontweight="bold"
    )

    ax_adc.set_xlabel("Sequence")
    ax_adc.set_ylabel("ADC Value")

    ax_adc.grid(True)
    ax_adc.legend()

    # ========================================================
    # DHT22 GRAPH WITH TWO Y-AXES
    # ========================================================

    ax_environment = fig.add_axes(
        [0.53, 0.47, 0.42, 0.25]
    )

    ax_humidity_graph = ax_environment.twinx()

    temperature_line = ax_environment.plot(
        recent["sequence"],
        recent["temperature"],
        label="Temperature (°C)"
    )

    humidity_line = ax_humidity_graph.plot(
        recent["sequence"],
        recent["humidity"],
        label="Humidity (%)"
    )

    ax_environment.set_title(
        "DHT22 Environmental Measurements",
        fontweight="bold"
    )

    ax_environment.set_xlabel("Sequence")
    ax_environment.set_ylabel("Temperature (°C)")
    ax_humidity_graph.set_ylabel("Humidity (%)")

    ax_environment.grid(True)

    lines = temperature_line + humidity_line

    labels = [
        line.get_label()
        for line in lines
    ]

    ax_environment.legend(
        lines,
        labels,
        loc="best"
    )

    # ========================================================
    # HC-SR04 GRAPH
    # ========================================================

    ax_distance_graph = fig.add_axes(
        [0.06, 0.16, 0.42, 0.23]
    )

    ax_distance_graph.plot(
        recent["sequence"],
        recent["distance"],
        label="Distance (cm)"
    )

    ax_distance_graph.axhline(
        10,
        linestyle="--",
        label="Proximity Threshold"
    )

    ax_distance_graph.set_title(
        "HC-SR04 Distance",
        fontweight="bold"
    )

    ax_distance_graph.set_xlabel("Sequence")
    ax_distance_graph.set_ylabel("Distance (cm)")

    ax_distance_graph.grid(True)
    ax_distance_graph.legend()

    # ========================================================
    # SENSOR HEALTH + STATISTICS
    # ========================================================

    ax_info = fig.add_axes(
        [0.53, 0.16, 0.42, 0.23]
    )

    ax_info.axis("off")

    health_text = (
        "SENSOR HEALTH\n\n"
        f"DHT22          : {'ONLINE' if dht_online else 'ERROR'}\n"
        f"HC-SR04        : {'ONLINE' if ultrasonic_online else 'ERROR'}\n"
        f"ADC            : {'ONLINE' if adc_online else 'ERROR'}\n"
        f"DATA LINK      : {'ACTIVE' if data_link_online else 'WAITING'}\n\n"
        "SYSTEM STATISTICS\n\n"
        f"Total Samples  : {total_samples}\n"
        f"Warnings       : {warning_count}\n"
        f"Warning Rate   : {warning_percentage:.2f}%"
    )

    ax_info.text(
        0.5,
        0.5,
        health_text,
        ha="center",
        va="center",
        fontsize=11
    )

    # ========================================================
    # FOOTER
    # ========================================================

    fig.text(
        0.5,
        0.04,
        "Arduino Nano  •  DHT22  •  HC-SR04  •  ADC Filtering  •  Python Telemetry",
        ha="center",
        fontsize=9
    )

    fig.canvas.draw_idle()


# ============================================================
# START
# ============================================================

animation = FuncAnimation(
    fig,
    update_dashboard,
    interval=REFRESH_INTERVAL,
    cache_frame_data=False
)

plt.show()