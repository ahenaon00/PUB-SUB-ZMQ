import zmq
import sys
import time

context = zmq.Context()
subSocket = context.socket(zmq.SUB)
subSocket.connect(f"tcp://localhost:5557")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "sumaFirst")

pubSocket = context.socket(zmq.PUB)
pubSocket.bind("tcp://localhost:5558")

while True:
    operandos = subSocket.recv_multipart()[1].decode().split(",")
    print(f"recibidos {operandos}")
    topic = "sumaSecond"
    suma = str(int(operandos[0]) + int(operandos[1]))
    pubSocket.send_multipart([topic.encode(), suma.encode()])
    time.sleep(1)
