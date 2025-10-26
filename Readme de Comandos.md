# Diccionario Distribuido (Servidor y Cliente)

Este proyecto implementa un **diccionario distribuido** basado en **sockets TCP** con soporte **multi-hilo**.  
El sistema permite que varios clientes se conecten simultáneamente a un **servidor central**, el cual mantiene un diccionario compartido en memoria.

---

## Descripción General

El proyecto consta de dos aplicaciones principales:

- **Servidor (`server.py`)**: Mantiene el diccionario en memoria y atiende múltiples clientes concurrentes mediante hilos.
- **Cliente (`client.py`)**: Permite enviar comandos al servidor para agregar, listar y obtener palabras del diccionario.

Ambos se comunican a través de una conexión TCP, utilizando un protocolo textual simple.

---

## Servidor (`server.py`)

### Descripción

El servidor se encarga de:

- Aceptar conexiones TCP en el puerto **65432**.
- Manejar varios clientes simultáneamente mediante **hilos** (`threading.Thread`).
- Proteger el acceso concurrente al diccionario mediante un **lock** (`threading.Lock`).
- Procesar comandos enviados por los clientes y devolver respuestas de texto plano.

### Ejecución

```bash
python3 server.py
```

Por defecto, el servidor escucha en:

```
Host: localhost
Puerto: 65432
```

### Señales y Finalización

- **SIGTERM**: al recibirla, el servidor deja de aceptar nuevas conexiones y espera a que terminen los hilos activos antes de finalizar.
- **Ctrl + C**: Detiene el servidor de forma controlada. Cierra el socket principal y espera a que todos los hilos clientes terminen antes de finalizar el proceso.

### Caracteristicas
- Puerto por defecto: 65432 (puede cambiarse editando la variable puerto en el código).
- Dirección: localhost (usa la IP local de tu máquina).
- Conexiones: cada cliente se maneja en un hilo independiente.
- Sincronización: el acceso al diccionario compartido se controla con threading.Lock() para evitar condiciones de carrera

---

## Cliente (`client.py`)

### Descripción

El cliente permite enviar comandos al servidor para operar sobre el diccionario compartido.  
Cada comando se envía como texto terminado en salto de línea (`\n`), y el servidor responde también en texto plano.

### Ejecución

Sintaxis general:

```bash
python3 client.py host port comando
```

Ejemplo básico:

```bash
python3 client.py localhost 65432 listar
```

### Parámetros

| Parámetro | Descripción |
|------------|-------------|
| `host` | Dirección del servidor (por ejemplo, `localhost`). |
| `port` | Puerto TCP (por defecto `65432`). |
| `comando` | Comando a ejecutar (ver comandos disponibles más abajo). |

---

## Protocolo de Comunicación

### Descripción General

El protocolo entre **cliente** y **servidor** se basa en comandos de texto terminados en `\n`.  
Cada comando puede incluir argumentos, separados por el carácter `|` cuando sea necesario.

### Comandos Soportados

| Comando | Formato de Envío | Descripción | Respuesta del Servidor |
|----------|------------------|--------------|------------------------|
| `listar` | `listar` | Lista todas las palabras registradas. | `OK\npalabra1\npalabra2...\n` o `OK: Diccionario Vacio` |
| `agregar` | `agregar palabra|definicion` | Agrega o actualiza una palabra en el diccionario. | `OK\nPalabra agregada\n` o `OK\nPalabra actualizada\n` |
| `obtener` | `obtener palabra` | Devuelve la definición de una palabra. | `OK\ndefinicion\n` o `ERR 3 Palabra no encontrada` |

### Códigos de Error

| Código | Mensaje | Descripción |
|--------|----------|-------------|
| `ERR 1` | Formato inválido o palabra vacía al agregar | Error de sintaxis en el comando `agregar`. |
| `ERR 2` | Palabra vacía al obtener | Se envió `obtener` sin especificar palabra. |
| `ERR 3` | Palabra no encontrada | La palabra solicitada no existe en el diccionario. |
| `ERR 4` | Comando desconocido | Se envió un comando no reconocido. |

---

## Ejemplos de Uso y Pruebas

### 1) Iniciar el Servidor

```bash
python3 server.py
```

El servidor mostrará un mensaje indicando que está escuchando:

```
[servicio] Escuchando en localhost:65432 ... (PID xxxx)
```

### 2) Ejecutar comandos desde otra terminal

#### Listar (diccionario vacío)

```bash
python3 client.py localhost 65432 listar
```
**Salida esperada:**
```
OK: Diccionario Vacio
```

#### Agregar palabras

```bash
python3 client.py localhost 65432 agregar sol|Estrella que ilumina la Tierra
python3 client.py localhost 65432 agregar luna|Satélite natural de la Tierra
```
**Salida esperada:**
```
OK
Palabra agregada
```

#### Listar palabras existentes

```bash
python3 client.py localhost 65432 listar
```
**Salida esperada:**
```
OK
luna
sol
```

#### Obtener definiciones

```bash
python3 client.py localhost 65432 obtener sol
```
**Salida esperada:**
```
OK
Estrella que ilumina la Tierra
```

#### Actualizar una palabra

```bash
python3 client.py localhost 65432 agregar sol|Cuerpo celeste que emite luz
```
**Salida esperada:**
```
OK
Palabra actualizada
```

#### Error de formato

```bash
python3 client.py localhost 65432 agregar palabra_sin_definicion
```
**Salida esperada:**
```
ERR 1 Formato inválido. Uso: agregar palabra|definicion
```

#### Comando no reconocido

```bash
python3 client.py localhost 65432 borrar sol
```
**Salida esperada:**
```
ERR 4 Comando desconocido
```

### Códigos de salida del cliente

| Código | Significado |
|--------|-------------|
| `0` | Operación exitosa (`OK`) |
| `2` | Respuesta no reconocida |
| `5` | No se pudo conectar al servidor |
| `6` | Error interno del cliente |
| `10–14` | Errores específicos (`ERR 1–4`) |


## Comandos de Prueba

```bash
python3 server.py &
python3 client.py localhost 65432 listar
python3 client.py localhost 65432 agregar sol|Estrella que ilumina la Tierra
python3 client.py localhost 65432 agregar luna|Satélite natural de la Tierra
python3 client.py localhost 65432 listar
python3 client.py localhost 65432 obtener sol
python3 client.py localhost 65432 obtener luna
python3 client.py localhost 65432 agregar sol|Cuerpo celeste que emite luz
python3 client.py localhost 65432 obtener sol
python3 client.py localhost 65432 borrar sol
kill -TERM <PID>
```
