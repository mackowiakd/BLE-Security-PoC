#!/bin/bash
# ==============================================================================
# BLE Security Audit Framework - HCI Traffic Interceptor
# ==============================================================================
#  MAC adr of  XIAO ESP32-C3 to clean up if connected many times
TARGET_MAC="98:3D:AE:AC:4D:B2"
# --- DYNAMIC PATH RESOLUTION (DevOps Standard) ---
# Skrypt sam namierza swój własny folder na dysku, unikając hardcodowania ścieżek
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_SCRIPT="$SCRIPT_DIR/ble_hacking/ble_hacking.py"

# --- VENV AUTODETECTION ---
# Szukamy środowiska najpierw w głównym katalogu projektu, potem w obecnym, a jak nie ma to bierzemy systemowego Pythona
if [ -f "$PROJECT_ROOT/venv/bin/python3" ]; then
    PYTHON_CMD="$PROJECT_ROOT/venv/bin/python3"
elif [ -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python3"
else
    PYTHON_CMD="python3"
fi
# -------------------------------------------------

CAPTURE_FILE="hci_capture_$(date +%Y%m%d_%H%M%S).snoop"

echo "==================================================="
echo "[*] Starting BLE Security Audit Framework"
echo "==================================================="

echo "[*] Initializing Kernel Driver Interaction..."

# sudo hciconfig hci0 down
# sleep 2
# sudo hciconfig hci0 up

# echo "[*] Waiting for Bluetooth daemon to wake up..."
# sleep 3 # KLUCZOWE: Dajemy Linuksowi 3 sekundy na ogarnięcie, że karta znów działa!

# --- BLUEZ CACHE SANITIZATION ---
echo "[*] Sanitizing BlueZ cache for target ($TARGET_MAC)..."
# Dodajmy profilaktyczny disconnect na wypadek zawieszonej sesji!
sudo bluetoothctl -- disconnect $TARGET_MAC > /dev/null 2>&1 || true
sudo bluetoothctl -- remove $TARGET_MAC > /dev/null 2>&1 || true
sleep 1
# ------------------------------------------

if hciconfig hci0 | grep -q "UP RUNNING"; then
    echo "[+] HCI0 interface driver is UP and RUNNING."
else
    echo "[-] Error communicating with Bluetooth kernel module."
    exit 1
fi

echo "[*] Starting lightweight background packet capture (btmon in SILENT MODE)..."
sudo btmon -w $CAPTURE_FILE > /dev/null 2>&1 &
BTMON_PID=$!

sleep 2

echo "[*] Launching Python Black-Box Scanner..."
echo "    -> Using Python interpreter: $PYTHON_CMD"
echo "    -> Executing payload: $PYTHON_SCRIPT"

# Dynamiczne wywołanie payloadu
if "$PYTHON_CMD" "$PYTHON_SCRIPT"; then
    echo "[+] Python payload executed successfully."
else
    echo "[-] Python script encountered an error."
fi

echo "[*] Waiting for kernel buffers to flush packets to disk..."
sleep 3

echo "[*] Gracefully stopping HCI capture (PID: $BTMON_PID)..."
sudo kill -INT $BTMON_PID
sleep 1

echo "[*] Analyzing Kernel logs (dmesg) for driver-level anomalies..."
sudo dmesg | tail -n 50 | grep -i -E "bluetooth|hci|ble" | grep -v -i "failed to write update baudrate" | grep -v -i "Apple ACPI bug"

echo "==================================================="
echo "[+] Audit complete! Hardware communication dump saved to '$CAPTURE_FILE'"
echo "==================================================="