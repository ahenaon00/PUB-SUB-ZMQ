import zmq
import time

context = zmq.Context()

# Intentar conectarse como broker primario primero
try:
    xsub = context.socket(zmq.XSUB)
    xsub.bind("tcp://*:7776")
    
    xpub = context.socket(zmq.XPUB)
    xpub.bind("tcp://*:7777")
    
    print("Broker de respaldo actuando como primario")
except zmq.ZMQError:
    # Si no puede bindear, asumir que hay un broker primario y esperar
    print("Broker primario detectado, actuando como respaldo")
    time.sleep(1)
    
    # Configurar como proxy para tomar el control si el primario falla
    xsub = context.socket(zmq.SUB)
    xsub.connect("tcp://localhost:7776")
    xsub.setsockopt_string(zmq.SUBSCRIBE, "")
    
    xpub = context.socket(zmq.PUB)
    xpub.connect("tcp://localhost:7777")
    
    # Socket para monitorear el broker primario
    monitor = context.socket(zmq.REQ)
    monitor.connect("tcp://localhost:7778")
    monitor.setsockopt(zmq.RCVTIMEO, 2000)  # Timeout de 2 segundos

poller = zmq.Poller()
poller.register(xsub, zmq.POLLIN)

# Si estamos en modo respaldo, monitorear al primario
if 'monitor' in locals():
    poller.register(monitor, zmq.POLLIN)

last_activity = time.time()
primary_timeout = 3  # segundos sin respuesta para considerar caído

while True:
    try:
        socks = dict(poller.poll(1000))  # Timeout de 1 segundo
        
        # Si estamos en modo respaldo y el primario no responde
        if 'monitor' in locals():
            if time.time() - last_activity > primary_timeout:
                try:
                    monitor.send(b"PING")
                    msg = monitor.recv()
                    last_activity = time.time()
                except zmq.Again:
                    print("Broker primario no responde, tomando control...")
                    # Cambiar a modo primario
                    xsub.close()
                    xpub.close()
                    
                    xsub = context.socket(zmq.XSUB)
                    xsub.bind("tcp://*:7776")
                    
                    xpub = context.socket(zmq.XPUB)
                    xpub.bind("tcp://*:7777")
                    
                    poller = zmq.Poller()
                    poller.register(xsub, zmq.POLLIN)
                    print("Ahora actuando como broker primario")
                    del monitor
        
        if xsub in socks:
            msg = xsub.recv_multipart()
            print(f"Broker recibió mensaje: {msg}")
            xpub.send_multipart(msg)
            
    except zmq.ZMQError as e:
        print(f"Error en broker: {e}")
        time.sleep(1)