import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import socket
from server import ChatServer  # Importa la clase del servidor para poder iniciarlo desde el cliente (opcional)

class ChatGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Cliente - Socket Bidireccional")
        self.window.geometry("750x450")
        self.window.configure(bg="#1e272e")
        self.window.resizable(False, False)

        self.HOST = '192.168.0.11'     # IP y Puerto al que se conecta el cliente
        self.PORT = 50000

        self.socket = None
        self.conectado = False

        self.crear_interfaz()
        self.conectar_al_servidor()

    def crear_interfaz(self):
        # === Título ===
        titulo = tk.Label(self.window, text="CHAT MULTIUSUARIO", font=("Consolas", 18, "bold"),
                          bg="#1e272e", fg="#00d2ff")
        titulo.pack(pady=10)

        # === Área de chat ===
        self.area_chat = scrolledtext.ScrolledText(
            self.window, wrap=tk.WORD, width=72, height=17, # tamaño del área de texto
            state='disabled', bg="#0f1419", fg="#ffffff",
            font=("Segoe UI", 10), insertbackground="white"
        )
        self.area_chat.pack(padx=15, pady=10)

        self.area_chat.tag_config("propio", foreground="#00ff9d", font=("Segoe UI", 10, "bold"))
        self.area_chat.tag_config("otros", foreground="#ffffff")
        self.area_chat.tag_config("sistema", foreground="#ff9f1c", font=("Segoe UI", 9, "italic")) # Colores para mensajes del sistema
        self.area_chat.tag_config("error", foreground="#ff5555")

        frame_inf = tk.Frame(self.window, bg="#1e272e")
        frame_inf.pack(pady=8)

        self.entrada = tk.Entry(frame_inf, width=42, font=("Segoe UI", 11), # Imput de texto para envio de mensajes
                                bg="#2d3436", fg="white", insertbackground="white")
        self.entrada.pack(side=tk.LEFT, padx=5)
        self.entrada.bind("<Return>", self.enviar_mensaje)
        self.entrada.focus()

        btn_enviar = tk.Button(frame_inf, text="Enviar", width=10, height=1,  # Botón para enviar mensajes
                               bg="#00d2ff", fg="black", font=("Arial", 10, "bold"),
                               command=self.enviar_mensaje)
        btn_enviar.pack(side=tk.LEFT, padx=5)

        btn_desconectar = tk.Button(frame_inf, text="Desconectar", width=12, height=1,
                                    bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), # Botón para desconectar del servidor
                                    command=self.desconectar)
        btn_desconectar.pack(side=tk.LEFT, padx=5)

    def conectar_al_servidor(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Iteración del socket
            self.socket.connect((self.HOST, self.PORT))
            self.conectado = True
            self.mostrar_mensaje("Conectado al servidor correctamente.\n", "sistema")

            hilo = threading.Thread(target=self.recibir_mensajes, daemon=True) # Iteración de hilo por usuario para recibir mensajes
            hilo.start()
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar al servidor:\n{e}")
            self.window.destroy() # Elimina la ventana si no se puede conectar

    def recibir_mensajes(self):
        while self.conectado:
            try:
                mensaje = self.socket.recv(1024).decode('utf-8') 
                if mensaje:
                   
                    self.mostrar_mensaje(mensaje, "otros") # Muestra mensajes recibidos de otros usuarios
                else:
                    break
            except:
                if self.conectado:
                    self.mostrar_mensaje("ERROR: Conexión perdida con el servidor.\n", "error")
                break
        self.desconectar() # Se desconecta si se pierde la conexión

    def mostrar_mensaje(self, texto, tipo="otros"):
        self.area_chat.config(state='normal')
        self.area_chat.insert(tk.END, texto, tipo) # Envía el mensaje en el área de chat con el formato default
        self.area_chat.config(state='disabled')
        self.area_chat.see(tk.END) # Desplaza automáticamente al final del área de chat

    def enviar_mensaje(self, event=None):
        mensaje = self.entrada.get().strip() # Obtiene el mensaje del input
        if not mensaje:
            return

        if not self.conectado:
            messagebox.showwarning("Desconectado", "No estás conectado al servidor.") # Mensaje de advertencia si no está conectado
            return

        if mensaje.lower() == "/salir":
            self.desconectar() # Opción para desconectarse 
            return

        try:
            self.socket.send((mensaje + "\n").encode('utf-8')) # Envía el mensaje al servidor
            self.mostrar_mensaje(f"Tú: {mensaje}\n", "propio") # Muestra el mensaje enviado  por el propio usuario en el área de chat
            self.entrada.delete(0, tk.END) # Limpia el input después de enviar
        except: 
            self.mostrar_mensaje("ERROR: No se pudo enviar el mensaje.\n", "error")
            self.desconectar() # Se desconecta si no se puede enviar el mensaje

    def desconectar(self):
        if self.conectado:
            self.conectado = False
            try:
                self.socket.send("/salir".encode('utf-8'))
                self.socket.close() # Elimina el socket al desconectarse
            except:
                pass
            self.mostrar_mensaje("\nDesconectado del servidor.\n", "sistema")
            self.entrada.config(state='disabled')

    def cerrar_ventana(self):
        if messagebox.askokcancel("Salir", "¿Seguro que quieres cerrar el chat?"):
            self.desconectar()
            self.window.destroy() # Destruye el frame al cerrar la ventana

    def iniciar(self):
        self.window.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
        self.window.mainloop() # Mantiene la ventana abierta y en espera de interacciones

    def encender_servidor(self):
        servidor = ChatServer(port=50000)
        servidor.iniciar() # Inicia el servidor (opcional que esté en este archivo)

if __name__ == "__main__":
    app = ChatGUI()
    app.iniciar() # Inicia la aplicación GUI del chat