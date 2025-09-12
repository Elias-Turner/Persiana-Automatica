# 📂 Script Organizador de Archivos por Tamaño

Este script en **Bash** organiza los archivos de un directorio en subcarpetas según su tamaño.  
Además, actualiza las fechas de acceso y modificación de los archivos y muestra un resumen de lo procesado utilizando colores en la terminal.  

---

## 📌 Requerimientos previos  
- Linux/Ubuntu con Bash.  
- Permisos de ejecución sobre el script.  

---

## 🚀 Ejecución en la terminal  

Para poder ejecutar el script correctamente, se usaron los siguientes comandos en la **terminal**: 
## ⚙️ Comandos utilizados

### Comandos de terminal para ejecutar el script

**chmod +x executor6.sh**  
Se utiliza para otorgar permisos de ejecución al script. Esto es necesario porque, por defecto, los archivos creados en Linux no siempre tienen permiso de ejecución, y sin este comando no podríamos ejecutar `executor6.sh` directamente desde la terminal.

**dos2unix executor6.sh**  
Convierte el archivo de formato Windows a formato Unix. Esto es importante porque los saltos de línea de Windows (`\r\n`) pueden generar errores en Bash; `dos2unix` los reemplaza por el formato correcto (`\n`), asegurando que el script funcione sin problemas en Linux.

**./executor6.sh ~/pruebaKION**  
Ejecuta el script indicando un directorio de trabajo como argumento. El script tomará todos los archivos dentro de este directorio para procesarlos, moverlos según su tamaño y actualizar sus fechas de acceso y modificación.

---

### Comandos dentro del script

**#!/bin/bash**  
Es el shebang del script y le indica al sistema que debe ejecutarse con Bash. Esto asegura que se interpreten correctamente todas las construcciones y sintaxis propias de Bash, evitando errores de compatibilidad con otros shells.

**set -e**  
Configura el script para que se detenga inmediatamente si ocurre cualquier error durante su ejecución. Esto es fundamental para evitar que el script continúe procesando archivos cuando se encuentra con un problema, garantizando integridad y consistencia.

**ROJO='\033[0;31m'**, **VERDE='\033[0;32m'**, **AZUL='\033[0;34m'**, **AMARILLO='\033[1;33m'**, **NC='\033[0m'**  
Definen variables con códigos ANSI para mostrar texto en colores dentro de la terminal. La finalidad es mejorar la legibilidad de los mensajes, permitiendo distinguir errores, advertencias e información de manera visual.

**echo -e**  
Se utiliza para imprimir mensajes en la terminal interpretando caracteres especiales como los códigos de color ANSI. Esto permite mostrar la información del script de manera clara y con formato, diferenciando mensajes de error, éxito y advertencia.

