// filepath: ts-worker/src/httpMonitor.ts
import * as net from 'net';

export class SimpleWorker {
    private host: string;
    private port: number;

    constructor(
    host = 'localhost',
    port = process.env.MONITOR_PORT ? parseInt(process.env.MONITOR_PORT) : 8007
    ) {
        this.host = host;
        this.port = isNaN(port) ? 8007 : port;
        console.log(`[SimpleWorker] httpMonitor instanciado en ${this.host}:${this.port}`);
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
}