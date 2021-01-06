"""

Python Interchangeable Virtual Instrument Library

Copyright (c) 2013-2017 Alex Forencich

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

from .. import ivi
from .. import dcpwr
from .. import scpi

TrackingType = set(['floating'])
TriggerSourceMapping = {
        'immediate': 'imm',
        'bus': 'bus'}

class rigolBaseDCPwr(scpi.dcpwr.Base, scpi.dcpwr.Trigger, scpi.dcpwr.SoftwareTrigger,
                scpi.dcpwr.Measurement):
    "Rigol generic IVI DC power supply driver"
    
    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', '')
        
        super(rigolBaseDCPwr, self).__init__(*args, **kwargs)
        
        self._output_count = 3
        
        self._output_spec = [
            {
                'range': {
                    'P8V': (8.0, 5.0)
                },
                'ovp_max': 8.8,
                'ocp_max': 5.5,
                'voltage_max': 8.0,
                'current_max': 5.0
            },
            {
                'range': {
                    'P30V': (30.0, 2.0)
                },
                'ovp_max': 33.0,
                'ocp_max': 2.2,
                'voltage_max': 30.0,
                'current_max': 2.0
            },
            {
                'range': {
                    'N30V': (-30.0, 2.0)
                },
                'ovp_max': -33.0,
                'ocp_max': 2.2,
                'voltage_max': -30.0,
                'current_max': 2.0
            }
        ]
        
        self._memory_size = 10
        
        self._identity_description = "Rigol generic IVI DC power supply driver"
        self._identity_identifier = ""
        self._identity_revision = ""
        self._identity_vendor = ""
        self._identity_instrument_manufacturer = "Rigol Technologies"
        self._identity_instrument_model = ""
        self._identity_instrument_firmware_revision = ""
        self._identity_specification_major_version = 3
        self._identity_specification_minor_version = 0
        self._identity_supported_instrument_models = ['DP831A', 'DP832', 'DP832A']
        
        self._add_method('memory.save',
                        self._memory_save)
        self._add_method('memory.recall',
                        self._memory_recall)
        
        self._init_outputs()

    def _get_bool_str(self, value):
        """
        redefining to change behavior from '0'/'1' to 'off'/'on'
        """
        if bool(value):
            return 'on'
        return 'off'
    
    def _memory_save(self, index):
        index = int(index)
        if index < 1 or index > self._memory_size:
            raise OutOfRangeException()
        if not self._driver_operation_simulate:
            self._write("*sav %d" % index)
    
    def _memory_recall(self, index):
        index = int(index)
        if index < 1 or index > self._memory_size:
            raise OutOfRangeException()
        if not self._driver_operation_simulate:
            self._write("*rcl %d" % index)

    def _utility_self_test(self):
        code = 0
        message = "No Response"
        if not self._driver_operation_simulate:
            self._write("*TST?")
            # wait for test to complete
            message = self._read()
            if 'FAIL' in message:
                code = -1
        return (code, message)