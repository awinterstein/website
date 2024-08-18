+++
title = "Proof of Concept for a System for Tracking Transported Goods"
description = "After goods have been transported, it should be possible to determine whether the cold chain has been maintained and the package has neither fallen down nor been tilted."
date = 2015-09-30

[extra]
date_start = 2015-07-01
image = "packages.jpg" # https://unsplash.com/de/fotos/-RWTUrJf7I5w

[taxonomies]
projects=["Software Development (Embedded)"]
skills=["C99", "Firmware", "Bluetooth Low-Energy", "Cortex M4", "FreeRTOS", "Eclipse", "Git"]
+++

For this purpose, a firmware was developed, which logs environmental values such as temperature and humidity on an SD card and can also detect and log shock and tilt events. A readout of the data was possible via Bluetooth LE. The system was based on a hardware platform and development environment created by the customer.

## Responsibilities
Firmware development with focus on energy efficiency. Clarification of requirements and guidance of junior colleagues.