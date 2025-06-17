FROM node:20
WORKDIR /app

# Copia el código fuente
COPY src/ ./src

# Si tienes package.json (para dependencias), descomenta estas líneas:
# COPY package*.json ./
# RUN npm install

# Expone el puerto por defecto (ajusta si usas otro)
EXPOSE 5003
EXPOSE 5004
EXPOSE 5005

# Comando para ejecutar el worker-server.js (puedes parametrizar el puerto si lo deseas)
# CMD ["node", "src/worker-server.js ${PORT}"]
# CMD ["node", "src/worker-server.js", "${PORT}"]
CMD sh -c "node src/worker-server.js $PORT"