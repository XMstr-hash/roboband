import time
import sys

try:
    import RPi.GPIO as GPIO
    _HAS_GPIO = True
except ImportError:
    _HAS_GPIO = False

# Importiere deine Module aus dem Ordner "modules"
from modules import display, encoder, menu, mqtt

def setup():
    print("Initializing system...")
    
    # 1. Menü-Struktur muss zwingend als ERSTES initialisiert werden
    menu.init()
    
    # 2. Encoder und Display hängen vom Menü ab
    encoder.init()
    display.init()
    
    # 3. Netzwerk-Modul (aktuell auskommentiert)
    # mqtt.init()
    
    print("System ready!")

def main():
    setup()
    
    print("System läuft. Drücke STRG+C zum Beenden.")
    
    # Hauptschleife für die kooperative Modul-Ausführung
    while True:
        try:
            # 1. Eingaben verarbeiten (falls Polling genutzt wird)
            encoder.update()
            
            # 2. Menü-Logik ausführen
            menu.update()
            
            # 3. Netzwerk-Kommunikation verarbeiten
            mqtt.update()
            
            # 4. Visuelle Ausgabe bei Textänderung aktualisieren
            display.update()
            
            # 10ms Pause schont die CPU (entspricht ca. 100 Hz Update-Rate)
            time.sleep(0.01) 
            
        except KeyboardInterrupt:
            print("\nStopping system safely...")
            
            # GPIO-Pins sauber freigeben, um Warnungen beim nächsten Start zu verhindern
            if _HAS_GPIO:
                try:
                    GPIO.cleanup()
                    print("✓ GPIO-Pins erfolgreich aufgeräumt.")
                except Exception as e:
                    print(f"⚠ Fehler beim GPIO-Cleanup: {e}")
            break

if __name__ == "__main__":
    main()
