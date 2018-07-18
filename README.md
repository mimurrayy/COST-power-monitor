# cost-power-monitor

GUI for continuously monitoring the COST Reference Microplasma Jets power.

## Install

We will assume Installation under Ubuntu 18.04. Other Linux Distributions should also work without any problems. Windows is also known to work, but the installation is a bit tricky.

### Prerequisites

scipy, pylab(from matplotlib), numpy, python-ivi, python-usbtmc, pyusb, PyQt5

```bash
sudo apt install python3-pip python3-numpy python3-matplotlib python3-scipy python3-pyqt5
sudo pip3 install python-ivi python-usbtmc
```

### Configure udev

If you want to use the program without root permissions, you need to add a udev rule:
Edit e.g. /etc/udev/rules.d/12-scope.rules and add:

```bash
	# USBTMC instruments

	# Agilent MSO7104
	SUBSYSTEMS=="usb", ACTION=="add", ATTRS{idVendor}=="0957", ATTRS{idProduct}=="1755", GROUP="plugdev", MODE="0660"

	# Devices
	KERNEL=="usbtmc/*",       MODE="0660", GROUP="plugdev"
	KERNEL=="usbtmc[0-9]*",   MODE="0660", GROUP="plugdev"
```

Then, add your user to the plugdev group:

sudo usermod [username] -aG plugdev
  
A reboot might be necessary before the change takes effect.

### Start
python3 cost-power-monitor.py

