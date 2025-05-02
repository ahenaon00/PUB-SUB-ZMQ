import zmq
import time

context = zmq.Context()

# Socket para recibir resultados
subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://localhost:7777")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "resultFinal")

# Socket para enviar operandos
pubSocket = context.socket(zmq.PUB)
pubSocket.connect("tcp://localhost:7776")

time.sleep(1)  # Espera inicial para conexiones

while True:
    topic = "operandos"
    num1 = int(input("Ingrese el primer número: "))
    num2 = int(input("Ingrese el segundo número: "))
    num3 = int(input("Ingrese el tercer número: "))
    data = f"{num1},{num2},{num3}"
    
    # Envía los operandos
    pubSocket.send_multipart([topic.encode(), data.encode()])
    print(f"Enviados operandos: {data}")
    
    # Espera activa por el resultado
    start_time = time.time()
    while time.time() - start_time < 5:  # Timeout de 5 segundos
        try:
            msg = subSocket.recv_multipart(flags=zmq.NOBLOCK)
            if msg[0].decode() == "resultFinal":
                print(f"\nEl resultado final es: {msg[1].decode()}\n")
                break
        except zmq.Again:
            time.sleep(0.1)  # Pequeña pausa para no saturar la CPU
        except Exception as e:
            print(f"Error recibiendo mensaje: {e}")
            break
    
    time.sleep(1)  # Pausa antes de pedir nuevos números