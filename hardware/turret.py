from gpiozero import AngularServo, Servo, LED
import config
import json
import os

class Turret:
    def __init__(self, pan_pin, tilt_pin, laser_pin):
        # Load last known position
        _, saved_tilt = self.load_state()

        print(f"Starting turret with continuous pan stopped and saved tilt={saved_tilt}°")

        # Initialize servos at a safe neutral state (prevents startup jerk).
        # Pan servo: continuous rotation, centered at stop.
        # Tilt servo: positional servo.
        self.pan_servo = Servo(
            pan_pin, 
            initial_value=0.0,
            min_pulse_width=config.SERVO_PAN_MIN_PULSE_WIDTH,
            max_pulse_width=config.SERVO_PAN_MAX_PULSE_WIDTH,
        )
        self.tilt_servo = AngularServo(
            tilt_pin, 
            initial_angle=saved_tilt,
            min_angle=config.SERVO_TILT_MIN_ANGLE, 
            max_angle=config.SERVO_TILT_MAX_ANGLE,
            min_pulse_width=config.MIN_PULSE_WIDTH,
            max_pulse_width=config.MAX_PULSE_WIDTH,
        )
        self.laser = LED(laser_pin)
        
        # Continuous pan uses speed commands instead of a stored angle.
        self.pan_speed = 0.0
        self.tilt_angle = saved_tilt

    def load_state(self):
        """Load turret state from file.

        Pan is continuous rotation, so only the tilt angle is restored.
        Returns (0.0, 0) if file doesn't exist.
        """
        if os.path.exists(config.SERVO_STATE_FILE):
            try:
                with open(config.SERVO_STATE_FILE, "r") as f:
                    data = json.load(f)
                    tilt = data.get("tilt", 0)
                    
                    # Validate loaded values are within bounds
                    tilt = max(config.SERVO_TILT_MIN_ANGLE, min(config.SERVO_TILT_MAX_ANGLE, tilt))
                    
                    return 0.0, tilt
            except Exception as e:
                print(f"Error reading turret state file: {e}. Starting at center.")
        return 0.0, 0

    def save_state(self):
        """Save current turret position to file."""
        data = {
            "pan": 0.0,
            "tilt": self.tilt_angle
        }
        try:
            with open(config.SERVO_STATE_FILE, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Turret position saved: Pan=continuous stop, Tilt={self.tilt_angle}°")
        except Exception as e:
            print(f"Error saving turret state: {e}")

    async def update(self):
        """Update servo positions"""
        self.pan_servo.value = self.pan_speed
        self.tilt_servo.angle = self.tilt_angle

    def set_position(self, pan_angle, tilt_angle):
        """Directly set turret pan speed and tilt angle.
        
        Args:
            pan_angle: -100 to +100 percent speed for continuous rotation
            tilt_angle: -90 to +90 degrees (down to up)
        """
        self.set_pan_speed(pan_angle / 100.0)
        self.set_tilt_angle(tilt_angle)

    def move(self, delta_pan, delta_tilt):
        """Backward-compatible wrapper for the continuous pan control path."""
        self.set_pan_speed(delta_pan)
        self.adjust_tilt(delta_tilt)
        self.tilt_angle = max(config.SERVO_TILT_MIN_ANGLE, min(config.SERVO_TILT_MAX_ANGLE, self.tilt_angle + delta_tilt))

    def set_pan_speed(self, pan_speed):
        """Set continuous pan speed in the range -1.0..1.0."""
        self.pan_speed = max(-1.0, min(1.0, pan_speed))

    def set_tilt_angle(self, tilt_angle):
        """Set the tilt servo position in degrees."""
        self.tilt_angle = max(config.SERVO_TILT_MIN_ANGLE, min(config.SERVO_TILT_MAX_ANGLE, tilt_angle))

    def adjust_tilt(self, delta_tilt):
        """Adjust tilt by a relative amount in degrees."""
        self.set_tilt_angle(self.tilt_angle + delta_tilt)

    async def shutdown(self):
        """Save position and prepare for shutdown (no movement required)"""
        self.save_state()
        print("Turret shutdown complete. Position preserved for next startup.")

    def set_laser(self, on: bool):
        """Control laser on/off."""
        if on:
            self.laser.on()
        else:
            self.laser.off()
    
    def toggle_laser(self):
        """Toggle laser on/off."""
        self.laser.toggle()