# BLE Security Misconfiguration & Memory Corruption: Proof of Concept (PoC)

This repository contains a Proof of Concept (PoC) demonstrating a common security misconfiguration and a critical memory corruption vulnerability in Bluetooth Low Energy (BLE) IoT devices. 

The project highlights an **"Insecure by Design"** flaw where a device is mechanically and software-wise fully functional, but lacks proper authorization on the communication layer, combined with unsafe memory handling.

## 📁 Repository Structure
* `/BLE_security_IoT` - PlatformIO project containing the C++ code for the vulnerable BLE server (target).
* `/attacker_script` - Python automated scanning and exploitation script (attacker).

## 🛠️ Hardware Setup
* **Microcontroller:** XIAO ESP32-C3
* **Actuator:** Adafruit NeoPixel RGB LED (Pin D1)

## 🚨 The Vulnerabilities

### 1. Broken Access Control (Insecure by Design)
The GATT characteristic responsible for controlling the LED state is created with `READ` and `WRITE` properties, but **without any encryption or authentication flags** (missing `WRITE_ENC`). This allows any unauthenticated central device to connect and write payloads to the characteristic, gaining full control over the actuator.

### 2. Buffer Overflow (Memory Corruption)
The firmware's write callback (`src/diode_faulty_ble.cpp`) contains a classic buffer overflow vulnerability. It utilizes `memcpy()` to transfer the incoming BLE payload into a fixed-size local buffer **without verifying the payload's length**. An attacker can exploit this by sending a payload larger than the allocated buffer (e.g., injecting `0x41` / "A" padding), leading to memory corruption, potential crashes, or arbitrary code execution.

## 🐍 The Exploit (Python Auto-Auditor)
The `ble_hacking.py` script acts as an automated Black-Box testing tool. It uses the `bleak` library to:
1. Scan the environment for the vulnerable device using advanced BlueZ filtering (`ad.local_name` fallback).
2. Establish a connection without pairing.
3. Perform GATT Discovery to map services and find open "write" characteristics.
4. Inject an unauthorized, oversized hexadecimal payload to trigger the Buffer Overflow and force a state change.
5. Generate a brief security audit report.

## 🐧 Linux Kernel & Driver Analysis (Bash Framework)
To elevate the testing process, I developed a **Bash wrapper script** (`run_audit.sh`) that integrates the Python exploit with Linux's low-level components. 

* **DevOps Best Practices:** The script implements **dynamic path resolution** and automatically detects or falls back to isolated **Virtual Environments (venv)**. This ensures robust, cross-platform execution without hardcoded paths, managing Python dependencies effectively.
* **Kernel-Level Hooking:** Before launching the attack, the script utilizes `btmon` to hook into the **BlueZ Bluetooth stack within the Linux Kernel**. It captures raw HCI (Host Controller Interface) traffic flowing between the OS platform components and the hardware Bluetooth driver.
* **Automated Log Analysis:** Post-execution, the framework automatically dumps and filters the Kernel Ring Buffer (`dmesg`) to identify driver-level anomalies during the attack.

## 🛠️ Hardware & Kernel Troubleshooting
During testing on a MacBook host running native Ubuntu, several hardware-specific challenges were mitigated:
* **Broadcom UART & ACPI Limitations:** Initial interaction with the `hci0` interface required patching the `macbook12-bluetooth-driver` to bypass ACPI baudrate errors.
* **BlueZ Advertising Packet Parsing:** The Broadcom chip periodically threw `unknown advertising packet type: 0x10 / 0x14` errors in `dmesg`. This required modifying the Python scanner to rely on both `d.name` and the raw advertisement packet (`ad.local_name`), as the Linux BlueZ stack handles Apple's hardware packet forwarding differently than Windows.

## 🚀 How to run the PoC

**1. Prepare the Target (ESP32-C3):**
Open the `/BLE_security_IoT` folder in VS Code with the PlatformIO extension installed. Build and upload the project to your XIAO board.

**2. Run the Automated Audit (Linux/Bash):**
Navigate to the attacker script directory and execute the wrapper. The script will handle the interface reset, packet capture, and payload injection.
```bash
cd attacker_script
chmod +x run_audit.sh
./run_audit.sh
```
**3. Offline Cryptographic Analysis (Wireshark):**
The script will generate an `.snoop` file containing the raw HCI dump.
1. Fix file permissions if necessary: `sudo chown $USER:$USER *.snoop`
2. Open the file in **Wireshark**.
3. Apply the `btatt` filter to analyze the Attribute Protocol traffic.
4. Locate the `Write Request` packet to observe the injected Buffer Overflow payload in the hexadecimal dump.
<img width="1920" height="1080" alt="Zrzut ekranu 2026-03-06 131958" src="https://github.com/user-attachments/assets/25757fba-c5ab-4131-9cfd-ada2ffc8b925" />

[Wireshark Buffer Overflow Proof of Concept]
