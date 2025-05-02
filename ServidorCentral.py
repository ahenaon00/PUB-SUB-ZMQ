import sys
import zmq

context = zmq.Context()
subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://localhost:5556")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "operandos")

pubSumaSocket = context.socket(zmq.PUB)
pubSumaSocket.bind("tcp://localhost:5557")

subSumaSocket = context.socket(zmq.SUB)
subSumaSocket.connect("tcp://localhost:5558")
subSumaSocket.setsockopt_string(zmq.SUBSCRIBE, "sumaSecond")

pubMultiSocket = context.socket(zmq.PUB)
pubMultiSocket.bind("tcp://localhost:5559")

subMultiSocket = context.socket(zmq.SUB)
subMultiSocket.connect("tcp://localhost:5560")
subMultiSocket.setsockopt_string(zmq.SUBSCRIBE, "multiSecond")

poller = zmq.Poller()
poller.register(subSocket, zmq.POLLIN)  # Subscribe to operandos
poller.register(subSumaSocket, zmq.POLLIN) 
poller.register(subMultiSocket, zmq.POLLIN) 


while True:
    socks = dict(poller.poll())
    
    if subSocket in socks and socks[subSocket] == zmq.POLLIN:
        msg = subSocket.recv_multipart()
        if msg[0].decode() == "operandos":
            print(f"llegaron los operandos")
            dataSumaAB = msg[1].decode()[:-3]
            print(dataSumaAB)
            dataC = msg[1].decode().split(",")[-1] 
            topicSuma = "sumaFirst"
            print("Mandando numeros a server suma")
            pubSumaSocket.send_multipart([topicSuma.encode(), dataSumaAB.encode()])
    
    elif subSumaSocket in socks and socks[subSumaSocket] == zmq.POLLIN:
        msg = subSumaSocket.recv_multipart()
        if msg[0].decode() == "sumaSecond":
            suma = msg[1].decode()
            print(f"Recibida suma = {suma}")
            topicMulti = "multiFirst"
            data = f"{suma}, {dataC}"
            print("Mandando numeros a server multiplicacion")
            pubMultiSocket.send_multipart([topicMulti.encode(), data.encode()])
            
    elif subMultiSocket in socks and socks[subMultiSocket] == zmq.POLLIN:
        msg = subMultiSocket.recv_multipart()
        if msg[0].decode() == "multiSecond":
            result = msg[1].decode()
            print(f"Recibido resultado final = {result}")
            
    
        
    


socket.close()
context.term()
