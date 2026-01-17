from gpiozero import Motor

class Drivetrain:
    def __init__(self, fl_pins, fr_pins, rl_pins, rr_pins):
        # Inicializace 4 motorů
        self.motor_fl = Motor(*fl_pins)
        self.motor_fr = Motor(*fr_pins)
        self.motor_rl = Motor(*rl_pins)
        self.motor_rr = Motor(*rr_pins)
        
        self.speed = 0.0
        self.turn = 0.0

    async def update(self):
        """Metoda volaná v hlavní smyčce, aplikuje rychlost na motory"""
        # Jednoduchý Arcade Drive (mixování plynu a zatáčení)
        left_speed = max(-1, min(1, self.speed + self.turn))
        right_speed = max(-1, min(1, self.speed - self.turn))

        # Aplikace na motory
        self.motor_fl.value = left_speed
        self.motor_rl.value = left_speed
        self.motor_fr.value = right_speed
        self.motor_rr.value = right_speed

    def set_move(self, speed, turn):
        """Nastaví požadovanou rychlost a zatáčení (-1.0 až 1.0)"""
        self.speed = speed
        self.turn = turn
    
    def stop(self):
        self.set_move(0, 0)
        self.motor_fl.stop()
        self.motor_fr.stop()
        self.motor_rl.stop()
        self.motor_rr.stop()