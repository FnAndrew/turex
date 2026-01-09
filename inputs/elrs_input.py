import serial
import asyncio
# Importujeme tvůj parser kanálů (nebo ho dej sem)
from utils.crsf_parser import parse_crsf_channels 

class ElrsInput:
    def __init__(self, port, logic_controller):
        self.port = port
        self.logic = logic_controller # Odkaz na RobotLogic
        self.running = True

    async def listen(self):
        """Hlavní smyčka pro ELRS"""
        print(f"Startuji ELRS na {self.port}")
        
        # Otevření portu (blokující, ale jen jednou)
        try:
            ser = serial.Serial(self.port, 420000, timeout=0.1)
        except Exception as e:
            print(f"ELRS Error: {e}")
            return

        buffer = bytearray()
        
        # Async smyčka
        while self.running:
            # Přečteme data (neblokujícím způsobem)
            if ser.in_waiting:
                data = ser.read(ser.in_waiting)
                buffer.extend(data)
            
            # Zpracování paketů (zjednodušeno pro ukázku)
            while len(buffer) >= 26:
                if buffer[0] != 0xC8:
                    buffer.pop(0)
                    continue
                
                length = buffer[1]
                if len(buffer) < length + 2: break
                
                if buffer[2] == 0x16: # RC Channels
                    channels = parse_crsf_channels(buffer[3:25])
                    if channels:
                        self._process_channels(channels)
                
                del buffer[:length + 2]

            # Důležité! Uvolníme CPU pro ostatní procesy (motory atd.)
            await asyncio.sleep(0.005)

    def _process_channels(self, ch):
        # Mapování kanálů (0-2047) na Logiku (-1.0 až 1.0)
        # CH1: Roll (Zatáčení), CH2: Pitch (Vpřed/Vzad) - Pozor na mapování AETR/TAER
        
        # Příklad AETR (Ail, Ele, Thr, Rud)
        turn = self._map(ch[0])  # CH1
        speed = self._map(ch[2]) # CH3 (Plyn)
        
        # Voláme logiku
        self.logic.set_movement(speed, turn)
        
        # Přepínač na střelbu (AUX1 / CH5)
        if ch[4] > 1500: # Pokud je přepínač nahoře
             # Musíme zajistit, aby to nestřílelo 50x za vteřinu (debounce řeší Gun třída nebo logika)
             asyncio.create_task(self.logic.fire_weapon())

    def _map(self, val):
        """Převod 172-1811 na -1.0 až 1.0"""
        norm = (val - 992) / 820.0 
        return max(-1.0, min(1.0, norm))