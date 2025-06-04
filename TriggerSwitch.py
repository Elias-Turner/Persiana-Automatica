import RPi.GPIO as GPIO
import time

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
DISTANCIA_PARADA_SUP = 20.0  # Distancia para detener en superior
DISTANCIA_PARADA_INF = 20.0  # Distancia para detener en inferior
INTENTOS_LECTURA = 3    # Intentos para lectura válida
TIEMPO_ESPERA = 0.1    # Tiempo entre lecturas (segundos)
DEBOUNCE_TIME = 0.3    # Tiempo antirrebote del botón

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

# Variable para antirrebote
ultimo_tiempo_boton = 0

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

def imprimir_estado(dist_sup, dist_inf, posicion):
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
    
    # Mostrar posición determinada
    print(f"Posición estimada: {posicion.upper()}")
    
    # Mostrar estado del motor
    estados = {
        MOTOR_DETENIDO: "DETENIDO",
        MOTOR_SUBIENDO: "SUBIENDO",
        MOTOR_BAJANDO: "BAJANDO"
    }
    print(f"Estado motor: {estados[estado_motor]}")
    
    print("="*50)
    print("Esperando pulsación del botón...")
    print("="*50 + "\n")

# Mensaje inicial
print("\n" + "="*50)
print("SISTEMA DE CORTINA CON BOTÓN FÍSICO")
print("="*50)
print("Configuración:")
print(f"- Distancia parada superior: {DISTANCIA_PARADA_SUP} cm")
print(f"- Distancia parada inferior: {DISTANCIA_PARADA_INF} cm")
print(f"- Botón conectado en GPIO{BOTON_PIN}")
print("="*50)

try:
    contador_actualizacion = 0
    while True:
        # Leer sensores
        dist_sup = medir_distancia(TRIG_SUP, ECHO_SUP, "SUPERIOR")
        dist_inf = medir_distancia(TRIG_INF, ECHO_INF, "INFERIOR")
        
        # Determinar posición actual
        posicion_actual = determinar_posicion(dist_sup, dist_inf)
        
        # Actualizar estado cada 5 ciclos
        contador_actualizacion += 1
        if contador_actualizacion >= 5:
            imprimir_estado(dist_sup, dist_inf, posicion_actual)
            contador_actualizacion = 0
        
        # Leer estado del botón con antirrebote
        estado_boton = GPIO.input(BOTON_PIN)
        tiempo_actual = time.time()
        
        # Detectar flanco descendente (botón presionado)
        if estado_boton == GPIO.LOW and tiempo_actual - ultimo_tiempo_boton > DEBOUNCE_TIME:
            ultimo_tiempo_boton = tiempo_actual
            print("\n[COMANDO] Botón presionado - Alternando movimiento")
            
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
        
        # Verificar límites durante movimiento
        if estado_motor == MOTOR_SUBIENDO:
            if dist_sup is not None and dist_sup <= DISTANCIA_PARADA_SUP:
                print("[LÍMITE] Cortina alcanzó tope SUPERIOR")
                control_motor("detener")
                
        elif estado_motor == MOTOR_BAJANDO:
            if dist_inf is not None and dist_inf <= DISTANCIA_PARADA_INF:
                print("[LÍMITE] Cortina alcanzó tope INFERIOR")
                control_motor("detener")
        
        time.sleep(TIEMPO_ESPERA)

except KeyboardInterrupt:
    print("\nPrograma interrumpido por el usuario")
finally:
    print("\nDeteniendo motor y limpiando GPIO...")
    control_motor("detener")
    GPIO.cleanup()
    print("Limpieza completada. Programa terminado.")
