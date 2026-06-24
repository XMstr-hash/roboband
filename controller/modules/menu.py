import sys

# Globale Modul-Zustände
_is_initialized = False

# Live-Hardwarezustände (werden vom MQTT-Modul gesetzt)
_controller_status = "Bereit"
_band_status = "Stopp"
_arm_status = "Bereit"

# Bauteil-Zähler (werden vom MQTT-Modul hochgezählt)
_count_a = 0
_count_b = 0

# ---------------------------------------------------------------------------
# MENÜSTRUKTUR (Nummeriert im Hauptmenü, Alphabetisch in Untermenüs)
# ---------------------------------------------------------------------------
_menu_tree = {
    "text": "Hauptmenue",
    "type": "menu",
    "items": [
        {
            "text": "1: Live Status", 
            "type": "menu",
            "items": [
                {"text": "a: System", "type": "status_view", "id": "STATUS_SYS"},
                {"text": "b: Band & Arm", "type": "status_view", "id": "STATUS_HW"}
            ]
        },
        {
            "text": "2: Statistik", 
            "type": "menu",
            "items": [
                {"text": "a: Paket A", "type": "status_view", "id": "COUNT_A"},
                {"text": "b: Paket B", "type": "status_view", "id": "COUNT_B"},
                {"text": "c: Gesamt", "type": "status_view", "id": "COUNT_TOTAL"},
                {"text": "d: Zaehler Reset", "type": "action", "cmd": "RESET_STATS"}
            ]
        },
        {
            "text": "3: Foerderband",
            "type": "menu",
            "items": [
                {"text": "a: Band Start", "type": "action", "cmd": "START_BAND"},
                {"text": "b: Band Stopp", "type": "action", "cmd": "STOP_BAND"},
                {
                    "text": "c: Tempo",
                    "type": "menu",
                    "items": [
                        {"text": "a: Tempo 30%", "type": "action", "cmd": "SPEED_30"},
                        {"text": "b: Tempo 50%", "type": "action", "cmd": "SPEED_50"},
                        {"text": "c: Tempo 80%", "type": "action", "cmd": "SPEED_80"},
                        {"text": "d: Tempo 100%", "type": "action", "cmd": "SPEED_100"},
                    ]
                }
            ]
        },
        {
            "text": "4: Roboterarm",
            "type": "menu",
            "items": [
                {"text": "a: Arm Reset", "type": "action", "cmd": "ARM_RESET"},
                {"text": "b: Arm Autark", "type": "action", "cmd": "ARM_AUTO"},
                {"text": "c: Arm Warten", "type": "action", "cmd": "ARM_WAIT"},
            ]
        }
    ]
}

# Navigations-Variablen
_current_menu = _menu_tree
_menu_history = []  
_menu_index = 0     
_scroll_top = 0     

# ---------------------------------------------------------------------------
# INTERNE HELFER
# ---------------------------------------------------------------------------
def _inject_back_buttons(menu):
    """Fügt rekursiv jedem Untermenü einen Zurück-Knopf am Ende hinzu."""
    if menu["type"] == "menu" and "items" in menu:
        if not any(item.get("type") == "back" for item in menu["items"]):
            menu["items"].append({"text": "<- Zurueck", "type": "back"})
        for sub_item in menu["items"]:
            _inject_back_buttons(sub_item)

def _get_dynamic_text(item):
    """Generiert live die Displaytexte für Statusanzeigen und Zähler."""
    if item["type"] == "status_view":
        view_id = item["id"]
        if view_id == "STATUS_SYS":
            return f"Ctrl: {_controller_status}"
        elif view_id == "STATUS_HW":
            return f"B:{_band_status} A:{_arm_status}"
        elif view_id == "COUNT_A":
            return f"Paket A: {_count_a}"
        elif view_id == "COUNT_B":
            return f"Paket B: {_count_b}"
        elif view_id == "COUNT_TOTAL":
            return f"Gesamt: {_count_a + _count_b}"
    return item["text"]

