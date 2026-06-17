import sys

try:
    import RPi.GPIO as GPIO
    print("✓ Echtes RPi.GPIO geladen (Raspberry Pi Hardware erkannt)")
except ImportError:
    try:
        import RPMock as GPIO
        print("⚠ Windows/PC erkannt. Nutze 'RPMock' als GPIO-Ersatz.")
    except ImportError:
        print("❌ Fehler: Weder RPi.GPIO noch RPMock sind installiert!")
        sys.exit(1)