# COST-power-monitor

GUI for continuously monitoring the COST Reference Microplasma Jets power.
We include a slightly modified version of python-ivi with minor fixes and adjustments as well as python-usbtmc (https://github.com/python-ivi).

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

## Supported oscilloscopes

Any scope with a sampling rate of 4 GS/s or better should work in theory, but additional code adjustments might be neccesary to use an unsupported scope. Right now, the following scopes work out of the box with the software:

- Agilent MSO7104B
- Agilent DSOX2004A
- Lecroy WR8404M
- Lecroy HDO6104A

I expect most modern Teledyne Lecroy scope to work out of the box. For scopes by other manufacturers which are not in this list, a small code adjustment will be neccesary in the get_scope() function at the very beginning of the code. 


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




