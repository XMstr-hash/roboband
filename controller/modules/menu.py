import sys

# Globale Modul-Zustände
_is_initialized = False

# Zustände der Hardware (vom MQTT-Modul gesetzt)
#_band_status = "Stopp"
#_arm_status = "Bereit"

# ---------------------------------------------------------------------------
# MENÜSTRUKTUR (Hierarchie mit Untermenüs)
# ---------------------------------------------------------------------------
_menu_tree = {
    "text": "Hauptmenue",
    "type": "menu",
    "items": [
        {"text": "1: Status anzeigen", "type": "action", "cmd": "SHOW_STATUS"},
        {
            "text": "a: Foerderband",
            "type": "menu",
            "items": [
                {"text": "Band Start", "type": "action", "cmd": "START"},
                {"text": "Band Stopp", "type": "action", "cmd": "STOP"},
                {
                    "text": "Geschwindigkeit",
                    "type": "menu",
                    "items": [
                        {"text": "Tempo: 30%", "type": "action", "cmd": "SPEED_30"},
                        {"text": "Tempo: 50%", "type": "action", "cmd": "SPEED_50"},
                        {"text": "Tempo: 80%", "type": "action", "cmd": "SPEED_80"},
                        {"text": "Tempo: 100%", "type": "action", "cmd": "SPEED_100"},
                    ]
                }
            ]
        },
        {
            "text": "Roboterarm",
            "type": "menu",
            "items": [
                {"text": "Arm Reset", "type": "action", "cmd": "ARM_RESET"},
                {"text": "Arm Autark", "type": "action", "cmd": "ARM_AUTO"},
            ]
        }
    ]
}

# Navigations-Variablen
_current_menu = _menu_tree
_menu_history = []  # Stack für den Weg zurück
_menu_index = 0     # Aktuell ausgewählter Index in der Liste
_scroll_top = 0     # Welcher Index wird in der ERSTEN Zeile des Displays angezeigt?

# ---------------------------------------------------------------------------
# INTERNE HELFER
# ---------------------------------------------------------------------------
def _inject_back_buttons(menu):
    #Fügt rekursiv jedem Untermenü einen Zurück-Knopf am Ende hinzu.
    if menu["type"] == "menu" and "items" in menu:
        if not any(item.get("type") == "back" for item in menu["items"]):
            menu["items"].append({"text": "<- Zurueck", "type": "back"})
        for sub_item in menu["items"]:
            _inject_back_buttons(sub_item)

# ---------------------------------------------------------------------------
# SCHNITTSTELLE FÜR ENCODER-MODUL
# ---------------------------------------------------------------------------
def encoder_rotated(direction):
    #Navigiert zeilenweise durch die Liste und verschiebt das Anzeigefenster.
    global _menu_index, _scroll_top
    if not _is_initialized:
        return
        
    items_count = len(_current_menu["items"])
    if items_count == 0:
        return
        
    # Neuen Index berechnen (mit sicherem Umlauf)
    _menu_index = (_menu_index + direction) % items_count

    # --- SCROLL-LOGIK FÜR DIE ANZEIGE ---
    # Wenn wir über das obere Sichtfenster hinausgehen
    if _menu_index < _scroll_top:
        _scroll_top = _menu_index
    # Wenn wir über das untere Sichtfenster hinausgehen (Display hat 2 Zeilen)
    elif _menu_index >= _scroll_top + 2:
        _scroll_top = _menu_index - 1
        
    # Sonderfall: Wenn am Ende der Liste auf 0 umgesprungen wird
    if _menu_index == 0:
        _scroll_top = 0
    # Sonderfall: Wenn am Anfang der Liste nach ganz unten gesprungen wird
    elif _menu_index == items_count - 1:
        _scroll_top = max(0, items_count - 2)


def encoder_pressed():
    #Verarbeitet den Klick (Ebene tiefer, Ebene höher oder MQTT-Befehl).
    global _current_menu, _menu_index, _menu_history, _scroll_top
    if not _is_initialized:
        return None

    items = _current_menu["items"]
    if not items:
        return None

    selected_item = items[_menu_index]

    # Untermenü öffnen
    if selected_item["type"] == "menu":
        _menu_history.append((_current_menu, _menu_index, _scroll_top))
        _current_menu = selected_item
        _menu_index = 0
        _scroll_top = 0
        return None

    # Eine Ebene raus (Zurück)
    elif selected_item["type"] == "back":
        if _menu_history:
            _current_menu, previous_index, previous_scroll = _menu_history.pop()
            _menu_index = previous_index
            _scroll_top = previous_scroll
        return None

    # MQTT-Befehl zurückgeben
    elif selected_item["type"] == "action":
        return selected_item["cmd"]

    return None

# ---------------------------------------------------------------------------
# SCHNITTSTELLE FÜR MQTT-MODUL
# ---------------------------------------------------------------------------
def set_statuses(band, arm):
    global _band_status, _arm_status
    _band_status = str(band)
    _arm_status = str(arm)

# ---------------------------------------------------------------------------
# SCHNITTSTELLE FÜR DISPLAY-MODUL
# ---------------------------------------------------------------------------
def get_display_lines():
    #Gibt die zwei Zeilen basierend auf dem Scroll-Fenster zurück.
    items = _current_menu["items"]
    
    if not items:
        return f"{_current_menu['text']:<16}", "Leer            "

    # Bestimme die Indizes für Zeile 1 und Zeile 2 anhand des Scroll-Fensters
    idx1 = _scroll_top
    idx2 = _scroll_top + 1

    # Zeile 1 generieren
    prefix1 = "> " if _menu_index == idx1 else "  "
    line1 = f"{prefix1}{items[idx1]['text']}"

    # Zeile 2 generieren (prüfen, ob ein zweites Element existiert)
    if idx2 < len(items):
        prefix2 = "> " if _menu_index == idx2 else "  "
        line2 = f"{prefix2}{items[idx2]['text']}"
    else:
        line2 = ""

    return f"{line1:<16}", f"{line2:<16}"

# ---------------------------------------------------------------------------
# STANDARD MODUL FUNKTIONEN
# ---------------------------------------------------------------------------
def init():
    global _is_initialized
    if _is_initialized:
        return
        
    print("menu.py Initializing smooth scroll tree...")
    _inject_back_buttons(_menu_tree)
    _is_initialized = True

def update():
    pass

def get_data():
    return {"current_menu": _current_menu["text"], "index": _menu_index}


# Standalone-Test für den PC
if __name__ == "__main__":
    init()
    
    def print_screen():
        z1, z2 = get_display_lines()
        print(f"|{z1}|\n|{z2}|\n----------------")

    print("--- START IM HAUPTMENÜ ---")
    print_screen()
    
    # Simuliere stückweises Herunterscrollen, um den Effekt zu sehen
    for _ in range(3):
        print("\nDrehung nach unten (+1):")
        encoder_rotated(1)
        print_screen()
