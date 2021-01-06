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

from .tektronixDPO7000 import *

class tektronixDPO70000(tektronixDPO7000):
    "Tektronix DPO70000 series IVI oscilloscope driver"

    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', 'DPO70000')

        super(tektronixDPO70000, self).__init__(*args, **kwargs)

        self._analog_channel_count = 4
        self._digital_channel_count = 0
        self._bandwidth = 35e9

        self._identity_description = "Tektronix DPO70000 series IVI oscilloscope driver"
        self._identity_supported_instrument_models = ['DPO70404', 'DPO70604', 'DPO70804',
                'DPO71254', 'DPO71604', 'DPO72004', 'DPO70404B', 'DPO70604B', 'DPO70804B',
                'DPO71254B', 'DPO71604B', 'DPO72004B', 'DPO70404C', 'DPO70604C', 'DPO70804C',
                'DPO71254C', 'DPO71604C', 'DPO72004C', 'DPO72304DX', 'DPO72504DX', 'DPO73304DX']

        self._init_channels()
