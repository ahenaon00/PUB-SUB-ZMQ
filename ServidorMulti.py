import zmq
import sys
import time

context = zmq.Context()
subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://localhost:5557")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "multi")

pubSocket = context.socket(zmq.PUB)
pubSocket.connect("tcp://localhost:5556")


while True:
    operandos = subSocket.recv_multipart()[1].decode().split(",")
    print(f"Recibios para multiplicar: {operandos}")
    multi = str(int(operandos[0]) * int(operandos[1]))
    topic = "resultFinal"
    pubSocket.send_multipart([topic.encode(), multi.encode()])
    time.sleep(1)
