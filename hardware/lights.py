from gpiozero import PWMLED
from config import LED_PINS
import asyncio

class Lights:
    def __init__(self):
        """Initialize multiple LEDs from config."""
        self.leds = {}
        for led_name, pin in LED_PINS.items():
            self.leds[led_name] = PWMLED(pin)
    
    def toggle_led(self, led_name='status'):
        """Toggle LED on/off by name."""
        if led_name in self.leds:
            self.leds[led_name].toggle()
        else:
            print(f"ERROR: LED '{led_name}' not found. Available: {list(self.leds.keys())}")
    
    def led_on(self, led_name='status'):
        """Turn LED on at full brightness."""
        if led_name in self.leds:
            self.leds[led_name].on()
        else:
            print(f"ERROR: LED '{led_name}' not found. Available: {list(self.leds.keys())}")
    
    def led_off(self, led_name='status'):
        """Turn LED off."""
        if led_name in self.leds:
            self.leds[led_name].off()
        else:
            print(f"ERROR: LED '{led_name}' not found. Available: {list(self.leds.keys())}")
    
    def set_led_brightness(self, led_name='status', value=1.0):
        """Set LED brightness (0.0 to 1.0)."""
        if led_name not in self.leds:
            print(f"ERROR: LED '{led_name}' not found. Available: {list(self.leds.keys())}")
            return
        
        if 0.0 <= value <= 1.0:
            self.leds[led_name].value = value
        else:
            print("ERROR: Brightness must be between 0.0 and 1.0")
    
    def pulse_led(self, led_name='status', fade_in_time=1, fade_out_time=1):
        """Pulse LED with fade in/out effect."""
        if led_name in self.leds:
            self.leds[led_name].pulse(fade_in_time=fade_in_time, fade_out_time=fade_out_time)
        else:
            print(f"ERROR: LED '{led_name}' not found. Available: {list(self.leds.keys())}")
    
    def pulse_all_leds(self, fade_in_time=1, fade_out_time=1):
        """Pulse all LEDs with fade in/out effect."""
        for led in self.leds.values():
            led.pulse(fade_in_time=fade_in_time, fade_out_time=fade_out_time)
    
    def cleanup(self):
        """Clean up GPIO resources."""
        for led in self.leds.values():
            led.close()