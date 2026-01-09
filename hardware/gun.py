from machine import Pin
import time

# --- NASTAVENÍ PINŮ ---
# Uprav si čísla pinů podle svého mikrokontroléru (např. GP6 a GP2 pro Pi Pico)
mosfet_pin = Pin(6, Pin.OUT)
sensor_pin = Pin(2, Pin.IN, Pin.PULL_UP)

# Ujistit se, že je motor vypnutý
mosfet_pin.value(0)

# --- PROMĚNNÉ ---
firing_in_progress = False
start_time = 0
safety_timeout = 2000  # ms

# --- FUNKCE (METODY) ---

def stop_firing(reason):
    global firing_in_progress
    mosfet_pin.value(0)  # Vypnout MOSFET
    firing_in_progress = False
    print("--> STOP:", reason)

def start_firing():
    global firing_in_progress, start_time
    
    # Pokud už střílíme, ignorujeme další příkazy
    if firing_in_progress:
        return

    print("--> START: Spoustim cyklus...")
    
    mosfet_pin.value(1)       # Zapnout MOSFET
    firing_in_progress = True    # Nastavit příznak
    start_time = time.ticks_ms() # Uložit čas startu
    
    # DŮLEŽITÉ: Prodleva 100ms, aby motor odjel ze spínače
    # než ho smyčka začne kontrolovat.
    time.sleep_ms(100)

# --- HLAVNÍ SMYČKA (LOOP) ---
print("--- SYSTEM PRIPRAVEN ---")
print("Cekam na zavolani start_firing()...")

while True:
    # ---------------------------------------------------------
    # 1. ZDE JE MÍSTO PRO TVŮJ OVLADAČ
    # ---------------------------------------------------------
    # TODO: Příklad: if ovladac.tlacitko_zmacknuto(): start_firing()
    # Pro testování můžeš odkomentovat následující řádky, které 
    # simulují náhodný výstřel každých 5 sekund:
    # ---------------------------------------------------------
    # if time.ticks_ms() % 5000 < 10:
    #     start_firing()


    # ---------------------------------------------------------
    # 2. ŘÍZENÍ STŘELBY
    # ---------------------------------------------------------
    if firing_in_progress:
        current_time = time.ticks_ms()

        # A) Kontrola koncového spínače (Cut-off)
        # value() == 0 znamená sepnuto (protože PULL_UP)
        if sensor_pin.value() == 0:
            stop_firing("HOTAVO: Senzor sepnul (cyklus dokoncen)")

        # B) Bezpečnostní pojistka (Timeout)
        # Používáme time.ticks_diff pro bezpečný odečet času
        elif time.ticks_diff(current_time, start_time) > safety_timeout:
            stop_firing("CHYBA: Timeout (motor bezi moc dlouho)")
            
    # Krátká pauza, aby procesor neběžel na 100% zbytečně
    time.sleep_ms(10)