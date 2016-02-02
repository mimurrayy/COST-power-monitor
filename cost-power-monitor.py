#!/usr/bin/python

import sys
import string
import configparser  
import time
import numpy as np
import pylab
#import visa
import ivi
import usbtmc
from multiprocessing import Process, Queue, cpu_count
import multiprocessing
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
sim = False
volcal = 2250
scope_id = "USB0::0x0957::0x175D::INSTR"
resistance = 4.2961608775
frequency = 13560000
result_queue = Queue(100)
voltage_ref_phase = 0
current_ref_phase = 0
ref_size = 20 # Number of phase reference points to average over

class main_window(QWidget):  
    def __init__(self):
        super().__init__()
        l_main_Layout = QHBoxLayout()
        this_data_monitor = data_monitor()
        this_ctrl_panel = ctrl_panel()
        l_main_Layout.addLayout(this_data_monitor)
        l_main_Layout.addLayout(this_ctrl_panel)
        #l_main_Layout.addWidget(l_ctl_panel)
        
        self.rand_data = np.random.normal(size=100)
        #this_data_monitor.update(rand_data)

        #l_data_monitor.addWidget(graph)
        
        self.setLayout(l_main_Layout)
        self.setGeometry(300, 300, 1300, 400)
        self.setWindowTitle("COST Power Monitor")
        self.show() 

