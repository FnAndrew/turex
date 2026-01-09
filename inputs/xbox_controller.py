import evdev
from evdev import ecodes
import asyncio
import config

class XboxController:
    def __init__(self, device_path_or_name, logic_controller):
        self.target_name = "Xbox" # Část názvu, kterou hledáme
        self.logic = logic_controller
        self.device = None
        
        # Stavové proměnné
        self.current_speed = 0.0
        self.current_turn = 0.0
        self.turret_pan = 0.0
        self.turret_tilt = 0.0

    async def connect(self, timeout=20):
        """
        Čeká na připojení ovladače po dobu 'timeout' sekund.
        Vrací True, pokud se ovladač objeví, jinak False.
        """
        print(f"Hledám ovladač '{self.target_name}' (Čekám max {timeout}s)...")
        
        for i in range(timeout):
            # 1. Projdeme všechna připojená zařízení
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            
            for dev in devices:
                if self.target_name in dev.name:
                    self.device = dev
                    print(f"-> ÚSPĚCH: Nalezen {dev.name} na {dev.phys}")
                    return True
            
            # 2. Pokud nenalezeno, počkáme 1 sekundu a zkusíme znovu
            if i < timeout - 1:
                print(f".", end="", flush=True) # Vypíše tečku jako indikátor čekání
                await asyncio.sleep(1)
        
        print(f"\n-> TIMEOUT: Ovladač '{self.target_name}' nebyl nalezen ani po {timeout} sekundách.")
        return False

    async def listen(self):
        """Hlavní smyčka čtení - spustí se až po úspěšném connect()"""
        if not self.device:
            return

        print(f"Začínám číst vstupy z {self.device.name}...")
        
        try:
            # async_read_loop je klíčové - neblokuje zbytek programu
            async for event in self.device.async_read_loop():
                self._handle_event(event)
                
        except OSError:
            print("CHYBA: Ovladač byl odpojen!")
            # Zde můžeme přidat logiku pro bezpečné zastavení robota
            self.logic.set_movement(0, 0) 

    def _handle_event(self, event):
        # ... (Tato část zůstává stejná jako v předchozí verzi) ...
        # Zde je mapování tlačítek a os na funkce self.logic
        
        # Příklad zkráceně:
        if event.type == ecodes.EV_ABS:
            if event.code == config.AXIS_LY:
                self.current_speed = -self._map_axis(event.value)
                self.logic.set_movement(self.current_speed, self.current_turn)
            elif event.code == config.AXIS_LX:
                self.current_turn = self._map_axis(event.value)
                self.logic.set_movement(self.current_speed, self.current_turn)
        
        elif event.type == ecodes.EV_KEY and event.value == 1:
            if event.code == config.BTN_A:
                asyncio.create_task(self.logic.fire_weapon())

    def _map_axis(self, value):
        centered = value - 32768
        if abs(centered) < config.DEADZONE:
            return 0.0
        return centered / 32768.0