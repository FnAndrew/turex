# config.py

# Piny pro motory (příklad pro H-Můstek L298N nebo podobné)
MOTOR_FL_PINS = (17, 27) # Front Left
MOTOR_FR_PINS = (22, 23) # Front Right
MOTOR_RL_PINS = (24, 25) # Rear Left
MOTOR_RR_PINS = (5, 6)   # Rear Right

# Piny pro věž
SERVO_PAN_PIN = 12  # Horizontální
SERVO_TILT_PIN = 13 # Vertikální
LASER_PIN = 16

# Zbraň a efekty # TODO: Nastavit správné piny
GUN_SENZOR_PIN = 6
GUN_MOSFET_PIN = 5
SAFETY_TIMEOUT = 2.0  # seconds (2000 ms = 2.0 s)

# Nastavení ovladače
# Cesta k zařízení (po spárování přes bluetooth se objeví v /dev/input/)
GAMEPAD_DEVICE = '/dev/input/event0'
BTN_HOLD_TIME = 1.0  # seconds pro dlouhý stisk

# Xbox ovladač
BTN_A = 304  # Příklad kódu pro tlačítko A
BTN_B = 305
BTN_TR = 311 # Pravý Bumper (R1)

# Deadzone pro páčky (aby robot neujizdel sam)
DEADZONE = 4000 # Pro rozsah 0-65535 je střed cca 32000, 4000 je ok tolerance

# LED pins (multiple LEDs with labels)
LED_PINS = {
    'status': 19,      # Status LED (original LED_PIN)
    'indicator': 20,   # Indicator LED
    'armed': 21,       # Armed LED
}

LASER_PIN = 16