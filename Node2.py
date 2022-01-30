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
    RND_ST = -3
    TERMINATE = -10

    
    def __init__(self, id, n_nodes, msg_dl, flr_rate, debug) -> None:
        print("initing " + str(id))
        self.id = id
        self.n_nodes = n_nodes
        self.state = self.NORMAL
        self.leader = -1
        self.T = 1.5
        self.waitt = 1/n_nodes
        self.last_leader_update = time()
        self.timeout = 2 * self.T
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
        self.rnd = False

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
            #Thread(target=self.msg_reader, args=(conn,)).start()
            self.msg_reader(conn)
            

    def msg_reader(self,conn):
        while True:
            msg = conn.recv(1024)
            if not msg:
                break
            with data_lock:
                line = msg.decode()

                
                line=line.split()

                from_id = int(line[0])
                msg =  int(line[1])

                if from_id == 999:
                    if msg == self.KILL and self.state != self.DOWN:
                        self.state = self.DOWN
                        print(str(self.id) + " was manually killed\n")
                        self.new_message = False
                    elif msg == self.KILL and self.state == self.DOWN:
                        print(str(self.id) + " was manually revived\n")
                        self.state = self.NORMAL
                        self.leader = -1
                        self.check_leader = 0
                        self.check_leader_time = 0
                        self.check_peer_time = 0
                        self.check_halt_time = 0
                        self.last_leader_update = 0

                    elif msg == self.WAKE:
                        self.state = self.ELECTION
                        self.new_message = False
                    
                    elif msg == self.RND_ST:
                        self.rnd = not self.rnd

                    elif msg == self.TERMINATE:
                        return
                else:
                    self.n_messages_received += 1

                if self.state == self.DOWN:
                    return
            
                
                if from_id == self.leader:
                    self.last_leader_update = time()

                if msg == self.ARE_U_THERE:
                    self.msg_send(from_id, self.YES)

                   
                
                    self.check_leader = 1
                    self.check_leader_time = 0
                    self.state = self.NORMAL
                    
                                    
                elif msg == self.YES:
                    self.check_leader = 0
                    self.state = self.NORMAL

                    self.last_leader_update = time()

                elif msg == self.HALT:
                    self.state = self.ELECTION
                    self.check_leader = 10
                    self.check_new_leader = time()
                

                elif msg == self.NEW_LEADER:
                    self.leader = from_id
                    self.state = self.NORMAL
                    self.check_leader = 0
                    self.last_leader_update = time()

                    self.n_elections += 1
                    
                
                elif msg == self.ECHO:
                    self.msg_send(from_id, self.REPLY)
            
                

                elif msg == self.REPLY and from_id == self.leader:
                    self.last_leader_update = time()
                    self.check_leader = 0


    def run(self):
        self.check_leader = 0
        self.check_leader_time = 0
        self.check_peer_time = 0
        self.check_halt_time = 0
        self.check_new_leader = 0
        

        self.t = Thread(target=self.listener, args=())
        self.t.start()
       

        try:
          while 1:
            sleep(0.05)
            if random() < 0.001 and self.rnd:
                if self.state == self.DOWN:
                    self.state = self.NORMAL
                    self.check_leader = 0
                    self.check_leader_time = 0
                    self.check_peer_time = 0
                    self.check_halt_time = 0
                    self.check_new_leader = 0
                    self.leader = -1
                    print(str(self.id) + " is alive\n")

                else:
                    self.state = self.DOWN
                    print(str(self.id) + " is dead\n")
                    

            with data_lock:
                match self.debug:
                    case "INITIAL":
                        if self.leader == 0:
                            self.measured_time = time() - self.measured_time
                            self.updateMasterFinish()
                            return

                    case "LEADER_FAILURE":
                        if self.leader == 1:
                            self.measured_time = time() - self.measured_time
                            self.updateMasterFinish()
                            return

                    case "REVIVAL":
                        if self.leader == 0:
                            self.measured_time = time() - self.measured_time
                            self.updateMasterFinish()
                            return

                    case _:
                        self.updateMaster()


                #Running for election
                if self.state == self.NORMAL:
                    # check time out last connection from leader
                    if time()-self.last_leader_update > 2*self.timeout and self.check_leader == 0 and self.leader != self.id:
                        if self.leader != -1:
                            self.msg_send(self.leader, self.ECHO)
                            self.check_leader_time = time()
                        else:
                            self.check_leader_time = 0
                            sleep(self.id*self.waitt)
                        
                        self.check_leader = 1
                        

                    #leader failure
                    elif time() - self.check_leader_time > self.timeout and self.check_leader == 1:
                        for n in range(self.id):
                            self.msg_send(n, self.ARE_U_THERE)

                        self.state = self.ELECTION
                        self.check_leader = 2
                        self.check_peer_time = time()
                

                #Asserting as leader if no other node answered
                elif self.state == self.ELECTION:
                    #proceed if the superior node
                    if time() - self.check_peer_time > self.timeout and self.check_leader == 2:
                        for n in range(self.id+1, self.n_nodes):
                            self.msg_send(n, self.HALT)

                        self.check_leader = 3
                        self.check_halt_time = time()

                    elif time() - self.check_halt_time > self.T and self.check_leader == 3:
                        for n in range(self.id+1, self.n_nodes):
                            self.msg_send(n, self.NEW_LEADER)
                        
                        self.leader = self.id
                        self.state = self.NORMAL

                        self.check_leader = 0

                        self.n_elections += 1

                    elif time() - self.check_new_leader > self.timeout and self.check_leader == 10:
                        self.check_leader = 0
                        self.state = self.NORMAL
                        self.last_leader_update = time()
                #if self.id == 1:
                    #print(self.id, self.check_leader, self.state, self.leader, time()-self.check_peer_time, time() - self.check_halt_time, time() - self.check_new_leader)
        except:
            print("Im ded booiiiiiiiiiiiiiiiiiiiiiiii", self.id, self.check_leader, self.state, self.leader)

    def msg_send(self, to_id, msg):
        #if to_id == 99:
        #print("FROM: " + str(self.id) + " TO: " + str(to_id) + " START Message: " + str(msg) +"\n")
        st = 0
        en = self.n_nodes

        if id != -1:   
            st = to_id
            en = to_id+1

        msg = str(self.id) + " " + str(msg)

        sleep(random()*self.message_delay)


        for node in range(st, en):
            if random() < self.message_failure_rate/100 and node < 999:
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
                if node < 999: 
                    self.n_messages_sent += 1
                s.close()
                
        
        #print("FROM: " + str(self.id) + " TO: " + str(to_id) + " FINISH\n")
    

    def updateMaster(self):
        msg = str(self.state) + " " + str(self.leader) 

        self.msg_send(999, msg)

        
    def updateMasterFinish(self):
        msg = str(self.state) + " " + str(self.leader) + " " + str(self.n_messages_sent) + " " + str(self.n_messages_received)  + " " + str(self.n_elections)  + " " + str(self.measured_time)
        #print(self.id, msg)
        self.msg_send(999, msg)

        