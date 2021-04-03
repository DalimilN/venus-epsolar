#!/usr/bin/env python

import gobject
import platform
import argparse
import logging
import sys
import os
import time # Library to use delays
import serial
from datetime import datetime
from logger import setup_logging

#logging
logger = setup_logging(debug=True)

# our own packages
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../ext/velib_python'))
from vedbus import VeDbusService

class DbusDummyService:
    def __init__(self, servicename, deviceinstance, paths, productname='SolarCharger EPSolar', connection='ttyUSB0'):
        self._dbusservice = VeDbusService(servicename)
        self._paths = paths

        # Create the management objects, as specified in the ccgx dbus-api document
        self._dbusservice.add_path('/Mgmt/ProcessName', __file__)
        self._dbusservice.add_path('/Mgmt/ProcessVersion', 'Version 1.0, and running on Python ' + platform.python_version())
        self._dbusservice.add_path('/Mgmt/Connection', connection)

        # Create the mandatory objects
        self._dbusservice.add_path('/DeviceInstance', deviceinstance)
        self._dbusservice.add_path('/ProductId', 0)
        self._dbusservice.add_path('/ProductName', productname)
        self._dbusservice.add_path('/FirmwareVersion', 11.1)
        self._dbusservice.add_path('/HardwareVersion', 2)
        self._dbusservice.add_path('/Connected', 1)
        self._dbusservice.add_path('/Dc/0/Voltage', 0)
	self._dbusservice.add_path('/Dc/0/Current', 0)        
        self._dbusservice.add_path('/Pv/V', 0)
        self._dbusservice.add_path('/Pv/I', 0)
        self._dbusservice.add_path('/Yield/System', 0)
        self._dbusservice.add_path('/Yield/User', 0)
        self._dbusservice.add_path('/Yield/Power', 0)
        self._dbusservice.add_path('/State', 3)
        self._dbusservice.add_path('/ErrorCode', 0)
        self._dbusservice.add_path('/History/Daily/0/Yield', 0)
        self._dbusservice.add_path('/History/Daily/0/MaxPower', 0)
        self._dbusservice.add_path('/History/Daily/1/Yield', 0)
        self._dbusservice.add_path('/History/Daily/1/MaxPower', 0)


        for path, settings in self._paths.iteritems():
            self._dbusservice.add_path(
                path, settings['initial'], writeable=True)
        

        global ser
        ser = serial.Serial()
        ser.port = "/dev/ttyUSB0"
        ser.baudrate = 115200
        ser.bytesize = serial.EIGHTBITS #number of bits per bytes
        ser.parity = serial.PARITY_NONE #set parity check: no parity
        ser.stopbits = serial.STOPBITS_ONE #number of stop bits
        ser.timeout = 0.1            #non-block read
        ser.xonxoff = False     #disable software flow control
        ser.rtscts = False     #disable hardware (RTS/CTS) flow control
        ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
        ser.writeTimeout = 0.1    #timeout for write

        global table
        table = (
        0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
        0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
        0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
        0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
        0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
        0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
        0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
        0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
        0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
        0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
        0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
        0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
        0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
        0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
        0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
        0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
        0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
        0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
        0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
        0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
        0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
        0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
        0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
        0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
        0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
        0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
        0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
        0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
        0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
        0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
        0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
        0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040 )
        
        gobject.timeout_add(500, self._update)

    def calcCRC(self, st ):
            #logging.info("C:"+st)
            st = st.decode("hex")
            crc = 0xFFFF
            """Given a bunary string and starting CRC, Calc a final CRC-16 """
            for ch in st:
                crc = (crc >> 8) ^ table[(crc ^ ord(ch)) & 0xFF]
            return crc

    def _update(self):

        try:
         if not ser.isOpen():
           ser.open()
        except:
           sys.exit("Port not open")

        try:
          ser.flushInput()  #flush input buffer, discarding all its content
          ser.flushOutput() #flush output buffer, aborting current output
        except:
          sys.exit("Port removed")

        try:

             #initial Status

             #read Pv Bat Power
             ser.write("01433100001B0AF2".decode("hex"))
             response = str(ser.readline().encode('hex'))
             logger.info("RessponsePV:"+response)
             if len(response) >= 40:
              #CRC Check
              #logger.info("Code:"+response[-2:]+response[-4:-2])
              #logger.info("Calc:"+str(hex(self.calcCRC(response[:-4]))))
              if int((response[-2:]+response[-4:-2]),16) == self.calcCRC( response[:-4]):
               PvU =  float(int( response[14:18],16))/100
               PvI =  float(int( response[18:22],16))/100
               BatU = float(int( response[30:34],16))/100
               BatI = float(int( response[34:38],16))/100
               self._dbusservice['/Dc/0/Voltage'] =  BatU
               self._dbusservice['/Dc/0/Current'] =  BatI
               self._dbusservice['/Pv/V'] =  PvU
               self._dbusservice['/Pv/I'] =  PvI
               self._dbusservice['/Yield/Power'] = int( PvI*PvU)
               if (PvU < 40):
                 self._dbusservice['/State'] = 0
               if ((PvI > 1) and (self._dbusservice['/State'] < 5)):
                 self._dbusservice['/State'] = 3
               if (BatU > 56):
                self._dbusservice['/State'] = 5
               else:
                if (BatI > 1):
                 self._dbusservice['/State'] = 3
               logger.info("PV:"+str(PvU)+"V "+str(PvI)+"A")
               logger.info("Bat:"+str(BatU)+"V "+str(BatI)+"A") 
             else:
               logger.info("PV CRC Error:"+response )
               logger.info("Code:"+response[-2:]+response[-4:-2])
               logger.info("Calc:"+str( hex(self.calcCRC( response[:-4]))))               


             #read Total
             response = str(ser.readline().encode('hex'))
             ser.write("010433020012DE83".decode("hex"))
             response = str(ser.readline().encode('hex'))
             logger.info("ResponseTot:"+response)
             if len(response) >= 40:
              if int((response[-2:]+response[-4:-2]),16) == self.calcCRC(response[:-4]):
               Day = float(int(response[50:54]+response[46:50],16))/100
               Monat = float(int(response[58:62]+response[54:58],16))/100
               Year = float(int(response[66:70]+response[62:66],16))/100
               Tot = float(int(response[74:78]+response[70:74],16))/100             
               self._dbusservice['/History/Daily/0/Yield'] =  Day
               self._dbusservice['/History/Daily/1/Yield'] =  Year
               self._dbusservice['/Yield/User'] =  Monat
               self._dbusservice['/Yield/System'] =  Tot
               logger.info("Day:"+str(Day)+"kWh ")
               logger.info("Mon:"+str(Monat)+"kWh ")
               logger.info("Year:"+str(Year)+"kWh ")
               logger.info("Tot:"+str(Tot)+"kWh ")
              else:
               logger.info("Tot CRC Error:"+response )
               logger.info("Code:"+response[-2:]+response[-4:-2])
               logger.info("Calc:"+str( hex(self.calcCRC( response[:-4]))))


        except:
           logger.info("Serial Error")

        gobject.timeout_add(300, self._update) 
        
    



     
if __name__ == "__main__":



    from dbus.mainloop.glib import DBusGMainLoop
    # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
    DBusGMainLoop(set_as_default=True)

    pvac_output = DbusDummyService(
        servicename='com.victronenergy.solarcharger.ttyO1',
        deviceinstance=0,
        paths={
            '/Position': {'initial': 0, 'update': 0},
            '/DbusInvalid': {'initial': None} })
    logger.info('Connected to dbus, gobject.MainLoop() (= event based)')
    mainloop = gobject.MainLoop()
    mainloop.run()

             