class data_monitor(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.results = []
        self.tab_bar = QTabWidget()
        self.graph = pyqtgraph.PlotWidget(name='Plot1')
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Voltage","Current","Phaseshift","Power"])
        self.tab_bar.addTab(self.graph, "Graph")
        self.tab_bar.addTab(self.table, "Table")

        self.update_timer = QtCore.QTimer(self)
        self.update_timer.setInterval(200)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start()
    
        self.power_dspl = QLabel("0 W")

        self.addWidget(self.tab_bar)
        self.addWidget(self.power_dspl)
        
    def update(self):
        while not result_queue.empty():
            new_data = result_queue.get()
            if new_data:
                self.results.append(new_data)
                self.update_table(new_data)
                self.update_graph()
                self.update_power_dspl(new_data[-1])
    
    def update_power_dspl(self, power):
        self.power_dspl.setText(str(power) + " W")
        
    def update_graph(self):
        """Updates the Graph with new data, 
        this data beeing an 2 dim array of voltage and power"""
        voltage = np.array(self.results)[:,0]
        power = np.array(self.results)[:,3]
        self.graph.plot(title="power", x=voltage, y=power)

    def update_table(self,data):
        """Updates the table with new data. 
        Data is array with voltage, current, phaseshift and power"""
        #print(data)
        self.table.insertRow(self.table.rowCount())
        for i,d in enumerate(data):
            self.table.setItem(self.table.rowCount()-1,i,QTableWidgetItem(str(d)))
            
        
    
class ctrl_panel(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.tab_bar = QTabWidget()
        this_sweep_tab = sweep_tab()
        this_settings_tab = settings_tab()
        this_scope_tab = scope_tab()
        self.tab_bar.addTab(this_sweep_tab, "Sweep")
        self.tab_bar.addTab(this_settings_tab, "Settings")
        self.tab_bar.addTab(this_scope_tab, "Scope")
        self.addWidget(self.tab_bar)

class sweep_tab(QWidget):
    def __init__(self):
        """ Don't look at it!"""
        super().__init__()
        
        l_main_Layout = QVBoxLayout()
        self.sweeping = False

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
        power_start_btn.clicked.connect(self.start_sweep)
        power_stop_btn = QPushButton("Pause")
        power_stop_btn.clicked.connect(self.stop_sweep)
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
        ref_start_btn = QPushButton("Find")
        ref_start_btn.clicked.connect(self.find_ref)
        ref_btn_row.addWidget(ref_start_btn)
        ref_layout.addLayout(ref_btn_row)
        
        l_main_Layout.addWidget(ref_group)
        
        self.setLayout(l_main_Layout)
        
    def start_sweep(self):
        if not self.sweeping:
            self.this_sweep = sweeper()
            self.this_sweep.start()
            self.sweeping = True

    def stop_sweep(self):
        self.sweeping = False
        self.this_sweep.stop()
        
    def find_ref(self):
        if not self.sweeping:
            self.this_sweep = sweeper()
            self.ref_label.setText(str(self.this_sweep.find_ref()))
        
        
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
        global volcal 
        volcal = int(self.volcal_box.text())
        

  
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
        global channel_assignment
        channel_assignment[self.number] = self.chan_cbox.currentText()
        
class scope_tab(QWidget):
    def __init__(self):
        """Choose and configure scope"""
        super().__init__()
        #visa_rm = visa.ResourceManager()
        #device_list = visa_rm.list_resources()
        device_list = ["USB0::0x0957::0x175D::INSTR"]
        l_main_Layout = QVBoxLayout()
        
        device_group = QGroupBox()
        device_layout = QVBoxLayout()
        device_group.setLayout(device_layout)
        device_row = QHBoxLayout()
        
        self.device_cbox = QComboBox()
        self.device_cbox.addItems(device_list)
        
        self.use_device_btn = QPushButton()
        self.use_device_btn.clicked.connect(self.choose_scope)        

        device_row.addWidget(QLabel("Device: "))
        device_row.addWidget(self.device_cbox)
        device_row.addWidget(self.use_device_btn)
        device_layout.addLayout(device_row)
        
        l_main_Layout.addWidget(device_group)
        self.setLayout(l_main_Layout)
        
    def choose_scope(self):
        print("Nope")
        #scope_id = self.device_cbox.currentText()
        #if not sim:
            #scope = ivi.agilent.agilentMSO7104B()
            #scope.initialize(scope_id)
   
    

class sweeper():
    def __init__(self):
        global result_queue
        mgr = multiprocessing.Manager()
        self.data_queue = mgr.Queue(10)
        self.io_process = Process(target=self.io_worker, args=(self.data_queue,))
        self.fit_process_list = []
        for i in range(cpu_count()-1):
            this_fit_proccess = Process(target=self.fit_worker, args=(self.data_queue, result_queue)) 
            self.fit_process_list.append(this_fit_proccess)
    
    
    def start(self):
        if not self.io_process.is_alive():
            self.io_process.start()
        for fit_process in self.fit_process_list:
            if not fit_process.is_alive():
                fit_process.start()
        
        
    def stop(self):
        if self.io_process.is_alive():
            self.io_process.terminate()
        for fit_process in self.fit_process_list:
            while not self.data_queue.empty():
                time.sleep(1)
            if fit_process.is_alive():
                fit_process.terminate()
            while not self.data_queue.empty():
                trash = self.data_queue.get()
        
    def find_ref(self):
        ref_queue = Queue(ref_size*2) # Don't ask
        ref_worker_list = []
        self.io_process.start()
        for i in range(int(cpu_count()-1)):
            this_ref_worker = Process(target=self.ref_worker, args=(self.data_queue, ref_queue))
            ref_worker_list.append(this_ref_worker)
            this_ref_worker.start()
        for ref_worker in ref_worker_list:
            ref_worker.join()
        self.stop()
        v_phases = []
        c_phases = []
        while not ref_queue.empty():
            phase_tuple = ref_queue.get()
            v_phases.append(phase_tuple[0])
            c_phases.append(phase_tuple[1])
        # Getting the average of an angle is hard:
        # https://en.wikipedia.org/wiki/Mean_of_circular_quantities
        mean_v_phase = np.arctan2(
            np.sum(np.sin(np.array(v_phases)))/len(v_phases),
            np.sum(np.cos(np.array(v_phases)))/len(v_phases)
            ) % (2*np.pi)
        mean_c_phase = np.arctan2(
            np.sum(np.sin(np.array(c_phases)))/len(c_phases),
            np.sum(np.cos(np.array(c_phases)))/len(c_phases)
            ) % (2*np.pi)
        global voltage_ref_phase
        voltage_ref_phase = mean_v_phase
        global current_ref_phase
        current_ref_phase = mean_c_phase
        return voltage_ref_phase - current_ref_phase
        
            
    def ref_worker(self, data_queue, ref_queue):
        for i in range(int(ref_size/cpu_count()-2)):
            data_dict = data_queue.get(timeout=1)
            voltage_data = data_dict["internal voltage"]
            current_data = data_dict["current"]
            v_amp, v_freq, v_phase = self.fit_func(voltage_data)
            c_amp, c_freq, c_phase = self.fit_func(current_data)
            result = (v_phase, c_phase)
            ref_queue.put(result)
    
    def io_worker(self, data_queue):
        """ Gets waveforms from the scope and puts them into the data_queue."""
        scope = ivi.agilent.agilentMSO7104B()
        if not sim:
            scope.initialize(scope_id)
        while True and not sim:
            data_dict = {}
            scope.measurement.initiate()
            for chan_num in channel_assignment:
                chan_name = channel_assignment[chan_num]
                if chan_name is not "nothing":
                    data_dict[chan_name] = scope.channels[chan_num-1].measurement.fetch_waveform()
            data_queue.put(data_dict)
                
    
    def fit_worker(self, data_queue, result_queue):
        while True:
            data_dict = data_queue.get()
            voltage_data = data_dict["internal voltage"]
            current_data = data_dict["current"]
            v_amp, v_freq, v_phase = self.fit_func(voltage_data)
            c_amp, c_freq, c_phase = self.fit_func(current_data)
            voltage_rms = v_amp/np.sqrt(2) * volcal
            current_rms = c_amp/np.sqrt(2)/resistance
            phaseshift = np.pi/2 + (current_ref_phase - c_phase) - (voltage_ref_phase - v_phase)
            power = voltage_rms * current_rms * np.absolute(np.cos(phaseshift))
            result = (voltage_rms, current_rms, phaseshift, power)
            result_queue.put(result)
        
    def fit_func(self,data):
        data = np.array(data)
        time = data[:,0]
        amplitude = data[:,1]
        guess_mean = np.mean(amplitude)
        guess_amplitude = np.amax(amplitude)
        guess_phase = 0
        guess_y0 = 0
        guess_frequency = frequency
        data_first_guess = (guess_amplitude
                    *np.sin(time*guess_frequency*2*np.pi + guess_phase%(2*np.pi))
                    + guess_mean)
        optimize_func = lambda x: (x[0]
                                    *np.sin(time* x[1] * 2*np.pi + x[2]%(2*np.pi))
                                    + x[3] - amplitude)
        solution = leastsq(optimize_func,
                        [guess_amplitude, guess_frequency, guess_phase, guess_y0],
                        full_output=0)
        est_ampl, est_freq, est_phase, est_y0 = solution[0]
        if est_ampl < 0:
            est_ampl = np.abs(est_ampl)
            est_phase = est_phase + np.pi
        return (est_ampl, est_freq, est_phase%(2*np.pi))
  
if __name__ == '__main__': 
    app = QApplication(sys.argv)
    #if debug:
        #print("DEBUGing is on, additional information will be printed to stdout\n")
    this_main_window = main_window()
    sys.exit(app.exec_())

    
    
