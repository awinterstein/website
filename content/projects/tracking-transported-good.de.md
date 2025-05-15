+++
title = "Proof-of-Concept für ein System zum Tracking transportierter Waren"
description = "Nach dem Transport von Waren sollte festgestellt werden können, ob beispielsweise die Kühlkette eingehalten wurde und das Paket weder herabgefallen noch gekippt ist."
date = 2015-09-30

[extra]
date_start = 2015-07-01
locations = ["München"]
image = "packages.jpg" # https://unsplash.com/de/fotos/-RWTUrJf7I5w

notes = [
    "Fokus auf Energie-Effizienz des batteriebetriebenen Systems",
]

responsibilities = [
    "**Firmwareentwicklung** auf Basis einer vom Kunden erstellten Hardwareplattform",
    "**Klären von Anforderungen** und Anleitung juniorer Kollegin",
]

[taxonomies]
projects=["Software Development (Embedded)"]
skills=["C99", "Firmware", "Bluetooth Low-Energy", "Arm Cortex", "FreeRTOS", "Eclipse", "Git"]
+++

Dazu wurde auf Basis einer vom Kunden erstellten Hardwareplattform und Entwicklungsumgebung eine Firmware entwickelt, welche Umgebungswerte wie Temperatur und Luftfeuchtigkeit auf eine SD-Karte loggt und zusätzlich Shock- und Tilt-Events erkennen und loggen kann. Ein Auslesen der Daten ist über Bluetooth LE möglich.
