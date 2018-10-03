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

from .tektronixBaseScope import *

ScreenshotImageFormatMapping = {
        'tif': 'tiff',
        'tiff': 'tiff',
        'bmp': 'bmp',
        'bmp24': 'bmp',
        'png': 'png',
        'png24': 'png',
        'jpg': 'jpeg',
        'jpeg': 'jpeg',
        'pcx': 'pcx'}

class tektronixDPO5000(tektronixBaseScope):
    "Tektronix DPO5000 series IVI oscilloscope driver"

    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', 'DPO5000')

        super(tektronixDPO5000, self).__init__(*args, **kwargs)

        self._analog_channel_count = 4
        self._digital_channel_count = 0
        self._bandwidth = 2e9

        self._display_screenshot_image_format_mapping = ScreenshotImageFormatMapping

        self._identity_description = "Tektronix DPO5000 series IVI oscilloscope driver"
        self._identity_supported_instrument_models = ['DPO5034', 'DPO5054', 'DPO5104',
                'DPO5204', 'DPO5034B', 'DPO5054B', 'DPO5104B', 'DPO5204B']

        self._init_channels()


    def _utility_self_test(self):
        code = 0
        message = "Self test passed"
        if not self._driver_operation_simulate:
            self._write("diag:select all")
            self._write("diag:control:loop off")
            self._write("diag:execute")
            # wait for test to complete
            res = ''
            while int(self._ask("diag:state?")):
                time.sleep(5)
            res = self._ask("diag:results?").strip('"').lower()
            code = 0 if res == 'pass' else 1
            if code != 0:
                message = "Self test failed"
        return (code, message)

    def _display_fetch_screenshot(self, format='png', invert=False):
        if self._driver_operation_simulate:
            return b''

        if format not in self._display_screenshot_image_format_mapping:
            raise ivi.ValueNotSupportedException()

        format = self._display_screenshot_image_format_mapping[format]

        if invert:
            self._write(":export:palette inksaver")
        else:
            self._write(":export:palette color")
        self._write(":export:filename \"C:\\temp\\screen.%s\"" % format)
        self._write(":export:format %s" % format)
        self._write(":export start")
        self._write(":filesystem:readfile \"C:\\temp\\screen.%s\"" % format)

        return self._read_raw()

    def _get_timebase_mode(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            if int(self._ask(":zoom:state?")):
                self._timebase_mode = "window"
            else:
                self._timebase_mode = "main"
            self._set_cache_valid()
        return self._timebase_mode

    def _set_timebase_mode(self, value):
        if value not in TimebaseModeMapping:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            if value == 'window':
                self._write(":zoom:state 1")
            else:
                self._write(":zoom:state 0")
        self._timebase_mode = value
        self._set_cache_valid()

    def _measurement_fetch_waveform(self, index):
        index = ivi.get_index(self._channel_name, index)

        if self._driver_operation_simulate:
            return ivi.TraceYT()

        self._write(":data:source %s" % self._channel_name[index])
        self._write(":data:encdg fastest")
        self._write(":data:width 2")
        self._write(":data:start 1")
        self._write(":data:stop 1e10")

        trace = ivi.TraceYT()

        # Read preamble
        pre = self._ask(":wfmoutpre?").split(';')

        acq_format = pre[7].strip().upper()
        points = int(pre[6])
        point_size = int(pre[0])
        point_enc = pre[2].strip().upper()
        point_fmt = pre[3].strip().upper()
        byte_order = pre[4].strip().upper()
        trace.x_increment = float(pre[9])
        trace.x_origin = float(pre[10])
        trace.x_reference = int(float(pre[11]))
        trace.y_increment = float(pre[13])
        trace.y_reference = int(float(pre[14]))
        trace.y_origin = float(pre[15])

        if acq_format != 'Y':
            raise UnexpectedResponseException()

        if point_enc != 'BINARY':
            raise UnexpectedResponseException()

        # Read waveform data
        raw_data = self._ask_for_ieee_block(":curve?")
        self._read_raw() # flush buffer

        # Store in trace object
        if point_fmt == 'RP' and point_size == 1:
            trace.y_raw = array.array('B', raw_data[0:points*point_size])
        elif point_fmt == 'RP' and point_size == 2:
            trace.y_raw = array.array('H', raw_data[0:points*point_size])
        elif point_fmt == 'RI' and point_size == 1:
            trace.y_raw = array.array('b', raw_data[0:points*point_size])
        elif point_fmt == 'RI' and point_size == 2:
            trace.y_raw = array.array('h', raw_data[0:points*point_size])
        elif point_fmt == 'FP' and point_size == 4:
            trace.y_increment = 1
            trace.y_reference = 0
            trace.y_origin = 0
            trace.y_raw = array.array('f', raw_data[0:points*point_size])
        else:
            raise UnexpectedResponseException()

        if (byte_order == 'LSB') != (sys.byteorder == 'little'):
            trace.y_raw.byteswap()

        return trace

