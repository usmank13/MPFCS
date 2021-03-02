# MPFCS

Code for the Mostly Printed Field Characterization System (MPFCS) developed at the [Sensor Systems Lab](https://sensor.cs.washington.edu/) at the University of Washington. The MPFCS is a high-resolution, high-fidelity robotic system that measures and creates spatial images for chacterizing electric/magnetic fields. Its main use case has been to collect and visualize electromagnetic field data for inductive wireless power transfer with the purpose of accelerating the research, design, and prototyping process. It was especially intended for architectures that were prohibtively taxing computationally to simulate. However, the system was designed to be modular and ubiquitous and can easily be extended to a variety of other applications. The system can perform scans of varying sizes and resolutions, supporting precision below a tenth of a millimeter and a scan volume of 600 mm x 600 mm x 300 mm. Compared to parametric simulations in ANSYS HFSS, our experiments found that the MPFCS produced field data **~2600x faster.** 

![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "MPFCS Full System")


### [User Guide](https://docs.google.com/document/d/1zT0MVRinPYnFrcWxW5tWwU1jPcRDlMU2P0lsJRck3NE)
### [Mechanical design details](https://www.thingiverse.com/thing:4729725)

## Operating Modes

The MPFCS has two operating modes:

### 1) Single Radiating DUT (RDUT) Field Characterization

In this mode, the system directly measures the B-fields of a radiating device under test. This is done using the Beehive 100B magnetic field probe. 

[insert image]
### 3) 2-Port DUT Power Transfer Characterization

In this mode, the system characterizes the wireless power transfer between a transmitting coil (Tx) as the DUT and a receiving coil (Rx) as the probe. 

[insert image]



A research paper describing the system and results in more detail will be forthcoming!
=======


