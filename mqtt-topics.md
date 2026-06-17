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