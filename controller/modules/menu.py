import sys

try:
    import RPi.GPIO as GPIO
    print("✓ Echtes RPi.GPIO geladen (Raspberry Pi Hardware erkannt)")
except ImportError:
    try:
        import Mock.GPIO as GPIO
        #print("⚠ Windows/PC erkannt. Nutze 'RPMock' als GPIO-Ersatz.")
    except ImportError:
        #print("❌ Fehler: Weder RPi.GPIO noch RPMock sind installiert!")
        sys.exit(1)

############## END OF IMPORTS / START OF CODE ###########################

_is_initialized = False
_local_data = None

def init():
    #Sets up hardware pins, connections, or initial data states.
    global _is_initialized, _local_data
    
    # Prevent double initialization if called by mistake
    if _is_initialized:
        return
        
    print("display.py Initializing resources...")
    _local_data = "Ready"
    _is_initialized = True


def update():
    #Executes a single step of loop logic. Called repeatedly by main.py
    global _local_data
    if not _is_initialized:
        return

    # Add your recurring logic here (e.g., polling a sensor, checking a queue)
    pass


def get_data():
    """Optional getter function to share module state with other modules."""
    return _local_data


# Optional: Allow testing this specific module by running it directly
if __name__ == "__main__":
    init()
    print("Testing module standalone...")
    while True:
        update()