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

class rigolDS4000(rigolBaseScope):
    "Rigol DS4000 series IVI oscilloscope driver"

    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', '')

        super(rigolDS4000, self).__init__(*args, **kwargs)

        self._analog_channel_count = 4
        self._digital_channel_count = 16
        self._bandwidth = 500e6
        self._bandwidth_limit = {'20M': 20e6, '100M': 100e6}
        self._max_averages = 8192

        self._horizontal_divisions = 12
        self._vertical_divisions = 8

        self._identity_description = "Rigol DS4000 series IVI oscilloscope driver"
        self._identity_supported_instrument_models = ['DS4012', 'DS4014', 'DS4022',
                'DS4024', 'DS4032', 'DS4034', 'DS4052', 'DS4054', 'MSO4012', 'MSO4014',
                'MSO4022', 'MSO4024', 'MSO4032', 'MSO4034', 'MSO4052', 'MSO4054']

        self._init_channels()

    def _display_fetch_screenshot(self, format='bmp', invert=False):
        if self._driver_operation_simulate:
            return b''

        if format not in self._display_screenshot_image_format_mapping:
            raise ivi.ValueNotSupportedException()

        self._write(":display:data?")

        data = self._read_raw()

        return ivi.decode_ieee_block(data)
    
    def _get_channel_input_impedance(self, index):
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            val = self._ask(":%s:impedance?" % self._channel_name[index])
            if val == 'OMEG':
                self._channel_input_impedance[index] = 1000000
            elif val == 'FIFT':
                self._channel_input_impedance[index] = 50
            self._set_cache_valid(index=index)
        return self._channel_input_impedance[index]
    
    def _set_channel_input_impedance(self, index, value):
        value = float(value)
        index = ivi.get_index(self._analog_channel_name, index)
        if value != 50 and value != 1000000:
            raise Exception('Invalid impedance selection')
        if not self._driver_operation_simulate:
            if value == 1000000:
                self._write(":%s:impedance omeg" % self._channel_name[index])
            elif value == 50:
                self._write(":%s:impedance fifty" % self._channel_name[index])
        self._channel_input_impedance[index] = value
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
            self._write(":%s:probe %s" % (self._channel_name[index], ("%f" %value).rstrip('0').rstrip('.')))
        self._channel_probe_attenuation[index] = value
        self._set_cache_valid(index=index)
        self._set_cache_valid(False, 'channel_offset', index)
        self._set_cache_valid(False, 'channel_scale', index)
        self._set_cache_valid(False, 'channel_range', index)
        self._set_cache_valid(False, 'trigger_level')

