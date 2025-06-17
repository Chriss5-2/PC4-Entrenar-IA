### Explicación del código:

1. **Módulo `net`**: Se utiliza para crear un cliente TCP que puede conectarse a un servidor.
2. **Clase `SimpleClient`**: Similar a la clase en Python, tiene métodos para enviar solicitudes al servidor (`sendRequest`), verificar el estado del servidor (`checkStatus`), entrenar un modelo (`trainModel`) y hacer predicciones (`predict`).
3. **Método `sendRequest`**: Este método establece una conexión con el servidor, envía un mensaje y espera una respuesta. Utiliza Promesas para manejar la asincronía.
4. **Función `main`**: Maneja la entrada del usuario y crea una instancia de `SimpleClient`. También se encarga de verificar el estado del servidor al inicio.

### Ejecución:
Para ejecutar este worker, asegúrate de tener Node.js instalado y ejecuta el siguiente comando en la terminal:

```bash
node worker.js localhost 5000
```

Asegúrate de que el servidor esté en funcionamiento y escuchando en el puerto especificado. Puedes expandir la lógica en `main` para interactuar con el usuario de manera similar a como lo hace el cliente en Python.