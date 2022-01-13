from multiprocessing import Process, Queue
from threading  import Thread

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


    def __init__(self, id, n_nodes, conns) -> None:
        self.id = id
        self.n_nodes = n_nodes
        self.conns = conns
        self.state = self.NORMAL
        self.leader = 0

        """ --------------------------- """
  

    #def run():
    #    while 1:
    #        if failureDet():

    def recv_thread(self,conns,q):

        while 1:
            for node in conns:
                if conns[node].poll():
                   #print("Node " + str(self.id) + " has received: " + conns[node].recv())
                    msg=conns[node].recv()
                    #print("Thread - Node " + str(self.id) + " has received: " + msg)
                    q.put(msg)

    


    

        
    def testNodes(self):
        #Send messages
        self.q=Queue()
        self.t = Thread(target=self.recv_thread, args=(self.conns, self.q,))
        self.t.start()

        for node in self.conns:    
            self.conns[node].send(str(self.id) + " ARE-YOU-THERE")
        
        while 1:
            if not self.q.empty():
                line=self.q.get()
                line=line.split()
                #print(line)
                print("TestNodes -Node " + str(self.id) + " from= "+line[0]+" msg= "+line[1])
                

