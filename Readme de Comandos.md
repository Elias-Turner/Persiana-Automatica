# Script Organizador de Archivos por Tamaño

Este script en **Bash** organiza los archivos de un directorio en subcarpetas según su tamaño.  
Además, actualiza las fechas de acceso y modificación de los archivos y muestra un resumen de lo procesado utilizando colores en la terminal.  


## Requerimientos previos  
- Linux/Ubuntu con Bash.  
- Permisos de ejecución sobre el script.  

## Lo Utilizado
- `EjercicioEntregable3.sh` → Programa principal.
- `prueba` → Carpeta con archivos para probar.

## Ejecución en la terminal  
Para poder ejecutar el script correctamente, se usaron los siguientes comandos en la **terminal**: 

## Comandos utilizados
### Comandos de terminal para ejecutar el script

**chmod +x EjercicioEntregable3.sh**  
Se utiliza para otorgar permisos de ejecución al script. Esto es necesario porque, por defecto, los archivos creados en Linux no siempre tienen permiso de ejecución, y sin este comando no podríamos ejecutar `executor6.sh` directamente desde la terminal.

**dos2unix EjercicioEntregable3.sh**  
Convierte el archivo de formato Windows a formato Unix. Esto es importante porque los saltos de línea de Windows (`\r\n`) pueden generar errores en Bash; `dos2unix` los reemplaza por el formato correcto (`\n`), asegurando que el script funcione sin problemas en Linux.

**./EjercicioEntregable3.sh ~/prueba**  
Ejecuta el script indicando un directorio de trabajo como argumento. El script tomará todos los archivos dentro de este directorio para procesarlos, moverlos según su tamaño y actualizar sus fechas de acceso y modificación.

**echo $?**
Se utiliza para ver el retorno del programa. Si hubo un error dara 2, si el directorio estaba vacio o no habia archivos regulares dara 1, y si se ejecuto correctamente y los archivos regulares se movieron a sus respectivas carpetas dara 0.


### Comandos dentro del script

**#!/bin/bash**  
Es el shebang del script y le indica al sistema que debe ejecutarse con Bash. Esto me aseguro que se interpreten correctamente todas las construcciones y sintaxis propias de Bash, evitando errores de compatibilidad con otros shells.

**set -e**  
Configura el script para que se detenga inmediatamente si ocurre cualquier error durante su ejecución. Lo utilice para evitar que el script continúe procesando archivos cuando se encuentra con un problema, garantizando integridad y consistencia.

**ROJO='\033[0;31m'**, **VERDE='\033[0;32m'**, **AZUL='\033[0;34m'**, **AMARILLO='\033[1;33m'**, **NC='\033[0m'**  
Definen variables con códigos ANSI para mostrar texto en colores dentro de la terminal. Se usó para mejorar la legibilidad de los mensajes, permitiendo distinguir errores, advertencias e información de manera visual.

**echo -e**  
Se utiliza para imprimir mensajes en la terminal interpretando caracteres especiales como los códigos de color ANSI. Esto me permitio mostrar la información del script de manera clara y con formato, diferenciando mensajes de error, éxito y advertencia.

**if [ $# -eq 0 ]**  
Verifica si el script se ejecutó sin argumentos. Lo utilice es prevenir errores posteriores al intentar procesar un directorio inexistente y notificar al usuario que debe proporcionar una ruta válida.

**if [ ! -d "$DIRECTORIO" ]**  
Comprueba si la ruta pasada como argumento no existe o no es un directorio. Lo use porque evita que el script falle al intentar cambiar de directorio o procesar archivos inexistentes.

**cd "$DIRECTORIO"**  
Cambia al directorio pasado como argumento. Esto es necesario para que todas las operaciones de creación de carpetas, recorrido de archivos y movimientos se realicen dentro del directorio correcto.

**mkdir -p SmallFiles MediumFiles LargeFiles**  
Crea las carpetas destino para organizar los archivos según su tamaño. La opción `-p` evita errores si las carpetas ya existen y asegura que el script pueda ejecutarse varias veces sin problemas.

**for archivo in "$DIRECTORIO"/*; do ... done**  
Recorre todos los elementos dentro del directorio. Con esto pude procesar cada archivo individualmente, aplicar la clasificación por tamaño y actualizar sus fechas de acceso y modificación.

**if [ -f "$archivo" ]**  
Comprueba si el elemento es un archivo regular y no un directorio. Lo utilice para evitar errores al intentar mover carpetas u otros tipos de archivos especiales.

**stat -c%s "$archivo"**  
Obtiene el tamaño del archivo en bytes. Esta forma es esencial para determinar en qué carpeta destino se moverá el archivo según los criterios de tamaño establecidos.

**tamano_mb=$((tamano_bytes / 1048576))**  
Convierte el tamaño de bytes a megabytes para simplificar las comparaciones. Me permitió clasificar los archivos en SmallFiles, MediumFiles o LargeFiles de manera más comprensible.

**mv "$archivo" "CarpetaDestino/"**  
Mueve el archivo a la carpeta correspondiente según su tamaño. Esto organiza automáticamente los archivos y mantiene limpio el directorio original.

**touch "$archivo"**  
Actualiza la fecha de acceso y modificación del archivo a la fecha y hora actuales. Lo use para marcar que el archivo fue procesado y reflejar el cambio en el sistema de archivos.

**exit 0**  
Finaliza el script con código de salida 0, indicando que se procesaron archivos correctamente. Esto permite que otros programas o scripts que llamen a este script sepan que todo se ejecutó sin errores.

**exit 1**  
Finaliza el script con código de salida 1 si no había archivos para procesar. Esto notifica al usuario o a otros scripts que el directorio estaba vacío.

**exit 2**  
Finaliza el script con código de salida 2 si ocurrió un error, como un directorio inexistente o argumento faltante. Esto ayuda a manejar errores de manera predecible y permite depuración.

## Colores utilizados (ANSI)  

El script imprime mensajes con colores para mejorar la legibilidad:  

- `\033[0;31m` → **Rojo**: errores.  
- `\033[0;32m` → **Verde**: mensajes de éxito.  
- `\033[0;34m` → **Azul**: información.  
- `\033[1;33m` → **Amarillo**: advertencias.  
- `\033[0m` → Resetear color.  



## Salida al Ejecutar el Programa 

```bash
Cambiado al directorio: /home/usuario/pruebaKION
Total de archivos procesados: 5
Movidos a SmallFiles (<1MB): 2
Movidos a MediumFiles (1MB–100MB): 2
Movidos a LargeFiles (>100MB): 1
