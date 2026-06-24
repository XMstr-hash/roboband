import sys
import time

try:
    import RPi.GPIO as GPIO
    print("✓ Echtes RPi.GPIO geladen (Raspberry Pi Hardware erkannt)")
except ImportError:
    try:
        import Mock.GPIO as GPIO
        print("⚠ RPi.GPIO nicht gefunden. Nutze Mock.GPIO (PC-Betrieb).")
    except ImportError:
        print("❌ Fehler: Weder RPi.GPIO noch Mock.GPIO sind installiert!")
        sys.exit(1)

# Importiere das Menü-Modul, um die Events weiterzuleiten
import menu

############## PIN-KONFIGURATION ###########################
# Passe die Pins hier an deine tatsächliche Verkabelung an
PIN_CLK = 17
PIN_DT = 18
PIN_SW = 27

# Modul-Zustände
_is_initialized = False

# Für die Entprellung (Debouncing) des Tasters
_last_button_time = 0
DEBOUNCE_TIME_MS = 250  # 250ms Verzögerung für den Taster

############## INTERNE HELFER ###########################

def _rotary_callback(channel):
    """Wird aufgerufen, wenn sich der Encoder dreht (Interrupt-basiert)."""
    global _is_initialized
    if not _is_initialized:
        return

    # CLK und DT auslesen
    clk_state = GPIO.input(PIN_CLK)
    dt_state = GPIO.input(PIN_DT)

    # Drehrichtung ermitteln
    if clk_state != dt_state:
        # Drehung im Uhrzeigersinn
        menu.encoder_rotated(1)
    else:
        # Drehung gegen den Uhrzeigersinn
        menu.encoder_rotated(-1)
        
    # Menü-Aktualisierung auf der Konsole (optional für ersten Test)
    z1, z2 = menu.get_display_lines()
    print(f"|{z1}|\n|{z2}|\n----------------")


def _button_callback(channel):
    """Wird aufgerufen, wenn der Taster gedrückt wird."""
    global _last_button_time, _is_initialized
    if not _is_initialized:
        return

    current_time = time.time() * 1000  # Zeit in Millisekunden
    
    # Entprell-Sperre: Klicks innerhalb von DEBOUNCE_TIME_MS ignorieren
    if (current_time - _last_button_time) > DEBOUNCE_TIME_MS:
        _last_button_time = current_time
        cmd = menu.encoder_pressed()
        
        # Falls ein Befehl (Action) zurückgegeben wird
        if cmd:
            print(f"-> Encoder gedrückt. Führe Befehl aus: {cmd}")
            # Hier könntest du später den Befehl an dein MQTT-Modul senden
        else:
            print("-> Encoder gedrückt (Menü gewechselt)")
            
            # Konsolen-Testausgabe
            z1, z2 = menu.get_display_lines()
            print(f"|{z1}|\n|{z2}|\n----------------")


############## SCHNITTSTELLE ###########################

def init():
    """Initialisiert die GPIO-Pins und startet die Interrupt-Überwachung."""
    global _is_initialized
    
    if _is_initialized:
        return
        
    print("encoder.py Initializing rotary encoder pins...")
    
    # GPIO-Setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PIN_DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PIN_SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Interrupts für Drehbewegung und Klick registrieren
    # Beide Flanken (falling/rising) abfangen, um alle Drehschritte sauber zu erkennen
    GPIO.add_event_detect(PIN_CLK, GPIO.BOTH, callback=_rotary_callback, bouncetime=1)
    
    # Interrupt für den Knopf (fallende Flanke, da Pull-Up)
    GPIO.add_event_detect(PIN_SW, GPIO.FALLING, callback=_button_callback)

    # Starte auch das Menü-Modul einmalig
    menu.init()
    
    _is_initialized = True
    print("Encoder bereit. Bitte am Rad drehen oder drücken...")

def update():
    """Wird in der Hauptschleife aufgerufen."""
    pass

def get_data():
    """Gibt Statusinformationen dieses Moduls zurück."""
    return "Encoder Running"


# Standalone-Test für den PC/Raspberry Pi
if __name__ == "__main__":
    init()
    try:
        # Halte das Skript am Leben, damit die Interrupts im Hintergrund arbeiten
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProgramm wird beendet...")
        GPIO.cleanup()
