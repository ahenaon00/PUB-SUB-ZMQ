import zmq
import sys
import time


context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind(f"tcp://*:{5556}")
while True:
    topic = "operandos"
    num1 = int(input("Ingrese el primer número: "))
    num2 = int(input("Ingrese el segundo número: "))
    num3 = int(input("Ingrese el tercer número: "))
    data = f"{num1},{num2},{num3} "
    socket.send_multipart([topic.encode(), data.encode()])
    print(topic, "enviado al topico")
    time.sleep(1)
