from multiprocessing import Process, Pipe, Queue
""" from node import * """
from teste_recv import *

if __name__ == '__main__':
    n_nodes = 5

    masterDict = {}
    nodeObj = []
    nodesProcess = []

    

    for nP in range(n_nodes):
        for nC in range(nP+1, n_nodes):
            if nP not in masterDict:
                masterDict[nP] = {}
            if nC not in masterDict:
                masterDict[nC] = {}

            masterDict[nP][nC], masterDict[nC][nP] = Pipe()
        
        print(nP)

    
    for i in range(n_nodes):
        nodeObj.append(Node(i, n_nodes, masterDict[i]))

    for obj in nodeObj:
        nodesProcess.append(Process(target=obj.testNodes))

    for node in nodesProcess:
        node.start()

    for node in nodesProcess:
        node.join()




