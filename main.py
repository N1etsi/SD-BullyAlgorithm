from multiprocessing import Process, Pipe, Queue
""" from node import * """
from teste_socket import *

if __name__ == '__main__':
    n_nodes = 3


    nodeObj = []
    nodesProcess = []


    
    for i in range(n_nodes):
        nodeObj.append(Node(i, n_nodes))

    for obj in nodeObj:
        nodesProcess.append(Process(target=obj.testNodes))

    for node in nodesProcess:
        node.start()

    for node in nodesProcess:
        node.join()