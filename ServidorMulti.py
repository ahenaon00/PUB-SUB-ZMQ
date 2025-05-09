import zmq
import time

context = zmq.Context()

subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://10.43.96.14:7777")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "multi")

pubSocket = context.socket(zmq.PUB)
pubSocket.connect("tcp://10.43.96.14:7776")

while True:
    try:
        msg = subSocket.recv_multipart(flags=zmq.NOBLOCK)
        if msg[0].decode() == "multi":
            suma, num3 = msg[1].decode().split(',')
            print(f"Recibidos para multiplicación: {suma}, {num3}")
            resultado = str(int(suma) * int(num3))
            pubSocket.send_multipart([b"resultFinal", resultado.encode()])
    except zmq.Again:
        pass
    
    time.sleep(0.1)