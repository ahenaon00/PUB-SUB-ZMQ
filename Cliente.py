import zmq
import time

context = zmq.Context()

# Conectarse al servidor central en vez del broker
subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://localhost:6002")  # Recibe resultado
subSocket.setsockopt_string(zmq.SUBSCRIBE, "resultFinal")

pubSocket = context.socket(zmq.PUB)
pubSocket.connect("tcp://localhost:6001")  # Envía operandos

time.sleep(1)  # Espera para asegurar conexiones

while True:
    topic = "operandos"
    num1 = int(input("Ingrese el primer número: "))
    num2 = int(input("Ingrese el segundo número: "))
    num3 = int(input("Ingrese el tercer número: "))
    data = f"{num1},{num2},{num3}"
    
    pubSocket.send_multipart([topic.encode(), data.encode()])
    print(f"Enviados operandos: {data}")
    
    start_time = time.time()
    while time.time() - start_time < 5:
        try:
            msg = subSocket.recv_multipart(flags=zmq.NOBLOCK)
            if msg[0].decode() == "resultFinal":
                print(f"\nEl resultado final es: {msg[1].decode()}\n")
                break
        except zmq.Again:
            time.sleep(0.1)
        except Exception as e:
            print(f"Error recibiendo mensaje: {e}")
            break
    
    time.sleep(1)
