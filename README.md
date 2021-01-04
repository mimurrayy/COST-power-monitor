# cost-power-monitor

GUI for continuously monitoring the COST Reference Microplasma Jets power.
For convenience we include a slightly modified version of python-ivi (https://github.com/python-ivi).

## Install

### Windows

#### Prerequisites
First, a python3 installation is neccesary. Anaconda is kown to work. 

You need the following packages:

scipy, pylab(from matplotlib), numpy, python-usbtmc, pyusb, PyQt5, pyqtgraph

Additionally, the "libusb-win32" driver is needed wich is best installed using the Zadig GUI: https://zadig.akeo.ie/

#### Adjust the code

You will need to adjust the code for your scope.
This will be improved soon.

#### Start
You might need to run the program as Administrator.

python3 cost-power-monitor.py

### Linux

We will assume Installation under Ubuntu 20.04. Other Linux Distributions should also work without any problems.

#### Prerequisites

scipy, pylab(from matplotlib), numpy, python-usbtmc, pyusb, PyQt5, pyqtgraph

```bash
sudo apt install python3-usb python3-pip python3-numpy python3-matplotlib python3-scipy python3-pyqt5 python3-pyqtgraph
pip3 install python-usbtmc
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

#### Adjust the code

You will need to adjust the code for your scope.
This will be improved soon.

#### Start
python3 cost-power-monitor.py

