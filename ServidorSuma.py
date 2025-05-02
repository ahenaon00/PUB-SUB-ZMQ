import zmq
import time

context = zmq.Context()
subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://localhost:5557")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "suma")

pubSocket = context.socket(zmq.PUB)
pubSocket.connect("tcp://localhost:5556")




while True:
    operandos = subSocket.recv_multipart()[1].decode().split(",")
    print(f"recibidos {operandos}")
    topic = "sumaResult"
    suma = str(int(operandos[0]) + int(operandos[1]), operandos[2])
    pubSocket.send_multipart([topic.encode(), suma.encode()])
    time.sleep(1)
