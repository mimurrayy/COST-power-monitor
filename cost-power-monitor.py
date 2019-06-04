#!/usr/bin/python3

import sys
import string
import configparser  
import time
import numpy as np
import pylab
import datetime
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

channel_assignment = {1: "nothing", 2: "internal voltage", 3: "current", 4: "nothing"}
sim = False
volcal = 2250
volcal_std = 50
scope_id = "USB0::0x0957::0x175D::INSTR"
resistance = 4.2961608775
frequency = 13560000
result_queue = Queue(100)
voltage_ref_phase = 0
voltage_ref_phase_std = 0
current_ref_phase = 0
current_ref_phase_std = 0
ref_size = 10 # Number of phase reference points to average over

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
        self.setGeometry(300, 300, 1000, 400)
        self.setWindowTitle("COST Power Monitor")
        self.show() 

class data_monitor(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.results = []
        self.tab_bar = QTabWidget()
        self.graph = pyqtgraph.PlotWidget(name='Plot1')
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Voltage","Current","Phaseshift","Power","Time"])
        self.tab_bar.addTab(self.table, "Table")
        self.tab_bar.addTab(self.graph, "Graph")

        self.update_timer = QtCore.QTimer(self)
        self.update_timer.setInterval(500)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start()
    
        #btn_group = QGroupBox()
        btn_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_data)
        save_btn = QPushButton("Save to Disk")
        save_btn.clicked.connect(self.save_data)
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_data)
        plot_btn = QPushButton("Plot Data")
        plot_btn.clicked.connect(self.update_graph)
        btn_layout.addWidget(clear_btn)
        btn_layout.addWidget(plot_btn)
        btn_layout.addWidget(copy_btn)
        btn_layout.addWidget(save_btn)
        
        #power_group.setLayout(power_layout)
        
        #show_power_row = QHBoxLayout()
    
        self.power_dspl = QLabel("0 W")
        self.addWidget(self.power_dspl)
        self.addWidget(self.tab_bar)
        self.addLayout(btn_layout)
        
     
    def clear_data(self):
        global result_queue
        result_queue.close()
        result_queue = Queue(100) 
        self.table.setRowCount(0)
        
    def save_data(self):
        seperator = "\t "
        next_line = " \n"
        filename = QFileDialog.getSaveFileName(caption='Save File',
            filter='*.txt')

        if filename[0]:
            phaseshift = (str(voltage_ref_phase - current_ref_phase) + " +- " + 
                str(voltage_ref_phase_std + current_ref_phase_std))

            header = ("## cost-power-monitor file ## \n"+
                      "# " + str(datetime.datetime.now()) + "\n" +
                      "# Reference phaseshift: " + phaseshift + "\n" +
                      "# Calibration factor: " + str(volcal) + "\n" +
                      "# Channel Settings: " +  str(channel_assignment) + "\n\n")
                    
            table_header = ("Voltage" + seperator + "Current" +  seperator + 
                "Phaseshift" + seperator + "Power" + seperator + "Time" + next_line)

            lines = [header, table_header]
            for x in range(self.table.rowCount()):
                this_line = ""
                for y in range(self.table.columnCount()):
                    this_line = this_line + str(self.table.item(x,y).text()) + seperator
                lines.append(this_line + next_line)

            try:
                f = open(filename[0], 'w')
                f.writelines(lines)
            except:
                 mb = QMessageBox()
                 mb.setIcon(QMessageBox.Information)
                 mb.setWindowTitle('Error')
                 mb.setText('Could not save file.')
                 mb.setStandardButtons(QMessageBox.Ok)
                 mb.exec_()


    def copy_data(self):
        return "Nope"
     
    def update(self):
        while not result_queue.empty():
            new_data = result_queue.get()
            if new_data:
                self.results.append(new_data)
                self.update_table(new_data)
                self.update_power_dspl(new_data[-1])
        #self.update_graph()
    
    def update_power_dspl(self, power):
        self.power_dspl.setText("Power: " + str(power) + " W")
        
    def update_graph(self):
        """Updates the Graph with new data, 
        this data beeing an 2 dim array of voltage and power"""
        if self.results:
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
        time = datetime.datetime.now().time().strftime("%H:%M:%S")
        self.table.setItem(self.table.rowCount()-1,self.table.columnCount()-1,QTableWidgetItem(str(time)))        
        self.table.scrollToBottom()
            
        
    
