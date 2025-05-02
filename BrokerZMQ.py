import zmq

context = zmq.Context()

# Sockets principales
xsub = context.socket(zmq.XSUB)
xsub.bind("tcp://*:7776")

xpub = context.socket(zmq.XPUB)
xpub.bind("tcp://*:7777")

# Socket para monitoreo por el broker de respaldo
monitor = context.socket(zmq.REP)
monitor.bind("tcp://*:7778")

poller = zmq.Poller()
poller.register(xsub, zmq.POLLIN)
poller.register(xpub, zmq.POLLIN)
poller.register(monitor, zmq.POLLIN)

while True:
    socks = dict(poller.poll())
    
    if xsub in socks:
        msg = xsub.recv_multipart()
        print(f"Broker recibió de XSUB: {msg}")
        xpub.send_multipart(msg)

    if xpub in socks:
        msg = xpub.recv()
        print(f"Broker recibió de XPUB (suscripciones): {msg}")
        xsub.send(msg)
        
    if monitor in socks:
        msg = monitor.recv()
        monitor.send(b"PONG")  # Responder al heartbeat