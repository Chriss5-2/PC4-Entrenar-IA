const net = require('net');

const PORT = process.argv[2] ? parseInt(process.argv[2]) : 5003;

// Aquí guardamos el modelo entrenado (simplemente un array de números)
let modeloEntrenado = null;

const server = net.createServer((socket) => {
    socket.on('data', (data) => {
        const message = data.toString().trim();
        console.log(`Mensaje recibido: ${message}`);

        if (message === "STATUS") {
            socket.write("OK|WORKER_JS\n");
        } else if (message.startsWith("TRAIN|")) {
            // Ejemplo: TRAIN|1,2,3,4,5|2,4,6,8,10
            const partes = message.split("|");
            if (partes.length >= 3) {
                // Guardamos los datos de salida como modelo (puedes cambiar la lógica)
                modeloEntrenado = partes[2].split(",").map(Number);
                socket.write("OK|TRAINED|js-model-1\n");
            } else {
                socket.write("ERROR|BAD_TRAIN_FORMAT\n");
            }
        } else if (message.startsWith("PREDICT|")) {
            if (!modeloEntrenado) {
                socket.write("ERROR|NO_MODEL\n");
                return;
            }
            // Ejemplo: PREDICT|js-model-1|1,2,3,4,5
            const partes = message.split("|");
            if (partes.length >= 3) {
                const input = partes[2].split(",").map(Number);
                // Lógica simple: suma de entrada * promedio del modelo entrenado
                const sumaInput = input.reduce((a, b) => a + b, 0);
                const promedioModelo = modeloEntrenado.reduce((a, b) => a + b, 0) / modeloEntrenado.length;
                const prediccion = sumaInput * promedioModelo;
                socket.write(`OK|${prediccion}\n`);
            } else {
                socket.write("ERROR|BAD_PREDICT_FORMAT\n");
            }
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