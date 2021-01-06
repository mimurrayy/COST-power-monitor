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

from .rigolBaseScope import *
from .rigolDSSource import *

ScreenshotImageFormatMapping = {
        'bmp': 'bmp',
        'bmp24': 'bmp24'}

class rigolDS2000A(rigolBaseScope, rigolDSSource):
    "Rigol DS2000A series IVI oscilloscope driver"

    def __init__(self, *args, **kwargs):
        super(rigolDS2000A, self).__init__(*args, **kwargs)

        self._analog_channel_count = 2
        self._digital_channel_count = 16
        self._bandwidth = 300e6
        self._bandwidth_limit = {'20M': 20e6, '100M': 100e6}
        self._max_averages = 8192

        self._horizontal_divisions = 14
        self._vertical_divisions = 8

        # Internal source
        self._output_count = 2

        self._display_screenshot_image_format_mapping = ScreenshotImageFormatMapping

        self._identity_description = "Rigol DS2000A series IVI oscilloscope driver"
        self._identity_supported_instrument_models = ['DS2074A', 'DS2104A', 'DS2204A',
                'DS2304A', 'MSO2074A', 'MSO2104A', 'MSO2204A', 'MSO2304A']

        self._init_channels()
        self._init_outputs()

    def _display_fetch_screenshot(self, format='bmp', invert=False):
        if self._driver_operation_simulate:
            return b''

        if format not in self._display_screenshot_image_format_mapping:
            raise ivi.ValueNotSupportedException()

        self._write(":display:data?")

        data = self._read_raw()

        return ivi.decode_ieee_block(data)

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
            self._write(":%s:probe %s" % (self._channel_name[index], ("%f" %value).rstrip('0').rstrip('.')))
        self._channel_probe_attenuation[index] = value
        self._set_cache_valid(index=index)
        self._set_cache_valid(False, 'channel_offset', index)
        self._set_cache_valid(False, 'channel_scale', index)
        self._set_cache_valid(False, 'channel_range', index)
        self._set_cache_valid(False, 'trigger_level')

    def _measurement_fetch_waveform(self, index):
        index = ivi.get_index(self._channel_name, index)

        if self._driver_operation_simulate:
            return ivi.TraceYT()

        if self._channel_name[index] in self._digital_channel_name:
            self._write(":waveform:source la")
            self._write(":waveform:format word")
        else:
            self._write(":waveform:source %s" % self._channel_name[index])
            self._write(":waveform:format byte")
        self._write(":waveform:mode max")

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

            # extract channel from group
            digital_index = self._digital_channel_name.index(self._channel_name[index])
            
            for k in range(points):
                trace.y_raw[k] = (trace.y_raw[k] >> offset) & 1

        return trace

