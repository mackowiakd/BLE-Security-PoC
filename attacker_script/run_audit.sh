#!/bin/bash

# ==============================================================================
# BLE Security Audit Framework - HCI Traffic Interceptor
# Description: This script automates Bluetooth Low Energy (BLE) traffic 
#              capture at the Linux Kernel level using BlueZ utilities.
# Requirements: sudo, btmon, bluez, python3
# ==============================================================================

# Exit immediately if a command exits with a non-zero status
set -e

echo "==================================================="
echo "[*] Starting BLE Security Audit Framework"
echo "==================================================="

# Step 1: Initialize Linux Kernel HCI capture (requires root privileges)
# We use 'btmon' to intercept raw HCI packets between BlueZ stack and the controller.
# Saving to .snoop format for professional post-analysis in Wireshark.
echo "[*] Initializing Linux Kernel HCI capture (btmon)..."
sudo btmon -w hci_capture.snoop > /dev/null 2>&1 &
BTMON_PID=$!

# Allow 1 second for the background process to initialize the hardware socket
sleep 1

# Step 2: Execute the Black-Box security scanner (Python Payload)
# This module performs device discovery and characteristic enumeration.
echo "[*] Launching Python Black-Box Scanner..."
if python3 ble_hacking/ble_hacking.py; then
    echo "[+] Python payload executed successfully."
else
    echo "[-] Python script encountered an error."
fi

# Step 3: Gracefully terminate the HCI monitor process
# Sending SIGTERM to ensure the .snoop file buffer is flushed correctly.
echo "[*] Stopping HCI capture (PID: $BTMON_PID)..."
sudo kill $BTMON_PID

echo "==================================================="
echo "[+] Audit complete! Hardware communication dump saved to 'hci_capture.snoop'"
echo "[+] Traffic can be analyzed using Wireshark or 'btmon -r'."
echo "==================================================="