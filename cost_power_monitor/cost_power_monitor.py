#!/usr/bin/python3

import sys
import string
import time
import numpy as np
import datetime
from . import ivi
from . import usbtmc

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
resistance = 4.2961608775
frequency = 13560000
result_queue = Queue(100)
voltage_ref_phase = 0
voltage_ref_phase_std = 0
current_ref_phase = 0
current_ref_phase_std = 0
ref_size = 10 # Number of phase reference points to average over
scope_id = None

def get_scope(scope_id):
    "Scope database. Add yours here!"
    device = usbtmc.Instrument(scope_id)
    idV = device.idVendor
    idP = device.idProduct
    device.close()

    if idV == 0x0957 and idP == 0x175D:
        scope = ivi.agilent.agilentMSO7104B(scope_id)

    # Lecroy scopes, seems to work for multiple models which send the same idP
    # tested for WR8404M, HDO6104A
    elif idV == 0x05ff and idP == 0x1023:
        scope = ivi.lecroy.lecroyWR8404M(scope_id)

    elif idV == 0x0957 and idP == 6042: # York, untested
        scope = ivi.agilent.agilentDSOX2004A(scope_id)

    else:
        scope = ivi.lecroy.lecroyWR8404M(scope_id) # your IVI scope here!

    return scope

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class main_window(QWidget):
    def __init__(self):
        super().__init__()
        l_main_Layout = QHBoxLayout()
        this_data_monitor = data_monitor()
        this_ctrl_panel = ctrl_panel()
        l_main_Layout.addLayout(this_data_monitor)
        l_main_Layout.addLayout(this_ctrl_panel)
        self.rand_data = np.random.normal(size=100)
        
        self.setLayout(l_main_Layout)
        self.setGeometry(300, 300, 1000, 450)
        self.setWindowTitle("COST Power Monitor")
        self.show() 

class data_monitor(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.results = []
        self.tab_bar = QTabWidget()
        pyqtgraph.setConfigOption('background', 'w')
        pyqtgraph.setConfigOption('foreground', 'k')
        self.graph = pyqtgraph.PlotWidget(name='Plot1')
        self.graph.setLabel("left","power / W")
        self.graph.setLabel("bottom","voltage / V")

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Voltage / V", "Current / A",
                                    "Phaseshift / rad", "Power / W", "Time"])
        self.tab_bar.addTab(self.table, "Table")
        self.tab_bar.addTab(self.graph, "Graph")

        self.update_timer = QtCore.QTimer(self)
        self.update_timer.setInterval(100)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start()
    
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
    
        self.power_dspl = QLabel("0 W")
        self.addWidget(self.power_dspl)
        self.addWidget(self.tab_bar)
        self.addLayout(btn_layout)


    def clear_data(self):
        global result_queue
        result_queue.close()
        result_queue = Queue(100) 
        self.table.setRowCount(0)
        self.results = []
        

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
        QApplication.clipboard().setText(np.array2string(np.array(self.results)))
     

    def update(self):
        while not result_queue.empty():
            new_data = result_queue.get()
            if new_data:
                self.results.append(new_data)
                self.update_table(new_data)
                self.update_power_dspl(new_data[-1])


    def update_power_dspl(self, power):
        self.power_dspl.setText("Power: " + str(round(power,3)) + " W")
        

    def update_graph(self):
        """Updates the Graph with new data, 
        this data beeing an 2 dim array of voltage and power"""
        self.graph.clear()
        if self.results:
            voltage = np.array(self.results)[:,0]
            power = np.array(self.results)[:,3]
            self.graph.plot(title="power", x=voltage, y=power, symbol='o')


    def update_table(self,data):
        """Updates the table with new data. 
        Data is array with voltage, current, phaseshift and power"""
        #print(data)
        self.table.insertRow(self.table.rowCount())
        for i,d in enumerate(data):
            if i == 2:
                r = 10 # round phaseshift very precise
            else:
                r = 3 # rest to third position after comma
            self.table.setItem(self.table.rowCount()-1,i,QTableWidgetItem(str(round(d,r))))
        time = datetime.datetime.now().time().strftime("%H:%M:%S")
        self.table.setItem(self.table.rowCount()-1,self.table.columnCount()-1,QTableWidgetItem(str(time)))        
        self.table.scrollToBottom()
            

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
        self.sweeping = False

        # Power stuff
        power_group = QGroupBox()
        power_layout = QVBoxLayout()
        power_group.setLayout(power_layout)
        
        show_power_row = QHBoxLayout()
        show_power_row.addWidget(QLabel("Start/Pause Measurement"))
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
            self.ref_label.setText(
                str(round(voltage_ref_phase - current_ref_phase,10))
                + " ± "
                + str(round(voltage_ref_phase_std + current_ref_phase_std, 10)))
        
        
