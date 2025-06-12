import threading
from datetime import datetime
import json
import os

class Storage:
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.models = {}
        self.logs = []
        self.lock = threading.Lock()
        
    def save_model(self, model_id, model):
        """Guarda un modelo en memoria"""
        try:
            with self.lock:
                self.models[model_id] = model
                self.add_log(f"Model {model_id} saved")
                print(f"Storage: Modelo {model_id} guardado exitosamente")
        except Exception as e:
            print(f"Storage ERROR al guardar modelo: {e}")
            raise
            
    def load_model(self, model_id):
        """Carga un modelo de memoria"""
        with self.lock:
            return self.models.get(model_id)
    
    def get_model_count(self):
        """Retorna la cantidad de modelos almacenados"""
        with self.lock:
            return len(self.models)
    
    def add_log(self, message):
        """Agrega un log con timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        # NO usar lock aquí porque ya estamos dentro de un lock en save_model
        self.logs.append(log_entry)
        # Mantener solo los últimos 100 logs
        if len(self.logs) > 100:
            self.logs.pop(0)
    
    def get_recent_logs(self):
        """Retorna los logs recientes"""
        with self.lock:
            # Retornar los últimos 20 logs
            return "\n".join(self.logs[-20:])