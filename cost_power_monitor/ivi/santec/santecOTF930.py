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

import time

from .. import ivi

class santecOTF930(ivi.Driver):
    "Santec OTF930 series optical tunable filter driver"
    
    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', '')
        
        super(santecOTF930, self).__init__(*args, **kwargs)
        
        self._identity_description = "Santec OTF930 series optical tunable filter driver"
        self._identity_identifier = ""
        self._identity_revision = ""
        self._identity_vendor = ""
        self._identity_instrument_manufacturer = "Santec"
        self._identity_instrument_model = "OTF930"
        self._identity_instrument_firmware_revision = ""
        self._identity_specification_major_version = 0
        self._identity_specification_minor_version = 0
        self._identity_supported_instrument_models = ['OTF930']
        
        self._wavelength = 1300.0
        self._offset = 0.0
        self._attenuation = 0.0

        self._add_property('wavelength',
                        self._get_wavelength,
                        self._set_wavelength,
                        None,
                        ivi.Doc("""
                        Specifies the filter center wavelength.  The units are meters.
                        """))
        self._add_property('offset',
                        self._get_offset,
                        self._set_offset,
                        None,
                        ivi.Doc("""
                        Specifies the offset for the wavelength setting. The units are meters.
                        """))
        self._add_property('attenuation',
                        self._get_attenuation,
                        self._set_attenuation,
                        None,
                        ivi.Doc("""
                        Specifies the attenuation of the optical path.  The units are dB.
                        """))
        self._add_method('peak_search',
                        self._peak_search,
                        ivi.Doc("""
                        Run peak search routine.
                        """))
        self._add_method('read_power',
                        self._read_power,
                        ivi.Doc("""
                        Read output optical power.  The units are dBm.
                        """))

    def _initialize(self, resource = None, id_query = False, reset = False, **keywargs):
        "Opens an I/O session to the instrument."

        super(santecOTF930, self)._initialize(resource, id_query, reset, **keywargs)

        # interface clear
        if not self._driver_operation_simulate:
            self._clear()

        # check ID not supported (no ID command)

        # reset
        if reset:
            self.utility_reset()


    def _get_identity_instrument_manufacturer(self):
        return self._identity_instrument_manufacturer

    def _get_identity_instrument_model(self):
        return self._identity_instrument_model

    def _get_identity_instrument_firmware_revision(self):
        return self._identity_instrument_firmware_revision

    def _utility_disable(self):
        pass

    def _utility_error_query(self):
        error_code = 0
        error_message = "No error"
        if not self._driver_operation_simulate:
            pass
        return (error_code, error_message)

    def _utility_lock_object(self):
        pass

    def _utility_reset(self):
        if not self._driver_operation_simulate:
            self._write("RE")
            self._clear()
            self.driver_operation.invalidate_all_attributes()

    def _utility_reset_with_defaults(self):
        self._utility_reset()

    def _utility_self_test(self):
        code = 0
        message = "Self test passed"
        if not self._driver_operation_simulate:
            pass
        return (code, message)

    def _utility_unlock_object(self):
        pass



    def _get_wavelength(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("WA")
            self._wavelength = float(resp)/1e9
            self._set_cache_valid()
        return self._wavelength

    def _set_wavelength(self, value):
        value = round(float(value), 12)
        if not self._driver_operation_simulate:
            self._write("WA %.3f" % (value*1e9))
        self._wavelength = value
        self._set_cache_valid()

    def _get_offset(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("CW")
            self._offset = float(resp)/1e9
            self._set_cache_valid()
        return self._offset

    def _set_offset(self, value):
        value = round(float(value), 12)
        if value <= -1e-9 or value >= 1e-9:
            raise ivi.OutOfRangeException()
        if not self._driver_operation_simulate:
            self._write("CW %.3f" % (value*1e9))
        self._offset = value
        self._set_cache_valid()
        self._set_cache_valid(False, 'wavelength')

    def _get_attenuation(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("AT")
            self._attenuation = float(resp)
            self._set_cache_valid()
        return self._attenuation

    def _set_attenuation(self, value):
        value = round(float(value), 3)
        if not self._driver_operation_simulate:
            self._write("AT %.3f" % (value))
        self._attenuation = value
        self._set_cache_valid()

    def _peak_search(self):
        if not self._driver_operation_simulate:
            self._write("PS")
            while self._ask("SU")[-2] in ('1', '3'):
                time.sleep(0.5)
        self._set_cache_valid(False, 'wavelength')

    def _read_power(self):
        if not self._driver_operation_simulate:
            return float(self._ask("OP"))
        return 0.0

