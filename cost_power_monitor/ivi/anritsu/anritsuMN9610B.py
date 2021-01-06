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

from .. import ivi

class anritsuMN9610B(ivi.Driver):
    "Anritsu MN9610B series optical attenuator driver"
    
    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', '')
        
        super(anritsuMN9610B, self).__init__(*args, **kwargs)
        
        self._identity_description = "Anritsu MN9610B series optical attenuator driver"
        self._identity_identifier = ""
        self._identity_revision = ""
        self._identity_vendor = ""
        self._identity_instrument_manufacturer = "Anritsu"
        self._identity_instrument_model = "MN9610B"
        self._identity_instrument_firmware_revision = ""
        self._identity_specification_major_version = 0
        self._identity_specification_minor_version = 0
        self._identity_supported_instrument_models = ['MN9610B']
        
        self._attenuation = 0.0
        self._reference = 0.0
        self._wavelength = 1300.0
        self._disable = False

        self._add_property('attenuation',
                        self._get_attenuation,
                        self._set_attenuation,
                        None,
                        ivi.Doc("""
                        Specifies the attenuation of the optical path.  The units are dB.
                        """))
        self._add_property('reference',
                        self._get_reference,
                        self._set_reference,
                        None,
                        ivi.Doc("""
                        Specifies the zero dB reference level for the attenuation setting. The
                        units are dB.
                        """))
        self._add_property('wavelength',
                        self._get_wavelength,
                        self._set_wavelength,
                        None,
                        ivi.Doc("""
                        Specifies the wavelength of light used for accurate attenuation.  The
                        units are meters.
                        """))
        self._add_property('disable',
                        self._get_disable,
                        self._set_disable,
                        None,
                        ivi.Doc("""
                        Controls a shutter in the optical path.  Shutter is closed when disable is
                        set to True.
                        """))

    def _initialize(self, resource = None, id_query = False, reset = False, **keywargs):
        "Opens an I/O session to the instrument."

        super(anritsuMN9610B, self)._initialize(resource, id_query, reset, **keywargs)

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
            error_code = int(self._ask("ERR?").split(' ')[1])
            error_message = ["No error", "Command error", "Execution error", "Command and execution error"][error_code]
        return (error_code, error_message)

    def _utility_lock_object(self):
        pass

    def _utility_reset(self):
        pass

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



    def _get_attenuation(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("ATT?").split(' ')[1]
            self._attenuation = float(resp)
            self._set_cache_valid()
        return self._attenuation

    def _set_attenuation(self, value):
        value = round(float(value), 2)
        if value < -99.99 or value > 159.99:
            raise ivi.OutOfRangeException()
        if not self._driver_operation_simulate:
            self._write("ATT %.2f" % (value))
        self._attenuation = value
        self._set_cache_valid()

    def _get_reference(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("OFS?").split(' ')[1]
            self._reference = float(resp)
            self._set_cache_valid()
        return self._reference

    def _set_reference(self, value):
        value = round(float(value), 2)
        if value < -99.99 or value > 99.99:
            raise ivi.OutOfRangeException()
        if not self._driver_operation_simulate:
            self._write("OFS %.2f" % (value))
        self._reference = value
        self._set_cache_valid()
        self._set_cache_valid(False, 'attenuation')

    def _get_wavelength(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("WVL?").split(' ')[1]
            self._wavelength = float(resp)
            self._set_cache_valid()
        return self._wavelength

    def _set_wavelength(self, value):
        value = round(float(value), 9)
        if value < -1100e-9 or value > 1650e-9:
            raise ivi.OutOfRangeException()
        if not self._driver_operation_simulate:
            self._write("WVL %de-9" % (int(value*1e9)))
        self._wavelength = value
        self._set_cache_valid()

    def _get_disable(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("D?").split(' ')[1]
            self._disable = bool(int(resp))
            self._set_cache_valid()
        return self._disable

    def _set_disable(self, value):
        value = bool(value)
        if not self._driver_operation_simulate:
            self._write("D %d" % (int(value)))
        self._disable = value
        self._set_cache_valid()

