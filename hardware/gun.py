from machine import Pin
import time

# --- NASTAVENÍ PINŮ ---
# Uprav si čísla pinů podle svého mikrokontroléru (např. GP6 a GP2 pro Pi Pico)
mosfet_pin = Pin(6, Pin.OUT)
sensor_pin = Pin(2, Pin.IN, Pin.PULL_UP)

# Ujistit se, že je motor vypnutý
mosfet_pin.value(0)

# --- PROMĚNNÉ ---
probiha_strelba = False
cas_spusteni = 0
bezpecnostni_limit = 2000  # ms

# --- FUNKCE (METODY) ---

def zastavit_palbu(duvod):
    global probiha_strelba
    mosfet_pin.value(0)  # Vypnout MOSFET
    probiha_strelba = False
    print("--> STOP:", duvod)

def spustit_strelbu():
    global probiha_strelba, cas_spusteni
    
    # Pokud už střílíme, ignorujeme další příkazy
    if probiha_strelba:
        return

    print("--> START: Spoustim cyklus...")
    
    mosfet_pin.value(1)       # Zapnout MOSFET
    probiha_strelba = True    # Nastavit příznak
    cas_spusteni = time.ticks_ms() # Uložit čas startu
    
    # DŮLEŽITÉ: Prodleva 100ms, aby motor odjel ze spínače
    # než ho smyčka začne kontrolovat.
    time.sleep_ms(100)

# --- HLAVNÍ SMYČKA (LOOP) ---
print("--- SYSTEM PRIPRAVEN ---")
print("Cekam na zavolani spustit_strelbu()...")

while True:
    # ---------------------------------------------------------
    # 1. ZDE JE MÍSTO PRO TVŮJ OVLADAČ
    # ---------------------------------------------------------
    # TODO: Příklad: if ovladac.tlacitko_zmacknuto(): spustit_strelbu()
    # Pro testování můžeš odkomentovat následující řádky, které 
    # simulují náhodný výstřel každých 5 sekund:
    # ---------------------------------------------------------
    # if time.ticks_ms() % 5000 < 10:
    #     spustit_strelbu()


    # ---------------------------------------------------------
    # 2. ŘÍZENÍ STŘELBY
    # ---------------------------------------------------------
    if probiha_strelba:
        current_time = time.ticks_ms()

        # A) Kontrola koncového spínače (Cut-off)
        # value() == 0 znamená sepnuto (protože PULL_UP)
        if sensor_pin.value() == 0:
            zastavit_palbu("HOTAVO: Senzor sepnul (cyklus dokoncen)")

        # B) Bezpečnostní pojistka (Timeout)
        # Používáme time.ticks_diff pro bezpečný odečet času
        elif time.ticks_diff(current_time, cas_spusteni) > bezpecnostni_limit:
            zastavit_palbu("CHYBA: Timeout (motor bezi moc dlouho)")
            
    # Krátká pauza, aby procesor neběžel na 100% zbytečně
    time.sleep_ms(10)