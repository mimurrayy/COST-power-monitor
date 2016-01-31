#!/usr/bin/python

import sys
import string
import configparser  
import time
import numpy as np
import pylab
from multiprocessing import Process, Queue, cpu_count
from scipy.optimize import leastsq,broyden1
from scipy import stats
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
import pyqtgraph
# importing this after pyqt5 tells pyqtgraph to use qt5 instead of 4

#cfg = configparser.ConfigParser()
#cfg.read('./placid.cfg')
#if cfg.get("debug", "sim") == "True" or cfg.get("debug", "sim") == "on":
    #sim = True
#else:
    #sim = False
#if cfg.get("debug", "debug") == "True" or cfg.get("debug", "debug") == "on":
    #debug = True
#else:
    #debug = False

channel_assignment = {1: "nothing", 2: "internal voltage", 3: "current", 4: "external voltage"}
volcal = 2250

class main_window(QWidget):  
    def __init__(self):
        super().__init__()
        l_main_Layout = QHBoxLayout()
        this_data_monitor = data_monitor()
        this_ctrl_panel = ctrl_panel()
        l_main_Layout.addLayout(this_data_monitor)
        l_main_Layout.addLayout(this_ctrl_panel)
        #l_main_Layout.addWidget(l_ctl_panel)
        
        rand_data = np.random.normal(size=100)
        this_data_monitor.update(rand_data)

        #l_data_monitor.addWidget(graph)
        
        self.setLayout(l_main_Layout)
        self.setGeometry(300, 300, 1300, 400)
        self.setWindowTitle("COST Power Monitor")
        self.show() 

class data_monitor(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.tab_bar = QTabWidget()
        self.graph = pyqtgraph.PlotWidget(name='Plot1')
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Voltage","Current","Phaseshift","Power"])
        self.tab_bar.addTab(self.graph, "Graph")
        self.tab_bar.addTab(self.table, "Table")

        self.addWidget(self.tab_bar)
        
    def update(self, data):
        self.update_graph(data)
        
    def update_graph(self,data):
        """Updates the Graph with new data, 
        this data beeing an 2 dim array of voltage and power"""
        self.graph.plot(title="power", y=data)

    def update_table(self,data):
        """Updates the table with new data. 
        Data is array with voltage, current, phaseshift and power"""
        fu = "fu"
        return fu
    
class ctrl_panel(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.tab_bar = QTabWidget()
        this_sweep_tab = sweep_tab()
        this_settings_tab = settings_tab()
        self.tab_bar.addTab(this_sweep_tab, "Sweep")
        self.tab_bar.addTab(this_settings_tab, "Settings")
        self.addWidget(self.tab_bar)

class sweep_tab(QWidget):
    def __init__(self):
        """ Don't look at it!"""
        super().__init__()
        
        l_main_Layout = QVBoxLayout()

        # Power stuff
        power_group = QGroupBox()
        power_layout = QVBoxLayout()
        power_group.setLayout(power_layout)
        
        show_power_row = QHBoxLayout()
        self.power_label = QLabel("0 W")
        show_power_row.addWidget(QLabel("Power:"))
        show_power_row.addWidget(self.power_label)
        power_layout.addLayout(show_power_row)
        
        power_btn_row = QHBoxLayout()
        power_start_btn = QPushButton("Start")
        power_stop_btn = QPushButton("Pause")
        power_btn_row.addWidget(power_start_btn)
        power_btn_row.addWidget(power_stop_btn)
        power_layout.addLayout(power_btn_row)
        
        l_main_Layout.addWidget(power_group)
        
        # Reference stuff
        ref_group = QGroupBox()
        ref_layout = QVBoxLayout()
        ref_group.setLayout(ref_layout)
        
        show_ref_row = QHBoxLayout()
        self.ref_label = QLabel("Undef")
        show_ref_row.addWidget(QLabel("Reference Phaseshift:"))
        show_ref_row.addWidget(self.ref_label)
        ref_layout.addLayout(show_ref_row)
                
        ref_btn_row = QHBoxLayout()
        ref_start_btn = QPushButton("Start")
        ref_stop_btn = QPushButton("Stop")
        ref_btn_row.addWidget(ref_start_btn)
        ref_btn_row.addWidget(ref_stop_btn)
        ref_layout.addLayout(ref_btn_row)
        
        l_main_Layout.addWidget(ref_group)
        
        self.setLayout(l_main_Layout)
        
class settings_tab(QWidget):
    def __init__(self):
        super().__init__()
        l_main_Layout = QVBoxLayout()
        
        # UI to assign scope channels
        chan_group =  QGroupBox()
        chan_layout = QVBoxLayout()
        chan_group.setLayout(chan_layout)
        
        chan_rows = []
        for channel_num in range(1,5):
            this_channel = channel_settings(channel_num)
            chan_rows.append(this_channel)
            chan_layout.addLayout(this_channel)
        
        l_main_Layout.addWidget(chan_group)
        
        
        # UI to set or find voltage callibration factor
        volcal_group = QGroupBox()
        volcal_layout = QVBoxLayout()
        volcal_group.setLayout(volcal_layout)
        volcal_row = QHBoxLayout()
        
        self.volcal_box = QLineEdit(str(volcal))
        self.volcal_box.setMaximumWidth(100)
        self.volcal_box.textChanged.connect(self.change_volcal)
        volcal_get = QPushButton("Find")
        volcal_row.addWidget(QLabel("Callibration Factor: "))
        volcal_row.addWidget(self.volcal_box)
        
        volcal_layout.addLayout(volcal_row)
        l_main_Layout.addWidget(volcal_group)
        
        self.setLayout(l_main_Layout)
        
    def change_volcal(self):
        volcal = int(self.volcal_box.text())
        print(volcal)
        

  
class channel_settings(QHBoxLayout):
    def __init__(self, number):
        """Beware, Channels are numbered 1 to 4"""
        super().__init__()
        self.number = number
        self.addWidget(QLabel("Channel " + str(self.number)))
        self.chan_cbox = QComboBox()
        chan_options = ["nothing", "internal voltage", "current", "external voltage"]
        self.chan_cbox.addItems(chan_options)
        self.addWidget(self.chan_cbox)
        self.chan_cbox.setCurrentIndex(chan_options.index(channel_assignment[self.number]))
        self.chan_cbox.currentIndexChanged.connect(self.change_channel)
        
    def change_channel(self):
        channel_assignment[self.number] = self.chan_cbox.currentText()
        
        
  
if __name__ == '__main__':   
    app = QApplication(sys.argv)
    #if sim:
        #print("SIMulate is on, no data will be sent to devices\n")
    #if debug:
        #print("DEBUGing is on, additional information will be printed to stdout\n")
    this_main_window = main_window()
    sys.exit(app.exec_())

    
    
