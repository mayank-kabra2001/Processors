import serial           # import the module
import time
ComPort = serial.Serial('/dev/ttyUSB1') # open COM24
ComPort.baudrate = 115200 # set Baud rate to 9600
ComPort.bytesize = 8    # Number of data bits = 8
ComPort.parity   = 'N'  # No parity
ComPort.stopbits = 1    # Number of Stop bits = 1
# Write character 'A' to serial port
#data=bytearray(b'A')
print ("enter a number for data1 in range(0-255):"),
x=input()

ot= ComPort.write(bytes(chr(int(x)) ,  encoding='utf8'))    #for sending data to FPGA

print ("enter a number for data2 in range(0-255):"),
x=input()

ot= ComPort.write(bytes(chr(int(x)) ,  encoding='utf8'))    #for sending data to FPGA


it=(ComPort.read(1))                #for receiving data from FPGA

print ("data received from FPGA (data1+data2):"),
print (it.hex())
    

ComPort.close()         # Close the Com port
