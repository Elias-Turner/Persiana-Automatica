import RPi.GPIO as GPIO
import time
import spidev
import sys

# Configuración de pines
TRIG_SUP = 23   # Sensor ultrasónico superior
ECHO_SUP = 24
TRIG_INF = 27   # Sensor ultrasónico inferior
ECHO_INF = 22
MOTOR_IN1 = 5   # Control motor
MOTOR_IN2 = 6
BOTON_PIN = 26   # Pin para el botón físico (GPIO4)

# Constantes configurables
DISTANCIA_MIN = 5.0    # Distancia mínima válida (cm)
DISTANCIA_MAX = 100.0  # Distancia máxima válida (cm)
DISTANCIA_PARADA_SUP = 10.0  # Distancia para detener en superior
DISTANCIA_PARADA_INF = 10.0  # Distancia para detener en inferior
INTENTOS_LECTURA = 3    # Intentos para lectura válida
TIEMPO_ESPERA = 0.2    # Tiempo entre lecturas (segundos)
DEBOUNCE_TIME = 0.2    # Tiempo antirrebote del botón

# Configuración sensor ALS SPI
UMBRAL_LUZ_ALTA = 10  # Valor SPI (0-255) para cerrar cortina
UMBRAL_LUZ_BAJA = 1   # Valor SPI (0-255) para abrir cortina
INTERVALO_LUZ = 0.1     # Segundos entre lecturas de luz
SPI_BUS = 0            # Bus SPI 0
SPI_DEVICE = 0         # Dispositivo 0 (CE0)

# --- Variables para modo de operación ---
MODO_AUTOMATICO = 0
MODO_MANUAL = 1
modo_operacion = MODO_AUTOMATICO  # Iniciar en modo automático

