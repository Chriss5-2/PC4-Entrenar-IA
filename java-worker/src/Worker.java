import java.net.*;
import java.io.*;
import java.util.concurrent.*;

public class Worker {
    private int port;
    public String workerId;
    public RaftConsensus raft;
    public Storage storage;
    private HttpMonitor monitor;
    private ExecutorService executor;
    private ServerSocket serverSocket;
    private volatile boolean running = true;
    
    public Worker(String workerId, int port, int monitorPort) {
        this.workerId = workerId;
        this.port = port;
        this.executor = Executors.newCachedThreadPool();
        this.storage = new Storage(workerId);
        this.raft = new RaftConsensus(workerId, port);
        this.monitor = new HttpMonitor(monitorPort, this);
    }
    
    private void configurePeers() {
        if (workerId.equals("java1")) {
            raft.addPeer("java2", "java-worker-2", 5001);
            raft.addPeer("python1", "python-worker-1", 5002);
            raft.addPeer("python2", "python-worker-2", 5003);
        } else if (workerId.equals("java2")) {
            raft.addPeer("java1", "java-worker-1", 5000);
            raft.addPeer("python1", "python-worker-1", 5002);
            raft.addPeer("python2", "python-worker-2", 5003);
        }
    }

    public void start() {
        configurePeers();
        
        // Iniciar monitor HTTP
        executor.submit(() -> {
            try {
                monitor.start();
            } catch (Exception e) {
                System.err.println("Error en monitor HTTP: " + e.getMessage());
            }
        });
        
        // Iniciar módulo RAFT
        executor.submit(() -> {
            try {
                raft.start();
            } catch (Exception e) {
                System.err.println("Error en RAFT: " + e.getMessage());
            }
        });
        
        // Esperar un poco para que RAFT se estabilice
        try {
            Thread.sleep(3000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        // Iniciar servidor principal con reintentos
        int retries = 0;
        while (retries < 5 && running) {
            try {
                serverSocket = new ServerSocket();
                serverSocket.setReuseAddress(true);
                serverSocket.bind(new InetSocketAddress("0.0.0.0", port), 50);
                System.out.println("Worker " + workerId + " iniciado exitosamente en puerto " + port);
                break;
            } catch (IOException e) {
                retries++;
                System.err.println("Intento " + retries + " fallido: " + e.getMessage());
                if (retries < 5) {
                    try {
                        Thread.sleep(2000);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        return;
                    }
                } else {
                    System.err.println("No se pudo iniciar el servidor después de 5 intentos");
                    return;
                }
            }
        }
        
        // Loop principal del servidor
        while (running) {
            try {
                Socket client = serverSocket.accept();
                executor.submit(() -> handleClient(client));
            } catch (IOException e) {
                if (running) {
                    System.err.println("Error aceptando conexión: " + e.getMessage());
                }
            }
        }
    }
    
    private void handleClient(Socket client) {
        try {
            client.setSoTimeout(10000); // 10 segundos timeout
            
            BufferedReader in = new BufferedReader(
                new InputStreamReader(client.getInputStream(), "UTF-8")
            );
            PrintWriter out = new PrintWriter(
                new OutputStreamWriter(client.getOutputStream(), "UTF-8"), true
            );
            
            String request = in.readLine();
            
            if (request == null) {
                out.println("ERROR|NULL_REQUEST");
                return;
            }
            
            request = request.trim();
            
            if (request.isEmpty()) {
                out.println("ERROR|EMPTY_REQUEST");
                return;
            }
            
            System.out.println("\n=== Nueva petición en " + workerId + " ===");
            System.out.println("Request completo: '" + request + "'");
            System.out.println("Longitud: " + request.length() + " caracteres");
            
            String[] parts = request.split("\\|", -1);
            System.out.println("Partes encontradas: " + parts.length);
            for (int i = 0; i < parts.length; i++) {
                System.out.println("  Parte[" + i + "]: '" + parts[i] + "'");
            }
            
            if (parts.length == 0 || parts[0].isEmpty()) {
                out.println("ERROR|INVALID_REQUEST|Sin comando");
                return;
            }
            
            String command = parts[0].toUpperCase();
            
            switch (command) {
                case "TRAIN":
                    handleTraining(parts, out);
                    break;
                case "PREDICT":
                    handlePrediction(parts, out);
                    break;
                case "STATUS":
                    out.println("OK|" + raft.getState() + "|Leader:" + raft.getLeaderId());
                    break;
                case "REPLICATE":
                    if (parts.length > 1) {
                        handleReplication(parts[1]);
                    }
                    out.println("OK");
                    break;
                default:
                    out.println("ERROR|UNKNOWN_COMMAND|" + command);
            }
            
        } catch (SocketTimeoutException e) {
            System.err.println("Timeout leyendo del cliente");
            try {
                PrintWriter out = new PrintWriter(client.getOutputStream(), true);
                out.println("ERROR|TIMEOUT");
            } catch (IOException ioe) {
                // Ignorar
            }
        } catch (Exception e) {
            System.err.println("Error procesando cliente: " + e.getMessage());
            e.printStackTrace();
            try {
                PrintWriter out = new PrintWriter(client.getOutputStream(), true);
                out.println("ERROR|SERVER_ERROR|" + e.getMessage());
            } catch (IOException ioe) {
                // Ignorar
            }
        } finally {
            try {
                if (!client.isClosed()) {
                    client.close();
                }
            } catch (IOException e) {
                // Ignorar
            }
        }
    }
    
    private void handleTraining(String[] parts, PrintWriter out) {
        System.out.println("\n--- Procesando TRAIN ---");
        
        if (parts.length < 3) {
            String error = "Se requieren 3 partes: TRAIN|input_data|output_data. Recibidas: " + parts.length;
            System.err.println(error);
            out.println("ERROR|INVALID_REQUEST|" + error);
            return;
        }
        
        String inputData = parts[1];
        String outputData = parts[2];
        
        if (inputData.isEmpty() || outputData.isEmpty()) {
            out.println("ERROR|INVALID_REQUEST|Datos de entrada o salida vacíos");
            return;
        }
        
        String modelId = generateModelId();
        System.out.println("Generado model ID: " + modelId);
        System.out.println("Input data: " + inputData);
        System.out.println("Output data: " + outputData);
        
        try {
            MLModel model = new MLModel(modelId);
            model.train(inputData, outputData);
            storage.saveModel(modelId, model);
            System.out.println("Modelo entrenado y guardado exitosamente");
            
            // Replicar si es necesario
            String modelData = "MODEL|" + modelId + "|" + model.serialize();
            if (raft.isLeader()) {
                raft.replicate(modelData);
            }
            
            out.println("OK|" + modelId);
            System.out.println("Respuesta enviada: OK|" + modelId);
            
        } catch (Exception e) {
            String error = "Error entrenando: " + e.getMessage();
            System.err.println(error);
            e.printStackTrace();
            out.println("ERROR|TRAINING_FAILED|" + error);
        }
    }
    
    private void handlePrediction(String[] parts, PrintWriter out) {
        System.out.println("\n--- Procesando PREDICT ---");
        
        if (parts.length < 3) {
            String error = "Se requieren 3 partes: PREDICT|model_id|input_data. Recibidas: " + parts.length;
            System.err.println(error);
            out.println("ERROR|INVALID_REQUEST|" + error);
            return;
        }
        
        String modelId = parts[1];
        String inputData = parts[2];
        
        if (modelId.isEmpty()) {
            out.println("ERROR|INVALID_REQUEST|model_id vacío");
            return;
        }
        
        if (inputData.isEmpty()) {
            out.println("ERROR|INVALID_REQUEST|input_data vacío");
            return;
        }
        
        System.out.println("Model ID: " + modelId);
        System.out.println("Input data: " + inputData);
        
        MLModel model = storage.loadModel(modelId);
        if (model == null) {
            System.err.println("Modelo no encontrado: " + modelId);
            out.println("ERROR|MODEL_NOT_FOUND|" + modelId);
            return;
        }
        
        try {
            String prediction = model.predict(inputData);
            System.out.println("Predicción: " + prediction);
            out.println("OK|" + prediction);
            
        } catch (Exception e) {
            String error = "Error en predicción: " + e.getMessage();
            System.err.println(error);
            e.printStackTrace();
            out.println("ERROR|PREDICTION_FAILED|" + error);
        }
    }
    
    private void handleReplication(String data) {
        try {
            if (data != null && data.contains("|")) {
                String[] parts = data.split("\\|");
                if (parts[0].equals("MODEL") && parts.length >= 3) {
                    String modelId = parts[1];
                    String modelData = parts[2];
                    
                    MLModel model = new MLModel(modelId);
                    model.deserialize(modelData);
                    storage.saveModel(modelId, model);
                    System.out.println("Modelo " + modelId + " replicado exitosamente");
                }
            }
        } catch (Exception e) {
            System.err.println("Error en replicación: " + e.getMessage());
        }
    }
    
    private String generateModelId() {
        return "model_" + System.currentTimeMillis() + "_" + workerId;
    }
    
    public void shutdown() {
        running = false;
        try {
            if (serverSocket != null && !serverSocket.isClosed()) {
                serverSocket.close();
            }
        } catch (IOException e) {
            // Ignorar
        }
        executor.shutdown();
    }
    
    public static void main(String[] args) {
        if (args.length < 3) {
            System.err.println("Uso: Worker <workerId> <port> <monitorPort>");
            System.exit(1);
        }
        
        String workerId = args[0];
        int port = Integer.parseInt(args[1]);
        int monitorPort = Integer.parseInt(args[2]);
        
        System.out.println("=== Iniciando Worker ===");
        System.out.println("ID: " + workerId);
        System.out.println("Puerto: " + port);
        System.out.println("Puerto Monitor: " + monitorPort);
        
        Worker worker = new Worker(workerId, port, monitorPort);
        
        // Shutdown hook
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("\nApagando worker " + workerId + "...");
            worker.shutdown();
        }));
        
        try {
            worker.start();
        } catch (Exception e) {
            System.err.println("Error fatal: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}