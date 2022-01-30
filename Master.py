from multiprocessing import Process, Queue
from pickle import FALSE
from threading  import Thread, Lock
import socket
import time
import keyboard
import os
import msvcrt

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
    RND_ST = -3
    TERMINATE = -10



    def __init__(self, n_nodes, id=999, debug = ""):
        self.id = id
        self.n_nodes = n_nodes
        self.leaders = {}
        self.states = {}
        self.msg_tx = 0
        self.msg_rx = 0
        self.n_elec = {}
        self.time_meas = 0
        self.debug = debug
        self.rnd = False
                

        """ --------------------------- """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('localhost', 123*100+self.id))
        self.s.listen()

    def run(self):
        self.t = Thread(target=self.listener, args=())
        self.t.start()

        

        while(1):
           # print("//////////////////////////////////////////\n")
            if self.debug == "":
                clearConsole()
                for node in self.leaders:
                    match int(self.states[node]):
                        case self.DOWN:
                            st = "DOWN    "
                        case self.NORMAL:
                            st = "NORMAL  "
                        case self.ELECTION:
                            st = "ELECTION"
                        case _:
                            st = "UNKNOWN"

                    print("id: " + node + " |  state: " + st + " |  leader: " + self.leaders[node])   
                
                if msvcrt.kbhit():
                    ch = msvcrt.getch()
                    print(ch)
                    if ch == b'r':
                        self.msg_send(-1, self.RND_ST)
                        
                        sta = "ON"
                        if self.rnd:
                            sta = "OFF"

                        print("RANDOM STATE is", sta)
                        self.rnd = not self.rnd
                        
                    else:
                        try:
                            nnn = int(ch)
                            self.msg_send(nnn, self.KILL)
                        except:
                            print("wrong usage, only numbers from 0-9 and 'r' for changing random state")


                    
    

                time.sleep(2)
            elif len(self.leaders) == self.n_nodes-1:
                self.msg_send(-1, self.TERMINATE)
                print("MSG_RX:", self.msg_rx/self.n_nodes, "\nMSG_TX:", self.msg_tx/self.n_nodes, "\nMSG_TIM:", self.time_meas/self.n_nodes)
                break

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

                if self.debug != "":
                    self.n_elec[msg[0]] = msg[5]

                    self.msg_tx += int(msg[3])
                    self.msg_rx += int(msg[4])
                    self.time_meas += float(msg[6])
                
            
    def msg_send(self, id, msg):
        st = 0
        en = self.n_nodes

        msg = str(self.id) + " " + str(msg)

        if id != -1:   
            st = id
            en = id+1

        for node in range(st, en):
            if node != self.id:    
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 123*100+node))
                s.send(msg.encode('utf-8'))
                s.close()
    
   
def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)