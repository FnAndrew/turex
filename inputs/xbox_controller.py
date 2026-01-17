import evdev
from evdev import ecodes
import asyncio
import config

class XboxController:
    def __init__(self, logic_controller):
        self.target_name = "Xbox"  # Část názvu zařízení, kterou hledáme
        self.logic = logic_controller
        self.device = None
        
        # Interní stavové proměnné (pro uchování hodnoty jedné osy, zatímco se mění druhá)
        self.speed = 0.0
        self.turn = 0.0
        self.turret_pan = 0.0
        self.turret_tilt = 0.0
        
        # Dictionary to track button press start times
        self.press_times = {}

    async def connect(self, timeout=20):
        """
        Pokusí se najít Xbox ovladač. Čeká max 'timeout' sekund.
        """
        print(f"Hledám ovladač '{self.target_name}' (Čekám max {timeout}s)...")
        print(f"MAC (z configu): {config.XBOX_MAC}")
        
        for i in range(timeout):
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            
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
        """
        Hlavní asynchronní smyčka pro čtení vstupů.
        """
        if not self.device:
            print("Chyba: Ovladač není připojen, nemohu číst.")
            return

        print(f"Začínám číst vstupy z {self.device.name} na {self.device.phys}...")
        
        try:
            # async_read_loop neblokuje zbytek programu!
            async for event in self.device.async_read_loop():
                self._handle_event(event)
                
        except OSError:
            print("CHYBA: Ovladač byl odpojen!")
            # Bezpečně zastavíme robota
            self.logic.zastavit_vse()

    def _handle_event(self, event):
        """
        Zpracování jedné události (stisk tlačítka nebo pohyb páčky).
        Zde mapujeme kódy z evdev na funkce robota.
        """
        # --- 1. TLAČÍTKA - bereme slovník z configu ---
        if event.type == ecodes.EV_KEY:
            nazev = config.BUTTON_MAP.get(event.code, f"Neznámé {event.code}")

            if event.value == 1:  # PRESS (DOWN)
                print(f"STISK: {nazev}")
                self.press_times[event.code] = event.timestamp()

            elif event.value == 0:  # RELEASE (UP)
                print(f"PUŠTĚNÍ: {nazev}")
                
                if event.code in self.press_times:
                    duration = event.timestamp() - self.press_times[event.code]
                    print(f"   -> Drženo po dobu: {duration:.2f} sekund")
                    
                    # Logic based on press duration
                    if duration > config.BTN_HOLD_TIME:
                        print(f"   -> (Dlouhý stisk!)")
                        self._handle_long_press(event.code, nazev, duration)
                    else:
                        self._handle_short_press(event.code, nazev, duration)
                    
                    del self.press_times[event.code]

            elif event.value == 2:  # HOLD
                print(f"DRŽENÍ: {nazev}")

        # --- 2. OSY - porovnáváme s ID z configu ---
        elif event.type == ecodes.EV_ABS:

            if event.code == config.AXIS_LX:
                print(f"Levá X: {self.map_axis_stick(event.value)}%")
                # Zachováme původní mapování na pohyb
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

            elif event.code == config.AXIS_GAS:
                print(f"PLYN: {self.map_trigger(event.value)}%")
                # val = self._map_trigger(event.value)
                # Příklad: pokud je plyn více než 50%, vystřelíme
                # if val > 50:
                #     asyncio.create_task(self.logic.fire_weapon())

            elif event.code == config.AXIS_BRAKE:
                print(f"BRZDA: {self.map_trigger(event.value)}%")

            elif event.code == config.AXIS_DPAD_X:
                smery = {-1: "Vlevo", 1: "Vpravo", 0: "Střed"}
                print(f"D-PAD X: {smery.get(event.value)}")

            elif event.code == config.AXIS_DPAD_Y:
                smery = {-1: "Nahoru", 1: "Dolů", 0: "Střed"}
                print(f"D-PAD Y: {smery.get(event.value)}")

    def _handle_short_press(self, code, nazev, duration):
        """Handle short button press (< 2 seconds)."""
        if code == config.BTN_A:
            asyncio.create_task(self.logic.fire_weapon())
        elif code == config.BTN_B:
            if hasattr(self.logic, 'stop_weapon_manual'):
                self.logic.stop_weapon_manual()
        elif code == config.BTN_Y:
            self.logic.toggle_laser()

    def _handle_long_press(self, code, nazev, duration):
        """Handle long button press (>= 2 seconds)."""
        # Add your long-press logic here
        pass

    def _map_axis(self, value):
        """
        Převede surovou hodnotu (0-65535) na rozsah -100 až 100 (nebo -1.0 až 1.0).
        Používá DEADZONE z configu.
        """
        centered = value - 32768
        
        # Aplikace Deadzone (z configu)
        if abs(centered) < config.DEADZONE:
            return 0.0
            
        # Normalizace na procenta (-100 až 100)
        # Pokud chceš raději -1.0 až 1.0, smaž "* 100"
        percent = (centered / 32768.0) * 100
        return int(percent)

    def map_axis_stick(self, value):
        """Wrapper that returns stick position as -100..100 percentage."""
        return int(self._map_axis(value))

    def map_trigger(self, value):
        """Normalize trigger raw value to 0-100% for printing.

        Handles common raw ranges (0-1023, 0-255, 0-65535).
        """
        # Heuristic to determine max range
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
        """
        Převede trigger (0-1023) na 0-100%.
        """
        return int((value / 1023.0) * 100)