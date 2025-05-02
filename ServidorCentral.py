import zmq
import sys
import time

context = zmq.Context()
subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://localhost:7777")
time.sleep(1)
subSocket.setsockopt_string(zmq.SUBSCRIBE, "operandos")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "multi")

pubSocket = context.socket(zmq.PUB)
pubSocket.connect("tcp://localhost:7776")
time.sleep(1)



while True:
    msg = subSocket.recv_multipart()
    if msg[0].decode() == "operandos":
        operandos = msg[1].decode()
        print(f"Recibidos operandos {operandos}")
        topic = "suma"
        pubSocket.send_multipart(topic.encode(), operandos.encode())
        time.sleep(1)
    if msg[0].decode() == "multi":
        operandos = msg[1].decode()
        print(f"Recibidos ultimos operandos para multiplicar")
        topic = "multi"
        pubSocket.send_multipart(topic.encode(), operandos.encode())
    if msg[0].decode() == "resultFinal":
        pubSocket.send_multipart(msg[0].decode(), f"El resultado final es {msg[1].decode()}")
        



