const net = require('net');

const PORT = process.argv[2] ? parseInt(process.argv[2]) : 5003;

const server = net.createServer((socket) => {
    socket.on('data', (data) => {
        const message = data.toString().trim();
        console.log(`Mensaje recibido: ${message}`);

        if (message === "STATUS") {
            socket.write("OK|WORKER_JS\n");
        } else if (message.startsWith("TRAIN|")) {
            socket.write("OK|TRAINED|js-model-1\n");
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

server.listen(PORT, () => {
    console.log(`Worker JS escuchando en el puerto ${PORT}`);
});