DOBLE_PULSO_TIEMPO = 0.7  # Tiempo máximo entre pulsaciones para doble clic
contador_pulsos = 0
tiempo_ultima_pulsacion = 0

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_SUP, GPIO.OUT)
GPIO.setup(ECHO_SUP, GPIO.IN)
GPIO.setup(TRIG_INF, GPIO.OUT)
GPIO.setup(ECHO_INF, GPIO.IN)
GPIO.setup(MOTOR_IN1, GPIO.OUT)
GPIO.setup(MOTOR_IN2, GPIO.OUT)
GPIO.setup(BOTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Resistencia pull-up

# Inicializar motor apagado
GPIO.output(MOTOR_IN1, GPIO.LOW)
GPIO.output(MOTOR_IN2, GPIO.LOW)

# Estados del motor
MOTOR_DETENIDO = 0
MOTOR_SUBIENDO = 1
MOTOR_BAJANDO = 2
estado_motor = MOTOR_DETENIDO

# Variables para control de tiempo
ultimo_tiempo_boton = 0
ultimo_tiempo_luz = 0

# Inicializar SPI
spi = None
try:
    spi = spidev.SpiDev()
    spi.open(SPI_BUS, SPI_DEVICE)
    spi.max_speed_hz = 1000000  # 1 MHz
    spi.mode = 0               # Modo 0 (CPOL=0, CPHA=0)
    print("SPI inicializado correctamente")
except Exception as e:
    print(f"Error al inicializar SPI: {e}")
    print("Funcionalidad de luz deshabilitada")
    spi = None

def medir_distancia(trig, echo, sensor_nombre):
    """Mide distancia con sensor ultrasónico con validación de errores"""
    for i in range(INTENTOS_LECTURA):
        GPIO.output(trig, True)
        time.sleep(0.00001)
        GPIO.output(trig, False)
        
        timeout = time.time() + 0.04  # Timeout de 40ms
        pulso_inicio = None
        while GPIO.input(echo) == 0 and time.time() < timeout:
            pulso_inicio = time.time()
        
        timeout = time.time() + 0.04
        pulso_fin = None
        while GPIO.input(echo) == 1 and time.time() < timeout:
            pulso_fin = time.time()
        
        if pulso_inicio is None or pulso_fin is None:
            continue
        
        try:
            duracion = pulso_fin - pulso_inicio
            distancia = (duracion * 34300) / 2  # Velocidad del sonido (343 m/s)
            
            if DISTANCIA_MIN <= distancia <= DISTANCIA_MAX:
                return distancia
        except:
            pass
    
    return None

def leer_luz():
    """Lee el valor de luz del sensor ALS SPI (0-255)"""
    if spi is None:
        return None
        
    try:
        # Enviar 2 bytes dummy y leer 2 bytes de respuesta
        data = spi.xfer2([0x00, 0x00])
        
        # Combinar los 2 bytes en un valor de 16 bits
        raw_value = (data[0] << 8) | data[1]
        
        # El valor de luz está en los bits 15-7 (9 bits)
        # Pero el ADC es de 8 bits, así que tomamos los 8 bits superiores
        luz_value = raw_value >> 7
        
        # Asegurar que está en rango 0-255
        return min(max(luz_value, 0), 255)
    except Exception as e:
        print(f"[ERROR ALS SPI] {e}")
        return None

def determinar_posicion(dist_sup, dist_inf):
    """Determina la posición actual basada en lecturas de sensores"""
    # Verificar si la cortina está en posición superior
    if dist_sup is not None and dist_sup <= DISTANCIA_PARADA_SUP:
        return "superior"
    
    # Verificar si la cortina está en posición inferior
    if dist_inf is not None and dist_inf <= DISTANCIA_PARADA_INF:
        return "inferior"
    
    # Si no está en ninguno de los topes
    return "intermedia"

def control_motor(accion):
    """Controla el motor con protección contra activación simultánea"""
    global estado_motor
    
    # Apagar ambos pines primero para evitar cortocircuitos
    GPIO.output(MOTOR_IN1, GPIO.LOW)
    GPIO.output(MOTOR_IN2, GPIO.LOW)
    time.sleep(0.05)  # Breve pausa de seguridad
    
    if accion == "subir":
        GPIO.output(MOTOR_IN1, GPIO.HIGH)
        GPIO.output(MOTOR_IN2, GPIO.LOW)
        estado_motor = MOTOR_SUBIENDO
        print("[MOTOR] Subiendo cortina")
        
    elif accion == "bajar":
        GPIO.output(MOTOR_IN1, GPIO.LOW)
        GPIO.output(MOTOR_IN2, GPIO.HIGH)
        estado_motor = MOTOR_BAJANDO
        print("[MOTOR] Bajando cortina")
        
    elif accion == "detener":
        GPIO.output(MOTOR_IN1, GPIO.LOW)
        GPIO.output(MOTOR_IN2, GPIO.LOW)
        estado_motor = MOTOR_DETENIDO
        print("[MOTOR] Motor detenido")

def imprimir_estado(dist_sup, dist_inf, posicion, luz=None):
    """Muestra el estado actual del sistema"""
    print("\n" + "="*50)
    print("ESTADO DEL SISTEMA")
    print("="*50)
    
    # Mostrar lecturas de sensores
    if dist_sup is not None:
        print(f"Distancia superior: {dist_sup:.1f} cm")
    else:
        print("Distancia superior: ERROR")
        
    if dist_inf is not None:
        print(f"Distancia inferior: {dist_inf:.1f} cm")
    else:
        print("Distancia inferior: ERROR")
    
    # Mostrar lectura de luz SPI
    if luz is not None:
        print(f"Luz ambiente (SPI): {luz}/255")
    else:
        print("Luz ambiente: NO DISPONIBLE")
    
    # Mostrar posición determinada
    print(f"Posición estimada: {posicion.upper()}")
    
    # Mostrar estado del motor
    estados = {
        MOTOR_DETENIDO: "DETENIDO",
        MOTOR_SUBIENDO: "SUBIENDO",
        MOTOR_BAJANDO: "BAJANDO"
    }
    print(f"Estado motor: {estados[estado_motor]}")
    
    # Mostrar modo de operación
    modos = {
        MODO_AUTOMATICO: "AUTOMÁTICO (ALS activado)",
        MODO_MANUAL: "MANUAL (ALS desactivado)"
    }
    print(f"Modo operación: {modos[modo_operacion]}")
    
    print("="*50)
    print("Esperando pulsación del botón o acción automática...")
    print("="*50 + "\n")

def manejar_pulsacion(posicion_actual):
    """Maneja la lógica de pulsaciones del botón"""
    global modo_operacion, tiempo_ultima_pulsacion, contador_pulsos

    tiempo_actual = time.time()

    # Primera pulsación
    if tiempo_actual - tiempo_ultima_pulsacion > DOBLE_PULSO_TIEMPO:
        contador_pulsos = 1
    else:
        contador_pulsos += 1

    tiempo_ultima_pulsacion = tiempo_actual

    # Detectar doble pulsación para cambiar modo
    if contador_pulsos == 2:
        modo_operacion = MODO_MANUAL if modo_operacion == MODO_AUTOMATICO else MODO_AUTOMATICO
        print(f"\n[COMANDO] Cambiando a modo {'MANUAL' if modo_operacion == MODO_MANUAL else 'AUTOMÁTICO'}")
        contador_pulsos = 0
        return

    # Si es pulsación simple y estamos en modo manual
    if modo_operacion == MODO_MANUAL and contador_pulsos == 1:
        print("\n[COMANDO] Botón presionado (modo manual) - Alternando movimiento")

        # Determinar acción basada en posición actual
        if posicion_actual == "superior":
            print("[LOGICA] Cortina en TOPE SUPERIOR - Bajando")
            control_motor("bajar")

        elif posicion_actual == "inferior":
            print("[LOGICA] Cortina en TOPE INFERIOR - Subiendo")
            control_motor("subir")

        elif posicion_actual == "intermedia":
            # Si está en posición intermedia, alternar dirección
            if estado_motor == MOTOR_SUBIENDO:
                print("[LOGICA] Cortina INTERMEDIA - Cambiando a BAJAR")
                control_motor("bajar")
            elif estado_motor == MOTOR_BAJANDO:
                print("[LOGICA] Cortina INTERMEDIA - Cambiando a SUBIR")
                control_motor("subir")
            else:
                # Por defecto subir si está detenido en medio
                print("[LOGICA] Cortina INTERMEDIA - Iniciando SUBIDA")
                control_motor("subir")

# Mensaje inicial
print("\n" + "="*50)
print("SISTEMA DE CORTINA INTELIGENTE CON SENSOR DE LUZ SPI")
print("="*50)
print("Configuración:")
print(f"- Distancia parada superior: {DISTANCIA_PARADA_SUP} cm")
print(f"- Distancia parada inferior: {DISTANCIA_PARADA_INF} cm")
print(f"- Botón conectado en GPIO{BOTON_PIN}")
print(f"- Umbral luz alta: >{UMBRAL_LUZ_ALTA}/255 (cerrar cortina)")
print(f"- Umbral luz baja: <{UMBRAL_LUZ_BAJA}/255 (abrir cortina)")
print(f"- Intervalo lectura luz: {INTERVALO_LUZ} segundos")
print(f"- Doble pulsación para cambiar modo: {DOBLE_PULSO_TIEMPO} segundos")
print("="*50)
print("Instrucciones:")
print("- Doble clic en el botón: Cambia entre modo automático y manual")
print("- En modo manual: Clic simple controla la cortina")
print("- En modo automático: El sensor ALS controla la cortina")
print("="*50)

try:
    contador_actualizacion = 0
    luz_actual = None

    while True:
        tiempo_actual = time.time()

        # Leer sensores ultrasónicos
        dist_sup = medir_distancia(TRIG_SUP, ECHO_SUP, "SUPERIOR")
        dist_inf = medir_distancia(TRIG_INF, ECHO_INF, "INFERIOR")

        # Determinar posición actual
        posicion_actual = determinar_posicion(dist_sup, dist_inf)

        # Leer sensor de luz en intervalos definidos
        if tiempo_actual - ultimo_tiempo_luz >= INTERVALO_LUZ:
            luz_actual = leer_luz()
            ultimo_tiempo_luz = tiempo_actual

        # Actualizar estado cada 5 ciclos
        contador_actualizacion += 1
        if contador_actualizacion >= 5:
            imprimir_estado(dist_sup, dist_inf, posicion_actual, luz_actual)
            contador_actualizacion = 0

        # Leer estado del botón con antirrebote
        estado_boton = GPIO.input(BOTON_PIN)

        # Detectar flanco descendente (botón presionado)
        if estado_boton == GPIO.LOW and tiempo_actual - ultimo_tiempo_boton > DEBOUNCE_TIME:
            ultimo_tiempo_boton = tiempo_actual
            manejar_pulsacion(posicion_actual)

        # Verificar límites durante movimiento
        if estado_motor == MOTOR_SUBIENDO:
            if dist_sup is not None and dist_sup <= DISTANCIA_PARADA_SUP:
                print("[LÍMITE] Cortina alcanzó tope SUPERIOR")
                control_motor("detener")

        elif estado_motor == MOTOR_BAJANDO:
            if dist_inf is not None and dist_inf <= DISTANCIA_PARADA_INF:
                print("[LÍMITE] Cortina alcanzó tope INFERIOR")
                control_motor("detener")

        # Lógica automática basada en luz ambiente SPI (solo en modo automático)
        if modo_operacion == MODO_AUTOMATICO and estado_motor == MOTOR_DETENIDO and luz_actual is not None:
            # Luz alta (valor alto) -> cerrar cortina (bajar)
            if luz_actual < UMBRAL_LUZ_ALTA and posicion_actual != "inferior":
                print(f"[AUTO] Luz alta ({luz_actual}/255) - Cerrando cortina")
                control_motor("bajar")

            # Luz baja (valor bajo) -> abrir cortina (subir)
            elif luz_actual > UMBRAL_LUZ_BAJA and posicion_actual != "superior":
                print(f"[AUTO] Luz baja ({luz_actual}/255) - Abriendo cortina")
                control_motor("subir")

        # Manejar contador de pulsaciones para resetear si pasa el tiempo
        if contador_pulsos > 0 and tiempo_actual - tiempo_ultima_pulsacion > DOBLE_PULSO_TIEMPO:
            contador_pulsos = 0

        time.sleep(TIEMPO_ESPERA)

except KeyboardInterrupt:
    print("\nPrograma interrumpido por el usuario")
except Exception as e:
    print(f"\nError en el sistema: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("\nDeteniendo motor y limpiando GPIO...")
    control_motor("detener")
    GPIO.cleanup()
    if spi is not None:
        spi.close()  # Cerrar conexión SPI
    print("Limpieza completada. Programa terminado.")
  
