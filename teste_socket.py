from multiprocessing import Process, Queue
from threading  import Thread
import socket
class Node():
    #States
    NORMAL = 1
    DOWN = -1
    ELECTION = 2

    #Messages
    ARE_U_THERE = 101
    YES = 102
    HALT = 103
    NEW_LEADER = 104


    def __init__(self, id, n_nodes) -> None:
        self.id = id
        self.n_nodes = n_nodes
        self.state = self.NORMAL
        self.leader = 0

        """ --------------------------- """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('localhost', 1234*10+self.id))
        self.s.listen()
        self.q=Queue()

    def listener(self):

        while 1:
            conn, addr = self.s.accept()
            Thread(target=self.msg_reader, args=(conn,addr,)).start()
            

    def msg_reader(self,conn,addr):
        print('conn=',conn,' addr=',addr)
        while True:
            msg = conn.recv(1024)
            if not msg:
                break
            print(msg.decode())
            self.q.put(msg.decode())

        #conn.send(data)  # simple ping
        
    

        
    def testNodes(self):
        #Send messages
        
        self.t = Thread(target=self.listener, args=())
        self.t.start()

        for node in range(self.n_nodes):
            if node != self.id:    
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 1234*10+node))
                s.send((str(self.id)+' ARE-YOU-THERE').encode('utf-8'))
                s.close()

        while 1:
            if not self.q.empty():
                line=self.q.get()
                line=line.split()
                #print(line)
                print("TestNodes -Node " + str(self.id) + " from= "+line[0]+" msg= "+line[1])
                