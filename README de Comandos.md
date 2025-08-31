# Ejecutor de Comandos con Manejo de Señales

Este programa ejecuta comandos leídos desde la entrada estándar, con soporte para
ejecución en modo monohilo o multihilo, y responde a señales **TERM** y **USR1**.

## Archivos incluidos
- `EjercicioEntregable2.py` → Programa principal.
- `comandos.txt` → Lista de comandos de prueba.

## Ejecución

### Modo monohilo
```bash
python3 EjercicioEntregable2.py -m single < comandos.txt
```

### Modo multihilo
```bash
python3 EjercicioEntregable2.py -m multi < comandos.txt
```

## Pruebas con señales

### Enviar señal USR1 para omitir comandos
1. Exportar la variable de entorno con la cantidad de comandos a omitir:
   ```bash
   export SKIP_COMMANDS=2
   ```
2. Ejecutar el programa ya sea en el modo monohilo o en el multihilo
3. Obtener el PID del proceso (el programa lo muestra al iniciar).
4. Enviar la señal:
   ```bash
   kill -USR1 PID
   ```

### Enviar señal TERM para finalizar ordenadamente
1. Ejecutar el programa ya sea en el modo monohilo o en el multihilo
2. Obtener el PID del proceso.
3. Enviar la señal:
   ```bash
   kill -TERM PID
   ```

El programa dejará de leer más comandos y esperará a que todos los hilos en ejecución terminen antes de finalizar.
