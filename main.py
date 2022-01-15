from multiprocessing import Process, Pipe, Queue
""" from node import * """
from Node import *
from Master import *

if __name__ == '__main__':
    n_nodes = 4


    nodeObj = []
    nodesProcess = []

    master = Master(n_nodes)

    Process(target=master.run).start()

    
    for i in range(n_nodes):
        nodeObj.append(Node(i, n_nodes))

    for obj in nodeObj:
        nodesProcess.append(Process(target=obj.run))

    for node in nodesProcess:
        node.start()

    for node in nodesProcess:
        node.join()

    