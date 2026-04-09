import serial
import serial.tools.list_ports
import time
import re
import requests

def find_esp32_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "USB" in port.description or "UART" in port.description or "CP210" in port.description:
            print(f"✅ ESP32 found on {port.device}")
            return port.device
    return None


def reset_esp32():
    try:
        requests.get("http://192.168.4.1/reset", timeout=3)
        print("🔄 ESP32 reset via WiFi...")
        time.sleep(1)
        return True
    except Exception:
        return False


def read_sensor_data():
    port = find_esp32_port()

    if port is None:
        print("❌ ESP32 not found. Please connect device.")
        return None, None

    try:
        ser = serial.Serial(port, 115200, timeout=2)
        print("⏳ Connecting to sensor... please wait")
        time.sleep(2)

        print("🔄 Resetting ESP32 for fresh session...")
        reset_esp32()

        print("✅ Connected! Waiting for finger placement on sensor...")
        print("-" * 45)
        print("🔍 DEBUG MODE — printing all raw lines from ESP32:")
        print("-" * 45)

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()

            # Print EVERY line raw so we can see exact format
            if line:
                print(f"RAW >>> {repr(line)}")

            if not line:
                continue

            # ── Sampling reset confirmed ───────────────────────
            if "Sampling reset" in line or "collecting new" in line:
                print("✅ Fresh session started! Place finger on sensor...")
                continue

            # ── Finger not placed ──────────────────────────────
            if "Finger: NO" in line:
                print("👆 Please place your finger on the sensor...")
                continue

            # ── Finger placed ──────────────────────────────────
            if "Finger: YES" in line:
                print("✅ Finger detected!")
                continue

            # ── Beat ──────────────────────────────────────────
            if line == "Beat!":
                print("💓 Beat!")
                continue

            # ── Per-sample ────────────────────────────────────
            sample_match = re.search(
                r'Sample\s+(\d+)/(\d+).*?HR=(\d+).*?SpO2=(\d+)', line
            )
            if sample_match:
                current = int(sample_match.group(1))
                total   = int(sample_match.group(2))
                hr      = int(sample_match.group(3))
                spo2    = int(sample_match.group(4))
                bar     = ("█" * current) + ("░" * (total - current))
                print(f"📊 [{bar}] {current}/{total}  HR={hr}  SpO2={spo2}")
                continue

            # ── Live loop ─────────────────────────────────────
            live_match = re.search(
                r'\[(\d+)/15\].*?HR:\s*(\d+).*?SpO2:\s*(\d+)', line
            )
            if live_match:
                current = int(live_match.group(1))
                hr      = int(live_match.group(2))
                spo2    = int(live_match.group(3))
                bar     = ("█" * current) + ("░" * (15 - current))
                print(f"📊 [{bar}] {current}/15  HR={hr}  SpO2={spo2}")
                continue

            # ── DONE ──────────────────────────────────────────
            done_match = re.search(
                r'\[DONE\].*?HR:\s*(\d+).*?SpO2:\s*(\d+)', line
            )
            if done_match:
                heart_rate = int(done_match.group(1))
                spo2       = int(done_match.group(2))
                print("-" * 45)
                print(f"✅ Measurement complete!")
                print(f"   ❤️  Heart Rate      : {heart_rate}")
                print(f"   🩸  Oxygen Saturation: {spo2}")
                print("-" * 45)
                ser.close()
                return heart_rate, spo2

    except Exception as e:
        print(f"❌ Serial Error: {e}")
        return None, None