import serial, time
import asyncio

# --- Configuration ---
SERIAL_PORT = '/dev/ttyAMA0'  
BAUD_RATE = 420000

def parse_crsf_channels(payload):
    """
    Unpacks 22 bytes of CRSF payload into 16 channels (11-bit values).
    """
    if len(payload) != 22:
        return None
    
    channels = [0] * 16
    
    # Bit shifts for CRSF protocol (11 bits per channel)
    channels[0]  = (payload[0]       | payload[1] << 8)  & 0x07FF
    channels[1]  = (payload[1] >> 3  | payload[2] << 5)  & 0x07FF
    channels[2]  = (payload[2] >> 6  | payload[3] << 2 | payload[4] << 10) & 0x07FF
    channels[3]  = (payload[4] >> 1  | payload[5] << 7)  & 0x07FF
    channels[4]  = (payload[5] >> 4  | payload[6] << 4)  & 0x07FF
    channels[5]  = (payload[6] >> 7  | payload[7] << 1 | payload[8] << 9) & 0x07FF
    channels[6]  = (payload[8] >> 2  | payload[9] << 6)  & 0x07FF
    channels[7]  = (payload[9] >> 5  | payload[10] << 3) & 0x07FF
    
    channels[8]  = (payload[11]      | payload[12] << 8) & 0x07FF
    channels[9]  = (payload[12] >> 3 | payload[13] << 5) & 0x07FF
    channels[10] = (payload[13] >> 6 | payload[14] << 2 | payload[15] << 10) & 0x07FF
    channels[11] = (payload[15] >> 1 | payload[16] << 7) & 0x07FF
    channels[12] = (payload[16] >> 4 | payload[17] << 4) & 0x07FF
    channels[13] = (payload[17] >> 7 | payload[18] << 1 | payload[19] << 9) & 0x07FF
    channels[14] = (payload[19] >> 2 | payload[20] << 6) & 0x07FF
    channels[15] = (payload[20] >> 5 | payload[21] << 3) & 0x07FF

    return channels

def map_pwm(x):
    """Convert to classic PWM 1000-2000 (for better readability)"""
    val = int((x - 172) * (1024 / 1639) + 988)
    return max(980, min(val, 2020))

def map_channel_to_normalized(x):
    """Convert CRSF channel value (172-1811) to normalized -1.0 to 1.0"""
    norm = (x - 992) / 820.0 
    return max(-1.0, min(1.0, norm))

def main():
    print(f"Otevírám {SERIAL_PORT}...")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    except Exception as e:
        print(f"Chyba: {e}")
        return

    print("Sledování kanálů 1-7. (Stiskněte Ctrl+C pro konec)")
    
    buffer = bytearray()
    
    try:
        while True:
            if ser.in_waiting:
                buffer.extend(ser.read(ser.in_waiting))
            
            while len(buffer) >= 26:
                if buffer[0] != 0xC8:
                    buffer.pop(0)
                    continue

                length = buffer[1]
                if len(buffer) < length + 2:
                    break

                packet_type = buffer[2]
                
                # 0x16 = RC Channels
                if packet_type == 0x16:
                    payload = buffer[3:25] 
                    channels = parse_crsf_channels(payload)
                    
                    if channels:
                        # Zde je upravený výpis pro 7 kanálů
                        # Používám map_pwm pro hezčí čísla (1000-2000)
                        # Pokud chcete RAW data (172-1811), smažte 'map_pwm'
                        
                        out = (
                            f"\r"
                            f"CH1:{map_pwm(channels[0]):4d} "
                            f"CH2:{map_pwm(channels[1]):4d} "
                            f"CH3:{map_pwm(channels[2]):4d} "
                            f"CH4:{map_pwm(channels[3]):4d} | " # Oddělovač
                            f"CH5:{map_pwm(channels[4]):4d} "
                            f"CH6:{map_pwm(channels[5]):4d} "
                            f"CH7:{map_pwm(channels[6]):4d}"
                            f"CH8:{map_pwm(channels[7]):4d}"
                        )
                        print(out, end="", flush=True)

                del buffer[:length + 2]

            time.sleep(0.002) # Velmi krátká pauza

    except KeyboardInterrupt:
        print("\nUkončeno.")
        ser.close()

if __name__ == "__main__":
    main()