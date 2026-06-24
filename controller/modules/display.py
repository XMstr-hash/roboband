import sys
import time

try:
    import RPi.GPIO as GPIO
    print("✓ Echtes RPi.GPIO geladen (Raspberry Pi Hardware erkannt)")
    _HARDWARE_AVAILABLE = True
except ImportError:
    try:
        import Mock.GPIO as GPIO
        print("⚠ RPi.GPIO nicht gefunden. Nutze Mock.GPIO (PC-Betrieb).")
        _HARDWARE_AVAILABLE = False
    except ImportError:
        print("❌ Fehler: Weder RPi.GPIO noch Mock.GPIO sind installiert!")
        sys.exit(1)

# Versuche den echten LCD-Treiber zu laden
try:
    from RPLCD.gpio import CharLCD
except ImportError:
    if _HARDWARE_AVAILABLE:
        print("❌ Fehler: 'RPLCD' Bibliothek fehlt! Bitte 'pip install RPLCD' ausführen.")
        sys.exit(1)

# Importiere das Menü-Modul für die Displaydaten
import menu

############## PIN-KONFIGURATION (BCM) ##################
# Exakt nach deinem Schaltplan gemappt:
PIN_RS = 22
PIN_E  = 23
PINS_DATA = [24, 25, 5, 6]  # D4, D5, D6, D7

############## MODUL-ZUSTÄNDE ###########################
_is_initialized = False
_last_line1 = ""
_last_line2 = ""
lcd = None  # Globales Display-Objekt

############## SCHNITTSTELLE ###########################

def init():
    global _is_initialized, _last_line1, _last_line2, lcd
    
    if _is_initialized:
        return
        
    print("display.py Initializing 16x2 text display (Direct GPIO 4-Bit)...")
    
    # 1. Stelle sicher, dass das Menü bereit ist
    time.sleep(1.0)
    menu.init()
    
    # 2. Hardware-Initialisierung (falls echter Pi)
    if _HARDWARE_AVAILABLE:
        try:
            GPIO.setmode(GPIO.BCM)
            # KORREKTUR: Komma am Ende der Zeilen hinzugefügt!
            lcd = CharLCD(
                pin_rs=PIN_RS,
                pin_e=PIN_E,
                pins_data=PINS_DATA,
                numbering_mode=GPIO.BCM,
                cols=16,
                rows=2,
                compat_mode=True
            )
            lcd.clear()
            print("✓ LCD1602 Hardware erfolgreich initialisiert.")
        except Exception as e:
            print(f"❌ Fehler bei der LCD-Initialisierung: {e}")
            lcd = None

    # Erste Zeilen holen, damit der Startzustand bekannt ist
    _last_line1, _last_line2 = menu.get_display_lines()
    
    _is_initialized = True
    
    # Initialen Bildschirm anzeigen
    _render_display(_last_line1, _last_line2)


def update():
    global _last_line1, _last_line2
    if not _is_initialized:
        return

    # Hole aktuellen Text aus dem Menü-Modul
    current_line1, current_line2 = menu.get_display_lines()

    # Nur aktualisieren, wenn sich der Inhalt wirklich geändert hat (Flackerschutz)
    if current_line1 != _last_line1 or current_line2 != _last_line2:
        _last_line1 = current_line1
        _last_line2 = current_line2
        _render_display(current_line1, current_line2)


def get_data():
    return {"line1": _last_line1, "line2": _last_line2}


############## INTERNE HELFER ###########################

def _render_display(l1, l2):
    if _HARDWARE_AVAILABLE and lcd is not None:
        try:
            # OPTIMIERUNG: lcd.home() statt lcd.clear() verhindert extremes Bildschirmflackern
            lcd.home()
            # \r\n springt sauber in die zweite Zeile des LCD
            lcd.write_string(f"{l1}\r\n{l2}")
        except Exception as e:
            print(f"⚠ Fehler beim Schreiben aufs LCD: {e}")
        
    # Konsolen-Fallback für PC-Tests und paralleles Debugging
    print("\n+----------------+")
    print(f"|{l1.rstrip():<16}|")
    print(f"|{l2.rstrip():<16}|")
    print("+----------------+")


# Standalone-Test für das Display-Modul
if __name__ == "__main__":
    init()
    print("Testmodus: Warte auf Menü-Änderungen über die update()-Schleife...")
    try:
        while True:
            update()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nDisplay-Test beendet.")
        if _HARDWARE_AVAILABLE and lcd is not None:
            # Schließt das Display sauber per RPLCD-Funktion
            lcd.close() 
