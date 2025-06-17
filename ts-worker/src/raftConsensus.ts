// filepath: ts-worker/src/raftConsensus.ts
import * as net from 'net';

export class SimpleWorker {
    private host: string;
    private port: number;

    constructor(host = 'localhost', port = 5005) {
        this.host = host;
        this.port = port;
    }

    sendRequest(message: string): Promise<string> {
        return new Promise((resolve, reject) => {
            const client = new net.Socket();
            client.connect(this.port, this.host, () => {
                client.write(message + '\n');
            });

            client.on('data', (data) => {
                resolve(data.toString());
                client.destroy(); // Close the connection
            });

            client.on('error', (err) => {
                reject(`ERROR|CONNECTION_FAILED|${err.message}`);
            });
        });
    }

    async checkStatus(): Promise<string> {
        const response = await this.sendRequest('STATUS');
        console.log(`Estado del servidor: ${response}`);
        return response;
    }

    async trainModel(inputData: string, outputData: string): Promise<string> {
        const message = `TRAIN|${inputData}|${outputData}`;
        const response = await this.sendRequest(message);
        console.log(`Resultado entrenamiento: ${response}`);
        return response;
    }

    async predict(modelId: string, inputData: string): Promise<string> {
        const message = `PREDICT|${modelId}|${inputData}`;
        const response = await this.sendRequest(message);
        console.log(`Resultado predicción: ${response}`);
        return response;
    }
}