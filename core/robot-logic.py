import asyncio

class RobotLogic:
    def __init__(self, drivetrain, turret, gun):
        self.drive = drivetrain
        self.turret = turret
        self.gun = gun

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
        self.turret.set_laser(state)

    def stop_all(self):
        self.drive.stop()
        self.turret.set_laser(False)
        # Další bezpečnostní kroky...

    async def loop(self):
        # Stejné jako předtím - pravidelný update hardwaru
        while True:
            await self.drive.update()
            # Aplikace pohybu věže...
            await asyncio.sleep(0.02)