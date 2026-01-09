from gpiozero import Motor

class Drivetrain:
    def __init__(self, fl_pins, fr_pins, rl_pins, rr_pins):
        # Inicializace 4 motorů
        self.m_fl = Motor(*fl_pins)
        self.m_fr = Motor(*fr_pins)
        self.m_rl = Motor(*rl_pins)
        self.m_rr = Motor(*rr_pins)
        
        self.speed = 0.0
        self.turn = 0.0

    async def update(self):
        """Metoda volaná v hlavní smyčce, aplikuje rychlost na motory"""
        # Jednoduchý Arcade Drive (mixování plynu a zatáčení)
        left_speed = max(-1, min(1, self.speed + self.turn))
        right_speed = max(-1, min(1, self.speed - self.turn))

        # Aplikace na motory
        self.m_fl.value = left_speed
        self.m_rl.value = left_speed
        self.m_fr.value = right_speed
        self.m_rr.value = right_speed

    def set_move(self, speed, turn):
        """Nastaví požadovanou rychlost a zatáčení (-1.0 až 1.0)"""
        self.speed = speed
        self.turn = turn
    
    def stop(self):
        self.set_move(0, 0)
        self.m_fl.stop()
        self.m_fr.stop() # atd...