class ctrl_panel(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.tab_bar = QTabWidget()
        this_sweep_tab = sweep_tab()
        this_settings_tab = settings_tab()
        this_scope_tab = scope_tab()
        self.tab_bar.addTab(this_sweep_tab, "Sweep")
        self.tab_bar.addTab(this_settings_tab, "Settings")
        #self.tab_bar.addTab(this_scope_tab, "Scope")
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
        #self.power_label = QLabel("0 W")
        show_power_row.addWidget(QLabel("Start/Pause Measurement"))
       # show_power_row.addWidget(self.power_label)
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
            self.this_sweep = sweeper(channel_assignment, volcal, voltage_ref_phase, current_ref_phase)
            self.this_sweep.start()
            self.sweeping = True

    def stop_sweep(self):
        self.sweeping = False
        self.this_sweep.stop()
        
    def find_ref(self):
        if not self.sweeping:
            global voltage_ref_phase, current_ref_phase, voltage_ref_phase_std, current_ref_phase_std
            self.this_sweep = sweeper(channel_assignment, volcal, voltage_ref_phase, current_ref_phase)
            voltage_ref_phase, current_ref_phase, voltage_ref_phase_std, current_ref_phase_std = self.this_sweep.find_ref()
            self.ref_label.setText(str(voltage_ref_phase - current_ref_phase) + " +- " + str(voltage_ref_phase_std + current_ref_phase_std))
        
        
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
        self.volcal_std_label = QLabel()
        volcal_get = QPushButton("Find")
        volcal_get.clicked.connect(self.get_volcal)
        volcal_row.addWidget(QLabel("Callibration Factor: "))
        volcal_row.addWidget(self.volcal_box)
        volcal_row.addWidget(self.volcal_std_label)
        volcal_row.addWidget(volcal_get)
        
        volcal_layout.addLayout(volcal_row)
        l_main_Layout.addWidget(volcal_group)
        
        self.setLayout(l_main_Layout)
        
    def change_volcal(self):
        global volcal 
        volcal = float(self.volcal_box.text())
        
    def get_volcal(self):
        self.this_sweep = sweeper(channel_assignment, volcal, voltage_ref_phase, current_ref_phase)
        self.volcal_box.setText(str(self.this_sweep.calibrate()))
        self.volcal_std_label.setText(str(volcal_std))
        
        

  
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
        this_chan_ass = channel_assignment
        
        this_chan_ass[self.number] = self.chan_cbox.currentText()
        channel_assignment = this_chan_ass

        
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
    def __init__(self, channels, volcal, v_ref, c_ref):
        global result_queue
        mgr = multiprocessing.Manager()
        self.channels = channels
        self.volcal = volcal
        self.v_ref = v_ref
        self.c_ref = c_ref
        self.data_queue = mgr.Queue(ref_size)
        self.io_process = Process(target=self.io_worker, args=(self.data_queue,))
        self.fit_process_list = []
        for i in range(cpu_count()-1):
            this_fit_proccess = Process(target=fit_worker,
                args=(self.data_queue, result_queue, volcal, v_ref, c_ref))

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
            while not self.data_queue.empty() and fit_process.is_alive():
                time.sleep(1)
            if fit_process.is_alive():
                fit_process.terminate()
            while not self.data_queue.empty():
                self.data_queue.get()
    
    def calibrate(self):
        global volcal, volcal_std
        ref_queue = Queue(ref_size*2) # Don't ask
        self.io_process.start()
        volcal_list = []
        for i in range(ref_size):
            data_dict = self.data_queue.get()
            try:
                external_voltage_data = data_dict["external voltage"]
            except KeyError:
                print("Channel 'External Voltage' not set.")
                volcal_std = "Error, 'External Voltage' not set."
                self.io_process.terminate()
                return 0
            voltage_data = data_dict["internal voltage"]
            v_amp, v_freq, v_phase = fit_func(voltage_data)
            ext_v_amp, ext_v_freq, ext_v_phase = fit_func(external_voltage_data)
            volcal_list.append(ext_v_amp/v_amp)

        self.io_process.terminate()
        while not self.data_queue.empty():
            self.data_queue.get()

        volcal = np.average(volcal_list)
        volcal_std = np.std(volcal_list)
    
        return volcal
    
    def find_ref(self):
        ref_queue = Queue(ref_size*2) # Don't ask
        self.io_process.start()
        v_phases = []
        c_phases = []
        for i in range(ref_size):
            data_dict = self.data_queue.get()
            voltage_data = data_dict["internal voltage"]
            v_amp, v_freq, v_phase = fit_func(voltage_data)
            current_data = data_dict["current"]
            c_amp, c_freq, c_phase = fit_func(current_data)
            v_phases.append(v_phase)
            c_phases.append(c_phase)

        self.io_process.terminate()
        while not self.data_queue.empty():
            self.data_queue.get()

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
        v_phase_diff_sum = 0
        c_phase_diff_sum = 0
        print(v_phases)
        print()
        print(c_phases)
        print()
        print(np.array(v_phases)-np.array(c_phases))
        for angle in v_phases:
            # Next line seems to work. It's all very complicated.
            v_phase_diff_sum = (v_phase_diff_sum
                            + np.square(np.diff(np.unwrap([angle, mean_v_phase])))[0])
        v_phase_std = np.sqrt(v_phase_diff_sum/len(v_phases))
        for angle in c_phases:
            # Next line seems to work. It's all very complicated.
            c_phase_diff_sum = (c_phase_diff_sum
                            + np.square(np.diff(np.unwrap([angle, mean_c_phase])))[0])
        c_phase_std = np.sqrt(c_phase_diff_sum/len(c_phases))
        global voltage_ref_phase, voltage_ref_phase_std
        voltage_ref_phase = mean_v_phase
        voltage_ref_phase_std = v_phase_std
        global current_ref_phase, current_ref_phase_std
        current_ref_phase = mean_c_phase
        current_ref_phase_std = c_phase_std
        self.v_ref = voltage_ref_phase
        self.c_ref = current_ref_phase
        return (voltage_ref_phase, current_ref_phase, voltage_ref_phase_std, current_ref_phase_std) 
        
    
    def io_worker(self, data_queue):
        """ Gets waveforms from the scope and puts them into the data_queue."""
        scope = ivi.agilent.agilentMSO7104B()
        if not sim:
            scope.initialize(scope_id)
            #scope.set_timeout(5)
        while True and not sim:
            data_dict = {}
            scope.measurement.initiate()
            for chan_num in self.channels:
                chan_name = self.channels[chan_num]
                if chan_name != "nothing":
                    data_dict[chan_name] = scope.channels[chan_num-1].measurement.fetch_waveform()
            data_queue.put(data_dict)
                
    
def fit_worker(data_queue, result_queue, volcal, v_ref, c_ref):
    """Takes data_queue and fits a sinus. Returns 4-tuple of voltage,current, phaseshift and power if raw=False,
    else a 6 tuple of amp, freq and phase for both voltage and current.
    Returns a 2-tuple if cal=True: internal voltage amplitude, external voltage amplitude.
    Use num to restict the amount of data the worker should fetech.
    Use cal to callibrate internal/external voltage probe"""
    while True:
        data_dict = data_queue.get()

        voltage_data = data_dict["internal voltage"]
        v_amp, v_freq, v_phase = fit_func(voltage_data)
        voltage_rms = v_amp/np.sqrt(2) * volcal

        current_data = data_dict["current"]
        c_amp, c_freq, c_phase = fit_func(current_data)
        current_rms = c_amp/np.sqrt(2)/resistance

        phaseshift = np.pi/2 + (c_ref - c_phase) - (v_ref - v_phase)
        power = voltage_rms * current_rms * np.absolute(np.cos(phaseshift))
        voltage_rms = v_amp/np.sqrt(2) * volcal
        result = (voltage_rms, current_rms, phaseshift, power)
        result_queue.put(result)

def fit_func(data):
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

    
    