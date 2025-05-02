import sys
import zmq

context = zmq.Context()
xsub = context.socket(zmq.XSUB)
xsub.bind("tcp://*:7776")

xpub = context.socket(zmq.XPUB)
xpub.bind("tcp://*:7777")


poller = zmq.Poller()
poller.register(xsub, zmq.POLLIN)
poller.register(xpub, zmq.POLLIN) 


while True:
    msg = xsub.recv_multipart()
    print(msg)
    if msg[0].decode() == "operandos":
        print(f"llegaron los operandos")
        print("Mandando numeros a server Central")
        xpub.send_multipart(msg)
    elif msg[0].decode() == "suma":
        print(f"Operandos listos para ser sumados")
        print(f"Enviando a Servidor Central...")
        xpub.send_multipart([msg[0].decode(), msg[1].decode()])
    elif msg[0].decode() == "sumaResult":
        print(f"Operandos finales listos para multiplicacion")
        print(f"Enviando operandos a Servidor Central...")
        topic = "multi"
        xpub.send_multipart([topic.encode(), msg[1].decode()])
socket.close()
context.term()
