import asyncio
import sys
import config
from gpiozero import Button

# Hardware imports
from hardware.drivetrain import Drivetrain
from hardware.turret import Turret
from hardware.gun import Gun
from hardware.lights import Lights

# Logic imports
from core.robot_logic import RobotLogic

# Input imports
from inputs.xbox_controller import XboxController
from inputs.elrs_input import ElrsInput

async def main():
    print("=== STARTING BATTLE ROBOT SYSTEM ===")

    # Hardware initialization
    print("-> Initializing hardware...")
    try:
        drivetrain = Drivetrain(
            config.MOTOR_FL_PINS, config.MOTOR_FR_PINS, 
            config.MOTOR_RL_PINS, config.MOTOR_RR_PINS
        )
        turret = Turret(
            config.SERVO_PAN_PIN, config.SERVO_TILT_PIN, config.LASER_PIN
        )
        gun = Gun(
            config.GUN_SENSOR_PIN, config.GUN_MOSFET_PIN, config.SAFETY_TIMEOUT
        )
        lights = Lights()
    except Exception as e:
        print(f"HARDWARE ERROR: {e}")
        return

    # Logic initialization
    logic = RobotLogic(drivetrain, turret, gun, lights)

    # Input selection based on mode switch
    mode_switch = Button(config.MODE_SWITCH_PIN, pull_up=True)
    input_system = None

    if mode_switch.is_pressed:
        # Mode 1: ELRS
        print("\n[MODE] ELRS (Radiomaster) detected")
        input_system = ElrsInput('/dev/ttyAMA0', logic)

    else:
        # Mode 2: Xbox
        print("\n[MODE] Xbox Controller detected")
        
        input_system = XboxController(logic)
        
        print("Please turn on the controller...")
        is_connected = await input_system.connect(timeout=30)
        
        if not is_connected:
            print("\n!!! Failed to connect controller !!!")
            return

    # Start loops
    print("\n>>> ROBOT READY FOR ACTION <<<")
    print("Press Ctrl+C to exit.")

    try:
        await asyncio.gather(
            input_system.listen(),
            logic.loop()
        )
    except asyncio.CancelledError:
        print("Tasks cancelled.")
    finally:
        print("\n-> Shutting down system...")
        
        logic.stop_all()
        
        print("System shutdown.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nUser terminated program.")