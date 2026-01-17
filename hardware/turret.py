from gpiozero import AngularServo, LED
import config

class Turret:
    def __init__(self, pan_pin, tilt_pin, laser_pin):
        # Pan servo: 270° range (-135° to +135°)
        self.pan_servo = AngularServo(pan_pin, min_angle=config.SERVO_PAN_MIN_ANGLE, max_angle=config.SERVO_PAN_MAX_ANGLE)
        # Tilt servo: 180° range (-90° to +90°)
        self.tilt_servo = AngularServo(tilt_pin, min_angle=config.SERVO_TILT_MIN_ANGLE, max_angle=config.SERVO_TILT_MAX_ANGLE)
        self.laser = LED(laser_pin)
        
        # Start at center position
        self.pan_angle = 0
        self.tilt_angle = 0
        
        # Boundaries
        self.pan_min = config.SERVO_PAN_MIN_ANGLE
        self.pan_max = config.SERVO_PAN_MAX_ANGLE
        self.tilt_min = config.SERVO_TILT_MIN_ANGLE
        self.tilt_max = config.SERVO_TILT_MAX_ANGLE

    async def update(self):
        """Update servo positions"""
        self.pan_servo.angle = self.pan_angle
        self.tilt_servo.angle = self.tilt_angle

    def set_position(self, pan_angle, tilt_angle):
        """Directly set turret position in degrees
        
        Args:
            pan_angle: -135 to +135 degrees (left to right)
            tilt_angle: -90 to +90 degrees (down to up)
        """
        self.pan_angle = max(self.pan_min, min(self.pan_max, pan_angle))
        self.tilt_angle = max(self.tilt_min, min(self.tilt_max, tilt_angle))

    def move(self, delta_pan, delta_tilt):
        """Add change in angle to current position"""
        self.pan_angle = max(self.pan_min, min(self.pan_max, self.pan_angle + delta_pan))
        self.tilt_angle = max(self.tilt_min, min(self.tilt_max, self.tilt_angle + delta_tilt))

    def set_laser(self, on: bool):
        """Control laser on/off."""
        if on:
            self.laser.on()
        else:
            self.laser.off()
    
    def toggle_laser(self):
        """Toggle laser on/off."""
        self.laser.toggle()