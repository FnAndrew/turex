# Using software PWM-capable pins, avoiding hardware PWM reserved for servos
MOTOR_FL_PINS = (25, 24)   # Rear Left   (around the 2nd top GND)
MOTOR_FR_PINS = (6, 4)     # Rear Right  (far away but working)
MOTOR_RL_PINS = (21, 20)   # Front Right (top corner)
MOTOR_RR_PINS = (22, 23)   # Front Left  (next to 3.3V)

# === TURRET SERVOS ===
# Using hardware PWM pins for smooth servo control
SERVO_PAN_PIN = 12   # Horizontal (PWM0)
SERVO_TILT_PIN = 13  # Vertical (PWM1)
# Select which turret implementation to use: "continuous" or "legacy".
TURRET_MODE = "continuous"

# Continuous pan calibration.
SERVO_PAN_MIN_PULSE_WIDTH = 0.0005
SERVO_PAN_MAX_PULSE_WIDTH = 0.0025
SERVO_PAN_STOP_PULSE_WIDTH = 0.0015
# Flip this if right-stick left/right rotates the pan servo in the wrong direction.
SERVO_PAN_INVERT_DIRECTION = False
SERVO_TITL_INVERT_DIRECTION = True

# Legacy positional pan travel limits and calibration.
# This is kept for the switchable old turret implementation.
SERVO_PAN_MIN_ANGLE = -135
SERVO_PAN_MAX_ANGLE = 135
SERVO_PAN_HW_MIN_ANGLE = -135
SERVO_PAN_HW_MAX_ANGLE = 135

# Tilt travel limits and calibration.
SERVO_TILT_MIN_ANGLE = -80
SERVO_TILT_MAX_ANGLE = 80
SERVO_TILT_HW_MIN_ANGLE = -90
SERVO_TILT_HW_MAX_ANGLE = 90
SERVO_STATE_FILE = "turret_state.json"

# Shared pulse-width calibration used by the positional tilt servo.
MIN_PULSE_WIDTH = 0.0005
MAX_PULSE_WIDTH = 0.0025

# Legacy pan movement step used when the old positional turret is selected.
SERVO_PAN_MOVE_STEP_DEGREES = 8.0

# === WEAPON SYSTEM ===
# FIXED: Changed from conflicting pins 5, 6
GUN_SENSOR_PIN = 26  # End-stop sensor (was 6)
GUN_MOSFET_PIN = 19  # Motor control (was 5)
SAFETY_TIMEOUT = 2.0  # seconds
# Burst firing from A button hold duration.
# Shots scale as: floor(hold_seconds / BURST_HOLD_STEP) + 1, capped by BURST_MAX_SHOTS.
BURST_HOLD_STEP = 0.45  # seconds required per additional shot
BURST_MAX_SHOTS = 5
BURST_INTER_SHOT_DELAY = 0.08  # seconds between burst shots

# === LASER ===
LASER_PIN = 16  # OK

# === LED INDICATORS ===
LED_PINS = {
    'status': 17,      # Status LED
    'indicator': 2,   # Indicator LED
    'armed': 18,        # Armed LED (keep it here, changed from 21 to avoid mode switch)
}

# === MODE SWITCH ===
MODE_SWITCH_PIN = 27

# === CONTROLLER SETTINGS ===
GAMEPAD_DEVICE = '/dev/input/event0'
ELRS_PORT = '/dev/ttyAMA0'  # Serial port for ELRS receiver

BTN_HOLD_TIME = 1.0  # seconds
XBOX_DEBUG = False  # Set to True to enable debug prints for Xbox controller events
XBOX_MAC = "44:16:22:8C:36:96" # Xbox MAC address

# Xbox controller button codes
BTN_A = 304
BTN_B = 305
BTN_X = 307
BTN_Y = 308
BTN_TR = 311  # Right Bumper
BTN_START = 315
BTN_BACK = 314
BTN_XBOX = 316
BTN_SHARE = 167

# Buttons that support long press (others use short press only)
LONG_PRESS_BUTTONS = [BTN_A, BTN_SHARE]

# Axis codes
AXIS_LX = 0    # Left stick X
AXIS_LY = 1    # Left stick Y
AXIS_RX = 2    # Right stick X
AXIS_RY = 5    # Right stick Y
AXIS_GAS = 9
AXIS_BRAKE = 10
AXIS_DPAD_X = 16
AXIS_DPAD_Y = 17

# Deadzone for joysticks
DEADZONE = 6000

# Button mapping for display
BUTTON_MAP = {
    304: "A", 305: "B", 307: "X", 308: "Y",
    310: "LB", 311: "RB", 314: "Select", 315: "Start",
    316: "Xbox Button", 317: "L3", 318: "R3",
    167: "Share Button"
}