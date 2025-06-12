import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
import threading

class ClientGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cliente Sistema Distribuido IA")
        self.root.geometry("800x600")
        
        self.leader_address = None
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Sección de conexión
        conn_frame = ttk.LabelFrame(main_frame, text="Conexión", padding="10")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(conn_frame, text="Servidor:").grid(row=0, column=0, sticky=tk.W)
        self.server_entry = ttk.Entry(conn_frame, width=20)
        self.server_entry.insert(0, "127.0.0.1")
        self.server_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(conn_frame, text="Puerto:").grid(row=0, column=2, sticky=tk.W)
        self.port_entry = ttk.Entry(conn_frame, width=10)
        self.port_entry.insert(0, "5000")
        self.port_entry.grid(row=0, column=3, padx=5)
        
        self.connect_btn = ttk.Button(conn_frame, text="Conectar", 
                                     command=self.connect)
        self.connect_btn.grid(row=0, column=4, padx=5)
        
        # Tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Tab Entrenamiento
        train_frame = ttk.Frame(notebook)
        notebook.add(train_frame, text="Entrenamiento")
        
        ttk.Label(train_frame, text="Datos de entrada (ejemplo: 1;2,3;4,5;6):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_text = scrolledtext.ScrolledText(train_frame, height=5, width=50)
        self.input_text.insert("1.0", "1;2,3;4,5;6")
        self.input_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        ttk.Label(train_frame, text="Datos de salida (ejemplo: 3,7,11):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_text = scrolledtext.ScrolledText(train_frame, height=5, width=50)
        self.output_text.insert("1.0", "3,7,11")
        self.output_text.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
        self.train_btn = ttk.Button(train_frame, text="Entrenar Modelo", 
                                   command=self.train_model)
        self.train_btn.grid(row=4, column=0, pady=10)
        
        # Tab Predicción
        predict_frame = ttk.Frame(notebook)
        notebook.add(predict_frame, text="Predicción")
        
        ttk.Label(predict_frame, text="ID del Modelo:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.model_id_entry = ttk.Entry(predict_frame, width=40)
        self.model_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(predict_frame, text="Datos de entrada (ejemplo: 7;8):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.predict_input = ttk.Entry(predict_frame, width=40)
        self.predict_input.insert(0, "7;8")
        self.predict_input.grid(row=1, column=1, padx=5, pady=5)
        
        self.predict_btn = ttk.Button(predict_frame, text="Predecir", 
                                     command=self.predict)
        self.predict_btn.grid(row=2, column=0, pady=10)
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()  # Forzar actualización de la UI
        
    def connect(self):
        self.connect_btn.config(text="Conectando...", state="disabled")
        threading.Thread(target=self._connect_thread, daemon=True).start()
    
    def _connect_thread(self):
        server = self.server_entry.get()
        port = int(self.port_entry.get())
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((server, port))
            sock.send(b"STATUS\n")
            response = sock.recv(1024).decode()
            sock.close()
            
            # Actualizar UI en hilo principal
            self.root.after(0, self._connection_success, server, port, response)
            
        except Exception as e:
            error_msg = str(e)
            # Actualizar UI en hilo principal
            self.root.after(0, self._connection_error, error_msg)
    
    def _connection_success(self, server, port, response):
        self.log(f"Conectado a {server}:{port} - Estado: {response}")
        self.connect_btn.config(text="Conectado", state="disabled")
        
    def _connection_error(self, error_msg):
        self.log(f"Error de conexión: {error_msg}")
        messagebox.showerror("Error", f"No se pudo conectar: {error_msg}")
        self.connect_btn.config(text="Conectar", state="normal")
    
    def train_model(self):
        threading.Thread(target=self._train_model_thread, daemon=True).start()
    
    def _train_model_thread(self):
        input_data = self.input_text.get("1.0", tk.END).strip()
        output_data = self.output_text.get("1.0", tk.END).strip()
        
        if not input_data or not output_data:
            self.root.after(0, self._show_warning, "Ingrese datos de entrada y salida")
            return
        
        server = self.server_entry.get()
        port = int(self.port_entry.get())
        
        try:
            self.root.after(0, self.log, "Enviando datos de entrenamiento...")
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            sock.connect((server, port))
            
            message = f"TRAIN|{input_data}|{output_data}"
            self.root.after(0, self.log, f"Mensaje a enviar: {message}")
            sock.send((message + '\n').encode())
            
            response = sock.recv(4096).decode()
            sock.close()
            
            self.root.after(0, self._handle_train_response, response)
                    
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, self.log, f"Error: {error_msg}")
            self.root.after(0, self._show_error, error_msg)
    
    def _handle_train_response(self, response):
        self.log(f"Respuesta del servidor: {response}")
        parts = response.split('|')
        if parts[0] == "OK":
            model_id = parts[1]
            self.log(f"Modelo entrenado exitosamente. ID: {model_id}")
            self.model_id_entry.delete(0, tk.END)
            self.model_id_entry.insert(0, model_id)
            messagebox.showinfo("Éxito", f"Modelo entrenado. ID: {model_id}")
        else:
            self.log(f"Error: {response}")
            messagebox.showerror("Error", response)
    
    def predict(self):
        threading.Thread(target=self._predict_thread, daemon=True).start()
    
    def _predict_thread(self):
        # Obtener valores de los campos
        model_id = self.model_id_entry.get().strip()
        input_data = self.predict_input.get().strip()
        
        # Debug: Imprimir valores
        self.root.after(0, self.log, f"Model ID: '{model_id}'")
        self.root.after(0, self.log, f"Input data: '{input_data}'")
        
        if not model_id:
            self.root.after(0, self._show_warning, "Ingrese ID del modelo")
            return
            
        if not input_data:
            self.root.after(0, self._show_warning, "Ingrese datos de entrada")
            return
        
        server = self.server_entry.get()
        port = int(self.port_entry.get())
        
        try:
            self.root.after(0, self.log, "Realizando predicción...")
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((server, port))
            
            # Construir mensaje asegurándose de que no haya valores vacíos
            message = f"PREDICT|{model_id}|{input_data}"
            self.root.after(0, self.log, f"Mensaje a enviar: '{message}'")
            self.root.after(0, self.log, f"Longitud del mensaje: {len(message)}")
            
            # Enviar mensaje
            sock.send((message + '\n').encode('utf-8'))
            
            # Recibir respuesta
            response = sock.recv(1024).decode('utf-8')
            sock.close()
            
            self.root.after(0, self._handle_predict_response, response)
                
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, self.log, f"Error: {error_msg}")
            self.root.after(0, self._show_error, error_msg)
    
    def _handle_predict_response(self, response):
        self.log(f"Respuesta del servidor: {response}")
        parts = response.split('|')
        if parts[0] == "OK":
            prediction = parts[1]
            self.log(f"Predicción: {prediction}")
            messagebox.showinfo("Resultado", f"Predicción: {prediction}")
        else:
            self.log(f"Error: {response}")
            messagebox.showerror("Error", response)
    
    def _show_warning(self, message):
        messagebox.showwarning("Advertencia", message)
    
    def _show_error(self, message):
        messagebox.showerror("Error", message)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    client = ClientGUI()
    client.run()