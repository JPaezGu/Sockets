import socket
import threading
import sys

class ChatClient:
    def __init__(self, host='192.168.0.11', port=50000):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.conectado = False

    def conectar(self):
        try:
            self.socket.connect((self.host, self.port)) # Conecta el cliente al servidor
            self.conectado = True
            print(f"Conectado al servidor {self.host}:{self.port}")
            print("Escribe mensajes y pulsa Enter.")
            print("Escribe '/salir' para desconectarte.\n")
        except Exception as e:
            print(f"No se pudo conectar al servidor: {e}")
            sys.exit() # Si no se puede conectar, sale del programa, para evitar intentos infinitos de conexión

    def recibir_mensajes(self):
        while self.conectado:
            try:
                mensaje = self.socket.recv(1024) # Espera mensajes del servidor
                if not mensaje:
                    print("\nSe perdió la conexión")
                    self.desconectar() # Si no hay mensaje, se desconecta
                    break
                print(mensaje.decode('utf-8'), end='')
            except:
                if self.conectado:
                    print("\nSe perdió la conexión")
                self.desconectar() # Se desconecta en caso de un error
                break

    def enviar_mensajes(self):
        while self.conectado:
            try:
                texto = input("")
                if texto.lower().strip() == "/salir":
                    self.socket.send("/salir".encode('utf-8'))
                    self.desconectar() # Envía el comando de salir al servidor y se desconecta
                    break
                self.socket.send(f"{texto}\n".encode('utf-8'))
            except:
                self.desconectar() # Se desconecta en caso de un error
                break

    def desconectar(self):
        if self.conectado:
            self.conectado = False
            try:
                self.socket.close() # Cierra la conexión con el servidor cuando el cliente se sale del chat
            except:
                pass
            print("\nTe has desconectado del chat.")

    def iniciar(self):
        self.conectar() # Conecta al cliente al servidor
        
        hilo_recepcion = threading.Thread(target=self.recibir_mensajes) # Enlaza un hilo para recibir los mensajes del servidor
        hilo_recepcion.daemon = True
        hilo_recepcion.start() # Inicia el hilo de recepción de mensajes

        self.enviar_mensajes() # Un hilo principal que envia los mensajes al servidor

if __name__ == "__main__": 
    cliente = ChatClient(host='192.168.0.11', port=50000)
    cliente.iniciar() # Inicia el cliente