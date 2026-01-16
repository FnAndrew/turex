import evdev
from evdev import ecodes
import asyncio
import sys

# --- 1. MOCK CONFIG (Náhrada za config.py) ---
class MockConfig:
    # Nastavení hledání
    XBOX_MAC = "XX:XX:XX:XX:XX:XX"  # Jen pro výpis
    DEADZONE = 4000  # Pásmo necitlivosti
    
    # Mapování tlačítek (Standardní Xbox One/360 layout)
    BTN_A = 304
    BTN_B = 305
    BTN_X = 307
    BTN_Y = 308
    
    # Mapování os
    AXIS_LX = 0
    AXIS_LY = 1
    AXIS_RX = 3
    AXIS_RY = 4
    AXIS_GAS = 5      # Často bývá 5 nebo 2, záleží na ovladači
    AXIS_BRAKE = 2    # Často bývá 2 nebo 5
    AXIS_DPAD_X = 16
    AXIS_DPAD_Y = 17
    
    # Slovník pro popis tlačítek
    BUTTON_MAP = {
        304: "A", 305: "B", 307: "X", 308: "Y",
        310: "LB", 311: "RB", 314: "Select", 315: "Start",
        316: "Xbox Button", 317: "L3", 318: "R3"
    }

# Vytvoříme instanci, aby kód mohl používat "config.NECO"
config = MockConfig()


# --- 2. MOCK LOGIC (Náhrada za skutečného robota) ---
class MockRobotLogic:
    """Simuluje metody, které volá ovladač na robotovi."""
    
    def set_movement(self, speed, turn):
        # Místo jízdy jen vypíšeme hodnoty
        # print(f" >>> ROBOT JEDE: Rychlost={speed}, Zatoceni={turn}")
        pass

    async def fire_weapon(self):
        print(" >>> ROBOT: Vystřelil zbraň! (Piu Piu)")
        await asyncio.sleep(0.5)

    def stop_weapon_manual(self):
        print(" >>> ROBOT: Zbraň zastavena manuálně.")
        
    def zastavit_vse(self):
        print(" !!! ROBOT: EMERGENCY STOP !!!")


