from multiprocessing import Process, Queue
from pickle import FALSE
from threading  import Thread
import socket
from time import *


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

    #Management Messages
    KILL = -1
    WAKE = -2

    
    def __init__(self, id, n_nodes) -> None:
        self.id = id
        self.n_nodes = n_nodes
        self.state = self.NORMAL
        self.leader = 0
        self.T = 1
        self.last_leader_update = time()
        self.timeout = 2 * self.T

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

        check_leader = 0
        check_leader_time = 0
        check_peer_time = 0
        check_halt_time = 0


        while 1:
            new_message = False
            if not self.q.empty():
                new_message = True
                line = self.q.get()
                line=line.split()

                from_id = int(line[0])
                msg =  int(line[1])

                if from_id == 99:
                    if msg == self.KILL:
                        self.state = self.DOWN
                    elif msg == self.WAKE:
                        self.state = self.ELECTION


            if self.state == self.DOWN:
                continue
            
            #READ MESSAGES
            if new_message:
                if from_id == self.leader:
                    self.last_leader_update = time()

                if msg == self.ARE_U_THERE:
                    #print(str(self.id) + " RX ARE-U-THERE from " + str(from_id))
                    self.msg_send(from_id, self.YES)

                    if from_id < self.id:
                        check_leader = 0

                elif msg == self.HALT:
                    self.state = self.ELECTION
                    check_leader = 0

                elif msg == self.NEW_LEADER:
                    self.leader = from_id
                    self.state = self.NORMAL
                    self.last_leader_update = time()

                elif msg == self.YES:
                    #print(str(self.id) + " RX YES from " + str(from_id))
                    if check_leader == 1 and from_id == self.leader:
                        check_leader = 0
                        self.last_leader_update = time()

                    if check_leader == 2 and from_id < self.id:
                        check_leader = 0

            #TAKE ACTION

            #Running for election
            if self.state == self.NORMAL and self.leader != self.id:
                if time()-self.last_leader_update > self.timeout and check_leader == 0: #Start election proccess
                    #SEND ARE U THERE to LEADER
                    #print(str(self.id) + " SENT CHECK LEADER to " + str(self.leader))
                    self.msg_send(self.leader, self.ARE_U_THERE)
                    check_leader = 1
                    check_leader_time = time()


                elif time()-check_leader_time > self.timeout and check_leader == 1:
                    for n in range(self.id):
                        self.msg_send(n, self.ARE_U_THERE)

                    check_leader = 2
                    check_peer_time = time()

                elif time()-check_peer_time > self.timeout and check_leader == 2:
                    for n in range(self.id, self.n_nodes):
                        self.msg_send(n, self.HALT)

                    self.state = self.ELECTION
                    check_leader = 3
                    check_halt_time = time()


            #Asserting as leader
            elif self.state == self.ELECTION:
                if time()-check_halt_time > self.T and check_leader == 3:
                    for n in range(self.id, self.n_nodes):
                        self.msg_send(n, self.NEW_LEADER)
                    
                    self.leader = self.id
                    self.state = self.NORMAL












            self.updateMaster()
            



        



    

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
                while 1:
                    try:
                        s.connect(('localhost', 123*100+node))
                        break
                    except:
                        pass
                s.send(msg.encode('utf-8'))
                s.close()
    

    def updateMaster(self):
        msg = str(self.state) + " " + str(self.leader)

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
                