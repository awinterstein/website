+++
title = "Sensor Connection Module for a Patient Monitor"
description = "Architecture and firmware development for the connection of additional sensors to an existing patient monitor."
date = 2022-07-31

[extra]
date_start = 2021-11-01
locations = ["Remote"]
image = "patient-monitor.jpg" # https://unsplash.com/de/fotos/-BvS7q4yFQt4
top_project = true

responsibilities = [
    "**Responsible for the device firmware** in an interdisciplinary, agile team",
    "Clarification of the software requirements",
    "**Tracing the requirements** through to architecture, implementation and tests with *Polarion*",
    "Definition and **documentation of the software architecture** (incl. the interfaces to the electronics)",
    "Software development of parts of the firmware for the module",
]

[taxonomies]
projects=["Architecture & Technical Lead"]
skills=["Architecture", "Tech Lead", "C++", "Firmware",  "CI / CD", "Arm Cortex", "FreeRTOS", "CMake", "Python", "Firmware Update", "Azure DevOps", "Polarion", "Google Test", "Pytest", "Qt", "Ansible", "Scrum", "Git"]
+++

The client needed a new connection module to connect additional sensors via *USB* to their existing hardware, which was only able to provide an *UART* interface. The module was supposed to provide the sensor data and allow for sensor configuration via a well-defined and structured protocol. This protocol was also to be defined and developed in the project.

We did the development in a team of mechanic, electronic and firmware developers and **provided the module ready for integration to the client**. This included automated and manual testing on the unit test and integration test layer of the *V-model*.

The development was done according to the *IEC 62304* standard and the *AUTOSAR C++14* guidelines.
