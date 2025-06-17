const net = require('net');

class SimpleWorker {
    constructor(host = 'localhost', port = 5000) {
        this.host = host;
        this.port = port;
    }

    sendRequest(message) {
        return new Promise((resolve, reject) => {
            const client = new net.Socket();
            client.connect(this.port, this.host, () => {
                // Agregar \n para el formato esperado
                client.write(message + '\n');
            });

            client.on('data', (data) => {
                resolve(data.toString());
                client.destroy(); // Cerrar la conexión
            });

            client.on('error', (err) => {
                reject(`ERROR|CONNECTION_FAILED|${err.message}`);
            });
        });
    }

    async checkStatus() {
        const response = await this.sendRequest('STATUS');
        console.log(`Estado del servidor: ${response}`);
        return response;
    }

    async trainModel(inputData, outputData) {
        const message = `TRAIN|${inputData}|${outputData}`;
        const response = await this.sendRequest(message);
        console.log(`Resultado entrenamiento: ${response}`);
        return response;
    }

    async predict(modelId, inputData) {
        const message = `PREDICT|${modelId}|${inputData}`;
        const response = await this.sendRequest(message);
        console.log(`Resultado predicción: ${response}`);
        return response;
    }
}

async function main() {
    const args = process.argv.slice(2);
    if (args.length < 1) {
        console.log("Uso: node worker.js <host> [puerto]");
        console.log("Ejemplo: node worker.js localhost 5000");
        process.exit(1);
    }

    const host = args[0];
    const port = args[1] ? parseInt(args[1]) : 5000;

    const worker = new SimpleWorker(host, port);

    console.log(`=== Worker Simple para Sistema Distribuido IA ===`);
    console.log(`Conectando a ${host}:${port}`);

    // Verificar estado
    await worker.checkStatus();

    // Aquí puedes agregar más lógica para entrenar modelos o hacer predicciones
}

// Ejecutar el worker
main().catch(err => console.error(err));