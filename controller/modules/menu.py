import sys
import time

# Globale Modul-Zustände
_is_initialized = False

# Live-Hardwarezustände (werden vom MQTT-Modul gesetzt)
_controller_status = "Bereit"
_band_status = "Stopp"
_arm_status = "Bereit"

# Bauteil-Zähler (werden vom MQTT-Modul hochgezählt)
_count_a = 0
_count_b = 0

# UX: Variablen für Bestätigungs-Bildschirm & Auto-Dashboard-Rückkehr
_confirmation_until = 0.0
_confirmation_msg = ""
_last_interaction_time = time.time()
DASHBOARD_TIMEOUT_SEC = 10.0  # Kehrt nach 10 Sekunden Inaktivität zum Dashboard zurück

# ---------------------------------------------------------------------------
# MENÜSTRUKTUR (Vorschlag 3: Abgeflachte Hierarchie zur Reduzierung der Klicktiefe)
# ---------------------------------------------------------------------------
_menu_tree = {
    "text": "Hauptmenue",
    "type": "menu",
    "items": [
        {"text": "0: Dashboard", "type": "dashboard_trigger"}, # Dient als visueller Startanker
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
                {"text": "c: Tempo 30%", "type": "action", "cmd": "SPEED_30"},
                {"text": "d: Tempo 50%", "type": "action", "cmd": "SPEED_50"},
                {"text": "e: Tempo 80%", "type": "action", "cmd": "SPEED_80"},
                {"text": "f: Tempo 100%", "type": "action", "cmd": "SPEED_100"}
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

def _trigger_confirmation(msg):
    """Aktiviert die temporäre Klick-Bestätigung (Vorschlag 2)."""
    global _confirmation_until, _confirmation_msg
    _confirmation_msg = msg
    _confirmation_until = time.time() + 1.5  # 1.5 Sekunden anzeigen

# ---------------------------------------------------------------------------
# SCHNITTSTELLE FÜR ENCODER-MODUL
# ---------------------------------------------------------------------------
def encoder_rotated(direction):
    """Navigiert zeilenweise durch die Liste und verschiebt das Anzeigefenster."""
    global _menu_index, _scroll_top, _last_interaction_time
    if not _is_initialized:
        return
        
    _last_interaction_time = time.time() # Inaktivitäts-Timer zurücksetzen
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
    global _current_menu, _menu_index, _menu_history, _scroll_top, _count_a, _count_b, _last_interaction_time
    if not _is_initialized:
        return None

    _last_interaction_time = time.time() # Inaktivitäts-Timer zurücksetzen
    items = _current_menu["items"]
    if not items:
        return None

    selected_item = items[_menu_index]

    # Sonderfall Dashboard-Trigger bei Klick auf "0: Dashboard"
    if selected_item["type"] == "dashboard_trigger":
        _menu_index = 0
        _scroll_top = 0
        return None

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

    # MQTT-Befehle zurückgeben & Bestätigung auslösen
    elif selected_item["type"] == "action":
        cmd_to_return = selected_item["cmd"]
        
        if cmd_to_return == "RESET_STATS":
            _count_a = 0
            _count_b = 0
            _trigger_confirmation("Zaehler Reset")
            cmd_to_return = "STATS_RESET_DONE"
        else:
            _trigger_confirmation(selected_item["text"])
            
        # Nach einer Aktion automatisch eine Menü-Ebene zurückspringen (Auto-Back UX)
        if _menu_history:
            _current_menu, previous_index, previous_scroll = _menu_history.pop()
            _menu_index = previous_index
            _scroll_top = previous_scroll
            
        return cmd_to_return

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
    if part_type in ["A", "a"]:
        _count_a += 1
    elif part_type in ["B", "b"]:
        _count_b += 1

# ---------------------------------------------------------------------------
# SCHNITTSTELLE FÜR DISPLAY-MODUL & UPDATE-LOGIK
# ---------------------------------------------------------------------------
def update():
    """Wird zyklisch aufgerufen. Überprüft Inaktivität für automatische Dashboard-Rückkehr."""
    global _current_menu, _menu_index, _scroll_top, _menu_history, _is_initialized
    if not _is_initialized:
        return

    # Inaktivitäts-Check: Bei Inaktivität im Hauptmenü auf Index 0 (Dashboard) zurückspringen
    if _current_menu != _menu_tree or _menu_index != 0:
        if (time.time() - _last_interaction_time) > DASHBOARD_TIMEOUT_SEC:
            _current_menu = _menu_tree
            _menu_history = []
            _menu_index = 0
            _scroll_top = 0

def get_display_lines():
    """Gibt die zwei Zeilen basierend auf dem aktuellen Zustand zurück."""
    # UX-Vorschlag 2: Überprüfen, ob gerade ein Bestätigungsbildschirm aktiv ist
    if time.time() < _confirmation_until:
        return f"{'Befehl gesendet':<16}", f">> {_confirmation_msg[:13]:<13}"

    # UX-Vorschlag 1: Wenn im Hauptmenü '0: Dashboard' ausgewählt ist, zeige das Live-Dashboard
    if _current_menu == _menu_tree and _menu_index == 0:
        line1 = f"{_controller_status:<4} | A:{_count_a:02d} B:{_count_b:02d}"
        line2 = f"B:{_band_status:<5} A:{_arm_status:<6}"
        return f"{line1:<16}", f"{line2:<16}"
        
    # Standard-Menü-Schleife für normales Scrolling
    items = _current_menu["items"]
    if not items:
        return f"{_current_menu['text']:<16}", "Leer            "

    idx1 = _scroll_top
    idx2 = _scroll_top + 1

    # Zeile 1 generieren
    prefix1 = "> " if _menu_index == idx1 else "  "
    line1 = f"{prefix1}{_get_dynamic_text(items[idx1])}"

    # Zeile 2 generieren (falls existent)
    if idx2 < len(items):
        prefix2 = "> " if _menu_index == idx2 else "  "
        line2 = f"{prefix2}{_get_dynamic_text(items[idx2])}"
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
