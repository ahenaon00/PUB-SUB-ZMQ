import zmq
import time

context = zmq.Context()

subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://localhost:7777")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "suma")

pubSocket = context.socket(zmq.PUB)
pubSocket.connect("tcp://localhost:7776")

while True:
    try:
        msg = subSocket.recv_multipart(flags=zmq.NOBLOCK)
        if msg[0].decode() == "suma":
            # Asegurarse de que solo recibimos 2 números
            datos = msg[1].decode().strip().split(',')
            if len(datos) == 2:
                num1, num2 = datos
                print(f"Recibidos para suma: {num1}, {num2}")
                resultado = str(int(num1) + int(num2))
                pubSocket.send_multipart([b"sumaResult", resultado.encode()])
            else:
                print(f"Error: Se recibieron {len(datos)} valores, se esperaban 2")
    except zmq.Again:
        pass
    
    time.sleep(0.1)