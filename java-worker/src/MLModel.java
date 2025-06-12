public class MLModel {
    private String modelId;
    private double[] weights;
    private double bias;
    private int inputSize;
    
    public MLModel(String modelId) {
        this.modelId = modelId;
    }
    
    public void train(String inputData, String outputData) {
        // Implementación simple de regresión lineal
        String[] inputs = inputData.split(",");
        String[] outputs = outputData.split(",");
          // Determinar el tamaño de entrada - flexible con separadores
        if (inputs[0].contains(";")) {
            inputSize = inputs[0].split(";").length;
        } else if (inputs[0].contains(",")) {
            inputSize = inputs[0].split(",").length;
        } else {
            inputSize = 1; // Entrada simple
        }
        
        weights = new double[inputSize];
        
        // Gradiente descendente simple
        double learningRate = 0.01;
        int epochs = 100;
        
        for (int epoch = 0; epoch < epochs; epoch++) {
            for (int i = 0; i < inputs.length; i++) {
                double[] x = parseInput(inputs[i]);
                double y = Double.parseDouble(outputs[i]);
                
                double prediction = predict(x);
                double error = y - prediction;
                
                // Actualizar pesos
                for (int j = 0; j < weights.length; j++) {
                    weights[j] += learningRate * error * x[j];
                }
                bias += learningRate * error;
            }
        }
    }
    
    public String predict(String inputData) {
        double[] x = parseInput(inputData);
        return String.valueOf(predict(x));
    }
    
    private double predict(double[] x) {
        double result = bias;
        for (int i = 0; i < weights.length && i < x.length; i++) {
            result += weights[i] * x[i];
        }
        return result;
    }
      private double[] parseInput(String input) {
        // Ser flexible: aceptar tanto ; como , como separador
        String[] parts;
        if (input.contains(";")) {
            parts = input.split(";");
        } else if (input.contains(",")) {
            parts = input.split(",");
        } else {
            // Un solo valor
            return new double[]{Double.parseDouble(input.trim())};
        }
        
        double[] result = new double[parts.length];
        for (int i = 0; i < parts.length; i++) {
            result[i] = Double.parseDouble(parts[i].trim());
        }
        return result;
    }
    
    public String serialize() {
        StringBuilder sb = new StringBuilder();
        sb.append(inputSize).append("|");
        sb.append(bias).append("|");
        for (double w : weights) {
            sb.append(w).append(";");
        }
        return sb.toString();
    }
    
    public void deserialize(String data) {
        String[] parts = data.split("\\|");
        if (parts.length >= 3) {
            inputSize = Integer.parseInt(parts[0]);
            bias = Double.parseDouble(parts[1]);
            String[] weightParts = parts[2].split(";");
            weights = new double[inputSize];
            for (int i = 0; i < inputSize && i < weightParts.length; i++) {
                if (!weightParts[i].isEmpty()) {
                    weights[i] = Double.parseDouble(weightParts[i]);
                }
            }
        }
    }
}