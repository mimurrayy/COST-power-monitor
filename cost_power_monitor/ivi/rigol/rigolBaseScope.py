"""

Python Interchangeable Virtual Instrument Library

Copyright (c) 2017 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import array
import math
import sys
import time

from .. import ivi
from .. import scope
from .. import scpi
from .. import extra

AcquisitionTypeMapping = {
        'normal': 'norm',
        'peak_detect': 'peak',
        'high_resolution': 'hres',
        'average': 'aver'}
VerticalCoupling = set(['ac', 'dc', 'gnd'])
TriggerTypeMapping = {
        'edge': 'edge',
        'tv': 'video',
        'width': 'puls',
        'glitch': 'puls',
        'runt': 'runt',
        #'immediate': '',
        'ac_line': 'edge',
        'window': 'wind',
        'nth_edge': 'nedg',
        'pattern': 'patt',
        'delay': 'del',
        'timeout': 'tim',
        'duration': 'dur',
        'setup_hold': 'shold',
        'rs232': 'rs232',
        'i2c': 'iic',
        'spi': 'spi'}
TriggerCouplingMapping = {
        'ac': ('ac', 0),
        'dc': ('dc', 0),
        'hf_reject': ('hfr', 0),
        'lf_reject': ('lfr', 0),
        'noise_reject': ('dc', 1),
        'ac_noise_reject': ('ac', 1),
        'hf_noise_reject': ('hfr', 1),
        'lf_noise_reject': ('lfr', 1)}
TVTriggerEventMapping = {
        'field1': 'oddf',
        'field2': 'even',
        'any_line': 'alin',
        'line_number': 'line'}
TVTriggerFormatMapping = {
        'ntsc': 'ntsc',
        'pal': 'pals',
        'secam': 'pals',
        'p480': '480p',
        'p576': '576p'}
PolarityMapping = {'positive': 'pos',
        'negative': 'neg'}
GlitchConditionMapping = {'less_than': 'less',
        'greater_than': 'gre'}
WidthConditionMapping = {'within': ''}
SlopeMapping = {
        'positive': 'pos',
        'negative': 'neg',
        'either': 'rfal'}
MeasurementFunctionMapping = {
        'rise_time': 'risetime',
        'fall_time': 'falltime',
        'frequency': 'frequency',
        'period': 'period',
        'voltage_rms': 'vrms display',
        'voltage_peak_to_peak': 'vpp',
        'voltage_max': 'vmax',
        'voltage_min': 'vmin',
        'voltage_high': 'vtop',
        'voltage_low': 'vbase',
        'voltage_average': 'vaverage display',
        'width_negative': 'nwidth',
        'width_positive': 'pwidth',
        'duty_cycle_positive': 'dutycycle',
        'amplitude': 'vamplitude',
        'voltage_cycle_rms': 'vrms cycle',
        'voltage_cycle_average': 'vaverage cycle',
        'overshoot': 'overshoot',
        'preshoot': 'preshoot',
        'ratio': 'vratio',
        'phase': 'phase',
        'delay': 'delay'}
MeasurementFunctionMappingDigital = {
        'rise_time': 'risetime',
        'fall_time': 'falltime',
        'frequency': 'frequency',
        'period': 'period',
        'width_negative': 'nwidth',
        'width_positive': 'pwidth',
        'duty_cycle_positive': 'dutycycle'}
ScreenshotImageFormatMapping = {
        'tif': 'tiff',
        'tiff': 'tiff',
        'bmp': 'bmp24',
        'bmp24': 'bmp24',
        'bmp8': 'bmp8',
        'png': 'png',
        'png24': 'png',
        'jpg': 'jpeg',
        'jpeg': 'jpeg'}
TimebaseModeMapping = {
        'main': 'main',
        'window': 'window',
        'xy': 'xy',
        'roll': 'roll'}
TriggerModifierMapping = {'none': 'norm', 'auto': 'auto'}

class rigolBaseScope(scpi.common.IdnCommand, scpi.common.ErrorQuery, scpi.common.Reset,
                scpi.common.SelfTest, scpi.common.Memory,
                scope.Base, scope.TVTrigger, scope.GlitchTrigger, scope.WidthTrigger,
                scope.AcLineTrigger, scope.WaveformMeasurement,
                scope.ContinuousAcquisition, scope.AverageAcquisition,
                scope.TriggerModifier, scope.AutoSetup,
                extra.common.SystemSetup, extra.common.Screenshot,
                ivi.Driver):
    "Rigol generic IVI oscilloscope driver"

    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', '')
        self._analog_channel_name = list()
        self._analog_channel_count = 4
        self._digital_channel_name = list()
        self._digital_channel_count = 16
        self._channel_invert = list()
        self._channel_bw_limit = list()

        super(rigolBaseScope, self).__init__(*args, **kwargs)

        self._self_test_delay = 0
        self._memory_size = 10

        self._analog_channel_name = list()
        self._analog_channel_count = 4
        self._digital_channel_name = list()
        self._digital_channel_count = 16
        self._channel_count = self._analog_channel_count + self._digital_channel_count
        self._bandwidth = 1e9
        self._bandwidth_limit = {'20M': 20e6}
        self._max_averages = 1024

        self._horizontal_divisions = 12
        self._vertical_divisions = 8

        self._timebase_mode = 'main'
        self._timebase_position = 0.0
        self._timebase_range = 1e-3
        self._timebase_scale = 100e-6
        self._timebase_window_position = 0.0
        self._timebase_window_range = 5e-6
        self._timebase_window_scale = 500e-9
        self._display_screenshot_image_format_mapping = ScreenshotImageFormatMapping
        self._display_vectors = True

        self._identity_description = "Rigol generic IVI oscilloscope driver"
        self._identity_identifier = ""
        self._identity_revision = ""
        self._identity_vendor = ""
        self._identity_instrument_manufacturer = "Rigol Technologies"
        self._identity_instrument_model = ""
        self._identity_instrument_firmware_revision = ""
        self._identity_specification_major_version = 4
        self._identity_specification_minor_version = 1
        self._identity_supported_instrument_models = ['DS1074Z', 'DS1104Z', 'MSO1074Z',
                'MSO1104Z', 'DS2074A', 'DS2104A', 'DS2204A', 'DS2304A', 'MSO2074A',
                'MSO2104A', 'MSO2204A', 'MSO2304A']

        self._add_property('channels[].invert',
                        self._get_channel_invert,
                        self._set_channel_invert,
                        None,
                        ivi.Doc("""
                        Selects whether or not to invert the channel.
                        """))
        self._add_property('channels[].label',
                        self._get_channel_label,
                        self._set_channel_label,
                        None,
                        ivi.Doc("""
                        Sets the channel label.  Setting a channel label also adds the label to
                        the nonvolatile label list.
                        """))
        self._add_property('channels[].probe_skew',
                        self._get_channel_probe_skew,
                        self._set_channel_probe_skew,
                        None,
                        ivi.Doc("""
                        Specifies the channel-to-channel skew factor for the channel.  Each analog
                        channel can be adjusted + or - 100 ns for a total of 200 ns difference
                        between channels.  This can be used to compensate for differences in cable
                        delay.  Units are seconds.
                        """))
        self._add_property('channels[].scale',
                        self._get_channel_scale,
                        self._set_channel_scale,
                        None,
                        ivi.Doc("""
                        Specifies the vertical scale, or units per division, of the channel.  Units
                        are volts.
                        """))
        self._add_property('timebase.mode',
                        self._get_timebase_mode,
                        self._set_timebase_mode,
                        None,
                        ivi.Doc("""
                        Sets the current time base. There are four time base modes:

                        * 'main': normal timebase
                        * 'window': zoomed or delayed timebase
                        * 'xy': channels are plotted against each other, no timebase
                        * 'roll': data moves continuously from left to right
                        """))
        self._add_property('timebase.position',
                        self._get_timebase_position,
                        self._set_timebase_position,
                        None,
                        ivi.Doc("""
                        Sets the time interval between the trigger event and the display reference
                        point on the screen. The display reference point is either left, right, or
                        center and is set with the timebase.reference property. The maximum
                        position value depends on the time/division settings.
                        """))
        self._add_property('timebase.range',
                        self._get_timebase_range,
                        self._set_timebase_range,
                        None,
                        ivi.Doc("""
                        Sets the full-scale horizontal time in seconds for the main window. The
                        range is 10 times the current time-per-division setting.
                        """))
        self._add_property('timebase.scale',
                        self._get_timebase_scale,
                        self._set_timebase_scale,
                        None,
                        ivi.Doc("""
                        Sets the horizontal scale or units per division for the main window.
                        """))
        self._add_property('timebase.window.position',
                        self._get_timebase_window_position,
                        self._set_timebase_window_position,
                        None,
                        ivi.Doc("""
                        Sets the horizontal position in the zoomed (delayed) view of the main
                        sweep. The main sweep range and the main sweep horizontal position
                        determine the range for this command. The value for this command must
                        keep the zoomed view window within the main sweep range.
                        """))
        self._add_property('timebase.window.range',
                        self._get_timebase_window_range,
                        self._set_timebase_window_range,
                        None,
                        ivi.Doc("""
                        Sets the fullscale horizontal time in seconds for the zoomed (delayed)
                        window. The range is 10 times the current zoomed view window seconds per
                        division setting. The main sweep range determines the range for this
                        command. The maximum value is one half of the timebase.range value.
                        """))
        self._add_property('timebase.window.scale',
                        self._get_timebase_window_scale,
                        self._set_timebase_window_scale,
                        None,
                        ivi.Doc("""
                        Sets the zoomed (delayed) window horizontal scale (seconds/division). The
                        main sweep scale determines the range for this command. The maximum value
                        is one half of the timebase.scale value.
                        """))
        self._add_property('display.vectors',
                        self._get_display_vectors,
                        self._set_display_vectors,
                        None,
                        ivi.Doc("""
                        When enabled, draws a line between consecutive waveform data points.
                        """))
        self._add_method('display.clear',
                        self._display_clear,
                        ivi.Doc("""
                        Clears the display and resets all associated measurements. If the
                        oscilloscope is stopped, all currently displayed data is erased. If the
                        oscilloscope is running, all the data in active channels and functions is
                        erased; however, new data is displayed on the next acquisition.
                        """))

        self._init_channels()

    def _initialize(self, resource = None, id_query = False, reset = False, **keywargs):
        "Opens an I/O session to the instrument."

        self._channel_count = self._analog_channel_count + self._digital_channel_count

        super(rigolBaseScope, self)._initialize(resource, id_query, reset, **keywargs)

        # interface clear
        if not self._driver_operation_simulate:
            self._clear()

        # check ID
        if id_query and not self._driver_operation_simulate:
            id = self.identity.instrument_model
            id_check = self._instrument_id
            id_short = id[:len(id_check)]
            if id_short != id_check:
                raise Exception("Instrument ID mismatch, expecting %s, got %s", id_check, id_short)

        # reset
        if reset:
            self.utility.reset()

    def _utility_disable(self):
        pass

    def _utility_lock_object(self):
        pass

    def _utility_unlock_object(self):
        pass

    def _init_channels(self):
        super(rigolBaseScope, self)._init_channels()

        self._channel_name = list()
        self._channel_label = list()
        self._channel_probe_skew = list()
        self._channel_invert = list()
        self._channel_scale = list()
        self._channel_bw_limit = list()

        self._analog_channel_name = list()
        for i in range(self._analog_channel_count):
            self._channel_name.append("channel%d" % (i+1))
            self._channel_label.append("%d" % (i+1))
            self._analog_channel_name.append("channel%d" % (i+1))
            self._channel_probe_skew.append(0)
            self._channel_invert.append(False)
            self._channel_scale.append(1.0)
            self._channel_bw_limit.append(False)

        # digital channels
        self._digital_channel_name = list()
        if (self._digital_channel_count > 0):
            for i in range(self._digital_channel_count):
                self._channel_name.append("d%d" % i)
                self._channel_label.append("D%d" % i)
                self._digital_channel_name.append("d%d" % i)

            for i in range(self._analog_channel_count, self._channel_count):
                self._channel_input_impedance[i] = 100000
                self._channel_input_frequency_max[i] = 1e9
                self._channel_probe_attenuation[i] = 1
                self._channel_coupling[i] = 'dc'
                self._channel_offset[i] = 0
                self._channel_range[i] = 1

        self._channel_count = self._analog_channel_count + self._digital_channel_count
        self.channels._set_list(self._channel_name)

    def _system_fetch_setup(self):
        if self._driver_operation_simulate:
            return b''

        self._write(":system:setup?")

        data = ivi.decode_ieee_block(self._read_raw())

        return data

    def _system_load_setup(self, data):
        if self._driver_operation_simulate:
            return

        self._write_ieee_block(data, ':system:setup ')

        self.driver_operation.invalidate_all_attributes()

    def _display_fetch_screenshot(self, format='png', invert=False):
        if self._driver_operation_simulate:
            return b''

        if format not in self._display_screenshot_image_format_mapping:
            raise ivi.ValueNotSupportedException()

        format = self._display_screenshot_image_format_mapping[format]

        self._write(":display:data? on, %d, %s" % (int(invert), format))

        data = self._read_raw()

        return ivi.decode_ieee_block(data)

    def _get_timebase_mode(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            if int(self._ask(":timebase:delay:enable?")):
                self._timebase_mode = "window"
            else:
                value = self._ask(":timebase:mode?").lower()
                self._timebase_mode = [k for k,v in TimebaseModeMapping.items() if v==value][0]
            self._set_cache_valid()
        return self._timebase_mode

    def _set_timebase_mode(self, value):
        if value not in TimebaseModeMapping:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            if value == 'window':
                self._write("timebase:mode main")
                self._write("timebase:delay:enable 1")
            else:
                self._write("timebase:delay:enable 0")
                self._write(":timebase:mode %s" % TimebaseModeMapping[value])
        self._timebase_mode = value
        self._set_cache_valid()

    def _get_timebase_position(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._timebase_position = float(self._ask(":timebase:offset?"))
            self._set_cache_valid()
        return self._timebase_position

    def _set_timebase_position(self, value):
        value = float(value)
        if not self._driver_operation_simulate:
            self._write(":timebase:offset %e" % value)
        self._timebase_position = value
        self._set_cache_valid()
        self._set_cache_valid(False, 'timebase_window_position')

    def _get_timebase_range(self):
        return self._get_timebase_scale() * self._horizontal_divisions

    def _set_timebase_range(self, value):
        value = float(value)
        self._set_timebase_scale(value / self._horizontal_divisions)

    def _get_timebase_scale(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._timebase_scale = float(self._ask(":timebase:scale?"))
            self._timebase_range = self._timebase_scale * self._horizontal_divisions
            self._set_cache_valid()
        return self._timebase_scale

    def _set_timebase_scale(self, value):
        value = float(value)
        if not self._driver_operation_simulate:
            self._write(":timebase:scale %e" % value)
        self._timebase_scale = value
        self._timebase_range = value * self._horizontal_divisions
        self._set_cache_valid()
        self._set_cache_valid(False, 'timebase_window_scale')

    def _get_timebase_window_position(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._timebase_window_position = float(self._ask(":timebase:delay:offset?"))
            self._set_cache_valid()
        return self._timebase_window_position

    def _set_timebase_window_position(self, value):
        value = float(value)
        if not self._driver_operation_simulate:
            self._write(":timebase:delay:offset %e" % value)
        self._timebase_window_position = value
        self._set_cache_valid()

    def _get_timebase_window_range(self):
        return self._get_timebase_window_scale() * self._horizontal_divisions

    def _set_timebase_window_range(self, value):
        value = float(value)
        self._set_timebase_window_scale(value / self._horizontal_divisions)

    def _get_timebase_window_scale(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._timebase_window_scale = float(self._ask(":timebase:delay:scale?"))
            self._timebase_window_range = self._timebase_window_scale * self._horizontal_divisions
            self._set_cache_valid()
            self._set_cache_valid(True, 'timebase_window_range')
        return self._timebase_window_scale

    def _set_timebase_window_scale(self, value):
        value = float(value)
        if not self._driver_operation_simulate:
            self._write(":timebase:delay:scale %e" % value)
        self._timebase_window_scale = value
        self._timebase_window_range = value * self._horizontal_divisions
        self._set_cache_valid()
        self._set_cache_valid(True, 'timebase_window_range')

    def _get_display_vectors(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._display_vectors = self._ask(":display:type?").lower() == 'vect'
            self._set_cache_valid()
        return self._display_vectors

    def _set_display_vectors(self, value):
        value = bool(value)
        if not self._driver_operation_simulate:
            self._write(":display:type %s" % ('vectors' if value else 'dots'))
        self._display_vectors = value
        self._set_cache_valid()

    def _display_clear(self):
        if not self._driver_operation_simulate:
            self._write(":display:clear")

    def _get_acquisition_start_time(self):
        pos = 0
        if not self._driver_operation_simulate and not self._get_cache_valid():
            pos = float(self._ask(":timebase:offset?"))
            self._set_cache_valid()
        self._acquisition_start_time = pos - self._get_acquisition_time_per_record() / 2
        return self._acquisition_start_time

    def _set_acquisition_start_time(self, value):
        value = float(value)
        value = value + self._get_acquisition_time_per_record() / 2
        if not self._driver_operation_simulate:
            self._write(":timebase:offset %e" % value)
        self._acquisition_start_time = value
        self._set_cache_valid()

    def _get_acquisition_type(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask(":acquire:type?").lower()
            self._acquisition_type = [k for k,v in AcquisitionTypeMapping.items() if v==value][0]
            self._set_cache_valid()
        return self._acquisition_type

    def _set_acquisition_type(self, value):
        if value not in AcquisitionTypeMapping:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write(":acquire:type %s" % AcquisitionTypeMapping[value])
        self._acquisition_type = value
        self._set_cache_valid()

    def _get_acquisition_number_of_points_minimum(self):
        return self._acquisition_number_of_points_minimum

    def _set_acquisition_number_of_points_minimum(self, value):
        value = int(value)
        self._acquisition_number_of_points_minimum = value

    def _get_acquisition_record_length(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._acquisition_record_length = int(self._ask(":waveform:points?"))
            self._set_cache_valid()
        return self._acquisition_record_length

    def _get_acquisition_time_per_record(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._acquisition_time_per_record = float(self._ask(":timebase:scale?")) * self._horizontal_divisions
            self._set_cache_valid()
        return self._acquisition_time_per_record

    def _set_acquisition_time_per_record(self, value):
        value = float(value)
        if not self._driver_operation_simulate:
            self._write(":timebase:scale %e" % (value / self._horizontal_divisions))
        self._acquisition_time_per_record = value
        self._set_cache_valid()
        self._set_cache_valid(False, 'acquisition_start_time')

    def _get_channel_label(self, index):
        index = ivi.get_index(self._channel_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._channel_label[index] = self._ask(":%s:label?" % self._channel_name[index]).strip('"')
            self._set_cache_valid(index=index)
        return self._channel_label[index]

    def _set_channel_label(self, index, value):
        value = str(value)
        index = ivi.get_index(self._channel_name, index)
        if not self._driver_operation_simulate:
            self._write(":%s:label \"%s\"" % (self._channel_name[index], value))
        self._channel_label[index] = value
        self._set_cache_valid(index=index)

    def _get_channel_enabled(self, index):
        index = ivi.get_index(self._channel_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._channel_enabled[index] = bool(int(self._ask(":%s:display?" % self._channel_name[index])))
            self._set_cache_valid(index=index)
        return self._channel_enabled[index]

    def _set_channel_enabled(self, index, value):
        value = bool(value)
        index = ivi.get_index(self._channel_name, index)
        if not self._driver_operation_simulate:
            self._write(":%s:display %d" % (self._channel_name[index], int(value)))
        self._channel_enabled[index] = value
        self._set_cache_valid(index=index)

    def _get_channel_input_impedance(self, index):
        index = ivi.get_index(self._analog_channel_name, index)
        return self._channel_input_impedance[index]

    def _set_channel_input_impedance(self, index, value):
        value = float(value)
        index = ivi.get_index(self._analog_channel_name, index)
        if value != 1000000:
            raise Exception('Invalid impedance selection')
        self._channel_input_impedance[index] = value

    def _get_channel_input_frequency_max(self, index):
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            value = self._ask(":%s:bwlimit?" % self._channel_name[index]).upper()
            if value == 'OFF':
                self._channel_input_frequency_max[index] = self._bandwidth
            else:
                self._channel_input_frequency_max[index] = self._bandwidth_limit[value]
        return self._channel_input_frequency_max[index]

    def _set_channel_input_frequency_max(self, index, value):
        value = float(value)
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate:
            limit = 'OFF'
            bw = self._bandwidth

            for l, b in self._bandwidth_limit.items():
                if b < bw and b > value:
                    limit, bw = l, b

            value = bw
            self._write(":%s:bwlimit %s" % (self._channel_name[index], limit))
        self._channel_input_frequency_max[index] = value
        self._set_cache_valid(index=index)

    def _get_channel_probe_attenuation(self, index):
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._channel_probe_attenuation[index] = float(self._ask(":%s:probe?" % self._channel_name[index]))
            self._set_cache_valid(index=index)
        return self._channel_probe_attenuation[index]

    def _set_channel_probe_attenuation(self, index, value):
        index = ivi.get_index(self._analog_channel_name, index)
        value = float(value)
        if not self._driver_operation_simulate:
            self._write(":%s:probe %e" % (self._channel_name[index], value))
        self._channel_probe_attenuation[index] = value
        self._set_cache_valid(index=index)
        self._set_cache_valid(False, 'channel_offset', index)
        self._set_cache_valid(False, 'channel_scale', index)
        self._set_cache_valid(False, 'channel_range', index)
        self._set_cache_valid(False, 'trigger_level')

    def _get_channel_probe_skew(self, index):
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._channel_probe_skew[index] = float(self._ask(":%s:tcal?" % self._channel_name[index]))
            self._set_cache_valid(index=index)
        return self._channel_probe_skew[index]

    def _set_channel_probe_skew(self, index, value):
        index = ivi.get_index(self._analog_channel_name, index)
        value = float(value)
        if not self._driver_operation_simulate:
            self._write(":%s:tcal %e" % (self._channel_name[index], value))
        self._channel_probe_skew[index] = value
        self._set_cache_valid(index=index)

    def _get_channel_invert(self, index):
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._channel_invert[index] = bool(int(self._ask(":%s:invert?" % self._channel_name[index])))
            self._set_cache_valid(index=index)
        return self._channel_invert[index]

    def _set_channel_invert(self, index, value):
        index = ivi.get_index(self._analog_channel_name, index)
        value = bool(value)
        if not self._driver_operation_simulate:
            self._write(":%s:invert %d" % (self._channel_name[index], value))
        self._channel_invert[index] = value
        self._set_cache_valid(index=index)

    def _get_channel_coupling(self, index):
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._channel_enabled[index] = self._ask(":%s:coupling?" % self._channel_name[index]).lower()
            self._set_cache_valid(index=index)
        return self._channel_coupling[index]

    def _set_channel_coupling(self, index, value):
        index = ivi.get_index(self._analog_channel_name, index)
        if value not in VerticalCoupling:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write(":%s:coupling %s" % (self._channel_name[index], value))
        self._channel_coupling[index] = value
        self._set_cache_valid(index=index)

    def _get_channel_offset(self, index):
        index = ivi.get_index(self._channel_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._channel_offset[index] = -float(self._ask(":%s:offset?" % self._channel_name[index]))
            self._set_cache_valid(index=index)
        return self._channel_offset[index]

    def _set_channel_offset(self, index, value):
        index = ivi.get_index(self._channel_name, index)
        value = float(value)
        if not self._driver_operation_simulate:
            self._write(":%s:offset %e" % (self._channel_name[index], -value))
        self._channel_offset[index] = value
        self._set_cache_valid(index=index)

    def _get_channel_range(self, index):
        index = ivi.get_index(self._channel_name, index)
        return self._get_channel_scale(index) * self._vertical_divisions

    def _set_channel_range(self, index, value):
        index = ivi.get_index(self._channel_name, index)
        value = float(value)
        self._set_channel_range(index, value / self._vertical_divisions)

    def _get_channel_scale(self, index):
        index = ivi.get_index(self._channel_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._channel_scale[index] = float(self._ask(":%s:scale?" % self._channel_name[index]))
            self._channel_range[index] = self._channel_scale[index] * self._vertical_divisions
            self._set_cache_valid(index=index)
            self._set_cache_valid(True, "channel_range", index)
        return self._channel_scale[index]

    def _set_channel_scale(self, index, value):
        index = ivi.get_index(self._channel_name, index)
        value = float(value)
        if not self._driver_operation_simulate:
            self._write(":%s:scale %e" % (self._channel_name[index], value))
        self._channel_scale[index] = value
        self._channel_range[index] = value * self._vertical_divisions
        self._set_cache_valid(index=index)
        self._set_cache_valid(True, "channel_range", index)
        self._set_cache_valid(False, "channel_offset", index)

    def _get_measurement_status(self):
        return self._measurement_status

    def _get_trigger_coupling(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            cpl = self._ask(":trigger:coupling?").lower()
            noise = int(self._ask(":trigger:nreject?"))
            for k in TriggerCouplingMapping:
                if (cpl, noise) == TriggerCouplingMapping[k]:
                    self._trigger_coupling = k
        return self._trigger_coupling

    def _set_trigger_coupling(self, value):
        if value not in TriggerCouplingMapping:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            cpl, noise = TriggerCouplingMapping[value]
            self._write(":trigger:coupling %s" % cpl)
            self._write(":trigger:nreject %d" % noise)
        self._trigger_coupling = value
        self._set_cache_valid()

    def _get_trigger_holdoff(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._trigger_holdoff = float(self._ask(":trigger:holdoff?"))
            self._set_cache_valid()
        return self._trigger_holdoff

    def _set_trigger_holdoff(self, value):
        value = float(value)
        if not self._driver_operation_simulate:
            self._write(":trigger:holdoff %e" % value)
        self._trigger_holdoff = value
        self._set_cache_valid()

    def _get_trigger_level(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._trigger_level = float(self._ask(":trigger:edge:level?"))
            self._set_cache_valid()
        return self._trigger_level

    def _set_trigger_level(self, value):
        value = float(value)
        if not self._driver_operation_simulate:
            self._write(":trigger:edge:level %e" % value)
        self._trigger_level = value
        self._set_cache_valid()

    def _get_trigger_edge_slope(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask(":trigger:edge:slope?").lower()
            self._trigger_edge_slope = [k for k,v in SlopeMapping.items() if v==value][0]
            self._set_cache_valid()
        return self._trigger_edge_slope

    def _set_trigger_edge_slope(self, value):
        if value not in SlopeMapping:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write(":trigger:edge:slope %s" % SlopeMapping[value])
        self._trigger_edge_slope = value
        self._set_cache_valid()

    def _get_trigger_source(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask(":trigger:edge:source?").lower()
            # TODO process value
            self._trigger_source = value
            self._set_cache_valid()
        return self._trigger_source

    def _set_trigger_source(self, value):
        if hasattr(value, 'name'):
            value = value.name
        value = str(value)
        if value not in self._channel_name:
            raise ivi.UnknownPhysicalNameException()
        if not self._driver_operation_simulate:
            self._write(":trigger:edge:source %s" % value)
        self._trigger_source = value
        self._set_cache_valid()

    def _get_trigger_type(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask(":trigger:mode?").lower()
            if value == 'edge':
                src = self._ask(":trigger:edge:source?").lower()
                if src == 'ac':
                    value = 'ac_line'
            elif value == 'puls':
                qual = self._ask(":trigger:pulse:when?").lower()
                if qual in ('pgl', 'ngl'):
                    value = 'width'
                else:
                    value = 'glitch'
            else:
                value = [k for k,v in TriggerTypeMapping.items() if v==value][0]
            self._trigger_type = value
            self._set_cache_valid()
        return self._trigger_type

    def _set_trigger_type(self, value):
        if value not in TriggerTypeMapping:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write(":trigger:mode %s" % TriggerTypeMapping[value])
            if value == 'ac_line':
                self._write(":trigger:edge:source ac")
            if value == 'glitch':
                if self._get_trigger_glitch_condition() == 'greater_than':
                    if self._get_trigger_width_polarity() == 'positive':
                        self._write(":trigger:pulse:when pgr")
                    else:
                        self._write(":trigger:pulse:when ngr")
                else:
                    if self._get_trigger_width_polarity() == 'positive':
                        self._write(":trigger:pulse:when ples")
                    else:
                        self._write(":trigger:pulse:when nles")
            if value == 'width':
                if self._get_trigger_width_polarity() == 'positive':
                    self._write(":trigger:pulse:when pgl")
                else:
                    self._write(":trigger:pulse:when ngl")
        self._trigger_type = value
        self._set_cache_valid()

    def _measurement_abort(self):
        pass

    def _get_trigger_tv_trigger_event(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask(":trigger:video:mode?").lower()
            # may need processing
            self._trigger_tv_trigger_event = [k for k,v in TVTriggerEventMapping.items() if v==value][0]
            self._set_cache_valid()
        return self._trigger_tv_trigger_event

    def _set_trigger_tv_trigger_event(self, value):
        if value not in TVTriggerEvent:
            raise ivi.ValueNotSupportedException()
        # may need processing
        if not self._driver_operation_simulate:
            self._write(":trigger:video:mode %s" % TVTriggerEventMapping[value])
        self._trigger_tv_trigger_event = value
        self._set_cache_valid()

    def _get_trigger_tv_line_number(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = int(self._ask(":trigger:video:line?"))
            # may need processing
            self._trigger_tv_line_number = value
            self._set_cache_valid()
        return self._trigger_tv_line_number

    def _set_trigger_tv_line_number(self, value):
        value = int(value)
        # may need processing
        if not self._driver_operation_simulate:
            self._write(":trigger:video:line %e" % value)
        self._trigger_tv_line_number = value
        self._set_cache_valid()

    def _get_trigger_tv_polarity(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask(":trigger:video:polarity?").lower()
            self._trigger_tv_polarity = [k for k,v in PolarityMapping.items() if v==value][0]
            self._set_cache_valid()
        return self._trigger_tv_polarity

    def _set_trigger_tv_polarity(self, value):
        if value not in PolarityMapping:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write(":trigger:video:polarity %s" % PolarityMapping[value])
        self._trigger_tv_polarity = value
        self._set_cache_valid()

    def _get_trigger_tv_signal_format(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask(":trigger:video:standard?").lower()
            self._trigger_tv_signal_format = [k for k,v in TVTriggerFormatMapping.items() if v==value][0]
            self._set_cache_valid()
        return self._trigger_tv_signal_format

    def _set_trigger_tv_signal_format(self, value):
        if value not in TVTriggerFormatMapping:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write(":trigger:video:standard %s" % TVTriggerFormatMapping[value])
        self._trigger_tv_signal_format = value
        self._set_cache_valid()

    def _get_trigger_glitch_condition(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask(":trigger:pulse:when?").lower()
            if value in ('pgr', 'ngr'):
                self._trigger_glitch_condition = 'greater_than'
                self._set_cache_valid()
            elif value in ('ples', 'nles'):
                self._trigger_glitch_condition = 'less_than'
                self._set_cache_valid()
        return self._trigger_glitch_condition

    def _set_trigger_glitch_condition(self, value):
        if value not in GlitchConditionMapping:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            if self._get_trigger_glitch_polarity() == 'positive':
                self._write(":trigger:pulse:when %s" % ('pgr' if value == 'greater_than' else 'ples'))
            else:
                self._write(":trigger:pulse:when %s" % ('ngr' if value == 'greater_than' else 'nles'))
        self._trigger_glitch_condition = value
        self._set_cache_valid()

    def _get_trigger_glitch_polarity(self):
        return self._get_trigger_width_polarity()

    def _set_trigger_glitch_polarity(self, value):
        self._set_trigger_width_polarity(value)

    def _get_trigger_glitch_width(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._trigger_glitch_width = float(self._ask(":trigger:pulse:width?"))
            self._set_cache_valid()
        return self._trigger_glitch_width

    def _set_trigger_glitch_width(self, value):
        value = float(value)
        if not self._driver_operation_simulate:
            self._write(":trigger:pulse:width %e" % value)
        self._trigger_glitch_width = value
        self._set_cache_valid()

    def _get_trigger_width_condition(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = 'within'
        return self._trigger_width_condition

    def _set_trigger_width_condition(self, value):
        if value not in WidthConditionMapping:
            raise ivi.ValueNotSupportedException()
        self._trigger_width_condition = value
        self._set_cache_valid()

    def _get_trigger_width_threshold_high(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._trigger_width_threshold_high = float(self._ask(":trigger:pulse:uwidth?"))
            self._set_cache_valid()
        return self._trigger_width_threshold_high

    def _set_trigger_width_threshold_high(self, value):
        value = float(value)
        if not self._driver_operation_simulate:
            self._write(":trigger:pulse:uwidth %e" % value)
        self._trigger_width_threshold_high = value
        self._set_cache_valid()

    def _get_trigger_width_threshold_low(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._trigger_width_threshold_low = float(self._ask(":trigger:pulse:lwidth?"))
            self._set_cache_valid()
        return self._trigger_width_threshold_low

    def _set_trigger_width_threshold_low(self, value):
        value = float(value)
        if not self._driver_operation_simulate:
            self._write(":trigger:pulse:lwidth %e" % value)
        self._trigger_width_threshold_low = value
        self._set_cache_valid()

    def _get_trigger_width_polarity(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask(":trigger:pulse:when?").lower()
            self._trigger_width_polarity = 'positive' if value.lower() in ('pgr', 'ples', 'pgl') else 'negative'
            self._set_cache_valid()
        return self._trigger_width_polarity

    def _set_trigger_width_polarity(self, value):
        if value not in PolarityMapping:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            if self._get_trigger_type() == 'glitch':
                if self._get_trigger_glitch_condition() == 'greater_than':
                    if value == 'positive':
                        self._write(":trigger:pulse:when pgr")
                    else:
                        self._write(":trigger:pulse:when ngr")
                else:
                    if value == 'positive':
                        self._write(":trigger:pulse:when ples")
                    else:
                        self._write(":trigger:pulse:when nles")
            if self._get_trigger_type() == 'width':
                if value == 'positive':
                    self._write(":trigger:pulse:when pgl")
                else:
                    self._write(":trigger:pulse:when ngl")
        self._trigger_width_polarity = value
        self._set_cache_valid()

    def _get_trigger_ac_line_slope(self):
        return self._get_trigger_edge_slope()

    def _set_trigger_ac_line_slope(self, value):
        self._set_trigger_edge_slope(value)

    def _measurement_fetch_waveform(self, index):
        index = ivi.get_index(self._channel_name, index)

        if self._driver_operation_simulate:
            return ivi.TraceYT()

        expected_points = float(self._ask("acquire:srate?"))*(self._horizontal_divisions*float(self._ask("timebase:scale?")))

        self._write(":waveform:source %s" % self._channel_name[index])
        self._write(":waveform:format byte")
        if expected_points == 1200:
            self._write(":waveform:mode normal")
        else:
            self._write(":waveform:mode raw")

        trace = ivi.TraceYT()

        # Read preamble
        pre = self._ask(":waveform:preamble?").split(',')

        acq_format = int(pre[0])
        acq_type = int(pre[1])
        points = int(pre[2])
        trace.average_count = int(pre[3])
        trace.x_increment = float(pre[4])
        trace.x_origin = float(pre[5])
        trace.x_reference = int(float(pre[6]))
        trace.y_increment = float(pre[7])
        trace.y_origin = 0.0
        trace.y_reference = int(float(pre[9]) + float(pre[8]))

        if acq_format == 0:
            block_size = 250000
        elif acq_format == 1:
            block_size = 125000
        else:
            raise UnexpectedResponseException()

        # Read waveform data
        data = bytearray()

        for offset in range(1, points+1, block_size):
            self._write(":waveform:start %d" % offset)
            self._write(":waveform:stop %d" % min(points, offset+block_size-1))
            self._write(":waveform:data?")
            raw_data = self._read_raw()
            data.extend(ivi.decode_ieee_block(raw_data))

        # Store in trace object
        if acq_format == 0:
            trace.y_raw = array.array('B', data[0:points])
        elif acq_format == 1:
            trace.y_raw = array.array('H', data[0:points*2])

            if sys.byteorder == 'big':
                trace.y_raw.byteswap()

        # handle digital channels
        if self._channel_name[index] in self._digital_channel_name:
            trace.y_increment = 1

            if points != 1200:
                # raw waveform; extract channel from group
                digital_index = self._digital_channel_name.index(self._channel_name[index])
                offset = digital_index % 8

                for k in range(points):
                    trace.y_raw[k] = (trace.y_raw[k] >> offset) & 1

        return trace

    def _measurement_read_waveform(self, index, maximum_time):
        return self._measurement_fetch_waveform(index)

    def _measurement_initiate(self):
        if not self._driver_operation_simulate:
            self._write(":single")
            self._set_cache_valid(False, 'trigger_continuous')

    def _get_reference_level_high(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._reference_level_high = float(self._ask(":measure:setup:max?"))
            self._set_cache_valid()
        return self._reference_level_high

    def _set_reference_level_high(self, value):
        value = float(value)
        if value < 7: value = 7
        if value > 95: value = 95
        if not self._driver_operation_simulate:
            self._write(":measure:setup:max %e" % value)
        self._reference_level_high = value
        self._set_cache_valid()

    def _get_reference_level_low(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._reference_level_low = float(self._ask(":measure:setup:min?"))
            self._set_cache_valid()
        return self._reference_level_low

    def _set_reference_level_low(self, value):
        value = float(value)
        if value < 5: value = 5
        if value > 93: value = 93
        if not self._driver_operation_simulate:
            self._write(":measure:setup:min %e" % value)
        self._reference_level_low = value
        self._set_cache_valid()

    def _get_reference_level_middle(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._reference_level_middle = float(self._ask(":measure:setup:mid?"))
            self._set_cache_valid()
        return self._reference_level_middle

    def _set_reference_level_middle(self, value):
        value = float(value)
        if value < 6: value = 6
        if value > 94: value = 94
        if not self._driver_operation_simulate:
            self._write(":measure:setup:mid %e" % value)
        self._reference_level_middle = value
        self._set_cache_valid()

    def _measurement_fetch_waveform_measurement(self, index, measurement_function, ref_channel = None):
        index = ivi.get_index(self._channel_name, index)
        if index < self._analog_channel_count:
            if measurement_function not in MeasurementFunctionMapping:
                raise ivi.ValueNotSupportedException()
            func = MeasurementFunctionMapping[measurement_function]
        else:
            if measurement_function not in MeasurementFunctionMappingDigital:
                raise ivi.ValueNotSupportedException()
            func = MeasurementFunctionMappingDigital[measurement_function]
        if not self._driver_operation_simulate:
            l = func.split(' ')
            l[0] = l[0] + '?'
            if len(l) > 1:
                l[-1] = l[-1] + ','
            func = ' '.join(l)
            query = ":measure:item? %s, %s" % (func, self._channel_name[index])
            if measurement_function in ['phase', 'delay']:
                ref_index = ivi.get_index(self._channel_name, ref_channel)
                query += ", %s" % self._channel_name[ref_index]
            return float(self._ask(query))
        return 0

    def _measurement_read_waveform_measurement(self, index, measurement_function, maximum_time):
        return self._measurement_fetch_waveform_measurement(index, measurement_function)

    def _get_trigger_continuous(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._trigger_continuous = self._ask(":trigger:sweep?").lower() != 'sing'
            self._set_cache_valid()
        return self._trigger_continuous

    def _set_trigger_continuous(self, value):
        value = bool(value)
        if not self._driver_operation_simulate:
            self._write(":%s" % ('run' if value else 'stop'))
        self._trigger_continuous = value
        self._set_cache_valid()

    def _get_acquisition_number_of_averages(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._acquisition_number_of_averages = int(self._ask(":acquire:averages?"))
            self._set_cache_valid()
        return self._acquisition_number_of_averages

    def _set_acquisition_number_of_averages(self, value):
        if value < 2 or value > self._max_averages:
            raise ivi.OutOfRangeException()
        value = 2**round(math.log(value, 2))
        if not self._driver_operation_simulate:
            self._write(":acquire:averages %d" % value)
        self._acquisition_number_of_averages = value
        self._set_cache_valid()

    def _get_trigger_modifier(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask(":trigger:sweep?").lower()
            if value == 'sing':
                self._trigger_modifier = 'none'
            else:
                self._trigger_modifier = [k for k,v in TriggerModifierMapping.items() if v==value][0]
                self._set_cache_valid()
        return self._trigger_modifier

    def _set_trigger_modifier(self, value):
        if value not in TriggerModifierMapping:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write(":trigger:sweep %s" % TriggerModifierMapping[value])
        self._trigger_modifier = value
        self._set_cache_valid()

    def _measurement_auto_setup(self):
        if not self._driver_operation_simulate:
            self._write(":autoscale")

