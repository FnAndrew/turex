from gpiozero import OutputDevice, Button
import asyncio

class Gun:
    def __init__(self, sensor_pin, mosfet_pin, safety_timeout):
        self.firing_in_progress = False
        self.burst_cancel_requested = False
        self.start_time = 0.0
        self.safety_timeout = safety_timeout
        self.mosfet = OutputDevice(mosfet_pin, active_high=True, initial_value=False)
        self.sensor = Button(sensor_pin, pull_up=False, bounce_time=None) # Pull-up - works on 3.3V

    async def fire_shot(self, logic):  # Pass logic reference
        if not logic.gun_armed:
            print("!!! GUN DISABLED: Not armed !!!")
            return False

        """Starts the firing process if not already in progress."""
        if self.firing_in_progress:
            return False

        print("--> START: Initiating firing cycle...")
        self.mosfet.on()  # Turn on the MOSFET
        self.firing_in_progress = True
        self.start_time = asyncio.get_event_loop().time()  # Record the start time

        # Burst-safe end-stop handling:
        # complete the shot only after we observe a fresh sensor edge.
        # This avoids immediate false "DONE" when the sensor is still latched
        # from the previous shot.
        saw_sensor_release = not self.sensor.is_pressed

        try:
            # Wait for the firing process to complete or timeout
            while self.firing_in_progress:
                current_time = asyncio.get_event_loop().time()

                # A) End-stop edge detection (release -> press)
                if not saw_sensor_release:
                    if not self.sensor.is_pressed:
                        saw_sensor_release = True
                elif self.sensor.is_pressed:
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
        return True

    async def fire_burst(self, logic, shots, inter_shot_delay=0.08):
        """Fire multiple shots in sequence with optional spacing."""
        if shots <= 0:
            return

        self.burst_cancel_requested = False
        print(f"--> BURST: Requested {shots} shot(s)")

        for shot_index in range(shots):
            if self.burst_cancel_requested:
                print("--> BURST: Cancelled")
                break

            fired = await self.fire_shot(logic)
            if not fired:
                break

            if shot_index < shots - 1 and inter_shot_delay > 0:
                await asyncio.sleep(inter_shot_delay)

    def stop_firing(self, reason, cancel_burst=False):
        """Stops the firing process and logs the reason."""
        if cancel_burst:
            self.burst_cancel_requested = True
        self.mosfet.off()  # Turn off the MOSFET
        self.firing_in_progress = False
        print(f"--> STOP: {reason}")