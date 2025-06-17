# Instrucciones:
---
# Levantar docker general
```bash
PS C:\Users\CHRISTIAN\Desktop\ConcurrentePC's\PC4-CC4P1-Entrenar-IA> docker compose up -d
```
---

# Levantar clientes
### Usando el cliente en la terminal
```bash
PS C:\Users\CHRISTIAN\Desktop\ConcurrentePC's\PC4-CC4P1-Entrenar-IA\client>
 python client.py localhost 5005
```
### Usando el cliente con gui
```bash
PS C:\Users\CHRISTIAN\Desktop\ConcurrentePC's\PC4-CC4P1-Entrenar-IA\client> python client_gui.py
```
---
## Workers
```
5000 -> java1
5001 -> java2
5002 -> python1
5003 -> python2
5004 -> js1
5005 -> js2
```

# Borrar containers
```bash
PS C:\Users\CHRISTIAN\Desktop\ConcurrentePC's\PC4-CC4P1-Entrenar-IA> docker-compose down   
```