class settings_tab(QWidget):
    def __init__(self):
        super().__init__()
        l_main_Layout = QVBoxLayout()

        # list of connected scopes
        self.scope_cbox = QComboBox()
        self.scope_list()

        # UI to select the scope
        scope_group = QGroupBox()
        scope_layout = QVBoxLayout()
        scope_group.setLayout(scope_layout)

        scope_sel_row = QHBoxLayout()
        scope_info_row = QHBoxLayout()

        scope_sel_row.addWidget(QLabel("Oscilloscope"))

        scope_sel_row.addWidget(self.scope_cbox)
        self.scope_cbox.setCurrentIndex(0)
        self.scope_cbox.currentIndexChanged.connect(self.change_scope)

        update_btn = QPushButton("Scan")
        scope_sel_row.addWidget(update_btn)

        self.scope_name = QLabel(" ")
        scope_info_row.addWidget(self.scope_name)

        self.change_scope()
        scope_layout.addLayout(scope_sel_row)
        scope_layout.addLayout(scope_info_row)
        
        l_main_Layout.addWidget(scope_group)
        l_main_Layout.addWidget(QHLine())

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
        l_main_Layout.addWidget(QHLine())
        
        # UI to set or find voltage Calibration factor
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
        volcal_row.addWidget(QLabel("Calibration Factor: "))
        volcal_row.addWidget(self.volcal_box)
        volcal_row.addWidget(self.volcal_std_label)
        volcal_row.addWidget(volcal_get)
        
        volcal_layout.addLayout(volcal_row)
        l_main_Layout.addWidget(volcal_group)
        
        self.setLayout(l_main_Layout)
        
        # monitor changes in scopelist
        update_btn.clicked.connect(self.scope_list)


    def change_scope(self):
        global scope_id
        idx = self.scope_cbox.currentIndex()
        try:
            device = self.devices[idx]
            scope_id = "USB::%d::%d::INSTR" % (device.idVendor, device.idProduct)
            manufacturer = device.manufacturer
            product = device.product
        except Exception as e:
            print(e)
            device = None
            scope_id = None
            manufacturer = ""
            product = ""

        try:
            scope = get_scope(scope_id)
            scope.close()
            scope_known = True
            mark = "✓"
        except Exception as e:
            print(e)
            scope_known = False
            mark = "✗"
        self.scope_name.setText(mark + " " + manufacturer + " " + product)


    def scope_list(self):
        # list of connected USB devices
        sel_entry = self.scope_cbox.currentText()
        devices = usbtmc.list_devices()
        dlist = []
        for device in devices:
            scope_idVendor = device.idVendor
            scope_idProduct = device.idProduct
            scope_label = (hex(scope_idVendor) + ":" + hex(scope_idProduct))
            dlist.append(scope_label)
        self.dlist, self.devices = dlist, devices
        self.scope_cbox.clear()
        self.scope_cbox.addItems(dlist)
        idx = self.scope_cbox.findText(sel_entry)
        if idx == -1:
            try:
                self.scope_cbox.setCurrentIndex(0)
            except:
                pass
        else:
            self.scope_cbox.setCurrentIndex(idx)


    def change_volcal(self):
        global volcal 
        volcal = float(self.volcal_box.text())
        

    def get_volcal(self):
        self.this_sweep = sweeper(channel_assignment, volcal, voltage_ref_phase, current_ref_phase)
        try:
            self.volcal_box.setText(str(round(self.this_sweep.calibrate(),1)))
        except Exception as e:
            print(e)

        if type(volcal_std) == int:
            self.volcal_std_label.setText("±" + str(round(volcal_std,1)))
        else:
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


class sweeper():
    def __init__(self, channels, volcal, v_ref, c_ref):
        global result_queue
        mgr = multiprocessing.Manager()
        self.channels = channels
        self.volcal = volcal
        self.v_ref = v_ref
        self.c_ref = c_ref
        self.data_queue = mgr.Queue(ref_size)
        self.io_process = Process(target=self.io_worker, args=(self.data_queue, scope_id))
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
        
    
    def io_worker(self, data_queue, scope_id):
        """ Gets waveforms from the scope and puts them into the data_queue."""
        device = usbtmc.Instrument(scope_id)
        idV = device.idVendor
        device.close()

        scope = get_scope(scope_id)

        while True and not sim:
            fail = False
            data_dict = {}
            if idV == 0x0957: # Agilent scopes want to be initialized (tested for DSO7104B)
                scope.measurement.initiate()
            for chan_num in self.channels:
                chan_name = self.channels[chan_num]
                if chan_name != "nothing":
                    data = scope.channels[chan_num-1].measurement.fetch_waveform()
                    if len(data) > 0: # check for empty data sent from the scope
                        data_dict[chan_name] = data
                    else:
                        fail = True
            if not fail:
                data_queue.put(data_dict)


def fit_worker(data_queue, result_queue, volcal, v_ref, c_ref):
    """Takes data_queue and fits a sinus. Returns 4-tuple of voltage,current, phaseshift and power if raw=False,
    else a 6 tuple of amp, freq and phase for both voltage and current.
    Returns a 2-tuple if cal=True: internal voltage amplitude, external voltage amplitude.
    Use num to restict the amount of data the worker should fetech.
    Use cal to Calibration internal/external voltage probe"""
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
    time = np.nan_to_num(data[:,0])
    amplitude = np.nan_to_num(data[:,1])
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
  

def run():
    app = QApplication(sys.argv)
    this_main_window = main_window()
    sys.exit(app.exec_())


    
    
