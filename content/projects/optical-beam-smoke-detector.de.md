+++
title = "Optischer Rauchwarnmelder"
description = "Architektur- und Firmware-Entwicklung für die nächste Generation eines Brandmeldesystems. Die Firmware des Melders musste in der Lage sein, Rauch mit einer sehr hohen Empfindlichkeit zu erkennen und gleichzeitig Fehlalarme zu vermeiden."
date = 2024-11-08

[extra]
date_start = 2022-08-01
image = "fire.jpg"
top_project = true

[taxonomies]
projects=["Architecture & Technical Lead"]
skills=["Architecture", "Tech Lead", "C++", "Firmware", "CI / CD", "Arm Cortex", "FreeRTOS", "CMake", "Python", "Firmware Update", "TeamCity", "Protobuf", "Polarion", "Cpputest", "Pytest", "Ansible", "Docker", "Gitlab"]
+++

In einem interdisziplinären Team aus Firmware-, Elektronik- und Mechanikentwicklern, Physikern und Prüfingenieuren haben wir den Rauchmelder mit einem **Fokus auf sehr hohe Empfindlichkeit in allen Betriebszuständen** entwickelt.

Die Firmware wurde für einen *Arm Arm Cortex* Controller in *C++* mit *FreeRTOS* als Echtzeitbetriebssystem entwickelt. Insbesondere der Messteil der Firmware musste **Echtzeitanforderungen** erfüllen. Die Rauchpegelberechnung musste verschiedene Kompensationen auf das gemessene Signal anwenden, um Signalschwankungen aufgrund des großen unterstützten Temperaturbereichs und der zunehmenden Geräteverschmutzung während der Lebensdauer des Melders zu berücksichtigen.

## Verantwortlichkeiten

Ich war verantwortlich für die **Firmware-Architektur** des Melders und für die Integration in das Gesamtsystem. Im Rahmen dieser Aufgabe kümmerte ich mich um die **Schnittstellen zwischen Firmware und Elektronik** und die **Schnittstellen zum Brandmeldesystem**. Ich leitete die Firmware-Entwickler an und unterstützte die Entwicklung des Testsystems (HIL) mit dem *Pytest*-Framework in *Python*.

Zusätzlich habe ich Teile der Melder-Firmware implementiert, zum Beispiel die Rauchpegelberechnung, das **Firmware-Update** und die **Persistenzschicht**. Und ich habe die Konzeption und Implementierung des Build-Systems mit *CMake* und der kontinuierlichen Integration im CI / CD-Tool *TeamCity* durchgeführt. Für die Automatisierung reproduzierbarer Build- und Testumgebungen habe ich in diesem Zusammenhang *Docker* und *Ansible* eingesetzt.

<a href="/documents/projektreferenz-hekatron.pdf" target="_blank">Projektreferenz anzeigen<i class="bi bi-filetype-pdf ml-2"></i></a>
