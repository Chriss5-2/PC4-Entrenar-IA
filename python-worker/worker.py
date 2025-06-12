import socket
import threading
import time
import os
import sys
from concurrent.futures import ThreadPoolExecutor

# Importar los otros módulos
try:
    from raft_consensus import RaftConsensus
    from http_monitor import HttpMonitor
    from ml_model import MLModel
    from storage import Storage
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrate de que todos los archivos estén en el directorio")
    sys.exit(1)

class Worker:
    def __init__(self, worker_id, port, monitor_port):
        self.worker_id = worker_id
        self.port = port
        self.monitor_port = monitor_port
        self.storage = Storage(worker_id)
        self.raft = RaftConsensus(worker_id, port)
        self.monitor = HttpMonitor(monitor_port, self)
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = True
        self.server_socket = None
    
    def configure_peers(self):
        """Configura los peers del RAFT según el worker_id"""
        if self.worker_id == "python1":
            self.raft.add_peer("java1", "java-worker-1:5000")
            self.raft.add_peer("java2", "java-worker-2:5001")
            self.raft.add_peer("python2", "python-worker-2:5003")
        elif self.worker_id == "python2":
            self.raft.add_peer("java1", "java-worker-1:5000")
            self.raft.add_peer("java2", "java-worker-2:5001")
            self.raft.add_peer("python1", "python-worker-1:5002")

    def start(self):
        print(f"Iniciando Worker {self.worker_id} en puerto {self.port}")
        
        # Configurar peers
        self.configure_peers()
        
        # Iniciar monitor HTTP en thread separado
        monitor_thread = threading.Thread(target=self.start_monitor, daemon=True)
        monitor_thread.start()
        
        # Iniciar RAFT
        raft_thread = threading.Thread(target=self.raft.start, daemon=True)
        raft_thread.start()
        
        # Esperar un poco
        time.sleep(2)
        
        # Iniciar servidor principal con reintentos
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_socket.bind(('0.0.0.0', self.port))
                self.server_socket.listen(5)
                print(f"Worker {self.worker_id} escuchando exitosamente en puerto {self.port}")
                break
            except OSError as e:
                if e.errno == 98:  # Address already in use
                    retry_count += 1
                    print(f"Puerto {self.port} en uso, reintento {retry_count}/{max_retries} en 5 segundos...")
                    time.sleep(5)
                else:
                    raise
        
        if retry_count >= max_retries:
            print(f"No se pudo iniciar el worker después de {max_retries} intentos")
            return
        
        # Loop principal
        while self.running:
            try:
                client, addr = self.server_socket.accept()
                self.executor.submit(self.handle_client, client)
            except Exception as e:
                if self.running:
                    print(f"Error aceptando conexión: {e}")
    
    def start_monitor(self):
        """Inicia el monitor HTTP con manejo de errores"""
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.monitor.start()
                break
            except OSError as e:
                if e.errno == 98:  # Address already in use
                    retry_count += 1
                    print(f"Puerto monitor {self.monitor_port} en uso, reintento {retry_count}/{max_retries}...")
                    time.sleep(5)
                else:
                    print(f"Error iniciando monitor: {e}")
                    break
    
    def handle_client(self, client):
        """Maneja las peticiones del cliente"""
        response = None
        try:
            # Recibir datos
            data = client.recv(4096).decode()
            if not data:
                client.close()
                return
            
            # Quitar saltos de línea y espacios
            data = data.strip()
            
            print(f"Worker {self.worker_id} recibió: {data}")
            parts = data.split('|')
            
            if len(parts) == 0:
                response = "ERROR|EMPTY_REQUEST"
            else:
                command = parts[0]
                
                # Procesar comando
                if command == 'TRAIN':
                    response = self.handle_training(parts)
                    print(f"DEBUG: handle_training retornó: {response}")
                elif command == 'PREDICT':
                    response = self.handle_prediction(parts)
                elif command == 'STATUS':
                    response = f"OK|{self.raft.get_state()}|Leader:{self.raft.leader_id}"
                elif command == 'REPLICATE':
                    if len(parts) > 1:
                        self.handle_replication(parts[1])
                    response = "OK"
                else:
                    response = f"ERROR|UNKNOWN_COMMAND|{command}"
            
            # CRÍTICO: Siempre enviar respuesta
            if response is None:
                response = "ERROR|NO_RESPONSE_GENERATED"
            
            print(f"Worker {self.worker_id} enviando respuesta: {response}")
            response_bytes = response.encode()
            total_sent = 0
            
            # Asegurar que se envíen todos los bytes
            while total_sent < len(response_bytes):
                sent = client.send(response_bytes[total_sent:])
                if sent == 0:
                    raise RuntimeError("Socket connection broken")
                total_sent += sent
            
            print(f"Worker {self.worker_id} respuesta enviada completamente ({total_sent} bytes)")
            
        except Exception as e:
            print(f"ERROR en handle_client: {e}")
            import traceback
            traceback.print_exc()
            
            # Intentar enviar error
            if response is None:
                try:
                    error_msg = f"ERROR|EXCEPTION|{str(e)}"
                    client.send(error_msg.encode())
                except:
                    print("No se pudo enviar mensaje de error")
        finally:
            print(f"Worker {self.worker_id} cerrando conexión con cliente")
            try:
                client.close()
            except:
                pass
    
    def handle_training(self, parts):
        """Maneja el entrenamiento de modelos"""
        print(f"DEBUG handle_training: Iniciando con parts={parts}")
        
        if len(parts) < 3:
            return "ERROR|INVALID_REQUEST|Se requieren 3 partes"
            
        model_id = self.generate_model_id()
        input_data = parts[1]
        output_data = parts[2]
        
        print(f"DEBUG: model_id={model_id}")
        
        try:
            # Entrenar el modelo localmente
            print("DEBUG: Creando MLModel")
            model = MLModel(model_id)
            
            print("DEBUG: Iniciando entrenamiento")
            model.train(input_data, output_data)
            
            print("DEBUG: Guardando modelo")
            self.storage.save_model(model_id, model)
            
            print(f"Modelo {model_id} entrenado exitosamente en {self.worker_id}")
            
            # Si somos líder, replicar (pero no bloquear)
            if self.raft.is_leader():
                try:
                    model_data = f"MODEL|{model_id}|{model.serialize()}"
                    self.raft.replicate(model_data)
                except Exception as e:
                    print(f"Error replicando: {e}")
            
            # IMPORTANTE: Siempre retornar respuesta
            result = f"OK|{model_id}"
            print(f"DEBUG handle_training: Retornando: {result}")
            return result
            
        except Exception as e:
            error_msg = f"Error en entrenamiento: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return f"ERROR|TRAINING_FAILED|{str(e)}"
    
    def handle_prediction(self, parts):
        """Maneja las predicciones"""
        if len(parts) < 3:
            return "ERROR|INVALID_REQUEST|Se requieren 3 partes"
            
        model_id = parts[1]
        input_data = parts[2]
        
        model = self.storage.load_model(model_id)
        if not model:
            return f"ERROR|MODEL_NOT_FOUND|{model_id}"
        
        try:
            prediction = model.predict(input_data)
            return f"OK|{prediction}"
        except Exception as e:
            return f"ERROR|PREDICTION_FAILED|{str(e)}"
    
    def handle_replication(self, data):
        """Maneja la replicación de modelos"""
        try:
            if data and '|' in data:
                parts = data.split('|')
                if parts[0] == 'MODEL' and len(parts) >= 3:
                    model_id = parts[1]
                    model_data = parts[2]
                    model = MLModel(model_id)
                    model.deserialize(model_data)
                    self.storage.save_model(model_id, model)
                    print(f"Modelo {model_id} replicado en {self.worker_id}")
        except Exception as e:
            print(f"Error en replicación: {e}")
    
    def generate_model_id(self):
        """Genera un ID único para el modelo"""
        timestamp = int(time.time() * 1000)
        return f"model_{timestamp}_{self.worker_id}"
    
    def stop(self):
        """Detiene el worker"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: worker.py <worker_id> <port> <monitor_port>")
        sys.exit(1)
        
    worker_id = sys.argv[1]
    port = int(sys.argv[2])
    monitor_port = int(sys.argv[3])
    
    print(f"=== Iniciando Python Worker ===")
    print(f"ID: {worker_id}")
    print(f"Puerto principal: {port}")
    print(f"Puerto monitor: {monitor_port}")
    
    try:
        worker = Worker(worker_id, port, monitor_port)
        worker.start()
    except KeyboardInterrupt:
        print("\nDeteniendo worker...")
        worker.stop()
    except Exception as e:
        print(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)