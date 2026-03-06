#!/bin/bash
# ==============================================================================
# BLE Security Audit Framework - HCI Traffic Interceptor
# ==============================================================================

CAPTURE_FILE="hci_capture_$(date +%Y%m%d_%H%M%S).snoop"

echo "==================================================="
echo "[*] Starting BLE Security Audit Framework"
echo "==================================================="

echo "[*] Initializing Kernel Driver Interaction..."

# Resetowanie interfejsu (na wypadek zawieszenia zmodyfikowanego sterownika Broadcom/Apple)
sudo hciconfig hci0 down
sleep 1
sudo hciconfig hci0 up

if hciconfig hci0 | grep -q "UP RUNNING"; then
    echo "[+] HCI0 interface driver is UP and RUNNING."
else
    echo "[-] Error communicating with Bluetooth kernel module."
    exit 1
fi

echo "[*] Starting lightweight background packet capture (btmon in SILENT MODE)..."
# Uruchamiamy btmon z przekierowaniem Standard Output (1) i Standard Error (2) do /dev/null
# Dzięki temu błędy baudrate'u i ACPI nie zaleją nam ekranu!
sudo btmon -w $CAPTURE_FILE > /dev/null 2>&1 &
BTMON_PID=$!

sleep 2

echo "[*] Launching Python Black-Box Scanner..."
# Ważne: Sprawdź, czy ścieżka do skryptu jest poprawna!
if venv/bin/python3 ble_hacking.py; then
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
# Filtrujemy 'dmesg', aby znaleźć crashe, ale CELOWO wykluczamy (grep -v) 
# błędy z Twojego patcha dla MacBooka, żeby nie zaciemniały raportu!
dmesg | tail -n 50 | grep -i -E "bluetooth|hci|ble" | grep -v -i "failed to write update baudrate" | grep -v -i "Apple ACPI bug"

echo "==================================================="
echo "[+] Audit complete! Hardware communication dump saved to '$CAPTURE_FILE'"
echo "==================================================="