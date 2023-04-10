
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3538281.svg)](https://doi.org/10.5281/zenodo.3538281)

# COST-power-monitor

GUI for continuously monitoring the power dissipated in [COST Reference Microplasma Jets](https://iopscience.iop.org/article/10.1088/0022-3727/49/8/084003) or other capacitively coupled RF plasmas.
The program connects to an oscilloscope, continuously fetches current and voltage measurements and uses that to calculate the power. It can use either the built-in probes of the COST jets or common commercial current and voltage probes.

## How it works

The program connects to an oscilloscope which measures current and voltage wave forms. From these measurements, the  power is calculated using either the phase shift ($P = U I \cos \varphi$) or the integration method ($P = \int U I dt$) as described by [Godyak and Piejak](https://doi.org/10.1116/1.576457). 
For both methods, a reference phase shift is required, as explained in detail [here](https://iopscience.iop.org/article/10.1088/0022-3727/49/8/084003). 

A video tutorial on how to perform measurements on COST jet devices can be found on [here]( https://www.jove.com/v/61801/treating-surfaces-with-cold-atmospheric-pressure-plasma-using-cost) (power measurements start at 3 minutes).

The reference phase shift is acquired by pressing the "Find phase shift" button while voltage is applied to the reactor, but no plasma is ignited. More accurate measurements are obtained for high voltages, which makes plasma ignition likely. To facilitate high applied voltages without igniting the plasma, the gas composition can be adjusted (e.g. flowing a high amount of molecular gases or pumping to pressures at which ignition is impossible). Alternatively, the inter electrode gap can be bridged with a capacitor while performing the reference phase measurement.

After the reference phase is obtained, measurements can be started or paused in the main UI, as needed. If the oscilloscope crashes during the measurement, simply pause the measurement, unplug and re-plug the USB cable to the scope and start the measurement again.  


## Usage for other capacitively coupled RF plasmas

The program is not limited to power measurements in COST jets but can be used for any plasma where the power can be calculated using the methods described above. __To perform measurements on other plasmas, the `Calibration factor` and `Measurement resistance` must both be set to `1` in the settings menu__, assuming that the attenuation of the employed voltage and current probes is handled on the scope. If not, these parameters can also be used to compensate for the probe attenuation:
- `Calibration factor` = 1/(Voltage probe attenuation)  E.g., for a x1000 probe like the Tektronix P6015a, you would use 0.001.
- `Measurement resistance` = V/A factor or 1/(A/V factor) E.g. for a Pearson 2878 with 0.1 V/A, you would just use 0.1.

## Supported oscilloscopes

Any modern scope with a sampling rate of 2 GS/s or better should work in theory, but additional code adjustments might be necessary to use an unsupported scope. Right now, the following scopes work out of the box with the software:

- Agilent MSO7104B
- Agilent DSOX2004A
- most Teledyne Lecroy (tested: WR8404M, HDO6104A, WS3014z)

I expect most modern Teledyne Lecroy scope to work out of the box. For scopes by other manufacturers which are not in this list, a small code adjustment will be necessary in the get_scope() function at the very beginning of the code. 

Communication with the scope is handled via USBTMC using slightly modified versions of python-ivi and python-usbtmc implementing minor fixes and tweaks. Communication via USBTMC might need to be enabled on the scope first. For Teledyne Lecroy scope, the option can be found in the utility settings menu.



## How to cite

When publishing results obtained with the software, please consider citing:
- J Held (2023) mimurrayy/COST-power-monitor: v1.2.0 (v1.2.0). Zenodo. https://doi.org/10.5281/zenodo.7812363
- Golda et al (2016) Concepts and characteristics of the 'COST Reference Microplasma Jet' _J. Phys. D: Appl. Phys._ **49** 084003 https://doi.org/10.1088/0022-3727/49/8/084003
-  Golda et al (2020) Treating Surfaces with a Cold Atmospheric Pressure Plasma using the COST-Jet _JoVE (Journal of Visualized Experiments)_ e61801 https://dx.doi.org/10.3791/61801

## Installation

### Windows
First, connect the scope to your computer. Then, use zardig (https://zadig.akeo.ie/) to install the "libusb-win32" driver for the correct device. After that, you can use the `.exe` file provided with the release to install COST-power-monitor. You might need to run the application as administrator. 

Please note that without installing the "libusb-win32" driver first, the program will not even start. 

### Linux
For Ubuntu 18.04 and 20.04 we provide `.deb` packages which should make the installation seemless. Make sure that your user is part of the `plugdev` group or run the software as root:
```
sudo cost-power-monitor
```
For other linux distributions, please use the manual install.

## Manual Install

### Windows

#### Prerequisites
First, a python3 installation is neccesary. Anaconda is kown to work. 

You need the following packages:
scipy, numpy, pyusb, PyQt5, pyqtgraph

All can be installed from pypi using pip:
```
python pip install scipy numpy pyusb PyQt5 pyqtgraph

```

Additionally, the "libusb-win32" driver is needed wich is best installed using the Zadig GUI: https://zadig.akeo.ie/


#### Start
You might need to run the program as Administrator.

python cost-power-monitor.py

### Linux

We will assume Installation under Ubuntu 20.04. Other Linux Distributions should also work without any problems.

#### Prerequisites

scipy, numpy, pyusb, PyQt5, pyqtgraph

```bash
sudo apt install python3-usb python3-numpy python3-scipy python3-pyqt5 python3-pyqtgraph
```

#### Configure udev

If you want to use the program without root permissions, you need to add a udev rule:
Edit e.g. /etc/udev/rules.d/12-scope.rules and add (e.g. for an Agilent DSO7104B and a Lecroy Waverunner 8404M):

```bash
# USBTMC instruments

# Agilent MSO7104
SUBSYSTEMS=="usb", ACTION=="add", ATTRS{idVendor}=="0957", ATTRS{idProduct}=="175d", GROUP="plugdev", MODE="0660"

# Teleyne LeCroy WR 8404M
SUBSYSTEMS=="usb", ACTION=="add", ATTRS{idVendor}=="05ff", ATTRS{idProduct}=="1023", GROUP="plugdev", MODE="0660"

# Devices
KERNEL=="usbtmc/*",       MODE="0660", GROUP="plugdev"
KERNEL=="usbtmc[0-9]*",   MODE="0660", GROUP="plugdev"

```
You will find the appropriate vendor and product ids using lsusb.

Then, add your user to the plugdev group:

sudo usermod [username] -aG plugdev
  
A reboot might be necessary before the change takes effect.

#### Start
python3 cost-power-monitor.py


## Debugging
On Linux, simply start the program in the terminal:
```
cost-power-monitor
```

On windows, stderr messages are written into a log file located in %appdata%, usually:
```
C:\Users\<username>\AppData\Roaming\COST-power-monitor.launch.pyw.log
```
If something goes wrong, this file should help with debugging.




