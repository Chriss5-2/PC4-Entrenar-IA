import * as net from 'net';

// const PORT = 5005;
const PORT = process.env.PORT ? parseInt(process.env.PORT) : 5006;

const server = net.createServer((socket) => {
    socket.on('data', (data) => {
        const message = data.toString().trim();
        console.log(`Mensaje recibido: ${message}`);

        if (message === "STATUS") {
            socket.write("OK|WORKER_TS\n");
        } else if (message.startsWith("TRAIN|")) {
            socket.write("OK|TRAINED|ts-model-1\n");
        } else if (message.startsWith("PREDICT|")) {
            socket.write("OK|PREDICTION|42\n");
        } else {
            socket.write("ERROR|UNKNOWN_COMMAND\n");
        }
    });

    socket.on('error', (err) => {
        console.error('Socket error:', err);
    });
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`Worker TS escuchando en el puerto ${PORT}`);
});