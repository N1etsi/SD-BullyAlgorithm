from multiprocessing import Process, Pipe, Queue
""" from node import * """
from Node2 import *
from Master import *
import sys


debug = ""
max_delay = 0.00
failure_rate = 0

if __name__ == '__main__':
    n_nodes = int(sys.argv[1])


    nodeObj = []
    nodesProcess = []

    master = Master(n_nodes, 999, debug)

    Process(target=master.run).start()

    
    for i in range(n_nodes):
        nodeObj.append(Node(i, n_nodes, max_delay, failure_rate, debug))

    for obj in nodeObj:
        nodesProcess.append(Process(target=obj.run))
        #nodesProcess.append(Thread(target=obj.run))
    for node in nodesProcess:
        node.start()
        sleep(0.01)
        

    for node in nodesProcess:
        node.join()

    