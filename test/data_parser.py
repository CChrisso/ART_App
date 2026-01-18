import time

START_TIME = time.time()

def normalize(value, min_val, max_val):
    value = max(min_val, min(max_val, value))
    return 100.0 * (value - min_val) / (max_val - min_val)


def parse_line(line):
    """
    Expected line example:
    GAS,512,BRK,300,AX,120,AY,-50,AZ,980
    """
    try:
        parts = line.strip().split(",")

        raw = {
            parts[i]: float(parts[i + 1])
            for i in range(0, len(parts), 2)
        }

        return {
            "time": time.time() - START_TIME,

            # ---- Pedals (ADC 0–100) ----
            "gas": normalize(raw["GAS"], 0, 100),
            "brake": normalize(raw["BRK"], 0, 100),

            # ---- IMU (example ranges) ----
            "ax": normalize(raw["AX"], -50, 50),
            "ay": normalize(raw["AY"], -50, 50),
            "az": normalize(raw["AZ"], -50, 50),
        }

    except Exception:
        return None