# --- 3. TVŮJ UPRAVENÝ KÓD OVLADAČE ---
class XboxController:
    def __init__(self, logic_controller):
        self.target_name = "Xbox"  # Část názvu zařízení, kterou hledáme
        self.logic = logic_controller
        self.device = None
        
        # Interní stavové proměnné
        self.speed = 0.0
        self.turn = 0.0
        self.turret_pan = 0.0
        self.turret_tilt = 0.0

    async def connect(self, timeout=20):
        """Pokusí se najít Xbox ovladač."""
        print(f"Hledám ovladač obsahující '{self.target_name}' (Čekám max {timeout}s)...")
        print(f"MAC (z configu): {config.XBOX_MAC}")
        
        for i in range(timeout):
            try:
                # List devices může vyhodit chybu, pokud nejsou práva, proto try/except
                devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            except OSError as e:
                print(f"Chyba přístupu k zařízením (potřebuješ sudo?): {e}")
                return False

            for dev in devices:
                if self.target_name in dev.name:
                    self.device = dev
                    print(f"-> ÚSPĚCH: Nalezen {dev.name} na {dev.phys}")
                    return True
            
            # Pokud nenalezeno, počkáme 1s a zkusíme znovu
            if i < timeout - 1:
                await asyncio.sleep(1)
        
        print(f"\n-> TIMEOUT: Ovladač nenalezen.")
        return False

    async def listen(self):
        """Hlavní smyčka."""
        if not self.device:
            print("Chyba: Ovladač není připojen.")
            return

        print(f"Začínám číst vstupy z {self.device.name}...")
        
        # Grab exclusive access (volitelné, zabrání psaní znaků do terminálu, pokud běžíš na konzoli)
        try:
            self.device.grab()
        except Exception:
            pass

        try:
            async for event in self.device.async_read_loop():
                self._handle_event(event)
                
        except OSError:
            print("CHYBA: Ovladač byl odpojen!")
            self.logic.zastavit_vse()
        except Exception as e:
            print(f"Neočekávaná chyba: {e}")

    def _handle_event(self, event):
        # --- 1. TLAČÍTKA ---
        if event.type == ecodes.EV_KEY:
            if event.value == 1: # Stisk
                nazev = config.BUTTON_MAP.get(event.code, f"Neznámé {event.code}")
                print(f"STISK: {nazev} (code {event.code})")

                if event.code == config.BTN_A:
                    asyncio.create_task(self.logic.fire_weapon())
                elif event.code == config.BTN_B:
                    if hasattr(self.logic, 'stop_weapon_manual'):
                        self.logic.stop_weapon_manual()

        # --- 2. OSY ---
        elif event.type == ecodes.EV_ABS:
            # Analogové páčky
            if event.code == config.AXIS_LX:
                print(f"Levá X: {self.map_axis_stick(event.value)}%")
                self.turn = self._map_axis(event.value)
                self.logic.set_movement(self.speed, self.turn)

            elif event.code == config.AXIS_LY:
                print(f"Levá Y: {self.map_axis_stick(event.value)}%")
                self.speed = -self._map_axis(event.value)
                self.logic.set_movement(self.speed, self.turn)

            elif event.code == config.AXIS_RX:
                print(f"Pravá X: {self.map_axis_stick(event.value)}%")
                self.turret_pan = self._map_axis(event.value)

            elif event.code == config.AXIS_RY:
                print(f"Pravá Y: {self.map_axis_stick(event.value)}%")
                self.turret_tilt = -self._map_axis(event.value)

            # Triggery (Plyn / Brzda)
            elif event.code == config.AXIS_GAS:
                val_pct = self.map_trigger(event.value)
                print(f"PLYN (Axis {event.code}): {val_pct}%")
                
            elif event.code == config.AXIS_BRAKE:
                val_pct = self.map_trigger(event.value)
                print(f"BRZDA (Axis {event.code}): {val_pct}%")

            # D-PAD (Křížový ovladač)
            elif event.code == config.AXIS_DPAD_X:
                smery = {-1: "Vlevo", 1: "Vpravo", 0: "Střed"}
                print(f"D-PAD X: {smery.get(event.value)}")

            elif event.code == config.AXIS_DPAD_Y:
                smery = {-1: "Nahoru", 1: "Dolů", 0: "Střed"}
                print(f"D-PAD Y: {smery.get(event.value)}")

    def _map_axis(self, value):
        centered = value - 32768
        if abs(centered) < config.DEADZONE:
            return 0.0
        percent = (centered / 32768.0) * 100
        return int(percent)

    def map_axis_stick(self, value):
        return int(self._map_axis(value))

    def map_trigger(self, value):
        # Heuristika pro rozsah triggeru
        if value > 16000:
            maxv = 65535
        elif value > 1023:
            maxv = 4095 if value <= 4095 else value
        else:
            maxv = 1023

        try:
            pct = int(round((value / float(maxv)) * 100))
        except Exception:
            pct = int(self._map_trigger(value))
        return max(0, min(100, pct))

    def _map_trigger(self, value):
        return int((value / 1023.0) * 100)


# --- 4. MAIN - SPOUŠTĚCÍ SMYČKA ---
async def main():
    # 1. Inicializace falešné logiky robota
    logic = MockRobotLogic()
    
    # 2. Inicializace ovladače
    controller = XboxController(logic)
    
    # 3. Připojení (čeká, dokud nenajde ovladač)
    print("--- Startuji Xbox Controller Test ---")
    connected = await controller.connect()
    
    if connected:
        # 4. Spuštění čtení
        await controller.listen()
    else:
        print("Konec programu: Ovladač nebyl nalezen.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram ukončen uživatelem.")