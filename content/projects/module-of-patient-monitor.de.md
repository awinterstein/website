+++
title = "Adaptionsmodul für einen Patientenmonitor"
description = "Architektur und Firmware-Entwicklung für die Verbindung zusätzlicher Sensoren an einen bestehenden Patientenmonitor."
date = 2022-07-31

[extra]
date_start = 2021-11-01
locations = ["Remote"]
image = "patient-monitor.jpg" # https://unsplash.com/de/fotos/-BvS7q4yFQt4
top_project = true

responsibilities = [
    "**Verantwortlich für die Gerätefirmware** in einem interdisziplinären, agilen Team",
    "Klärung der Softwareanforderungen",
    "**Tracing der Anforderungen** bis hin zu Architektur, Implementierung und Tests mit *Polarion*",
    "Definition und **Dokumentation der Softwarearchitektur** (inkl. der Schnittstellen zur Elektronik)",
    "Software-Entwicklung von Teilen der Firmware für das Modul",
]

[taxonomies]
projects=["Architecture & Technical Lead"]
skills=["Architecture", "Tech Lead", "C++", "Firmware",  "CI / CD", "Arm Cortex", "FreeRTOS", "CMake", "Python", "Firmware Update", "Azure DevOps", "Polarion", "Google Test", "Pytest", "Qt", "Ansible", "Scrum", "Git"]
+++

Der Kunde benötigte ein neues Adaptionsmodul, um zusätzliche Sensoren über *USB* an seine bestehende Hardware anzuschließen, die nur über  *UART*-Schnittstellen verfügt. Das Modul sollte die Sensordaten bereitstellen und die Konfiguration der Sensoren über ein wohldefiniertes und strukturiertes Protokoll ermöglichen. Dieses Protokoll sollte ebenfalls im Rahmen des Projekts definiert und entwickelt werden.

Wir haben die Entwicklung in einem Team aus Mechanik-, Elektronik- und Firmware-Entwicklern durchgeführt und **dem Kunden das Modul integrationsbereit zur Verfügung gestellt**. Dies beinhaltete automatisierte und manuelle Tests auf der Unit-Test- und Integrationstest-Ebene des *V-Modells*.

Die Entwicklung erfolgte nach der Norm *IEC 62304* und den *AUTOSAR C++14* Richtlinien.
