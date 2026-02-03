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
        
        # Runtime state
        self.gun_armed = False
        
        # Turret speed storage
        self.turret_speed_pan = 0.0
        self.turret_speed_tilt = 0.0
        
        # Sync armed LED on startup
        self.lights.set_led_brightness('armed', 0.0)
    
    def toggle_armed(self):
        """Toggle gun armed state and sync LED."""
        self.gun_armed = not self.gun_armed
        self.lights.set_led_brightness('armed', 1.0 if self.gun_armed else 0.0)
        status = "ARMED" if self.gun_armed else "DISARMED"
        print(f">>> ROBOT {status} <<<")

    def set_movement(self, speed, turn):
        """speed: -1.0 to 1.0, turn: -1.0 to 1.0"""
        self.drive.set_move(speed, turn)

    def set_turret_position(self, pan_percent, tilt_percent):
        """Set turret position directly from controller stick
        
        Args:
            pan_percent: -100 to +100 (left to right)
            tilt_percent: -100 to +100 (down to up)
        """
        pan_angle = (pan_percent / 100.0) * 135
        tilt_angle = (tilt_percent / 100.0) * 90
        
        self.turret.set_position(pan_angle, tilt_angle)

    def move_turret(self, pan_speed, tilt_speed):
        """Turret rotation speed (for other controllers)"""
        self.turret_speed_pan = pan_speed
        self.turret_speed_tilt = tilt_speed

    async def fire_weapon(self):
        """Fire weapon only if armed"""
        if not self.gun_armed:
            print("!!! GUN DISABLED: Robot not armed !!!")
            return
        await self.gun.fire_shot(self)
    
    def set_laser(self, state: bool):
        """Control laser on/off via turret."""
        self.turret.set_laser(state)
        
    def toggle_laser(self):
        """Toggle laser on/off via turret."""
        self.turret.toggle_laser()

    async def stop_all(self):
        self.drive.stop()
        self.turret.set_laser(False)
        await self.turret.shutdown()  # Changed from default_position()
        self.lights.cleanup()

    async def loop(self):
        """Main robot control loop"""
        while True:
            await self.drive.update()
            
            if self.turret_speed_pan != 0 or self.turret_speed_tilt != 0:
                delta_pan = self.turret_speed_pan * 8
                delta_tilt = self.turret_speed_tilt * 5
                
                self.turret.move(delta_pan, delta_tilt)
            
            await self.turret.update()
            
            await asyncio.sleep(0.02)