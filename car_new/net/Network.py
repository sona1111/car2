from car_pb2 import Info, Command
import socket
import time
from threading import Thread
import psutil
import logging



UDP_PORT_INCOMING = 7777
UDP_PORT_OUTGOING = 7778
REMOTE_ADDRESS = '192.168.2.20'
SUPPORTED_PROTO_INFO = ['grid','lsens','rsens','fsens','bsens','bpress','temp','cpu'] #the info supported in the info protocol

	
class NetworkCommandListner(object):

    def __init__(self, hardware, gridmap=None):
        
        self.logr = logging.getLogger('car.network')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	
        self.csocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', UDP_PORT_INCOMING))
        self.logr.info("UDP Server Operational, waiting for connections incoming on port %d, outgoing on port %d" % (UDP_PORT_INCOMING, UDP_PORT_OUTGOING))
        self.info = Info()
        self.cmd = Command()        
        self.grid = gridmap
        self.network_direct = False
        self.running = True
        self.hw = hardware
        self.net_th = Thread(target = self.listen_th)
        self.net_th.setDaemon(True)
        self.net_th.start()
        self.sendInfothread = Thread(target=self.sendInfo_th)
        self.sendInfothread.setDaemon(True)
        self.sendInfothread.start()
        
        
    def hasRequest(self):
        if self.network_direct == True:
            return True
        else:
            return False
        
    def run_direct(self):
        if self.network_direct == False:
            self.logr.warning("network command received but network direct currently disabled")
        else:
            self.logr.info("network command received, %s ; executing..." % (self.cmd.name))
            if self.cmd.name == 'stop':
                self.hw['mainEngine'].move(0)
            elif self.cmd.name == 'go':
                self.hw['mainEngine'].move(self.cmd.value)
            elif self.cmd.name == 'turn':                
                if int(self.cmd.value) == 0:
                    self.hw['wheel'].turn('center')
                elif int(self.cmd.value) == -100:
                    self.hw['wheel'].turn('left')
                elif int(self.cmd.value) == 100:
                    self.hw['wheel'].turn('right')
        
    def sendInfo_th(self):
    
        while True:
            info = {'bsens':self.hw['bsens'].getReading(),
                    'fsens':self.hw['fsens'].getReading(),
                    'lsens':self.hw['lsens'].getReading(),
                    'rsens':self.hw['rsens'].getReading(),
                    'bpress':self.hw['tempsens'].read_pressure(),
                    'temp':self.hw['tempsens'].read_temperature(),
                    'cpu':psutil.cpu_percent()
                    }            
            
            if self.grid != None:
                info['grid'] = str((self.grid.prox())).replace('array','').strip()
            self.sendInfo(info)
            
            time.sleep(1)
    
    def sendInfo(self, info):
        
        nSuccess = 0
        for name in info:
            if name in SUPPORTED_PROTO_INFO:
                setattr(self.info, name, info[name])
                nSuccess += 1
        if nSuccess > 0:
            self.send(self.info.SerializeToString())

        
    def send(self, data):
        self.csocket.sendto(data, (REMOTE_ADDRESS, UDP_PORT_OUTGOING))
        
    def listen_th(self):
    
        while self.running == True:
        
            dataFromClient, address = self.socket.recvfrom(60000) # blocks until packet received
            self.cmd.ParseFromString(dataFromClient)
            if self.cmd.name == "SIG_DIRECT_ENABLE":
                self.network_direct = True
                self.logr.info("Direct network-to-hardware enabled")
            elif self.cmd.name == "SIG_DIRECT_DISABLE":
                self.network_direct = False
                self.logr.info("Direct network-to-hardware disabled")
            else:
                self.run_direct()
	
if __name__ == "__main__":

    test = NetworkCommandListner(None)
    test.sendInfo({'bsens':0.432,'fsens':4.432,'rsens':93.432,'lsens':41293.432})
    time.sleep(700)
