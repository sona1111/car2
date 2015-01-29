from car_pb2 import Info
from car_pb2 import Command
import car_pb2
import socket

UDP_PORT_INCOMING = 7778
UDP_PORT_OUTGOING = 7777
REMOTE_ADDRESS = 'localhost'
SUPPORTED_PROTO_INFO = ['lsens','rsens','fsens','bsens'] #the info supported in the info protocol

class UDPClient(object):

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.info = Info()
        self.cmd = Command()
        self.network_direct = False
        self.connect()
        
    def send(self)
        self.socket.sendto(self.cmd.SerializeToString(), (REMOTE_ADDRESS,UDP_PORT_OUTGOING))
        
    def connect(self):
        
        self.cmd.name = "SIG_DIRECT_ENABLE"
        self.send()
        
    def disconnect(self):
    
        self.cmd.name = "SIG_DIRECT_DISABLE"
        self.send()
        self.socket.close()
        
    def sendCommand(self, command):
        self.cmd.name = command['name']
        if 'value' in command:
            self.cmd.value = command['value']
        self.send()







