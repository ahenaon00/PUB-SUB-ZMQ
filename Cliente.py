import zmq
import sys
import time


context = zmq.Context()
subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://localhost:7777")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "resultFinal")

pubSocket = context.socket(zmq.PUB)
pubSocket.connect("tcp://localhost:7776")
time.sleep(1)


while True:
    topic = "operandos"
    num1 = int(input("Ingrese el primer número: "))
    num2 = int(input("Ingrese el segundo número: "))
    num3 = int(input("Ingrese el tercer número: "))
    data = f"{num1},{num2},{num3} "
    pubSocket.send_multipart([topic.encode(), data.encode()])
    print(topic, "enviado al topico")
    time.sleep(1) 
