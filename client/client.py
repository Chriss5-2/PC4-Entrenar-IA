import socket
import sys

class SimpleClient:
    def __init__(self, host="localhost", port=5000):
        self.host = host
        self.port = port
    
    def send_request(self, message):
        """Envía una solicitud al servidor y retorna la respuesta"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            # Agregar \n para Java workers
            sock.send((message + '\n').encode())
            response = sock.recv(4096).decode()
            sock.close()
            return response
        except Exception as e:
            return f"ERROR|CONNECTION_FAILED|{e}"
    
    def check_status(self):
        """Verifica el estado del servidor"""
        response = self.send_request("STATUS")
        print(f"Estado del servidor: {response}")
        return response
    
    def train_model(self, input_data, output_data):
        """Entrena un modelo con los datos proporcionados"""
        message = f"TRAIN|{input_data}|{output_data}"
        response = self.send_request(message)
        print(f"Resultado entrenamiento: {response}")
        return response
    
    def predict(self, model_id, input_data):
        """Hace una predicción usando el modelo especificado"""
        message = f"PREDICT|{model_id}|{input_data}"
        response = self.send_request(message)
        print(f"Resultado predicción: {response}")
        return response

def main():
    if len(sys.argv) < 2:
        print("Uso: python client.py <host> [puerto]")
        print("Ejemplo: python client.py localhost 5000")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    
    client = SimpleClient(host, port)
    
    print(f"=== Cliente Simple para Sistema Distribuido IA ===")
    print(f"Conectando a {host}:{port}")
    
    # Verificar estado
    client.check_status()
    
    while True:
        print("\nOpciones:")
        print("1. Verificar estado")
        print("2. Entrenar modelo")
        print("3. Hacer predicción")
        print("4. Salir")
        
        choice = input("Seleccione una opción (1-4): ").strip()
        
        if choice == "1":
            client.check_status()
            
        elif choice == "2":
            print("\nEntrenamiento de modelo:")
            print("IMPORTANTE: Use el mismo formato para entrada y salida")
            print("\nFormato 1 - Valores simples:")
            print("  Entrada: 1,2,3,4,5")
            print("  Salida: 2,4,6,8,10")
            print("\nFormato 2 - Valores múltiples (con ;):")
            print("  Entrada: 1;2,3;4,5;6")
            print("  Salida: 3,7,11")
            
            input_data = input("\nDatos de entrada: ").strip()
            output_data = input("Datos de salida: ").strip()
            
            if input_data and output_data:
                client.train_model(input_data, output_data)
            else:
                print("ERROR: Debe proporcionar datos de entrada y salida")
                
        elif choice == "3":
            model_id = input("ID del modelo: ").strip()
            print("\nFormato de entrada debe coincidir con el formato de entrenamiento:")
            print("  Si entrenó con valores simples: 15")
            print("  Si entrenó con valores múltiples: 7;8")
            input_data = input("\nDatos de entrada: ").strip()
            
            if model_id and input_data:
                client.predict(model_id, input_data)
            else:
                print("ERROR: Debe proporcionar ID del modelo y datos de entrada")
                
        elif choice == "4":
            print("¡Hasta luego!")
            break
            
        else:
            print("Opción inválida")

if __name__ == "__main__":
    main()