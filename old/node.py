from multiprocessing import Process, Queue
from pickle import FALSE
from threading  import Thread, Lock
import socket
from time import *
from random import random

data_lock = Lock()


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

    #Application Messages
    ECHO = 201
    REPLY = 202

    #Management Messages
    KILL = -1
    WAKE = -2

    
    def __init__(self, id, n_nodes, msg_dl, flr_rate, debug) -> None:
        print("initing " + str(id))
        self.id = id
        self.n_nodes = n_nodes
        self.state = self.NORMAL
        self.leader = -1
        self.tempLeader = 98
        self.T = 1
        self.last_leader_update = time()
        self.timeout = 2 * self.T
        self.wakeTime = 0
        self.message_delay = msg_dl #TODO
        self.message_failure_rate = flr_rate

        """ --------------------------- """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('localhost', 123*100+self.id))
        self.s.listen()
        self.q=Queue()

        #stats
        self.debug = debug
        self.n_messages_sent = 0
        self.n_messages_received = 0
        self.measured_time = time()

        self.n_elections = 0

        match debug:
            case "INITIAL":
                pass

            case "LEADER_FAILURE":
                self.leader = 0
                if self.id == 0:
                    self.state = self.DOWN
                

            case "REVIVAL":
                self.leader = 1
                if self.id == 0:
                    self.leader = -1

            case _:
                pass



    def listener(self):

        while 1:
            conn, addr = self.s.accept()
            Thread(target=self.msg_reader, args=(conn,)).start()
            

    def msg_reader(self,conn):
        while True:
            msg = conn.recv(1024)
            if not msg:
                break
            with data_lock:
                self.q.put(msg.decode())



    def run(self):
        self.t = Thread(target=self.listener, args=())
        self.t.start()

        check_leader = 0
        check_leader_time = 0
        check_peer_time = 0
        check_halt_time = 0
        im_back = False
        


        while 1:
            sleep(0.1)
            match self.debug:
                case "INITIAL":
                    if self.leader == 0:
                        self.measured_time = time() - self.measured_time
                        self.updateMasterFinish()
                        break

                case "LEADER_FAILURE":
                    if self.leader == 1:
                        self.measured_time = time() - self.measured_time
                        self.updateMasterFinish()
                        break

                case "REVIVAL":
                    if self.leader == 0:
                        self.measured_time = time() - self.measured_time
                        self.updateMasterFinish()
                        break

                case _:
                    self.updateMaster()



            new_message = False 
            if not self.q.empty():
                new_message = True
                self.n_messages_received += 1
                line = self.q.get()
                line=line.split()

                from_id = int(line[0])
                msg =  int(line[1])

                if from_id == 99:
                    if msg == self.KILL and self.state != self.DOWN:
                        self.state = self.DOWN
                        print(str(self.id) + " is ded\n")
                        new_message = False
                    elif msg == self.KILL and self.state == self.DOWN:
                        print(str(self.id) + " back alive\n")
                        self.state = self.NORMAL
                        self.leader = -1
                        check_leader = 0
                        check_leader_time = 0
                        check_peer_time = 0
                        check_halt_time = 0
                        self.last_leader_update = 0
                        self.wakeTime = time()
                        new_message = False
                        im_back = True

                    elif msg == self.WAKE:
                        self.state = self.ELECTION
                        new_message = False


            if self.state == self.DOWN:
                continue
            
            #READ MESSAGES
            if new_message:
                if from_id == self.leader:
                    self.last_leader_update = time()

                if msg == self.ARE_U_THERE:
                    #print(str(self.id) + " RX ARE-U-THERE from " + str(from_id))
                    self.msg_send(from_id, self.YES)
                    check_leader_time = 0
                    check_leader = 1
                    self.state = self.NORMAL
                    

                   

                elif msg == self.HALT:
                    self.state = self.ELECTION
                    check_leader = 0

                elif msg == self.NEW_LEADER:
                    self.leader = from_id
                    self.state = self.NORMAL
                    check_leader = 0
                    self.n_elections += 1

                    self.last_leader_update = time()
                
                elif msg == self.ECHO:
                   self.msg_send(from_id, self.REPLY)
                   

                elif msg == self.REPLY and from_id == self.leader and check_leader==1:
                    self.last_leader_update = time()
                    check_leader = 0


                elif msg == self.YES and self.leader != -1:
                        check_leader = 0
                        self.last_leader_update = time()
                
                elif msg == self.YES:
                    pass



            

            #TAKE ACTION

            #Running for election
            if self.state == self.NORMAL:
                if time()-self.last_leader_update > self.timeout-1 and check_leader == 0 and self.leader != -1 and self.leader != self.id: #Start election proccess
                    #SEND ARE U THERE to LEADER
                    self.msg_send(self.leader, self.ECHO)
                    check_leader = 1
                    check_leader_time = time()

                elif self.leader == -1 and check_leader == 0:
                    for n in range(self.id):
                        self.msg_send(n, self.ARE_U_THERE)

                    print("Im starting an electionA " + str(self.id))
                    check_leader = 2
                    check_peer_time = time()


                elif time()-check_leader_time > self.timeout and check_leader == 1:
                    for n in range(self.id):
                        self.msg_send(n, self.ARE_U_THERE)

                    print("Im starting an electionB " + str(self.id))
                    check_leader = 2
                    check_peer_time = time()
                    check_leader_time = time()

                elif time()-check_peer_time > self.timeout and check_leader == 2:
                    for n in range(self.id+1, self.n_nodes):
                        self.msg_send(n, self.HALT)

                    print("Sending HALT " + str(self.id))
                    self.state = self.ELECTION
                    check_leader = 3
                    check_halt_time = time()
                    check_peer_time = time()


            #Asserting as leader
            elif self.state == self.ELECTION:

                if time()-check_halt_time > self.T and check_leader == 3:
                    for n in range(self.id, self.n_nodes):
                        self.msg_send(n, self.NEW_LEADER)
                    
                    print("Sending NEW LEADER " + str(self.id))
                    

                    self.n_elections += 1
                    self.leader = self.id
                    self.state = self.NORMAL   



    

    def msg_send(self, to_id, msg):
        print("FROM: " + str(self.id) + " TO: " + str(to_id) + " START Message: " + str(msg) +"\n")
        st = 0
        en = self.n_nodes

        if id != -1:   
            st = to_id
            en = to_id+1

        msg = str(self.id) + " " + str(msg)

        sleep(random()*self.message_delay)


        for node in range(st, en):
            if random() < self.message_failure_rate/100:
                continue
            if node != self.id:    
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                while 1:
                    try:
                        s.connect(('localhost', 123*100+node))      
                        break
                    except:
                        pass
                s.send(msg.encode('utf-8'))
                self.n_messages_sent += 1
                s.close()
        
        #print("FROM: " + str(self.id) + " TO: " + str(to_id) + " FINISH\n")
    

    def updateMaster(self):
        msg = str(self.state) + " " + str(self.leader) 

        self.msg_send(99, msg)

        
    def updateMasterFinish(self):
        msg = str(self.state) + " " + str(self.leader) + " " + str(self.n_messages_sent) + " " + str(self.n_messages_received)  + " " + str(self.n_elections)  + " " + str(self.measured_time)
        #print(self.id, msg)
        self.msg_send(99, msg)

        