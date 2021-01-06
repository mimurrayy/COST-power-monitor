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

# Oscilloscopes
# DS1000Z
from .rigolDS1054Z import rigolDS1054Z
from .rigolDS1074Z import rigolDS1074Z
from .rigolDS1104Z import rigolDS1104Z
from .rigolMSO1074Z import rigolMSO1074Z
from .rigolMSO1104Z import rigolMSO1104Z
# DS2000A
from .rigolDS2072A import rigolDS2072A
from .rigolDS2102A import rigolDS2102A
from .rigolDS2202A import rigolDS2202A
from .rigolDS2302A import rigolDS2302A
from .rigolMSO2072A import rigolMSO2072A
from .rigolMSO2102A import rigolMSO2102A
from .rigolMSO2202A import rigolMSO2202A
from .rigolMSO2302A import rigolMSO2302A
# DS4000
from .rigolDS4012 import rigolDS4012
from .rigolDS4014 import rigolDS4014
from .rigolDS4022 import rigolDS4022
from .rigolDS4024 import rigolDS4024
from .rigolDS4032 import rigolDS4032
from .rigolDS4034 import rigolDS4034
from .rigolDS4052 import rigolDS4052
from .rigolDS4054 import rigolDS4054
from .rigolMSO4012 import rigolMSO4012
from .rigolMSO4014 import rigolMSO4014
from .rigolMSO4022 import rigolMSO4022
from .rigolMSO4024 import rigolMSO4024
from .rigolMSO4032 import rigolMSO4032
from .rigolMSO4034 import rigolMSO4034
from .rigolMSO4052 import rigolMSO4052
from .rigolMSO4054 import rigolMSO4054

# DC Power Supplies
# DP800
from .rigolDP831A import rigolDP831A
from .rigolDP832 import rigolDP832
from .rigolDP832A import rigolDP832A
# DP1000
from .rigolDP1116A import rigolDP1116A
from .rigolDP1308A import rigolDP1308A

# Digital Multimeters
#DM3068
from .rigolDM3068Agilent import rigolDM3068Agilent
