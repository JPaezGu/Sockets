import socket
import threading

class ChatServer:
    def __init__(self, host='192.168.0.11', port=50000):
        self.host = host
        self.port = port
        self.clientes = []           # lista de objetos Cliente
        self.lock = threading.Lock() # para acceder a la lista de forma segura
        
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.servidor.bind((self.host, self.port))
        self.servidor.listen(10)
        print(f"Servidor escuchando en {self.host}:{self.port}")

    def broadcast(self, mensaje, origen=None):
        with self.lock:  # protege la lista de clientes
            for cliente in self.clientes[:]:  # crea una copia de la lista
                if cliente.socket != origen:
                    try:
                        cliente.socket.send(mensaje)
                    except:
                        cliente.desconectar()
                        self.clientes.remove(cliente)

    def manejar_cliente(self, cliente_socket, direccion):
        cliente = Cliente(cliente_socket, direccion, self)
        with self.lock:
            self.clientes.append(cliente)
        
        self.broadcast(f"¡{direccion} entró al chat!\n".encode('utf-8'))
        
        while cliente.conectado:
            try:
                datos = cliente_socket.recv(1024) # recibe el mensaje del cliente
                if not datos:
                    break
                self.broadcast(datos, cliente_socket) # reenvía el mensaje a todos menos al origen
            except:
                break
                
        cliente.desconectar()
        with self.lock:
            if cliente in self.clientes:
                self.clientes.remove(cliente) # elimina al cliente de la lista cuando se desconecta
        self.broadcast(f"¡{direccion} se desconectó\n".encode('utf-8'))

    def iniciar(self):
        while True:
            cliente_socket, direccion = self.servidor.accept()
            hilo = threading.Thread(
                target=self.manejar_cliente,
                args=(cliente_socket, direccion) # pone de parametros la ip y el puerto del cliente
            )
            hilo.daemon = True
            hilo.start() # Crea un hilo para cada cliente conectado al servidor


class Cliente:
    def __init__(self, socket, direccion, servidor):
        self.socket = socket
        self.direccion = direccion
        self.servidor = servidor
        self.conectado = True

    def desconectar(self):
        if self.conectado:
            self.conectado = False
            try:
                self.socket.close() # Elimina el hilo del cliente cuando se desconecta
            except:
                pass

if __name__ == "__main__":
    servidor = ChatServer(port=50000)
    servidor.iniciar() # Inicia el servidor