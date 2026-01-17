import asyncio
from hardware.drivetrain import Drivetrain
from hardware.turret import Turret
from hardware.gun import Gun
from hardware.lights import Lights

class RobotLogic:
    def __init__(self, drivetrain: Drivetrain, turret: Turret, gun: Gun, lights: Lights):
        self.drive = drivetrain
        self.turret = turret
        self.gun = gun
        self.lights = lights
        
        # Turret speed storage
        self.turret_speed_pan = 0.0
        self.turret_speed_tilt = 0.0
        
        # Armed state
        self.armed = False
        self._update_armed_led()

    def toggle_armed(self):
        """Toggle armed state and update LED"""
        self.armed = not self.armed
        self._update_armed_led()
        print(f">>> ROBOT {'ARMED' if self.armed else 'DISARMED'} <<<")

    def _update_armed_led(self):
        """Update armed LED based on armed state"""
        if self.armed:
            self.lights.led_on('armed')
        else:
            self.lights.led_off('armed')

    # Tyto metody bude volat JAKÝKOLIV ovladač
    def set_movement(self, speed, turn):
        """ speed: -1.0 až 1.0, turn: -1.0 až 1.0 """
        self.drive.set_move(speed, turn)

    def set_turret_position(self, pan_percent, tilt_percent):
        """Set turret position directly from controller stick
        
        Args:
            pan_percent: -100 to +100 (left to right)
            tilt_percent: -100 to +100 (down to up)
        """
        # Map -100..+100 to servo angle ranges
        # Pan: -100..+100 -> -135..+135 degrees
        pan_angle = (pan_percent / 100.0) * 135
        # Tilt: -100..+100 -> -90..+90 degrees
        tilt_angle = (tilt_percent / 100.0) * 90
        
        self.turret.set_position(pan_angle, tilt_angle)

    def move_turret(self, pan_speed, tilt_speed):
        """ Rychlost otáčení věže (pro jiné ovladače) """
        # Uložíme si rychlosti a aplikujeme je v loop()
        self.turret_speed_pan = pan_speed
        self.turret_speed_tilt = tilt_speed

    async def fire_weapon(self):
        """Fire weapon only if armed"""
        if not self.armed:
            print("!!! GUN DISABLED: Robot not armed !!!")
            return
        await self.gun.fire_shot()
    
    def set_laser(self, state: bool):
        """Control laser on/off via turret."""
        self.turret.set_laser(state)
        
    def toggle_laser(self):
        """Toggle laser on/off via turret."""
        self.turret.toggle_laser()

    def stop_all(self):
        self.drive.stop()
        self.turret.set_laser(False)
        self.lights.cleanup()
        # Další bezpečnostní kroky...

    async def loop(self):
        """Main robot control loop"""
        while True:
            # Update drivetrain
            await self.drive.update()
            
            # Update turret movement from stored speeds
            # Convert speed (-1.0 to 1.0) to angle delta per cycle
            if self.turret_speed_pan != 0 or self.turret_speed_tilt != 0:
                # Speed multiplier: degrees per cycle (adjust for sensitivity)
                # Pan: 270° range, use larger multiplier for faster movement
                delta_pan = self.turret_speed_pan * 8  # Max ~8 degrees per 0.02s cycle
                # Tilt: 180° range
                delta_tilt = self.turret_speed_tilt * 5  # Max ~5 degrees per 0.02s cycle
                
                self.turret.move(delta_pan, delta_tilt)
            
            # Always update turret to apply new position
            await self.turret.update()
            
            await asyncio.sleep(0.02)