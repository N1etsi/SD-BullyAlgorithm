from multiprocessing import Process, Queue
from threading  import Thread
import socket
import time

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

    KILL = -1

    
    def __init__(self, id, n_nodes) -> None:
        self.id = id
        self.n_nodes = n_nodes
        self.state = self.NORMAL
        self.leader = 0

        """ --------------------------- """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('localhost', 123*100+self.id))
        self.s.listen()
        self.q=Queue()

    def listener(self):

        while 1:
            conn, addr = self.s.accept()
            Thread(target=self.msg_reader, args=(conn,)).start()
            

    def msg_reader(self,conn):
        while True:
            msg = conn.recv(1024)
            if not msg:
                break
            self.q.put(msg.decode())


    def run(self):
        self.t = Thread(target=self.listener, args=())
        self.t.start()

        while 1:
            while not self.q.empty():
                line = self.q.get()
                line=line.split()

                from_id = int(line[0])
                msg =  int(line[1])

                if self.state == self.DOWN:
                    continue

                if msg == self.ARE_U_THERE :
                    self.msg_send(from_id, self.YES)
    

                if msg == self.YES:
                    x = 5





            self.updateMaster()
            time.sleep(1)



        



    

    def msg_send(self, to_id, msg):
        st = 0
        en = self.n_nodes

        if id != -1:   
            st = to_id
            en = to_id+1

            msg = str(self.id) + " " + str(msg)

        for node in range(st, en):
            if node != self.id:    
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 123*100+node))
                s.send(msg.encode('utf-8'))
                s.close()
    

    def updateMaster(self):
        msg = str(self.id) + " " + str(self.state) + " " + str(self.leader)

        self.msg_send(99, msg)

        
    def testNodes(self):
        
        self.t = Thread(target=self.listener, args=())
        self.t.start()

        for node in range(self.n_nodes):
            if node != self.id:    
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 123*100+node))
                s.send((str(self.id)+' ARE-YOU-THERE').encode('utf-8'))
                s.close()

        while 1:
            if not self.q.empty():
                line=self.q.get()
                line=line.split()
                print("TestNodes -Node " + str(self.id) + " from= "+line[0]+" msg= "+line[1])
                