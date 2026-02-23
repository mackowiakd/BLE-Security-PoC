# BLE Security Misconfiguration: Proof of Concept (PoC)

This repository contains a Proof of Concept (PoC) demonstrating a common security misconfiguration in Bluetooth Low Energy (BLE) IoT devices. 

The project highlights an **"Insecure by Design"** flaw where a device is mechanically and software-wise fully functional, but lacks proper authorization on the communication layer.

## 📁 Repository Structure
* `/BLE_security_IoT` - PlatformIO project containing the C++ code for the vulnerable BLE server (target).
* `/attacker_script` - Python automated scanning and exploitation script (attacker).

## 🛠️ Hardware Setup
* **Microcontroller:** XIAO ESP32-C3
* **Actuator:** Adafruit NeoPixel RGB LED (Pin 2)

## 🚨 The Vulnerability
The vulnerability lies in the BLE server configuration (`src/diode_faulty_ble.cpp`). The GATT characteristic responsible for controlling the LED state is created with `READ` and `WRITE` properties, but **without any encryption or authentication flags** (missing `WRITE_ENC`). 

This allows any unauthenticated central device to connect and write payloads to the characteristic, gaining full control over the actuator.

## 🐍 The Exploit (Python Auto-Auditor)
The `ble_hacking.py` script acts as an automated Black-Box testing tool. It uses the `bleak` library to:
1. Scan the environment for the vulnerable device name.
2. Establish a connection without pairing.
3. Perform GATT Discovery to map services and find open "write" characteristics.
4. Inject unauthorized hexadecimal payloads to force a state change.
5. Generate a brief security audit report.

## 🚀 How to run the PoC

**1. Prepare the Target (ESP32-C3):**
Open the `/BLE_security_IoT` folder in VS Code with the PlatformIO extension installed. Build and upload the project to your XIAO board.

**2. Run the Attacker Script:**
Navigate to the Python script directory:
```bash
cd attacker_script/ble_hacking