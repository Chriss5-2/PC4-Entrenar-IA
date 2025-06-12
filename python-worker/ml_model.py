class MLModel:
    def __init__(self, model_id):
        self.model_id = model_id
        self.weights = []
        self.bias = 0.0
        self.input_size = 0
    
    def train(self, input_data, output_data):
        print(f"DEBUG: Iniciando entrenamiento con input_data={input_data}, output_data={output_data}")
        
        # Parse training data
        inputs = input_data.split(',')
        outputs = output_data.split(',')
        
        if not inputs or not outputs:
            raise ValueError("Datos de entrenamiento vacíos")
        
        if len(inputs) != len(outputs):
            raise ValueError(f"Cantidad de entradas ({len(inputs)}) no coincide con salidas ({len(outputs)})")
        
        # Determinar el formato de entrada del primer ejemplo
        first_input = inputs[0].strip()
        if ';' in first_input:
            # Formato múltiple: "1;2"
            self.input_size = len(first_input.split(';'))
        else:
            # Formato simple: "1"
            self.input_size = 1
        
        self.weights = [0.0] * self.input_size
        
        print(f"DEBUG: Input size detectado: {self.input_size}")
        
        # Simple gradient descent
        learning_rate = 0.01
        epochs = 100
        
        for epoch in range(epochs):
            total_error = 0
            for i in range(len(inputs)):
                try:
                    x = self._parse_input(inputs[i])
                    y = float(outputs[i])
                    
                    # Forward pass
                    prediction = self._predict(x)
                    error = y - prediction
                    total_error += error ** 2
                    
                    # Update weights
                    for j in range(len(self.weights)):
                        if j < len(x):  # Verificar índice
                            self.weights[j] += learning_rate * error * x[j]
                    self.bias += learning_rate * error
                except Exception as e:
                    print(f"Error en epoch {epoch}, ejemplo {i}: {e}")
                    raise
        
        print(f"DEBUG: Entrenamiento completado. Weights: {self.weights}, Bias: {self.bias}")
    
    def predict(self, input_data):
        x = self._parse_input(input_data)
        prediction = self._predict(x)
        return str(prediction)
    
    def _predict(self, x):
        result = self.bias
        for i in range(min(len(self.weights), len(x))):
            result += self.weights[i] * x[i]
        return result
    
    def _parse_input(self, input_str):
        input_str = input_str.strip()
        
        # Manejar diferentes formatos
        if ';' in input_str:
            # Formato múltiple: "1;2"
            parts = input_str.split(';')
        else:
            # Formato simple: "1" 
            parts = [input_str]
        
        # Convertir a float y validar
        result = []
        for part in parts:
            try:
                result.append(float(part.strip()))
            except ValueError:
                raise ValueError(f"No se puede convertir '{part}' a número")
        
        # Asegurar que el tamaño coincida con lo esperado
        if self.input_size > 0 and len(result) != self.input_size:
            raise ValueError(f"Entrada tiene {len(result)} valores, se esperaban {self.input_size}")
        
        return result
    
    def serialize(self):
        weights_str = ';'.join(str(w) for w in self.weights)
        return f"{self.input_size}|{self.bias}|{weights_str}"
    
    def deserialize(self, data):
        parts = data.split('|')
        if len(parts) >= 3:
            self.input_size = int(parts[0])
            self.bias = float(parts[1])
            weight_parts = parts[2].split(';')
            self.weights = []
            for w in weight_parts:
                if w:  # Ignorar strings vacíos
                    self.weights.append(float(w))