import * as net from 'net';

const PORT = process.env.PORT ? parseInt(process.env.PORT) : 5006;

// Guardar el modelo entrenado (array de números)
let modeloEntrenado: number[] | null = null;

const server = net.createServer((socket) => {
    socket.on('data', (data) => {
        const message = data.toString().trim();
        console.log(`Mensaje recibido: ${message}`);

        if (message === "STATUS") {
            socket.write("OK|WORKER_TS\n");
        } else if (message.startsWith("TRAIN|")) {
            // Ejemplo: TRAIN|1,2,3,4,5|2,4,6,8,10
            const partes = message.split("|");
            if (partes.length >= 3) {
                modeloEntrenado = partes[2].split(",").map(x => Number(x.trim()));
                socket.write("OK|TRAINED|ts-model-1\n");
            } else {
                socket.write("ERROR|BAD_TRAIN_FORMAT\n");
            }
        } else if (message.startsWith("PREDICT|")) {
            if (!modeloEntrenado) {
                socket.write("ERROR|NO_MODEL\n");
                return;
            }
            // Ejemplo: PREDICT|ts-model-1|2,4,1
            const partes = message.split("|");
            if (partes.length >= 3) {
                const input = partes[2].split(",").map(x => Number(x.trim()));
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

server.listen(PORT, '0.0.0.0', () => {
    console.log(`Worker TS escuchando en el puerto ${PORT}`);
});