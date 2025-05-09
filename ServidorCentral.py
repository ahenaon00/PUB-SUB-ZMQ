import zmq
import time

context = zmq.Context()

# Socket hacia el broker (para suma y multiplicación)
subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://localhost:7777")  # IP del broker
subSocket.setsockopt_string(zmq.SUBSCRIBE, "sumaResult")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "multi")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "resultFinal")

pubSocket = context.socket(zmq.PUB)
pubSocket.connect("tcp://localhost:7776")

# Socket para comunicarse con el cliente directamente
pubCliente = context.socket(zmq.PUB)
pubCliente.bind("tcp://*:6002")  # Enviar resultado al Cliente

subCliente = context.socket(zmq.SUB)
subCliente.bind("tcp://*:6001")  # Recibir operandos del Cliente
subCliente.setsockopt_string(zmq.SUBSCRIBE, "operandos")

time.sleep(1)

tercer_numero = None
suma_timeout = 2
servidor_suma_activo = True
servidor_multi_activo = True

def realizar_suma_local(num1, num2):
    return str(int(num1) + int(num2))

def realizar_multiplicacion_local(num1, num2):
    return str(int(num1) * int(num2))

while True:
    try:
        msg = None
        try:
            msg = subCliente.recv_multipart(flags=zmq.NOBLOCK)  # Mensaje del Cliente
        except zmq.Again:
            try:
                msg = subSocket.recv_multipart(flags=zmq.NOBLOCK)  # Mensaje del Broker
            except zmq.Again:
                time.sleep(0.1)
                continue

        if not msg:
            continue

        topic = msg[0].decode()

        if topic == "operandos":
            nums = msg[1].decode().strip().split(',')
            if len(nums) == 3:
                print(f"Recibidos operandos: {nums}")
                tercer_numero = nums[2]
                
                if servidor_suma_activo:
                    pubSocket.send_multipart([b"suma", f"{nums[0]},{nums[1]}".encode()])
                    print("Enviados a suma")

                    start_time = time.time()
                    suma_recibida = False
                    suma = None
                    while time.time() - start_time < suma_timeout:
                        try:
                            msg_suma = subSocket.recv_multipart(flags=zmq.NOBLOCK)
                            if msg_suma[0].decode() == "sumaResult":
                                suma = msg_suma[1].decode().strip()
                                print(f"Suma recibida: {suma}")
                                pubSocket.send_multipart([b"multi", f"{suma},{tercer_numero}".encode()])
                                suma_recibida = True
                                break
                        except zmq.Again:
                            time.sleep(0.1)

                    if not suma_recibida:
                        print("Timeout suma, realizando local")
                        servidor_suma_activo = False
                        suma_local = realizar_suma_local(nums[0], nums[1])
                        pubSocket.send_multipart([b"multi", f"{suma_local},{tercer_numero}".encode()])
                else:
                    print("Servidor suma inactivo, suma local")
                    suma_local = realizar_suma_local(nums[0], nums[1])
                    pubSocket.send_multipart([b"multi", f"{suma_local},{tercer_numero}".encode()])

        elif topic == "sumaResult":
            servidor_suma_activo = True
            print("Servidor de suma confirmado como activo")

        elif topic == "multi":
            valores = msg[1].decode().strip().split(',')
            if len(valores) == 2:
                suma, tercer_numero = valores
                print(f"Recibido mensaje 'multi': {suma}, {tercer_numero}")

                start_time = time.time()
                multi_recibida = False
                while time.time() - start_time < suma_timeout:
                    try:
                        msg_multi = subSocket.recv_multipart(flags=zmq.NOBLOCK)
                        if msg_multi[0].decode() == "resultFinal":
                            resultado = msg_multi[1].decode()
                            pubCliente.send_multipart([b"resultFinal", resultado.encode()])
                            print("Resultado final reenviado al cliente")
                            servidor_multi_activo = True
                            multi_recibida = True
                            break
                    except zmq.Again:
                        time.sleep(0.1)

                if not multi_recibida:
                    print("Timeout multi, ejecutando localmente")
                    servidor_multi_activo = False
                    resultado = realizar_multiplicacion_local(suma, tercer_numero)
                    pubCliente.send_multipart([b"resultFinal", resultado.encode()])

        elif topic == "resultFinal":
            resultado = msg[1].decode().strip()
            pubCliente.send_multipart([b"resultFinal", resultado.encode()])
            print("Resultado final reenviado al cliente (canal alternativo)")

    except Exception as e:
        print(f"Error en servidor central: {e}")
    
    time.sleep(0.1)
