"""

Python Interchangeable Virtual Instrument Library

Copyright (c) 2012-2017 Alex Forencich

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
# DPO4000
from .tektronixDPO4032 import tektronixDPO4032
from .tektronixDPO4034 import tektronixDPO4034
from .tektronixDPO4054 import tektronixDPO4054
from .tektronixDPO4104 import tektronixDPO4104
# MSO4000
from .tektronixMSO4032 import tektronixMSO4032
from .tektronixMSO4034 import tektronixMSO4034
from .tektronixMSO4054 import tektronixMSO4054
from .tektronixMSO4104 import tektronixMSO4104
# DPO4000B
from .tektronixDPO4014B import tektronixDPO4014B
from .tektronixDPO4034B import tektronixDPO4034B
from .tektronixDPO4054B import tektronixDPO4054B
from .tektronixDPO4102B import tektronixDPO4102B
from .tektronixDPO4104B import tektronixDPO4104B
# MSO4000B
from .tektronixMSO4014B import tektronixMSO4014B
from .tektronixMSO4034B import tektronixMSO4034B
from .tektronixMSO4054B import tektronixMSO4054B
from .tektronixMSO4102B import tektronixMSO4102B
from .tektronixMSO4104B import tektronixMSO4104B
# MDO4000
from .tektronixMDO4054 import tektronixMDO4054
from .tektronixMDO4104 import tektronixMDO4104
# MDO4000B
from .tektronixMDO4014B import tektronixMDO4014B
from .tektronixMDO4034B import tektronixMDO4034B
from .tektronixMDO4054B import tektronixMDO4054B
from .tektronixMDO4104B import tektronixMDO4104B
# MDO3000
from .tektronixMDO3012 import tektronixMDO3012
from .tektronixMDO3014 import tektronixMDO3014
from .tektronixMDO3022 import tektronixMDO3022
from .tektronixMDO3024 import tektronixMDO3024
from .tektronixMDO3032 import tektronixMDO3032
from .tektronixMDO3034 import tektronixMDO3034
from .tektronixMDO3052 import tektronixMDO3052
from .tektronixMDO3054 import tektronixMDO3054
from .tektronixMDO3102 import tektronixMDO3102
from .tektronixMDO3104 import tektronixMDO3104
# DPO5000
from .tektronixDPO5034 import tektronixDPO5034
from .tektronixDPO5054 import tektronixDPO5054
from .tektronixDPO5104 import tektronixDPO5104
from .tektronixDPO5204 import tektronixDPO5204
# DPO5000B
from .tektronixDPO5034B import tektronixDPO5034B
from .tektronixDPO5054B import tektronixDPO5054B
from .tektronixDPO5104B import tektronixDPO5104B
from .tektronixDPO5204B import tektronixDPO5204B
# MSO5000
from .tektronixMSO5034 import tektronixMSO5034
from .tektronixMSO5054 import tektronixMSO5054
from .tektronixMSO5104 import tektronixMSO5104
from .tektronixMSO5204 import tektronixMSO5204
# MSO5000B
from .tektronixMSO5034B import tektronixMSO5034B
from .tektronixMSO5054B import tektronixMSO5054B
from .tektronixMSO5104B import tektronixMSO5104B
from .tektronixMSO5204B import tektronixMSO5204B
# DPO7000
from .tektronixDPO7054 import tektronixDPO7054
from .tektronixDPO7104 import tektronixDPO7104
from .tektronixDPO7254 import tektronixDPO7254
# DPO7000C
from .tektronixDPO7054C import tektronixDPO7054C
from .tektronixDPO7104C import tektronixDPO7104C
from .tektronixDPO7254C import tektronixDPO7254C
from .tektronixDPO7354C import tektronixDPO7354C
# DPO70000
from .tektronixDPO70404 import tektronixDPO70404
from .tektronixDPO70604 import tektronixDPO70604
from .tektronixDPO70804 import tektronixDPO70804
from .tektronixDPO71254 import tektronixDPO71254
from .tektronixDPO71604 import tektronixDPO71604
from .tektronixDPO72004 import tektronixDPO72004
# DPO70000B
from .tektronixDPO70404B import tektronixDPO70404B
from .tektronixDPO70604B import tektronixDPO70604B
from .tektronixDPO70804B import tektronixDPO70804B
from .tektronixDPO71254B import tektronixDPO71254B
from .tektronixDPO71604B import tektronixDPO71604B
from .tektronixDPO72004B import tektronixDPO72004B
# DPO70000C
from .tektronixDPO70404C import tektronixDPO70404C
from .tektronixDPO70604C import tektronixDPO70604C
from .tektronixDPO70804C import tektronixDPO70804C
from .tektronixDPO71254C import tektronixDPO71254C
from .tektronixDPO71604C import tektronixDPO71604C
from .tektronixDPO72004C import tektronixDPO72004C
# DPO70000DX
from .tektronixDPO72304DX import tektronixDPO72304DX
from .tektronixDPO72504DX import tektronixDPO72504DX
from .tektronixDPO73304DX import tektronixDPO73304DX
# MSO70000
from .tektronixMSO70404 import tektronixMSO70404
from .tektronixMSO70604 import tektronixMSO70604
from .tektronixMSO70804 import tektronixMSO70804
from .tektronixMSO71254 import tektronixMSO71254
from .tektronixMSO71604 import tektronixMSO71604
from .tektronixMSO72004 import tektronixMSO72004
# MSO70000C
from .tektronixMSO70404C import tektronixMSO70404C
from .tektronixMSO70604C import tektronixMSO70604C
from .tektronixMSO70804C import tektronixMSO70804C
from .tektronixMSO71254C import tektronixMSO71254C
from .tektronixMSO71604C import tektronixMSO71604C
from .tektronixMSO72004C import tektronixMSO72004C
# MSO70000DX
from .tektronixMSO72304DX import tektronixMSO72304DX
from .tektronixMSO72504DX import tektronixMSO72504DX
from .tektronixMSO73304DX import tektronixMSO73304DX

# Function Generators
from .tektronixAWG2005 import tektronixAWG2005
from .tektronixAWG2020 import tektronixAWG2020
from .tektronixAWG2021 import tektronixAWG2021
from .tektronixAWG2040 import tektronixAWG2040
from .tektronixAWG2041 import tektronixAWG2041

# Power Supplies
from .tektronixPS2520G import tektronixPS2520G
from .tektronixPS2521G import tektronixPS2521G

# Optical attenuators
from .tektronixOA5002 import tektronixOA5002
from .tektronixOA5012 import tektronixOA5012
from .tektronixOA5022 import tektronixOA5022
from .tektronixOA5032 import tektronixOA5032

# Current probe amplifiers
from .tektronixAM5030 import tektronixAM5030
