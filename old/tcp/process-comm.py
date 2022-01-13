from socket import *
import multiprocessing
import time



class Node:
    def __init__(self, id, n):
        self.id = id
        self.n = n
        self.conns = {}
        self.base_addr = "127.0.0."
        self.addr =  self.base_addr + str(id)

    def run(self):
        self.connect(self.id, self.n)

    def connect(self, id, n_ids):
        s = socket(AF_INET, SOCK_DGRAM)
        

        for x in range(2, n_ids+2):
            if x == id:
                continue
            if id < x:
                port = 654 * 100 + id * 10 + x
                print("Im the server: " + str(port))
                s.bind((self.addr, port))
                print("Node " + str(self.addr) + " connected to " + str(addr) + "\n")
                #self.conns[id] = conn




            elif id > x:
                port = 654 * 100 + x * 10 + id 
                print("Im the client: " + str(port))
                s.bind((self.addr, port))
                print("Client node " + str(id) + "trying to connect " + str(x) + "\n")
                #s.connect((self.base_addr + str(x), port))
                #s.sendall(("Node " + str(id) + " sent and received their regards \n").encode("utf-8"))
                #data = s.recv(1024)
                #print('Received', str(data, 'utf-8'))






if __name__ == '__main__':
    
    node2 = Node(2, 3)
    node3 = Node(3, 3)
    node4 = Node(4, 3)
    
    n2 = multiprocessing.Process(name='n2', target=node2.run)
    n3 = multiprocessing.Process(name='n3', target=node3.run)
    n4 = multiprocessing.Process(name='n4', target=node4.run)


    n2.start()
    n3.start()
    n4.start()