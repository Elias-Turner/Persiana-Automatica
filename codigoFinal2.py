import RPi.GPIO as GPIO
import time

# Configuración de pines
LDR_PIN = 17    # Sensor de luz (LDR)
TRIG_SUP = 23   # Sensor ultrasónico superior
ECHO_SUP = 24
TRIG_INF = 27   # Sensor ultrasónico inferior
ECHO_INF = 22
MOTOR_IN1 = 5   # Control motor
MOTOR_IN2 = 6

# Constantes configurables
DISTANCIA_MIN = 5.0    # Distancia mínima válida (cm)
DISTANCIA_MAX = 100.0  # Distancia máxima válida (cm)
UMBRAL_LUZ = 0.5       # Umbral luz/oscuridad (0-1)
TIEMPO_ESPERA = 0.1    # Tiempo entre lecturas (segundos)
DISTANCIA_PARADA_SUP = 20.0  # Distancia para detener en superior
DISTANCIA_PARADA_INF = 20.0  # Distancia para detener en inferior
INTENTOS_LECTURA = 5    # Intentos para lectura válida

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LDR_PIN, GPIO.IN)
GPIO.setup(TRIG_SUP, GPIO.OUT)
GPIO.setup(ECHO_SUP, GPIO.IN)
GPIO.setup(TRIG_INF, GPIO.OUT)
GPIO.setup(ECHO_INF, GPIO.IN)
GPIO.setup(MOTOR_IN1, GPIO.OUT)
GPIO.setup(MOTOR_IN2, GPIO.OUT)

# Inicializar motor apagado
GPIO.output(MOTOR_IN1, GPIO.LOW)
GPIO.output(MOTOR_IN2, GPIO.LOW)

def medir_distancia(trig, echo):
    """Mide distancia con sensor ultrasónico con validación de errores"""
    for _ in range(INTENTOS_LECTURA):
        GPIO.output(trig, True)
        time.sleep(0.00001)
        GPIO.output(trig, False)
        
        timeout = time.time() + 0.04  # Timeout de 40ms
        while GPIO.input(echo) == 0 and time.time() < timeout:
            pulso_inicio = time.time()
        
        timeout = time.time() + 0.04
        while GPIO.input(echo) == 1 and time.time() < timeout:
            pulso_fin = time.time()
        
        try:
            duracion = pulso_fin - pulso_inicio
            distancia = (duracion * 34300) / 2  # Velocidad del sonido (343 m/s)
            
            if DISTANCIA_MIN <= distancia <= DISTANCIA_MAX:
                return distancia
        except UnboundLocalError:
            pass
    
    return None  # Retorna None si todas las lecturas fallan

def control_motor(accion):
    """Controla el motor con protección contra activación simultánea"""
    GPIO.output(MOTOR_IN1, GPIO.LOW)
    GPIO.output(MOTOR_IN2, GPIO.LOW)
    time.sleep(0.05)  # Breve pausa para evitar cortocircuitos
    
    if accion == "subir":
        GPIO.output(MOTOR_IN1, GPIO.HIGH)
        GPIO.output(MOTOR_IN2, GPIO.LOW)
    elif accion == "bajar":
        GPIO.output(MOTOR_IN1, GPIO.LOW)
        GPIO.output(MOTOR_IN2, GPIO.HIGH)
    elif accion == "detener":
        GPIO.output(MOTOR_IN1, GPIO.LOW)
        GPIO.output(MOTOR_IN2, GPIO.LOW)

def leer_luz():
    """Lee el sensor de luz con filtro antirrebote"""
    lecturas = [GPIO.input(LDR_PIN) for _ in range(5)]
    return sum(lecturas) / len(lecturas) > UMBRAL_LUZ

# Variables de estado
estado_actual = "detenido"
ultimo_cambio = time.time()

try:
    while True:
        # 1. Leer condiciones ambientales
        hay_luz = leer_luz()
        
        # 2. Medir distancias con manejo de errores
        dist_sup = medir_distancia(TRIG_SUP, ECHO_SUP)
        dist_inf = medir_distancia(TRIG_INF, ECHO_INF)
        
        # 3. Lógica de control principal
        if hay_luz and estado_actual != "subiendo":
            if dist_sup is not None and dist_sup > DISTANCIA_PARADA_SUP:
                control_motor("subir")
                estado_actual = "subiendo"
        
        elif not hay_luz and estado_actual != "bajando":
            if dist_inf is not None and dist_inf <= DISTANCIA_PARADA_INF:
                control_motor("bajar")
                estado_actual = ("bajando")
        
        # 4. Verificar límites durante movimiento
        if estado_actual == "subiendo" and dist_sup is not None:
            if dist_sup <= DISTANCIA_PARADA_SUP:
                control_motor("detener")
                estado_actual = "detenido"
        
        elif estado_actual == "bajando" and dist_inf is not None:
            if dist_inf > DISTANCIA_PARADA_INF:
                control_motor("detener")
                estado_actual = "detenido"
        
        time.sleep(TIEMPO_ESPERA)

except KeyboardInterrupt:
    print("\nPrograma detenido por el usuario")
finally:
    control_motor("detener")
    GPIO.cleanup()
