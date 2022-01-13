from socket import *
import multiprocessing
import time



class Node:
    def __init__(self, id):
        self.id = id
        #self.addr += str(id)

    def run(self):
        if self.id == 1: #Send
            print("start server")
            with socket(AF_INET, SOCK_STREAM) as s:
                s.bind(("127.0.0.1", 65432))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        conn.sendall(data)

        else: #Listen and print received
            print("start client")
            with socket(AF_INET, SOCK_STREAM) as s:
                s.connect(("127.0.0.1", 65432))
                s.sendall(b'Hello, world')
                data = s.recv(1024)

            print('Received', repr(data))




if __name__ == '__main__':
    
    node2 = Node(2)
    
    n2 = multiprocessing.Process(name='n2', target=node2.run)

    n2.start()