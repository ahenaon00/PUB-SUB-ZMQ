import zmq
import sys
import time


context = zmq.Context()
subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://localhost:5559")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "multiFirst")

pubSocket = context.socket(zmq.PUB)
pubSocket.bind("tcp://localhost:5560")

while True:
    operandos = subSocket.recv_multipart()[1].decode().split(",")
    print(f"Recibidos numeros a multiplicar : {operandos}")
    topic = "multiSecond"
    multi = str(int(operandos[0]) * int(operandos[1]))
    pubSocket.send_multipart([topic.encode(), multi.encode()])
    time.sleep(1)
