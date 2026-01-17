import asyncio
import sys
import config
from gpiozero import Button

# --- Importy hardwaru ---
from hardware.drivetrain import Drivetrain
from hardware.turret import Turret
from hardware.gun import Gun
from hardware.lights import Lights

# --- Import logiky ---
from core.robot_logic import RobotLogic

# --- Importy vstupů ---
from inputs.xbox_controller import XboxController
from inputs.elrs_input import ElrsInput

async def main():
    print("=== STARTUJI SYSTÉM BATTLE ROBOT ===")

    # ---------------------------------------------------------
    # 1. Inicializace Hardwaru
    # ---------------------------------------------------------
    print("-> Inicializace hardwaru...")
    try:
        dt = Drivetrain(
            config.MOTOR_FL_PINS, config.MOTOR_FR_PINS, 
            config.MOTOR_RL_PINS, config.MOTOR_RR_PINS
        )
        turret = Turret(
            config.SERVO_PAN_PIN, config.SERVO_TILT_PIN, config.LASER_PIN
        )
        gun = Gun(
            config.GUN_SENZOR_PIN, config.GUN_MOSFET_PIN, config.SAFETY_TIMEOUT
        )
        lights = Lights()
    except Exception as e:
        print(f"CHYBA HARDWARU: {e}")
        return

    # ---------------------------------------------------------
    # 2. Inicializace Mozku (Logiky)
    # ---------------------------------------------------------
    logic = RobotLogic(dt, turret, gun, lights)

    # ---------------------------------------------------------
    # 3. Volba vstupu podle přepínače
    # ---------------------------------------------------------
    mode_switch = Button(config.MODE_SWITCH_PIN, pull_up=True)
    input_system = None

    if mode_switch.is_pressed:
        # --- REŽIM 1: ELRS ---
        print("\n[REŽIM] Detekován ELRS (Radiomaster)")
        input_system = ElrsInput('/dev/ttyAMA0', logic)

    else:
        # --- REŽIM 2: XBOX ---
        print("\n[MODE] Xbox Controller detected")
        
        input_system = XboxController(logic)
        
        # Wait up to 30 seconds for controller to connect
        print("Please turn on the controller...")
        is_connected = await input_system.connect(timeout=30)
        
        if not is_connected:
            print("\n!!! Failed to connect controller !!!")
            return

    # ---------------------------------------------------------
    # 4. Spuštění smyček
    # ---------------------------------------------------------
    print("\n>>> ROBOT PŘIPRAVEN K AKCI <<<")
    print("Stiskni Ctrl+C pro ukončení.")

    try:
        # Spustíme paralelně naslouchání vstupu a hlavní smyčku logiky
        await asyncio.gather(
            input_system.listen(),
            logic.loop()
        )
    except asyncio.CancelledError:
        print("Úlohy zrušeny.")
    finally:
        # Tento blok se provede VŽDY při ukončení (i při chybě)
        print("\n-> Vypínám systém...")
        
        logic.stop_all()
        
        print("Systém vypnut.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Zachycení Ctrl+C, aby to nevypisovalo ošklivý traceback
        print("\nUživatel ukončil program.")