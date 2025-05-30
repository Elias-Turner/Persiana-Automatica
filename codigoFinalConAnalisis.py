# Inicializar motor apagado
GPIO.output(MOTOR_IN1, GPIO.LOW)
GPIO.output(MOTOR_IN2, GPIO.LOW)

# Variables de estado
estado_actual = "detenido"
ultimo_cambio = time.time()

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
            print(f"[{sensor_nombre}] Error: Pulso no detectado (Intento {i+1}/{INTENTOS_LECTURA})")
            continue
        
        try:
            duracion = pulso_fin - pulso_inicio
            distancia = (duracion * 34300) / 2  # Velocidad del sonido (343 m/s)
            
            if DISTANCIA_MIN <= distancia <= DISTANCIA_MAX:
                print(f"[{sensor_nombre}] Distancia medida: {distancia:.1f} cm")
                return distancia
            else:
                print(f"[{sensor_nombre}] Lectura fuera de rango: {distancia:.1f} cm (Intento {i+1}/{INTENTOS_LECTURA})")
        except Exception as e:
            print(f"[{sensor_nombre}] Error en cálculo: {str(e)}")
    
    print(f"[{sensor_nombre}] ERROR: Todas las lecturas fallaron")
    return None

def control_motor(accion):
    """Controla el motor con protección contra activación simultánea"""
    global estado_actual
    
    # Solo imprimir si hay cambio de estado
    if estado_actual != accion:
        print(f"[MOTOR] Cambiando estado: {estado_actual} → {accion}")
    
    GPIO.output(MOTOR_IN1, GPIO.LOW)
    GPIO.output(MOTOR_IN2, GPIO.LOW)
    time.sleep(0.1)  # Breve pausa para evitar cortocircuitos
    
    if accion == "subir":
        GPIO.output(MOTOR_IN1, GPIO.HIGH)
        GPIO.output(MOTOR_IN2, GPIO.LOW)
    elif accion == "bajar":
        GPIO.output(MOTOR_IN1, GPIO.LOW)
        GPIO.output(MOTOR_IN2, GPIO.HIGH)
    elif accion == "detener":
        GPIO.output(MOTOR_IN1, GPIO.LOW)
        GPIO.output(MOTOR_IN2, GPIO.LOW)
    
    estado_actual = accion

def leer_luz():
    """Lee el sensor de luz con filtro antirrebote"""
    lecturas = [GPIO.input(LDR_PIN) for _ in range(5)]
    valor_promedio = sum(lecturas) / len(lecturas)
    hay_luz = valor_promedio > UMBRAL_LUZ
    
    estado_luz = "LUZ" if hay_luz else "OSCURIDAD"
    print(f"[LDR] Estado: {estado_luz} (Lectura: {valor_promedio:.2f})")
    
    return hay_luz

def imprimir_estado():
    """Imprime estado actual del sistema"""
    print("\n" + "="*50)
    print(f"ESTADO ACTUAL: {estado_actual.upper()}")
    print(f"Última actualización: {time.strftime('%H:%M:%S')}")
    print("="*50)

# Mensaje inicial
print("\n" + "="*50)
print("SISTEMA DE CORTINA AUTÓNOMA INICIADO")
print("="*50)
print(f"Configuración:")
print(f"- Umbral luz: {UMBRAL_LUZ}")
print(f"- Distancia parada superior: {DISTANCIA_PARADA_SUP} cm")
print(f"- Distancia parada inferior: {DISTANCIA_PARADA_INF} cm")
print("="*50 + "\n")

try:
    contador_ciclos = 0
    while True:
        contador_ciclos += 1
        
        # Imprimir estado cada 10 ciclos
        if contador_ciclos % 10 == 0:
            imprimir_estado()
        
        # 1. Leer condiciones ambientales
        hay_luz = leer_luz()
        
        # 2. Medir distancias con manejo de errores
        dist_sup = medir_distancia(TRIG_SUP, ECHO_SUP, "SUPERIOR")
        dist_inf = medir_distancia(TRIG_INF, ECHO_INF, "INFERIOR")
        
        # 3. Lógica de control principal
        if hay_luz and estado_actual != "subiendo":
            if dist_sup is not None and dist_sup > DISTANCIA_PARADA_SUP:
                print("[CONTROL] Condición: LUZ detectada y cortina no en tope superior")
                control_motor("subir")
            else:
                print("[CONTROL] Condición: LUZ detectada pero no se requiere movimiento")
        
        elif not hay_luz and estado_actual != "bajando":
            if dist_inf is not None and dist_inf <= DISTANCIA_PARADA_INF:
                print("[CONTROL] Condición: OSCURIDAD detectada y cortina no en tope inferior")
                control_motor("bajar")
            else:
                print("[CONTROL] Condición: OSCURIDAD detectada pero no se requiere movimiento")
        
        # 4. Verificar límites durante movimiento
        if estado_actual == "subiendo" and dist_sup is not None:
            if dist_sup <= DISTANCIA_PARADA_SUP:
                print("[LÍMITE] Cortina alcanzó tope SUPERIOR")
                control_motor("detener")
        
        elif estado_actual == "bajando" and dist_inf is not None:
            if dist_inf > DISTANCIA_PARADA_INF:
                print("[LÍMITE] Cortina alcanzó tope INFERIOR")
                control_motor("detener")
        
        time.sleep(TIEMPO_ESPERA)

except KeyboardInterrupt:
    print("\n" + "="*50)
    print("PROGRAMA DETENIDO POR EL USUARIO")
    print("="*50)
finally:
    print("[MOTOR] Deteniendo motor y limpiando GPIO...")
    control_motor("detener")
    GPIO.cleanup()
    print("Limpieza completada. Programa terminado.")
