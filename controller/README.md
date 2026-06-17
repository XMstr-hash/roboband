# Control Unit

Responsible for:
- MQTT communication
- Process control
- Status monitoring
- Statistics
- Display output

## Installation
python -m venv .venv
(Linux/Mac:) source .venv/bin/activate
(Windows:) .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python3 main.py

## Feature-Branches
feature/g3/mqtt-broker-setup
- Inhalt: Konfiguration des zentralen Mosquitto Brokers und Definition der Topic-Struktur (anlage/control, anlage/feedback).

feature/g3/state-machine-logic
- Inhalt: Programmierung der übergeordneten Ablaufsteuerung (Verwaltung von Start-, Stopp- und Wartebefehlen für Roboterarm und Förderband).

feature/g3/display-parallel-driver
- Inhalt: Implementierung des 1602A QAPASS Treibers im direkten Parallel-Modus.

feature/g3/encoder-menu-input
- Inhalt: KY-040 Drehgeber zur Menüführung und Anpassung von Parametern (z.B. Förderbandgeschwindigkeit).