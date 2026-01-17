from gpiozero import OutputDevice, Button
import asyncio

class Gun:
    def __init__(self, sensor_pin, mosfet_pin, safety_timeout):
        self.firing_in_progress = False
        self.start_time = 0.0
        self.safety_timeout = safety_timeout
        self.mosfet = OutputDevice(mosfet_pin, active_high=True, initial_value=False)
        self.sensor = Button(sensor_pin, pull_up=True, bounce_time=None)

    async def fire_shot(self):
        """Starts the firing process if not already in progress."""
        if self.firing_in_progress:
            return

        print("--> START: Initiating firing cycle...")
        self.mosfet.on()  # Turn on the MOSFET
        self.firing_in_progress = True
        self.start_time = asyncio.get_event_loop().time()  # Record the start time

        try:
            # Wait for the firing process to complete or timeout
            while self.firing_in_progress:
                current_time = asyncio.get_event_loop().time()

                # A) End-stop sensor check (Cut-off)
                if self.sensor.is_pressed:
                    self.stop_firing("DONE: Sensor triggered (cycle complete)")
                    break

                # B) Safety timeout check
                elif (current_time - self.start_time) > self.safety_timeout:
                    self.stop_firing("ERROR: Timeout (motor running too long)")
                    break

                # Short delay to prevent busy-waiting
                await asyncio.sleep(0.01)

        finally:
            self.firing_in_progress = False

    def stop_firing(self, reason):
        """Stops the firing process and logs the reason."""
        self.mosfet.off()  # Turn off the MOSFET
        self.firing_in_progress = False
        print(f"--> STOP: {reason}")