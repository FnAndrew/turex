from gpiozero import AngularServo, LED

class Turret:
    def __init__(self, pan_pin, tilt_pin, laser_pin):
        # Oprava: Servo nastavení závisí na hardwaru, toto je příklad
        self.pan_servo = AngularServo(pan_pin, min_angle=-90, max_angle=90)
        self.tilt_servo = AngularServo(tilt_pin, min_angle=-45, max_angle=45)
        self.laser = LED(laser_pin)
        
        self.pan_angle = 0
        self.tilt_angle = 0

    async def update(self):
        """Aktualizuje polohu serv"""
        self.pan_servo.angle = self.pan_angle
        self.tilt_servo.angle = self.tilt_angle

    def move(self, delta_pan, delta_tilt):
        """Příčte změnu úhlu (např. z joysticku) k aktuální poloze"""
        self.pan_angle = max(-90, min(90, self.pan_angle + delta_pan))
        self.tilt_angle = max(-45, min(45, self.tilt_angle + delta_tilt))

    def set_laser(self, on: bool):
        if on: self.laser.on()
        else: self.laser.off()