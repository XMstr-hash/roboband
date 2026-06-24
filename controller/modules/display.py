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

# Importiere das Menü-Modul für die Displaydaten
import menu

############## MODUL-ZUSTÄNDE ###########################
_is_initialized = False
_last_line1 = ""
_last_line2 = ""

############## HARDWARE TREIBER SETUP ###################
# Falls du ein I2C-Display (z.B. mit dem PCF8574-Rucksack) nutzt,
# kannst du hier später die entsprechende Bibliothek laden.
# Beispiel: import RPLCD.i2c as l_i2c

############## SCHNITTSTELLE ###########################

def init():
    """Initialisiert die Display-Hardware und zieht die ersten Menü-Zeilen."""
    global _is_initialized, _last_line1, _last_line2
    
    if _is_initialized:
        return
        
    print("display.py Initializing 16x2 text display...")
    
    # 1. Stelle sicher, dass das Menü bereit ist
    menu.init()
    
    # 2. Hardware-Initialisierung (falls echter Pi)
    if _HARDWARE_AVAILABLE:
        # Hier die Display-Pins oder I2C initialisieren
        # Beispiel: lcd = l_i2c.CharLCD(i2c_expander='PCF8574', address=0x27)
        pass

    # Erste Zeilen holen, damit der Startzustand bekannt ist
    _last_line1, _last_line2 = menu.get_display_lines()
    
    _is_initialized = True
    
    # Initialen Bildschirm anzeigen
    _render_display(_last_line1, _last_line2)


def update():
    """Prüft fortlaufend auf Textänderungen und aktualisiert das Display bei Bedarf."""
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
    """Gibt den aktuellen Display-Inhalt als Dictionary zurück."""
    return {"line1": _last_line1, "line2": _last_line2}


############## INTERNE HELFER ###########################

def _render_display(l1, l2):
    """Schreibt die zwei Textzeilen auf die Konsole oder die echte Hardware."""
    if _HARDWARE_AVAILABLE:
        # HIER DEINEN ECHTEN DISPLAY-SCHREIBBEFEHL EINFÜGEN
        # Beispiel:
        # lcd.clear()
        # lcd.write_string(f"{l1}\n{l2}")
        pass
        
    # Konsolen-Fallback für PC-Tests und Debugging
    print("\n+----------------+")
    print(f"|{l1.rstrip():<16}|")
    print(f"|{l2.rstrip():<16}|")
    print("+----------------+")


# Standalone-Test für das Display-Modul
if __name__ == "__main__":
    init()
    print("Testmodus: Warte auf Menü-Änderungen über die update()-Schleife...")
    try:
        # Simulierter Durchlauf für die Konsole
        while True:
            update()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nDisplay-Test beendet.")
        if _HARDWARE_AVAILABLE:
            GPIO.cleanup()
