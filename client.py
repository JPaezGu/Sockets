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
            self.socket.connect((self.host, self.port))
            self.conectado = True
            print(f"¡Conectado al servidor {self.host}:{self.port}!")
            print("Escribe tus mensajes y pulsa Enter.")
            print("Escribe '/salir' para desconectarte.\n")
        except Exception as e:
            print(f"No se pudo conectar al servidor: {e}")
            sys.exit()

    def recibir_mensajes(self):
        while self.conectado:
            try:
                mensaje = self.socket.recv(1024)
                if not mensaje:
                    print("\nSe perdió la conexión")
                    self.desconectar()
                    break
                print(mensaje.decode('utf-8'), end='')
            except:
                if self.conectado:
                    print("\nSe perdió la conexión")
                self.desconectar()
                break

    def enviar_mensajes(self):
        while self.conectado:
            try:
                texto = input("")
                if texto.lower().strip() == "/salir":
                    self.socket.send("/salir".encode('utf-8'))
                    self.desconectar()
                    break
                self.socket.send(f"{texto}\n".encode('utf-8'))
            except:
                self.desconectar()
                break

    def desconectar(self):
        if self.conectado:
            self.conectado = False
            try:
                self.socket.close()
            except:
                pass
            print("\nTe has desconectado. ¡Hasta pronto!")

    def iniciar(self):
        self.conectar()
        
        # Hilo para recibir mensajes del servidor
        hilo_recepcion = threading.Thread(target=self.recibir_mensajes)
        hilo_recepcion.daemon = True
        hilo_recepcion.start()

        # El hilo principal se encarga de escribir mensajes
        self.enviar_mensajes()


# ============ INICIO ============
if __name__ == "__main__":
    # Puedes cambiar la IP y puerto aquí fácilmente
    # Ejemplo para conectar desde otro dispositivo en la misma red:
    # cliente = ChatClient(host='192.168.1.37', port=55555)
    
    cliente = ChatClient(host='192.168.0.11', port=50000)  # localhost por defecto
    cliente.iniciar()