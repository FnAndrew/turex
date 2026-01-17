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

    # Tyto metody bude volat JAKÝKOLIV ovladač
    def set_movement(self, speed, turn):
        """ speed: -1.0 až 1.0, turn: -1.0 až 1.0 """
        self.drive.set_move(speed, turn)

    def move_turret(self, pan_speed, tilt_speed):
        """ Rychlost otáčení věže """
        # Uložíme si rychlosti a aplikujeme je v loop()
        self.turret_speed_pan = pan_speed
        self.turret_speed_tilt = tilt_speed

    async def fire_weapon(self):
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
            if self.turret_speed_pan != 0 or self.turret_speed_tilt != 0:
                delta_pan = self.turret_speed_pan * 5  # Adjust sensitivity (degrees per cycle)
                delta_tilt = self.turret_speed_tilt * 5
                self.turret.move(delta_pan, delta_tilt)
                await self.turret.update()
            
            await asyncio.sleep(0.02)