+++
title = "Optical Beam Smoke Detector"
description = "Architecture and firmware development for the next generation of a fire alarm system. The detector firmware had to be able to detect smoke with a very high sensitivity, while avoiding false alarms."
date = 2025-05-31 # End of the development project: 2024-11-08

[extra]
date_start = 2022-08-01
company = "Hekatron Brandschutz"
locations = ["Bern", "Freiburg", "Remote"]
image = "fire.jpg"
top_project = true

responsibilities = [
    "Responsible for the **firmware architecture** and the integration into the overall system",
    "Technical leadership for 3 firmware developers",
    "Support of **test system development** (HIL) with the *Pytest* framework in *Python*",
    "Implementation of, among other things smoke level calculation, **firmware update** and **persistence layer**",
    "Design and implementation of the build system with *CMake* and continuous integration in the CI/CD tool *TeamCity*",
    "Automation of reproducible build and test environments with *Ansible* and *Docker*",
    "Firmware maintenance during the initial live phase since the end of the development project in November 2024"
]

[taxonomies]
projects=["Architecture & Technical Lead"]
skills=["Architecture", "Tech Lead", "C++", "Firmware", "CI / CD", "Arm Cortex", "FreeRTOS", "CMake", "Python", "Firmware Update", "TeamCity", "Protobuf", "Polarion", "Cpputest", "Pytest", "Ansible", "Docker", "Gitlab"]
+++

In an interdisciplinary team of firmware, electronics and mechanics developers, physicists and test engineers, we developed the smoke detector with a **focus on very high sensitivity in all operation conditions**.

The firmware was developed for an *Arm Cortex M4* controller in *C++* with *FreeRTOS* as the real-time operating system. Especially the measurement part of the firmware had to fulfill **real-time requirements**. The smoke level calculation had to apply various compensations to the measured signal, to account for signal variations due to the large supported temperature range or the increasing device soiling during the detector lifetime.

<a href="/documents/projektreferenz-hekatron.pdf" target="_blank">View Reference (German){{ icon(type="pdf") }}</a>
