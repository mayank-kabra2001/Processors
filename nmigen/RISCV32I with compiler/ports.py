import serial
import time
from serial import Serial

ComPort = serial.Serial("/dev/ttyACM0")
ComPort.baudrate = 9600
ComPort.bytesize =8
ComPort.parity = 'N'
ComPort.stopbits =1
x=input()
print("enter Ra")
ot = ComPort.write(bytes(chr(int(x))))
x=input()
print("enter Rb")
ot = ComPort.write(bytes(chr(x)))

it = ComPort.read(1)
print("data:")
print(it.encode('hex'))
ComPort.close()