from gpiozero import AngularServo, LED
import config
import json
import os


def _pulse_width_for_angle(angle, hardware_min_angle, hardware_max_angle):
    """Map an angle within the hardware calibration range to a pulse width."""
    hardware_span = hardware_max_angle - hardware_min_angle
    if hardware_span == 0:
        raise ValueError("Servo hardware angle range cannot be zero")

    clamped_angle = max(hardware_min_angle, min(hardware_max_angle, angle))
    pulse_span = config.MAX_PULSE_WIDTH - config.MIN_PULSE_WIDTH
    return config.MIN_PULSE_WIDTH + ((clamped_angle - hardware_min_angle) / hardware_span) * pulse_span

class Turret:
    def __init__(self, pan_pin, tilt_pin, laser_pin):
        # Load last known position
        saved_pan, saved_tilt = self.load_state()
        
        print(f"Starting turret at saved position: Pan={saved_pan}°, Tilt={saved_tilt}°")

        pan_min_pulse_width = _pulse_width_for_angle(
            config.SERVO_PAN_MIN_ANGLE,
            config.SERVO_PAN_HW_MIN_ANGLE,
            config.SERVO_PAN_HW_MAX_ANGLE,
        )
        pan_max_pulse_width = _pulse_width_for_angle(
            config.SERVO_PAN_MAX_ANGLE,
            config.SERVO_PAN_HW_MIN_ANGLE,
            config.SERVO_PAN_HW_MAX_ANGLE,
        )
        tilt_min_pulse_width = _pulse_width_for_angle(
            config.SERVO_TILT_MIN_ANGLE,
            config.SERVO_TILT_HW_MIN_ANGLE,
            config.SERVO_TILT_HW_MAX_ANGLE,
        )
        tilt_max_pulse_width = _pulse_width_for_angle(
            config.SERVO_TILT_MAX_ANGLE,
            config.SERVO_TILT_HW_MIN_ANGLE,
            config.SERVO_TILT_HW_MAX_ANGLE,
        )

        # Initialize servos at saved position (prevents startup jerk)
        # Pan servo: 270° range (-135° to +135°)
        # Tilt servo: 180° range (-90° to +90°)
        self.pan_servo = AngularServo(
            pan_pin, 
            initial_angle=saved_pan,
            min_angle=config.SERVO_PAN_MIN_ANGLE, 
            max_angle=config.SERVO_PAN_MAX_ANGLE,
            min_pulse_width=pan_min_pulse_width,
            max_pulse_width=pan_max_pulse_width,
        )
        self.tilt_servo = AngularServo(
            tilt_pin, 
            initial_angle=saved_tilt,
            min_angle=config.SERVO_TILT_MIN_ANGLE, 
            max_angle=config.SERVO_TILT_MAX_ANGLE,
            min_pulse_width=tilt_min_pulse_width,
            max_pulse_width=tilt_max_pulse_width,
        )
        self.laser = LED(laser_pin)
        
        # Set current angles to saved values
        self.pan_angle = saved_pan
        self.tilt_angle = saved_tilt
        
        # Boundaries
        self.pan_min = config.SERVO_PAN_MIN_ANGLE
        self.pan_max = config.SERVO_PAN_MAX_ANGLE
        self.tilt_min = config.SERVO_TILT_MIN_ANGLE
        self.tilt_max = config.SERVO_TILT_MAX_ANGLE

    def load_state(self):
        """Load turret position from file. Returns (0, 0) if file doesn't exist."""
        if os.path.exists(config.SERVO_STATE_FILE):
            try:
                with open(config.SERVO_STATE_FILE, "r") as f:
                    data = json.load(f)
                    pan = data.get("pan", 0)
                    tilt = data.get("tilt", 0)
                    
                    # Validate loaded values are within bounds
                    pan = max(config.SERVO_PAN_MIN_ANGLE, min(config.SERVO_PAN_MAX_ANGLE, pan))
                    tilt = max(config.SERVO_TILT_MIN_ANGLE, min(config.SERVO_TILT_MAX_ANGLE, tilt))
                    
                    return pan, tilt
            except Exception as e:
                print(f"Error reading turret state file: {e}. Starting at center.")
        return 0, 0

    def save_state(self):
        """Save current turret position to file."""
        data = {
            "pan": self.pan_angle,
            "tilt": self.tilt_angle
        }
        try:
            with open(config.SERVO_STATE_FILE, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Turret position saved: Pan={self.pan_angle}°, Tilt={self.tilt_angle}°")
        except Exception as e:
            print(f"Error saving turret state: {e}")

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