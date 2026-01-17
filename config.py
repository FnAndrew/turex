# Using software PWM-capable pins, avoiding hardware PWM reserved for servos
MOTOR_FL_PINS = (17, 27)  # Front Left - OK
MOTOR_FR_PINS = (22, 23)  # Front Right - OK
MOTOR_RL_PINS = (24, 25)  # Rear Left - OK
MOTOR_RR_PINS = (5, 6)    # Rear Right - OK (FIXED: No longer conflicts with gun)

# === TURRET SERVOS ===
# Using hardware PWM pins for smooth servo control
SERVO_PAN_PIN = 12   # Horizontal (PWM0)
SERVO_TILT_PIN = 13  # Vertical (PWM1)

# === WEAPON SYSTEM ===
# FIXED: Changed from conflicting pins 5, 6
GUN_SENZOR_PIN = 26  # End-stop sensor (was 6)
GUN_MOSFET_PIN = 19  # Motor control (was 5)
SAFETY_TIMEOUT = 2.0  # seconds

# === LASER ===
LASER_PIN = 16  # OK

# === LED INDICATORS ===
LED_PINS = {
    'status': 20,      # Status LED (changed from 19 to avoid gun conflict)
    'indicator': 21,   # Indicator LED
    'armed': 4,        # Armed LED (changed from 21 to avoid mode switch)
}

# === MODE SWITCH ===
# This is defined in main.py as MODE_SWITCH_PIN = 21
# Suggested change: Use GPIO14 instead (see main.py fix below)
MODE_SWITCH_PIN = 14  # Changed from 21 to avoid conflict with 'armed' LED

# === CONTROLLER SETTINGS ===
GAMEPAD_DEVICE = '/dev/input/event0'
BTN_HOLD_TIME = 1.0  # seconds

# Xbox MAC address (for reference)
XBOX_MAC = "XX:XX:XX:XX:XX:XX"

# Xbox controller button codes
BTN_A = 304
BTN_B = 305
BTN_X = 307
BTN_Y = 308
BTN_TR = 311  # Right Bumper

# Axis codes
AXIS_LX = 0    # Left stick X
AXIS_LY = 1    # Left stick Y
AXIS_RX = 3    # Right stick X
AXIS_RY = 4    # Right stick Y
AXIS_GAS = 5
AXIS_BRAKE = 2
AXIS_DPAD_X = 16
AXIS_DPAD_Y = 17

# Deadzone for joysticks
DEADZONE = 4000

# Button mapping for display
BUTTON_MAP = {
    304: "A", 305: "B", 307: "X", 308: "Y",
    310: "LB", 311: "RB", 314: "Select", 315: "Start",
    316: "Xbox Button", 317: "L3", 318: "R3"
}