**if [ $# -eq 0 ]**  
Verifica si el script se ejecutó sin argumentos. Su finalidad es prevenir errores posteriores al intentar procesar un directorio inexistente y notificar al usuario que debe proporcionar una ruta válida.

**if [ ! -d "$DIRECTORIO" ]**  
Comprueba si la ruta pasada como argumento no existe o no es un directorio. Esto evita que el script falle al intentar cambiar de directorio o procesar archivos inexistentes.

**cd "$DIRECTORIO"**  
Cambia al directorio pasado como argumento. Esto es necesario para que todas las operaciones de creación de carpetas, recorrido de archivos y movimientos se realicen dentro del directorio correcto.

**mkdir -p SmallFiles MediumFiles LargeFiles**  
Crea las carpetas destino para organizar los archivos según su tamaño. La opción `-p` evita errores si las carpetas ya existen y asegura que el script pueda ejecutarse varias veces sin problemas.

**for archivo in "$DIRECTORIO"/*; do ... done**  
Recorre todos los elementos dentro del directorio. Esto permite procesar cada archivo individualmente, aplicar la clasificación por tamaño y actualizar sus fechas de acceso y modificación.

**if [ -f "$archivo" ]**  
Comprueba si el elemento es un archivo regular y no un directorio. Esto es importante para evitar errores al intentar mover carpetas u otros tipos de archivos especiales.

**stat -c%s "$archivo"**  
Obtiene el tamaño del archivo en bytes. Esta información es esencial para determinar en qué carpeta destino se moverá el archivo según los criterios de tamaño establecidos.

**tamano_mb=$((tamano_bytes / 1048576))**  
Convierte el tamaño de bytes a megabytes para simplificar las comparaciones. Permite clasificar los archivos en SmallFiles, MediumFiles o LargeFiles de manera más comprensible.

**(( ... ))**  
Se utiliza para realizar comparaciones y operaciones aritméticas dentro del script. Esto permite implementar la lógica condicional para mover los archivos según su tamaño.

**mv "$archivo" "CarpetaDestino/"**  
Mueve el archivo a la carpeta correspondiente según su tamaño. Esto organiza automáticamente los archivos y mantiene limpio el directorio original.

**touch "$archivo"**  
Actualiza la fecha de acceso y modificación del archivo a la fecha y hora actuales. Esto sirve para marcar que el archivo fue procesado y reflejar el cambio en el sistema de archivos.

**exit 0**  
Finaliza el script con código de salida 0, indicando que se procesaron archivos correctamente. Esto permite que otros programas o scripts que llamen a este script sepan que todo se ejecutó sin errores.

**exit 1**  
Finaliza el script con código de salida 1 si no había archivos para procesar. Esto notifica al usuario o a otros scripts que el directorio estaba vacío.

**exit 2**  
Finaliza el script con código de salida 2 si ocurrió un error, como un directorio inexistente o argumento faltante. Esto ayuda a manejar errores de manera predecible y permite depuración.


| Comando | Descripción |
|---------|-------------|
| `chmod +x executor6.sh` | Da permisos de ejecución al script. |
| `dos2unix executor6.sh` | Convierte el archivo a formato Unix (útil si fue editado en Windows). |
| `./executor6.sh ~/pruebaKION` | Ejecuta el script indicando un directorio (`~/pruebaKION`). |

---

## ⚙️ Comandos utilizados dentro del script  

A continuación, se listan todos los comandos utilizados dentro del **script Bash** con su explicación:  

| Comando / Sintaxis | Descripción |
|--------------------|-------------|
| `#!/bin/bash` | **Shebang**: indica que el script debe ejecutarse con Bash. |
| `set -e` | Hace que el script termine inmediatamente si ocurre un error. |
| `ROJO='\033[0;31m'` | Variables con códigos **ANSI** para mostrar colores en la terminal. |
| `echo -e` | Imprime mensajes en pantalla interpretando colores ANSI. |
| `if [ $# -eq 0 ]` | Verifica si no se pasó ningún argumento al script. |
| `if [ ! -d "$DIRECTORIO" ]` | Comprueba si la ruta no existe o no es un directorio. |
| `cd "$DIRECTORIO"` | Cambia al directorio pasado como argumento. |
| `mkdir -p SmallFiles MediumFiles LargeFiles` | Crea las carpetas de destino (sin error si ya existen). |
| `for archivo in "$DIRECTORIO"/*; do ... done` | Recorre todos los elementos del directorio. |
| `if [ -f "$archivo" ]` | Procesa solo si es un archivo regular (ignora directorios). |
| `stat -c%s "$archivo"` | Obtiene el tamaño del archivo en bytes. |
| `tamano_mb=$((tamano_bytes / 1048576))` | Convierte el tamaño de bytes a megabytes. |
| `(( ... ))` | Estructura para operaciones aritméticas y comparaciones. |
| `mv "$archivo" "CarpetaDestino/"` | Mueve el archivo a la carpeta correspondiente. |
| `touch "$archivo"` | Actualiza la fecha de acceso y modificación del archivo a la actual. |
| `exit 0` | Finaliza el script con estado **éxito** si se procesaron archivos. |
| `exit 1` | Finaliza el script si no había archivos (directorio vacío). |
| `exit 2` | Finaliza el script si ocurrió un error (ejemplo: directorio no existe). |

---

## 🎨 Colores utilizados (ANSI)  

El script imprime mensajes con colores para mejorar la legibilidad:  

- `\033[0;31m` → **Rojo**: errores.  
- `\033[0;32m` → **Verde**: mensajes de éxito.  
- `\033[0;34m` → **Azul**: información.  
- `\033[1;33m` → **Amarillo**: advertencias.  
- `\033[0m` → Resetear color.  

---

## ✅ Flujo de funcionamiento del script  

1. Valida que se pase un directorio como argumento.  
2. Comprueba que el directorio exista y cambia a él.  
3. Crea las carpetas `SmallFiles`, `MediumFiles` y `LargeFiles`.  
4. Recorre cada archivo dentro del directorio.  
5. Determina el tamaño de cada archivo:  
   - **< 1MB** → se mueve a `SmallFiles`.  
   - **1MB–100MB** → se mueve a `MediumFiles`.  
   - **> 100MB** → se mueve a `LargeFiles`.  
6. Actualiza la fecha de acceso y modificación (`touch`).  
7. Muestra un resumen de cuántos archivos se procesaron y a dónde fueron movidos.  
8. Devuelve un **código de salida** (`0`, `1` o `2`).  

---

## 📊 Ejemplo de ejecución  

```bash
$ ./executor6.sh ~/pruebaKION

Cambiado al directorio: /home/usuario/pruebaKION
Total de archivos procesados: 5
Movidos a SmallFiles (<1MB): 2
Movidos a MediumFiles (1MB–100MB): 2
Movidos a LargeFiles (>100MB): 1
