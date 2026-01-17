import serial
import asyncio
from inputs.crsf_parser import parse_crsf_channels, map_channel_to_normalized

class ElrsInput:
    def __init__(self, port, logic_controller):
        self.port = port
        self.logic = logic_controller
        self.running = True
        self.ser = None
        self._fire_task = None

    async def listen(self):
        """Non-blocking ELRS main loop"""
        print(f"Starting ELRS on {self.port}")
        
        try:
            # Open port with non-blocking behavior
            self.ser = serial.Serial(self.port, 420000, timeout=0.01)
        except Exception as e:
            print(f"ELRS Error: {e}")
            return

        buffer = bytearray()
        
        try:
            while self.running:
                # Non-blocking read
                if self.ser.in_waiting:
                    data = self.ser.read(self.ser.in_waiting)
                    buffer.extend(data)
                
                # Process packets
                while len(buffer) >= 26:
                    if buffer[0] != 0xC8:
                        buffer.pop(0)
                        continue
                    
                    length = buffer[1]
                    if len(buffer) < length + 2:
                        break
                    
                    if buffer[2] == 0x16:  # RC Channels
                        channels = parse_crsf_channels(buffer[3:25])
                        if channels:
                            self._process_channels(channels)
                    
                    del buffer[:length + 2]

                # Yield control to other coroutines
                await asyncio.sleep(0.005)
        
        finally:
            if self.ser:
                self.ser.close()

    def _process_channels(self, ch):
        """Map channels to robot logic (non-blocking)"""
        # Channel mapping (AETR layout - adjust if needed)
        # CH1: Roll/Turn, CH2: Pitch/Speed, CH3: Throttle, CH5: Aux/Fire
        
        turn = map_channel_to_normalized(ch[0])      # CH1 - Roll
        speed = map_channel_to_normalized(ch[2])     # CH3 - Throttle (often more intuitive)
        
        # Apply movement
        self.logic.set_movement(speed, turn)
        
        # Handle turret (if channels available)
        if len(ch) > 5:
            pan = map_channel_to_normalized(ch[5])   # CH6 optional
            tilt = map_channel_to_normalized(ch[6])  # CH7 optional
            self.logic.move_turret(pan, tilt)
        
        # Fire weapon on CH5 switch (debounced)
        if len(ch) > 4 and ch[4] > 1500:
            # Only fire if not already firing
            if self._fire_task is None or self._fire_task.done():
                self._fire_task = asyncio.create_task(self.logic.fire_weapon())