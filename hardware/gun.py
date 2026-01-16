from gpiozero import OutputDevice, Button
import asyncio

# --- GPIO PIN CONFIGURATION (BCM numbering for Raspberry Pi) ---
# Adjust pin numbers according to your Raspberry Pi setup (GPIO 6 and GPIO 2)
mosfet = OutputDevice(6, active_high=True, initial_value=False)  # MOSFET control
sensor = Button(2, pull_up=True, bounce_time=None)  # End-stop sensor

# --- VARIABLES ---
SAFETY_TIMEOUT = 2.0  # seconds (2000 ms = 2.0 s)

class Gun:
    def __init__(self):
        self.firing_in_progress = False
        self.start_time = 0.0

    async def fire_shot(self):
        """Starts the firing process if not already in progress."""
        if self.firing_in_progress:
            return

        print("--> START: Initiating firing cycle...")
        mosfet.on()  # Turn on the MOSFET
        self.firing_in_progress = True
        self.start_time = asyncio.get_event_loop().time()  # Record the start time

        try:
            # Wait for the firing process to complete or timeout
            while self.firing_in_progress:
                current_time = asyncio.get_event_loop().time()

                # A) End-stop sensor check (Cut-off)
                if sensor.is_pressed:
                    self.stop_firing("DONE: Sensor triggered (cycle complete)")
                    break

                # B) Safety timeout check
                elif (current_time - self.start_time) > SAFETY_TIMEOUT:
                    self.stop_firing("ERROR: Timeout (motor running too long)")
                    break

                # Short delay to prevent busy-waiting
                await asyncio.sleep(0.01)

        finally:
            self.firing_in_progress = False

    def stop_firing(self, reason):
        """Stops the firing process and logs the reason."""
        mosfet.off()  # Turn off the MOSFET
        self.firing_in_progress = False
        print(f"--> STOP: {reason}")