# venus-epsolar
Victron Venus GX Epsolar Tracker driver

This driver is based on velib_python systemcalc library dummysolarcharger example

Modbus commands have been sniffed from original EPsolar software.

All you need is working RS458 (or RS232 in my model case) connection like ttyUSB0

Unfortunalelly, original, Exar based RS485 USB Cable supplied with EPsolar charger is not working  with Venus GX 

Installing:
After succcesfull installation of RS485 dongle, you should ensure free communication for your ttyUSB0 port:

your ps | grep ttyUSB0 command result should look like this:

root@beaglebone: ps | grep ttyUSB0

1948 root      2244 S    grep ttyUSB0

root@beaglebone:


In my case, I had to eliminate disturbing gps service by deleting the line in /etc/venus/serial-starter.conf


Now you can test the driver starting it from command line:

nohup  /opt/victronenergy/epsolar/dbus_epsolar.py


Enjoy!






