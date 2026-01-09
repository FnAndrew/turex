import asyncio
import sys
import config
from gpiozero import Button

# --- Importy hardwaru ---
from hardware.drivetrain import Drivetrain
from hardware.turret import Turret
from hardware.gun import Gun

# --- Import logiky ---
from core.robot_logic import RobotLogic

# --- Importy vstupů ---
from inputs.xbox_controller import XboxController
from inputs.elrs_input import ElrsInput

# Nastavení pinu pro výběr režimu
# Zapojení: Pin 21 <-> Přepínač <-> GND
# Pokud je přepínač SEPNUTÝ (spojen se zemí) -> Button detekuje stisk (is_pressed)
MODE_SWITCH_PIN = 21

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
            config.GUN_TRIGGER_PIN, config.LED_PIN
        )
    except Exception as e:
        print(f"CHYBA HARDWARU: {e}")
        return

    # ---------------------------------------------------------
    # 2. Inicializace Mozku (Logiky)
    # ---------------------------------------------------------
    logic = RobotLogic(dt, turret, gun)

    # ---------------------------------------------------------
    # 3. Volba vstupu podle přepínače
    # ---------------------------------------------------------
    mode_switch = Button(MODE_SWITCH_PIN, pull_up=True)
    input_system = None

    if mode_switch.is_pressed:
        # --- REŽIM 1: ELRS ---
        print("\n[REŽIM] Detekován ELRS (Radiomaster)")
        input_system = ElrsInput('/dev/ttyAMA0', logic)

    else:
        # --- REŽIM 2: XBOX ---
        print("\n[REŽIM] Detekován Xbox Controller")
        
        input_system = XboxController(config.GAMEPAD_DEVICE, logic)
        
        # Zde voláme vylepšený connect, který čeká 30 sekund
        # Pokud zapneš robota a až pak ovladač, tady se to chytí
        print("Zapni prosím ovladač...")
        is_connected = await input_system.connect(timeout=30)
        
        if not is_connected:
            print("\n!!! Ovladač se nepodařilo připojit !!!")
            # Volitelné: Můžeme zde program ukončit, nebo přepnout na autonomní režim
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
        print("\nCleaning up...")
        dt.stop() # Zastavíme motory, aby robot neujel
        # Případně vypnout laser: turret.set_laser(False)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Zachycení Ctrl+C, aby to nevypisovalo ošklivý traceback
        print("\nUživatel ukončil program.")