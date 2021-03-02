# MPFCS

Code for the Mostly Printed Field Characterization System (MPFCS) developed at the [Sensor Systems Lab](https://sensor.cs.washington.edu/) at the University of Washington. The MPFCS is a high-resolution, high-fidelity robotic system that measures and creates spatial images for chacterizing electric/magnetic fields. Its main use case has been to collect and visualize electromagnetic field data for inductive wireless power transfer with the purpose of accelerating the research, design, and prototyping process. It was especially intended for architectures that were prohibtively taxing computationally to simulate. However, the system was designed to be modular and ubiquitous and can easily be extended to a variety of other applications. The system can perform scans of varying sizes and resolutions, supporting precision below a tenth of a millimeter and a scan volume of 600 mm x 600 mm x 300 mm. Compared to parametric simulations in ANSYS HFSS, our experiments found that the MPFCS produced field data **~2600x faster.** 

### [User Guide](https://docs.google.com/document/d/1zT0MVRinPYnFrcWxW5tWwU1jPcRDlMU2P0lsJRck3NE)
### [Mechanical design details](https://www.thingiverse.com/thing:4729725)

![mpfcs](https://github.com/usmank13/MPFCS/blob/master/mpfcs_full_system.png "MPFCS Full System")


## Operating Modes

The MPFCS has two operating modes:

### 1) Single Radiating DUT (RDUT) Field Characterization

In this mode, the system directly measures the B-fields of a radiating device under test. This is done using the Beehive 100B magnetic field probe. 


![mpfcs_beehive](https://github.com/usmank13/MPFCS/blob/master/mounted%20beehive.png "MPFCS Beehive Probe")

### 3) 2-Port DUT Power Transfer Characterization

In this mode, the system characterizes the wireless power transfer between a transmitting coil (Tx) as the DUT and a receiving coil (Rx) as the probe.


![mpfcs_coil_mount](https://github.com/usmank13/MPFCS/blob/master/universal_coil_mount.png "Universal Coil Mount")


## Software Interface

The user specifies parameters for the scan, such as resolution, volume, frequency range, and others via a GUI. This GUI also plots results in real time and allows for manual control of the system. 

![mpfcs_gui](https://github.com/usmank13/MPFCS/blob/master/mpfcs%20gui.png "MPFCS GUI")

## Results

Testing on a simple coil, we found that there was very close agreement between the MPFCS data and the ANSYS HFSS simulation. 

![sim](https://github.com/usmank13/MPFCS/blob/master/coil_loop_38p5_sim.png "simulation")
![exp](https://github.com/usmank13/MPFCS/blob/master/38p5_to_bh_100b_20210206-1309.png "experiment")


We were also, for the first time, able to characterize a system that we could not simulate. This system consists of a 2D planar array of coils, which has applications in localized charging and range adapatation. 

![array](https://github.com/usmank13/MPFCS/blob/master/planar_array_to_coil_loop_38p5mm_spiral_50mm.png "Planar array")

A research paper describing the system and results in more detail will be forthcoming!
==


