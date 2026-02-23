import asyncio
import logging
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

# Professional logger setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("BLE_Auto_Auditor")

class BLEVulnerabilityScanner:
    def __init__(self, target_name):
        self.target_name = target_name
        self.target_device = None
        self.vulnerable_characteristics = []

    async def run_scan(self):
        logger.info(f"Starting automated Black-Box audit for: {self.target_name}")
        
        # STEP 1: Device Discovery (Finding the target)
        self.target_device = await BleakScanner.find_device_by_filter(
            lambda d, ad: d.name and d.name == self.target_name,
            timeout=10.0
        )

        if not self.target_device:
            logger.error("Target not found in the vicinity.")
            return

        logger.info(f"Target found: MAC {self.target_device.address}. Establishing connection...")

        # STEP 2: Exploration and Attack (Looking for unlocked doors)
        try:
            async with BleakClient(self.target_device, timeout=15.0) as client:
                logger.info("Connected. Starting service mapping (GATT Discovery)...")
                
                # Retrieve all services and characteristics from the device (LIKE A REAL HACKER)
                services = client.services
                
                for service in services:
                    for char in service.characteristics:
                        # Look for characteristics that CAN be written to
                        if "write" in char.properties or "write-without-response" in char.properties:
                            logger.info(f"[INFO] Found entry point (Write): UUID {char.uuid}")
                            
                            # STEP 3: Attack attempt (Injecting test payload)
                            logger.info(f"    -> Attempting unauthorized write to {char.uuid}...")
                            test_payload = bytes([255, 0, 0]) # Red color payload for XIAO LED
                            
                            try:
                                await client.write_gatt_char(char.uuid, test_payload, response=True)
                                
                                # If we reached this point, the device did not reject the write! VULNERABILITY FOUND!
                                logger.warning(f"    -> [!] CRITICAL VULNERABILITY: Write to {char.uuid} succeeded without authorization/pairing!")
                                self.vulnerable_characteristics.append(char.uuid)
                                
                            except BleakError as e:
                                if "Authentication" in str(e) or "Paired" in str(e):
                                    logger.info(f"    -> [SECURE] Device blocked the write attempt. Authorization required.")
                                else:
                                    logger.info(f"    -> [WRITE ERROR] Other error: {e}")
                                    
        except Exception as e:
            logger.error(f"Critical error during scanning: {e}")

        # Final report
        self.print_report()

    def print_report(self):
        print("\n" + "="*60)
        print("SECURITY AUDIT REPORT (BLE VULNERABILITY SCAN)")
        print("="*60)
        print(f"Target: {self.target_name}")
        print(f"Found open write vulnerabilities: {len(self.vulnerable_characteristics)}")
        for vuln in self.vulnerable_characteristics:
            print(f" - [CRITICAL] Open write on UUID: {vuln}")
        if len(self.vulnerable_characteristics) == 0:
            print("System appears secure (No open entry points found).")
        print("="*60 + "\n")


if __name__ == "__main__":
    # Now you ONLY provide the device name, the script "hacks" the rest by itself!
    TARGET_DEVICE_NAME = "XIAO_Vulnerable_LED"

    scanner = BLEVulnerabilityScanner(TARGET_DEVICE_NAME)
    asyncio.run(scanner.run_scan())