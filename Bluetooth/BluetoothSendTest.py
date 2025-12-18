import bluetooth

# def receiveMessages():
#   server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
  
#   port = 1
#   server_sock.bind(("",port))
#   server_sock.listen(1)
  
#   client_sock,address = server_sock.accept()
#   print "Accepted connection from " + str(address)
  
#   data = client_sock.recv(1024)
#   print "received [%s]" % data
  
#   client_sock.close()
#   server_sock.close()
  
# def sendMessageTo(targetBluetoothMacAddress):
#   print(targetBluetoothMacAddress)
#   port = 1
#   sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
#   sock.connect((targetBluetoothMacAddress, port))
#   sock.send("hello!!")
#   sock.close()
  
# def lookUpNearbyBluetoothDevices():
#   nearby_devices = bluetooth.discover_devices()
#   return nearby_devices[3]    
    
# sendMessageTo(lookUpNearbyBluetoothDevices())
import serial

ser = serial.Serial("COM7", 115200)
ser.write(b"hello from tablet\n")
ser.close()