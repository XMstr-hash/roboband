#!/bin/bash

set -e

mkdir -p docs diagrams robot_arm conveyor controller

cat > README.md << 'EOF'
# RoboBand

## English

School project for LF7 - Cyber-Physical Systems.

Components:
- Robot Arm
- Conveyor Belt
- Control Unit

Communication via MQTT.

---

## Deutsch

Schulprojekt für LF7 - Cyber-physische Systeme.

Komponenten:
- Roboterarm
- Förderband
- Steuereinheit

Kommunikation über MQTT.
EOF

cat > docs/architecture.md << 'EOF'
# Architecture

## English

The system consists of three independent modules communicating via MQTT.

- Robot Arm
- Conveyor Belt
- Control Unit

## Deutsch

Das System besteht aus drei unabhängigen Modulen, die über MQTT kommunizieren.

- Roboterarm
- Förderband
- Steuereinheit
EOF

cat > docs/mqtt-topics.md << 'EOF'
# MQTT Topics

Topics to be defined by all teams before implementation.

Examples:

roboband/control/start
roboband/control/stop
roboband/robot/status
roboband/conveyor/status
roboband/sort/result
EOF

cat > docs/team-communication.md << 'EOF'
# Team Communication

## English

Microsoft Teams:
- Meetings
- Communication
- Planning

GitHub:
- Source Code
- Documentation
- Issues
- Version Control

## Deutsch

Microsoft Teams:
- Besprechungen
- Kommunikation
- Planung

GitHub:
- Quellcode
- Dokumentation
- Aufgaben
- Versionsverwaltung
EOF

cat > docs/project-plan.md << 'EOF'
# Project Plan

Phase 1
- Planning
- Architecture
- MQTT

Phase 2
- Development

Phase 3
- Integration

Phase 4
- Testing and Competition
EOF

cat > robot_arm/README.md << 'EOF'
# Robot Arm

Responsible for:
- Picking up components
- Moving components
- Placing components on conveyor belt
- Reporting status via MQTT
EOF

cat > conveyor/README.md << 'EOF'
# Conveyor Belt

Responsible for:
- Detecting components
- Identifying components
- Sorting components
- Reporting results via MQTT
EOF

cat > controller/README.md << 'EOF'
# Control Unit

Responsible for:
- MQTT communication
- Process control
- Status monitoring
- Statistics
- Display output
EOF

echo "Done."
