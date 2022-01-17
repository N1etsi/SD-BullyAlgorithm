from multiprocessing import Process, Queue
from threading  import Thread, Lock
import socket
import time
import keyboard

from itsdangerous import exc

data_lock = Lock()

class Master():
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



    def __init__(self, n_nodes, id=99):
        self.id = id
        self.n_nodes = n_nodes
        self.leaders = {}
        self.states = {}
                

        """ --------------------------- """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('localhost', 123*100+self.id))
        self.s.listen()

    def run(self):
        self.t = Thread(target=self.listener, args=())
        self.t.start()

        

        while(1):
           # print("//////////////////////////////////////////\n")
            for node in self.leaders:
                print("id: " + node + " |  state: " + self.states[node] + " |  leaders: " + self.leaders[node])    
                
            

            ch = keyboard.read_key()
            print(ch)
            try:
                if int(ch) >= 0 and int(ch) < 10:
                    id = int(ch)
                    self.msg_send(id, self.KILL)
                    print("sent kill to " + str(id))
            except:
                pass


            time.sleep(1)


    def listener(self):

        while 1:
            conn, addr = self.s.accept()
            Thread(target=self.msg_reader, args=(conn,)).start()
            

    def msg_reader(self,conn):
        while True:
            msg = conn.recv(1024).decode()
            if not msg:
                break
            msg = msg.split()
            with data_lock:
                self.states[msg[0]] = msg[1]
                self.leaders[msg[0]] = msg[2]
            
    def msg_send(self, id, msg):
        st = 0
        en = self.n_nodes

        msg = "99 " + str(msg)

        if id != -1:   
            st = id
            en = id+1

        for node in range(st, en):
            if node != self.id:    
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 123*100+node))
                s.send(msg.encode('utf-8'))
                s.close()
    
   