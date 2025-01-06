+++
title = "Optical Beam Smoke Detector"
description = "Architecture and firmware development for the next generation of a fire alarm system. The detector firmware had to be able to detect smoke with a very high sensitivity, while avoiding false alarms."
date = 2024-10-07

[extra]
date_start = 2022-08-01
image = "fire.jpg"
top_project = true

[taxonomies]
projects=["Architecture & Technical Lead"]
skills=["Architecture", "C++", "Firmware", "CI / CD", "Arm Cortex", "FreeRTOS", "CMake", "Python", "Firmware Update", "TeamCity", "Protobuf", "Polarion", "Cpputest", "Ansible", "Docker", "Gitlab"]
+++

In an interdisciplinary team of firmware, electronics and mechanics developers, physicists and test engineers, we developed the smoke detector with a **focus on very high sensitivity in all operation conditions**.

The firmware was developed for an *Arm Cortex M4* controller in *C++* with *FreeRTOS* as the real-time operating system. Especially the measurement part of the firmware had to fulfill **real-time requirements**. The smoke level calculation had to apply various compensations to the measured signal, to account for signal variations due to the large supported temperature range or the increasing device soiling during the detector lifetime.

## Responsibilities

I was responsible for the **firmware architecture** of the detector and the
integration into the overall system. As part of this role,
I took care of the **interfaces between firmware and electronics** and the **interfaces
to the fire alarm system**. I lead the firmware
developers and supported the test system development (HIL) in *Python*.

Additionally, I implemented parts of the detector firmware, for example the smoke
level calculation, the **firmware update** and the **persistence layer**.
And did the conception and implementation of the build system with *CMake* and of the
continuous integration in the *TeamCity* CI / CD tool.

<a href="/documents/projektreferenz-hekatron.pdf" target="_blank">View Reference (German)<i class="bi bi-filetype-pdf ml-2"></i></a>