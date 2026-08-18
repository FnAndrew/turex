import evdev
from evdev import ecodes
import asyncio
import math
import config

DEBUG = config.XBOX_DEBUG

class XboxController:
    def __init__(self, logic_controller):
        self.target_name = "Xbox"
        self.logic = logic_controller
        self.device = None
        
        self.speed = 0.0
        self.turn = 0.0
        self.turret_pan_speed = 0.0
        self.turret_tilt_speed = 0.0
        
        self.press_times = {}

    async def connect(self, timeout=20):
        """
        Attempts to find Xbox controller. Waits max 'timeout' seconds.
        """
        print(f"Looking for controller '{self.target_name}' (waiting max {timeout}s)...")
        print(f"MAC (from config): {config.XBOX_MAC}")
        
        for i in range(timeout):
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            
            for dev in devices:
                if self.target_name in dev.name:
                    self.device = dev
                    print(f"-> SUCCESS: Found {dev.name} on {dev.phys}")
                    return True
            
            if i < timeout - 1:
                await asyncio.sleep(1)
        
        print(f"\n-> TIMEOUT: Controller not found.")
        return False

    async def listen(self):
        """
        Main asynchronous loop for reading inputs.
        """
        if not self.device:
            print("Error: Controller not connected, cannot read.")
            return

        print(f"Starting to read inputs from {self.device.name} on {self.device.phys}...")
        
        try:
            async for event in self.device.async_read_loop():
                self._handle_event(event)
                
        except OSError:
            print("ERROR: Controller was disconnected!")
            await self.logic.stop_all()

    def _handle_event(self, event):
        """
        Process single event (button press or stick movement).
        """
        # Buttons
        if event.type == ecodes.EV_KEY:
            button_name = config.BUTTON_MAP.get(event.code, f"Unknown {event.code}")

            if event.value == 1:  # PRESS (DOWN)
                if DEBUG:
                    print(f"PRESS: {button_name}")
                self.press_times[event.code] = event.timestamp()

            elif event.value == 0:  # RELEASE (UP)
                if DEBUG:
                    print(f"RELEASE: {button_name}")
                
                if event.code in self.press_times:
                    duration = event.timestamp() - self.press_times[event.code]
                    
                    supports_long_press = event.code in config.LONG_PRESS_BUTTONS
                    
                    if supports_long_press and duration > config.BTN_HOLD_TIME:
                        if DEBUG:
                            print(f"   -> (Long press! {duration:.2f} seconds)")
                        self._handle_long_press(event.code, button_name, duration)
                    else:
                        self._handle_short_press(event.code, button_name, duration)
                    
                    del self.press_times[event.code]

            elif event.value == 2:  # HOLD
                if DEBUG:
                    print(f"HOLD: {button_name}")

        # Axes
        elif event.type == ecodes.EV_ABS:

            if event.code == config.AXIS_LX:
                if DEBUG:
                    print(f"Left X: {self.map_axis_stick(event.value)}%")
                self.turn = self._map_axis(event.value) / 100.0
                self.logic.set_movement(self.speed, self.turn)

            elif event.code == config.AXIS_LY:
                if DEBUG:
                    print(f"Left Y: {self.map_axis_stick(event.value)}%")
                self.speed = -self._map_axis(event.value) / 100.0
                self.logic.set_movement(self.speed, self.turn)

            elif event.code == config.AXIS_RX:
                self.turret_pan_speed = self._map_axis(event.value) / 100.0
                self._apply_turret_stick()

            elif event.code == config.AXIS_RY:
                self.turret_tilt_speed = -self._map_axis(event.value) / 100.0
                self._apply_turret_stick()

            elif event.code == config.AXIS_GAS:
                if DEBUG:
                    print(f"GAS: {self.map_trigger(event.value)}%")

            elif event.code == config.AXIS_BRAKE:
                if DEBUG:
                    print(f"BRAKE: {self.map_trigger(event.value)}%")

            elif event.code == config.AXIS_DPAD_X:
                directions = {-1: "Left", 1: "Right", 0: "Center"}
                if DEBUG:
                    print(f"D-PAD X: {directions.get(event.value)}")

            elif event.code == config.AXIS_DPAD_Y:
                directions = {-1: "Up", 1: "Down", 0: "Center"}
                if DEBUG:
                    print(f"D-PAD Y: {directions.get(event.value)}")

    def _handle_short_press(self, code, button_name, duration):
        """Handle short button press (< 2 seconds)."""
        if code == config.BTN_A:
            self._start_burst_fire(duration)
        elif code == config.BTN_B:
            self.logic.stop_weapon("B button pressed")
        elif code == config.BTN_Y:
            self.logic.toggle_laser()
        elif code == config.BTN_START:
            self.logic.toggle_armed()

    def _handle_long_press(self, code, button_name, duration):
        """Handle long button press (>= 2 seconds)."""
        if DEBUG:
            print(f"   -> BUTTON {button_name} long pressed for {duration:.2f} seconds.")
        if code == config.BTN_A:
            self._start_burst_fire(duration)

    def _start_burst_fire(self, hold_duration):
        """Convert A-button hold duration to burst size and fire it asynchronously."""
        shots = self._shots_from_hold_duration(hold_duration)
        if DEBUG:
            print(f"A hold {hold_duration:.2f}s -> burst {shots} shot(s)")

        asyncio.create_task(
            self.logic.fire_burst(
                shots,
                inter_shot_delay=config.BURST_INTER_SHOT_DELAY
            )
        )

    def _shots_from_hold_duration(self, hold_duration):
        """Scale burst size with hold time using BTN_HOLD_TIME as the step."""
        if hold_duration <= 0:
            return 1

        hold_step = getattr(config, "BURST_HOLD_STEP", config.BTN_HOLD_TIME)
        hold_step = max(0.05, hold_step)
        raw_shots = math.floor(hold_duration / hold_step) + 1
        return max(1, min(config.BURST_MAX_SHOTS, raw_shots))

    def _apply_turret_stick(self):
        """Push the current right-stick state into the turret control path."""
        pan_speed = self.turret_pan_speed
        if config.SERVO_PAN_INVERT_DIRECTION:
            pan_speed = -pan_speed

        if DEBUG:
            print(f"Right stick -> pan={pan_speed * 100:.0f}%, tilt={self.turret_tilt_speed * 100:.0f}%")

        self.logic.move_turret(pan_speed, self.turret_tilt_speed)

    def _map_axis(self, value):
        """
        Convert raw value (0-65535) to range -100 to 100.
        Uses DEADZONE from config.
        """
        centered = value - 32768
        
        # Deadzone check
        if abs(centered) < config.DEADZONE:
            return 0.0
        
        # Normalize from -100 to 100
        percent = (centered / 32768.0) * 100
        return percent

    def map_axis_stick(self, value):
        """Wrapper that returns stick position as -100..100 percentage."""
        return int(round(self._map_axis(value)))

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
            pct = int(int((value / 1023.0) * 100))
        return max(0, min(100, pct))