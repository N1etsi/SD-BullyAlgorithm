


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


    #def run():
    #    while 1:
    #        if failureDet():




    #def failureDet():

    


    

        
    def testNodes(self):
        #Send messages
        for node in self.conns:    
            self.conns[node].send("From " + str(self.id))
    


        #Receive messages
        for node in self.conns:
            print("Node " + str(self.id) + " has received: " + self.conns[node].recv())