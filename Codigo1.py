from gpiozero import LightSensor, DistanceSensor, Servo, Button
from time import sleep


# Configuración de pines GPIO
ldr = LightSensor(18)  # PIN del sensor de luz (puede cambiar según tu conexión)
ultrasonico = DistanceSensor(echo=24, trigger=23)  # Pines del sensor ultrasónico
servo = Servo(17)  # PIN del servo motor
boton = Button(27)  # Botón para modo manual

# Umbrales (ajustar según tus pruebas)
DISTANCIA_MINIMA = 0.2  # metros
TIEMPO_VERIFICACION = 1  # segundos

# Estado actual de la persiana
abierta = False

def abrir_persiana():
    global abierta
    if not abierta:
        print("Abriendo persiana...")
        servo.max()  # Mueve el servo a una posición de apertura (puede variar)
        abierta = True
        sleep(1)

def cerrar_persiana():
    global abierta
    if abierta:
        print("Cerrando persiana...")
        servo.min()  # Mueve el servo a posición de cierre
        abierta = False
        sleep(1)

def accion_manual():
    if abierta:
        cerrar_persiana()
    else:
        abrir_persiana()

# Asignar función al botón
boton.when_pressed = accion_manual

try:
    while True:
        print(f"Luz: {ldr.value:.2f}, Distancia: {ultrasonico.distance:.2f} m")

        # Verifica si hay algo bloqueando la persiana
        if ultrasonico.distance < DISTANCIA_MINIMA:
            print("Obstáculo detectado. Motor detenido.")
            sleep(TIEMPO_VERIFICACION)
            continue

        # Si hay mucha luz, cerrar la persiana. Si está oscuro, abrirla.
        if ldr.value > 0.5:
            cerrar_persiana()
        else:
            abrir_persiana()

        sleep(TIEMPO_VERIFICACION)

except KeyboardInterrupt:
    print("Programa terminado por el usuario.")
