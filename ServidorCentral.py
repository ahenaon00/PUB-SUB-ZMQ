import zmq
import time

context = zmq.Context()

# Socket para recibir mensajes
subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://localhost:7777")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "operandos")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "sumaResult")

# Socket para enviar mensajes
pubSocket = context.socket(zmq.PUB)
pubSocket.connect("tcp://localhost:7776")

time.sleep(1)

# Variables de estado
tercer_numero = None
suma_timeout = 2  # segundos para esperar respuesta de suma
servidor_suma_activo = True  # Asumimos activo inicialmente
servidor_multi_activo = True  # Asumimos activo inicialmente

def realizar_suma_local(num1, num2):
    """Realiza la suma localmente"""
    return str(int(num1) + int(num2))

def realizar_multiplicacion_local(num1, num2):
    """Realiza la multiplicación localmente"""
    return str(int(num1) * int(num2))

while True:
    try:
        msg = subSocket.recv_multipart(flags=zmq.NOBLOCK)
        topic = msg[0].decode()
        
        if topic == "operandos":
            operandos = msg[1].decode().strip()
            nums = operandos.split(',')
            if len(nums) == 3:
                print(f"Recibidos operandos: {nums[0]}, {nums[1]}, {nums[2]}")
                tercer_numero = nums[2]
                
                # Opción 1: Enviar a servidor de suma si está activo
                if servidor_suma_activo:
                    pubSocket.send_multipart([b"suma", f"{nums[0]},{nums[1]}".encode()])
                    print("Enviados números para suma")
                    
                    # Esperar respuesta con timeout
                    start_time = time.time()
                    suma_recibida = False
                    while time.time() - start_time < suma_timeout:
                        try:
                            msg_suma = subSocket.recv_multipart(flags=zmq.NOBLOCK)
                            if msg_suma[0].decode() == "sumaResult":
                                suma = msg_suma[1].decode().strip()
                                print(f"Recibido resultado de suma: {suma}")
                                pubSocket.send_multipart([b"multi", f"{suma},{tercer_numero}".encode()])
                                print("Enviados números para multiplicación")
                                suma_recibida = True
                                break
                        except zmq.Again:
                            time.sleep(0.1)
                    
                    if not suma_recibida:
                        print("Timeout: Servidor de suma no respondió, realizando suma local")
                        servidor_suma_activo = False
                        suma_local = realizar_suma_local(nums[0], nums[1])
                        pubSocket.send_multipart([b"multi", f"{suma_local},{tercer_numero}".encode()])
                
                # Opción 2: Realizar suma local si servidor no está activo
                else:
                    print("Servidor de suma inactivo, realizando suma local")
                    suma_local = realizar_suma_local(nums[0], nums[1])
                    pubSocket.send_multipart([b"multi", f"{suma_local},{tercer_numero}".encode()])
                
        elif topic == "sumaResult":
            # Si recibimos respuesta de suma, el servidor está activo
            servidor_suma_activo = True
            if tercer_numero is not None:
                suma = msg[1].decode().strip()
                print(f"Recibido resultado de suma: {suma}")
                
                # Opción 1: Enviar a servidor de multiplicación si está activo
                if servidor_multi_activo:
                    pubSocket.send_multipart([b"multi", f"{suma},{tercer_numero}".encode()])
                    print("Enviados números para multiplicación")
                    
                    # Esperar respuesta con timeout
                    start_time = time.time()
                    multi_recibida = False
                    while time.time() - start_time < suma_timeout:
                        try:
                            msg_multi = subSocket.recv_multipart(flags=zmq.NOBLOCK)
                            if msg_multi[0].decode() == "resultFinal":
                                print("Resultado de multiplicación recibido")
                                multi_recibida = True
                                break
                        except zmq.Again:
                            time.sleep(0.1)
                    
                    if not multi_recibida:
                        print("Timeout: Servidor de multiplicación no respondió, realizando multiplicación local")
                        servidor_multi_activo = False
                        resultado = realizar_multiplicacion_local(suma, tercer_numero)
                        pubSocket.send_multipart([b"resultFinal", resultado.encode()])
                
                # Opción 2: Realizar multiplicación local si servidor no está activo
                else:
                    print("Servidor de multiplicación inactivo, realizando operación local")
                    resultado = realizar_multiplicacion_local(suma, tercer_numero)
                    pubSocket.send_multipart([b"resultFinal", resultado.encode()])
                
                tercer_numero = None
                
    except zmq.Again:
        pass
    
    time.sleep(0.1)