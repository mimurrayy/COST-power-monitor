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

class rigolDS1000Z(rigolBaseScope, rigolDSSource):
    "Rigol DS1000Z series IVI oscilloscope driver"

    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', '')

        super(rigolDS1000Z, self).__init__(*args, **kwargs)

        self._analog_channel_count = 4
        self._digital_channel_count = 16
        self._bandwidth = 100e6
        self._bandwidth_limit = {'20M': 20e6}
        self._max_averages = 1024

        self._horizontal_divisions = 12
        self._vertical_divisions = 8

        # Internal source
        self._output_count = 2

        self._identity_description = "Rigol DS1000Z series IVI oscilloscope driver"
        self._identity_supported_instrument_models = ['DS1074Z', 'DS1104Z', 'MSO1074Z', 'MSO1104Z']

        self._init_channels()
        self._init_outputs()

