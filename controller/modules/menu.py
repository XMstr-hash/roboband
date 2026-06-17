import sys

# Globale Modul-Zustände
_is_initialized = False

# Zustände der Hardware-Komponenten (werden vom MQTT-Modul befüllt)
_band_status = "Stopp"
_arm_status = "Bereit"

# Menüstruktur (Text im Display und der interne Befehlswert)
_menu_items = [
    {"text": "Band: Start", "cmd": "START"},
    {"text": "Band: Stopp", "cmd": "STOP"},
    {"text": "Tempo: 30%",   "cmd": "SPEED_30"},
    {"text": "Tempo: 50%",   "cmd": "SPEED_50"},
    {"text": "Tempo: 80%",   "cmd": "SPEED_80"},
    {"text": "Tempo: 100%",  "cmd": "SPEED_100"}
]
_menu_index = 0

############## SCHNITTSTELLE FÜR ENCODER-MODUL ###########################

def encoder_rotated(direction):
    """
    Wird vom Encoder-Modul aufgerufen.
    direction: +1 für Rechtsdrehung, -1 für Linksdrehung
    """
    global _menu_index
    if not _is_initialized:
        return
    _menu_index = (_menu_index + direction) % len(_menu_items)

def encoder_pressed():
    """
    Wird vom Encoder-Modul aufgerufen.
    Gibt den dem Menüpunkt zugewiesenen Befehls-String zurück,
    den dein MQTT-Modul dann abschicken kann.
    """
    if not _is_initialized:
        return None
    return _menu_items[_menu_index]["cmd"]

############## SCHNITTSTELLE FÜR MQTT-MODUL ###########################

def set_statuses(band, arm):
    """
    Wird vom MQTT-Modul aufgerufen, wenn neue Status-Nachrichten 
    vom Förderband oder Roboterarm empfangen wurden.
    """
    global _band_status, _arm_status
    if not _is_initialized:
        return
    _band_status = str(band)
    _arm_status = str(arm)

############## SCHNITTSTELLE FÜR DISPLAY-MODUL ###########################

def get_display_lines():
    """
    Wird vom Display-Modul in dessen Update-Schleife aufgerufen.
    Gibt ein Tupel (Zeile1, Zeile2) zurück, exakt auf 16 Zeichen formatiert.
    """
    # Zeile 1: Status (z.B. "B:Stopp  A:Bereit")
    line1 = f"B:{_band_status[:5]} A:{_arm_status[:6]}"
    
    # Zeile 2: Aktuelles Menü-Element mit Auswahlpfeil
    line2 = f"> {_menu_items[_menu_index]['text']}"
    
    # Auf exakt 16 Zeichen mit Leerzeichen auffüllen
    return f"{line1:<16}", f"{line2:<16}"

############## STANDARD MODUL FUNKTIONEN ###########################

def init():
    global _is_initialized
    if _is_initialized:
        return
        
    print("menu.py Initializing resources...")
    _is_initialized = True

def update():
    # Da dieses Modul rein eventbasiert über Funktionen gesteuert wird,
    # bleibt die periodische Update-Schleife leer.
    pass

def get_data():
    """Optionaler Getter für den aktuellen Zustand des Menüs."""
    return {
        "index": _menu_index,
        "text": _menu_items[_menu_index]["text"],
        "cmd": _menu_items[_menu_index]["cmd"]
    }
