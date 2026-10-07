import numpy as np
import pandas as pd

np.random.seed(42)

# -------------------
# CONFIG
# -------------------
N_VEHICLES = 5000
TIMESTEPS = 50
N_SENSORS = 21
FAILURE_RATE = 0.07
FAILURE_SENSOR_SHARE = 0.25
HEALTHY_DRIFT_SCALE = 0.45
FAILURE_DRIFT_RANGE = (0.08, 0.35)
SENSOR_NOISE_STD = 0.7
FAILURE_EXTRA_NOISE_STD = 0.1
MIN_EVENT_STEP = 20

manufacturers = ["Scania", "Volvo", "MAN", "DAF"]
engine_types = ["Diesel_A", "Diesel_B", "Diesel_C"]
regions = ["Urban", "Highway", "Mixed"]

rows = []

for v in range(N_VEHICLES):

    vehicle_id = f"V_{v:05d}"

    # -------------------
    # VEHICLE SPECIFICATIONS (STATIC)
    # -------------------
    manufacturer = np.random.choice(manufacturers)
    engine = np.random.choice(engine_types)
    region = np.random.choice(regions)

    vehicle_age = np.random.randint(1, 12)
    engine_power = np.random.normal(350, 40)
    payload = np.random.normal(18, 4)

    # -------------------
    # FAILURE LABELS (TTE)
    # -------------------
    fail = np.random.rand() < FAILURE_RATE
    event_time = np.random.randint(MIN_EVENT_STEP, TIMESTEPS) if fail else TIMESTEPS

    base = np.random.normal(0, 1, N_SENSORS)
    vehicle_sensor_bias = np.random.normal(0, 0.45, N_SENSORS)
    seasonal_phase = np.random.uniform(0, np.pi, N_SENSORS)
    healthy_random_walk = np.zeros(N_SENSORS)

    transient_spike_step = np.random.randint(0, TIMESTEPS)
    transient_spike = np.random.normal(0, 0.4, N_SENSORS)

    affected_sensors = np.random.choice(
        [0, 1],
        size=N_SENSORS,
        p=[1 - FAILURE_SENSOR_SHARE, FAILURE_SENSOR_SHARE]
    )

    if fail and not affected_sensors.any():
        affected_sensors[np.random.randint(0, N_SENSORS)] = 1

    failure_drift = affected_sensors * np.random.uniform(
        FAILURE_DRIFT_RANGE[0],
        FAILURE_DRIFT_RANGE[1],
        N_SENSORS
    )

    # -------------------
    # OPERATIONAL READOUTS (TIME SERIES)
    # -------------------
    for t in range(TIMESTEPS):

        time_ratio = t / max(TIMESTEPS - 1, 1)

        healthy_random_walk += np.random.normal(
            0, HEALTHY_DRIFT_SCALE / 6, N_SENSORS
        )

        healthy_trend = (
            healthy_random_walk
            + np.random.normal(0, HEALTHY_DRIFT_SCALE, N_SENSORS)
            + 0.25 * np.sin((2 * np.pi * time_ratio) + seasonal_phase)
        )

        if abs(t - transient_spike_step) <= 1:
            healthy_trend += transient_spike

        event_progress = 0.0
        if fail:
            event_progress = max(
                0.0,
                (t - (event_time * 0.6)) / max(event_time * 0.4, 1)
            )
            event_progress = min(event_progress, 1.0)

        if fail:
            trend = healthy_trend + (event_progress * failure_drift)
            noise = np.random.normal(
                0, SENSOR_NOISE_STD + FAILURE_EXTRA_NOISE_STD, N_SENSORS
            )
        else:
            trend = healthy_trend
            noise = np.random.normal(0, SENSOR_NOISE_STD, N_SENSORS)

        sensors = base + vehicle_sensor_bias + trend + noise

        row = {

            # identifiers
            "vehicle_id": vehicle_id,
            "time_step": t,

            # -------- VEHICLE SPECIFICATIONS --------
            "manufacturer": manufacturer,
            "engine_type": engine,
            "region": region,
            "vehicle_age": vehicle_age,
            "engine_power_kw": round(engine_power, 2),
            "payload_capacity_tons": round(payload, 2),

            # -------- FAILURE LABELS (TTE) --------
            "failure": int(fail),
            "event_occurred": int(fail and t >= event_time),
            "event_time": event_time if fail else np.nan,
            "time_to_event": max(event_time - t, 0) if fail else np.nan,
            "is_censored": int(not fail)
        }

        # -------- OPERATIONAL SENSOR READOUTS --------
        for s in range(N_SENSORS):
            row[f"sensor_{s+1}"] = sensors[s]

        rows.append(row)

df = pd.DataFrame(rows)

from pathlib import Path
Path("Dataset").mkdir(exist_ok=True)

df.to_csv("Dataset/predictive_maintenance_dataset_v2.csv", index=False)

print("Dataset shape:", df.shape)
print("Saved as predictive_maintenance_dataset_v2.csv")