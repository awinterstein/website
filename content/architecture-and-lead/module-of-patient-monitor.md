+++
title = "Sensor Connection Module for a Patient Monitor"
description = "Architecture and firmware development for the connection of additional sensors to an existing patient monitor."
date = 2022-07-31

[extra]
date_start = 2021-11-01
image = "patient-monitor.jpg" # https://unsplash.com/de/fotos/-BvS7q4yFQt4
top_project = true

[taxonomies]
projects=["Architecture & Technical Lead"]
skills=["C++", "Firmware", "Cortex M4", "FreeRTOS", "CMake", "Python", "Azure DevOps", "Polarion", "Google Test", "Qt", "Ansible", "Scrum", "Git"]
+++

The client needed a new connection module to connect additional sensors via *USB* to their existing hardware, which was only able to provide an *UART* interface. The module was supposed to provide the sensor data and allow for sensor configuration via a well-defined and structured protocol. This protocol was also to be defined and developed in the project.

We did the development in a team of mechanic, electronic and firmware developers and provided the module ready for integration to the client. This included automated and manual testing on the unit test and integration test layer of the *V-model*.

The development was done according to the *IEC 62304* standard and the *AUTOSAR C++14* guidelines.

## Responsibilities

I was responsible for the device firmware within the interdisciplinary team. My role included the clarification of the **software requirements**, the definition and documentation of the **software architecture** and the **tracing of requirements** to architecture, implementation and tests according to the development standard. As part of the architecture part of the role, I also made sure that the **interfaces between software and electronics** were defined well and according to the requirements. In addition, I did part of the actual module **firmware development** together with the other developers.
