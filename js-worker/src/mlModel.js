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
                // Agregar \n para el servidor
                client.write(message + '\n');
            });

            client.on('data', (data) => {
                resolve(data.toString());
                client.destroy(); // Cierra la conexión
            });

            client.on('error', (err) => {
                reject(`ERROR|CONNECTION_FAILED|${err.message}`);
            });
        });
    }

    async checkStatus() {
        try {
            const response = await this.sendRequest('STATUS');
            console.log(`Estado del servidor: ${response}`);
            return response;
        } catch (error) {
            console.error(error);
        }
    }

    async trainModel(inputData, outputData) {
        const message = `TRAIN|${inputData}|${outputData}`;
        try {
            const response = await this.sendRequest(message);
            console.log(`Resultado entrenamiento: ${response}`);
            return response;
        } catch (error) {
            console.error(error);
        }
    }

    async predict(modelId, inputData) {
        const message = `PREDICT|${modelId}|${inputData}`;
        try {
            const response = await this.sendRequest(message);
            console.log(`Resultado predicción: ${response}`);
            return response;
        } catch (error) {
            console.error(error);
        }
    }
}

// Función principal para ejecutar el worker
async function main() {
    const args = process.argv.slice(2);
    const host = args[0] || 'localhost';
    const port = parseInt(args[1]) || 5000;

    const worker = new SimpleWorker(host, port);

    console.log(`=== Worker Simple para Sistema Distribuido IA ===`);
    console.log(`Conectando a ${host}:${port}`);

    // Verificar estado
    await worker.checkStatus();

    // Aquí puedes agregar más lógica para interactuar con el worker
    // como entrenar modelos o hacer predicciones.
}

// Ejecutar el worker
main().catch(console.error);