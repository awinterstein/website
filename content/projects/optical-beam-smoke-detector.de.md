+++
title = "Optischer Rauchwarnmelder"
description = "Architektur- und Firmware-Entwicklung für die nächste Generation eines Brandmeldesystems. Die Firmware des Melders musste in der Lage sein, Rauch mit einer sehr hohen Empfindlichkeit zu erkennen und gleichzeitig Fehlalarme zu vermeiden."
date = 2024-11-08

[extra]
date_start = 2022-08-01
company = "Hekatron Brandschutz"
locations = ["Bern", "Freiburg", "Remote"]
image = "fire.jpg"
top_project = true

responsibilities = [
    "Verantwortlich für die **Firmware-Architektur** und die Integration in das Gesamtsystem",
    "Technische Leitung von 3 Firmware-Entwicklern",
    "Unterstützung der **Testsystementwicklung** (HIL) mit dem *Pytest*-Framework in *Python*",
    "Implementierung u.a. der Rauchpegelberechnung, des **Firmware-Updates** und der **Persistenzschicht**",
    "Konzeption und Implementierung des Build-Systems mit *CMake* sowie der kontinuierlichen Integration im CI/CD-Tool *TeamCity*",
    "Automatisierung reproduzierbarer Build- und Testumgebungen mit *Ansible* und *Docker*",
]

[taxonomies]
projects=["Architecture & Technical Lead"]
skills=["Architecture", "Tech Lead", "C++", "Firmware", "CI / CD", "Arm Cortex", "FreeRTOS", "CMake", "Python", "Firmware Update", "TeamCity", "Protobuf", "Polarion", "Cpputest", "Pytest", "Ansible", "Docker", "Gitlab"]
+++

In einem interdisziplinären Team aus Firmware-, Elektronik- und Mechanikentwicklern, Physikern und Prüfingenieuren haben wir den Rauchmelder mit einem **Fokus auf sehr hohe Empfindlichkeit in allen Betriebszuständen** entwickelt.

Die Firmware wurde für einen *Arm Cortex* Controller in *C++* mit *FreeRTOS* als Echtzeitbetriebssystem entwickelt. Insbesondere der Messteil der Firmware musste **Echtzeitanforderungen** erfüllen. Die Rauchpegelberechnung musste verschiedene Kompensationen auf das gemessene Signal anwenden, um Signalschwankungen aufgrund des großen unterstützten Temperaturbereichs und der zunehmenden Geräteverschmutzung während der Lebensdauer des Melders zu berücksichtigen.

<a href="/documents/projektreferenz-hekatron.pdf" target="_blank">Projektreferenz anzeigen{{ icon(type="pdf") }}</a>
