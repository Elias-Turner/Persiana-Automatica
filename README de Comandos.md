# Ejecutor de Comandos con Manejo de Señales

Este programa ejecuta comandos leídos desde la entrada estándar, con soporte para
ejecución en modo monohilo o multihilo, y responde a señales **SIGTERM** y **SIGUSR1**.

## Archivos incluidos
- `EjercicioEntregable.py` → Programa principal.
- `comandos.txt` → Lista de comandos de prueba.

## Ejecución

### Modo monohilo
```bash
python3 EjercicioEntregable.py -m single < comandos.txt
### Modo multihilo
```bash
python3 EjercicioEntregable.py -m multi < comandos.txt

## Pruebas con las Señales
### Enviar señal USR1 para omitir comandos
1. Exportar la variable de entorno con la cantidad de comandos a omitir:
```bash
export SKIP_COMMANDS=2
2.Obtener el PID del proceso (el programa lo muestra al iniciar).
3. Enviar la señal:
```bash
kill -USR1 <PID>
Ejemplo: si el programa estaba leyendo y ejecutando comandos, al recibir la señal omitirá los 2 siguientes.

### Enviar señal TERM para finalizar ordenadamente
1. Obtener el PID del proceso.
2. Enviar la señal:
```bash
kill -TERM <PID>
El programa dejará de leer más comandos y esperará a que todos los hilos en ejecución terminen antes de finalizar

