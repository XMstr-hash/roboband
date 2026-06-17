# Control Unit

Responsible for:
- MQTT communication
- Process control
- Status monitoring
- Statistics
- Display output

# Folder Structure
main.py
│
├─ display.py
├─ encoder.py
├─ menu.py
├─ mqtt.py
└─ config.py


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

# Pinbelegung
LCD1602     Raspberry Pi

1  VSS  -> GND
2  VDD  -> 5V
3  VO   -> Potentiometer (contrast)

4  RS   -> GPIO22
5  RW   -> GND
6  E    -> GPIO23

11 D4   -> GPIO24
12 D5   -> GPIO25
13 D6   -> GPIO5
14 D7   -> GPIO6

15 A    -> 5V (220Ω)
16 K    -> GND


contrast
5V ----\
        > 10k Pot
GND ---/

mittel -> VO (pin 3 LCD)



KY040       Raspberry Pi

GND     -> GND
VCC     -> 3.3V
CLK     -> GPIO17
DT      -> GPIO18
SW      -> GPIO27



# MQTT.md
\#Raspberry Pi 1  Control Unit

\#├─ MQTT Broker

\#├─ LCD1602

\#├─ KY-040 Encoder

\#└─ Main logic

\#

\#Raspberry Pi 2  Robot Arm

\#└─ Robot control

\#

\#Raspberry Pi 3  Conveyor + Sorting

\#├─ Belt motor

\#├─ RFID reader

\#└─ Sorting mechanism



| Topic                       | Kommentar                              |

| --------------------------- | --------------------------------------------------- |

| `roboband/control/cmd`      | Steuerbefehle der Steuereinheit an alle Komponenten |

| `roboband/control/state`    | Aktueller Betriebszustand der Anlage                |

| `roboband/robot/status`     | Statusmeldung des Roboterarms                       |

| `roboband/robot/event`      | Ereignisse des Roboterarms, z. B. Bauteil abgelegt  |

| `roboband/conveyor/status`  | Statusmeldung des Förderbands                       |

| `roboband/conveyor/event`   | Ereignisse des Förderbands, z. B. RFID gelesen      |

| `roboband/conveyor/cmd`     | Befehle an Förderband und Sortierung                |

| `roboband/system/error`     | Fehlermeldungen aller Komponenten                   |

| `roboband/system/heartbeat` | Lebenszeichen der Komponenten                       |