# ---------------------------------------------------------------------------
# SCHNITTSTELLE FÜR ENCODER-MODUL
# ---------------------------------------------------------------------------
def encoder_rotated(direction):
    """Navigiert zeilenweise durch die Liste und verschiebt das Anzeigefenster."""
    global _menu_index, _scroll_top
    if not _is_initialized:
        return
        
    items_count = len(_current_menu["items"])
    if items_count == 0:
        return
        
    _menu_index = (_menu_index + direction) % items_count

    # Sichtfenster-Logik für 2 Zeilen
    if _menu_index < _scroll_top:
        _scroll_top = _menu_index
    elif _menu_index >= _scroll_top + 2:
        _scroll_top = _menu_index - 1
        
    # Umlauf-Sonderfälle absichern
    if _menu_index == 0:
        _scroll_top = 0
    elif _menu_index == items_count - 1:
        _scroll_top = max(0, items_count - 2)

def encoder_pressed():
    """Verarbeitet den Klick (Ebene tiefer, Ebene höher oder MQTT-Befehl)."""
    global _current_menu, _menu_index, _menu_history, _scroll_top, _count_a, _count_b
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

    # MQTT-Befehle zurückgeben
    elif selected_item["type"] == "action":
        # Interner Abfang-Befehl für Statistik-Reset
        if selected_item["cmd"] == "RESET_STATS":
            _count_a = 0
            _count_b = 0
            return "STATS_RESET_DONE"
        return selected_item["cmd"]

    return None

# ---------------------------------------------------------------------------
# SCHNITTSTELLE FÜR MQTT-MODUL (Datenempfang)
# ---------------------------------------------------------------------------
def set_statuses(controller, band, arm):
    """Aktualisiert die Zustände der Hardware aus dem MQTT-Netzwerk."""
    global _controller_status, _band_status, _arm_status
    _controller_status = str(controller)
    _band_status = str(band)
    _arm_status = str(arm)

def increment_part(part_type):
    """Erhöht den entsprechenden Bauteil-Zähler bei erfolgreicher Sortierung."""
    global _count_a, _count_b
    if part_type == "A" or part_type == "a":
        _count_a += 1
    elif part_type == "B" or part_type == "b":
        _count_b += 1

# ---------------------------------------------------------------------------
# SCHNITTSTELLE FÜR DISPLAY-MODUL
# ---------------------------------------------------------------------------
def get_display_lines():
    """Gibt die zwei Zeilen basierend auf dem Scroll-Fenster zurück."""
    items = _current_menu["items"]
    
    if not items:
        return f"{_current_menu['text']:<16}", "Leer            "

    idx1 = _scroll_top
    idx2 = _scroll_top + 1

    # Zeile 1 mit dynamischem Text auflösen
    prefix1 = "> " if _menu_index == idx1 else "  "
    text1 = _get_dynamic_text(items[idx1])
    line1 = f"{prefix1}{text1}"

    # Zeile 2 mit dynamischem Text auflösen
    if idx2 < len(items):
        prefix2 = "> " if _menu_index == idx2 else "  "
        text2 = _get_dynamic_text(items[idx2])
        line2 = f"{prefix2}{text2}"
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
        
    print("menu.py Initializing smooth industrial scroll tree...")
    _inject_back_buttons(_menu_tree)
    _is_initialized = True

def update():
    pass

def get_data():
    return {
        "current_menu": _current_menu["text"], 
        "index": _menu_index,
        "count_a": _count_a,
        "count_b": _count_b
    }

# Standalone-Test für den PC
if __name__ == "__main__":
    init()
    
    def print_screen():
        z1, z2 = get_display_lines()
        print(f"|{z1}|\n|{z2}|\n----------------")

    print("--- 1. START: HAUPTMENÜ ANZEIGEN ---")
    print_screen()
    
    print("\n--- 2. SIMULATION: SIMULIERE EINTRAGUNG VON STATUSWERTE ---")
    set_statuses("Lauft", "Aktiv", "Wartet")
    increment_part("A")
    increment_part("A")
    increment_part("B")
    
    print("\n--- 3. NAVIGIERE ZU DEN STATS (Runter zu Punkt 2) ---")
    encoder_rotated(1) # Zu 2: Statistik
    print_screen()
    
    print("\n--- 4. KLICK: ÖFFNE STATISTIK-UNTERMENÜ ---")
    encoder_pressed()
    print_screen()
    
    print("\n--- 5. NAVIGIERE ZU GESAMT-ZÄHLER (Runter zu c) ---")
    encoder_rotated(1) # b: Paket B
    encoder_rotated(1) # c: Gesamt
    print_screen()
