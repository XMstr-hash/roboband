import time

from modules import display, encoder, menu, mqtt

def setup():
    print("Initializing system...")
    #display.init()
    #encoder.init()
    #menu.init()
    #mqtt.init()
    print("System ready!")

def main():
    setup()
    
    # Main loop running all module updates together
    while True:
        try:
            # 1. Read inputs
            encoder.update()
            
            # 2. Process logic / navigation
            menu.update()
            
            # 3. Handle network communications
            mqtt.update()
            
            # 4. Refresh the visual output
            display.update()
            
            # Small delay to prevent 100% CPU usage (adjust as needed)
            time.sleep(0.01) 
            
        except KeyboardInterrupt:
            print("\nStopping system safely...")
            break

if __name__ == "__main__":
    main()
