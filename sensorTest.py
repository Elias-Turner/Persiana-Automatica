import RPi.GPIO as GPIO
import time

# Configuración de los pines
TRIG = 23  # Pin GPIO conectado al TRIG del sensor
ECHO = 24  # Pin GPIO conectado al ECHO del sensor

# Configuración de los pines GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def medir_distancia():
    # Enviar un pulso de 10µs al TRIG
    GPIO.output(TRIG, True)
    time.sleep(0.00000000001)
    GPIO.output(TRIG, False)

    # Esperar a que el ECHO se active
    while GPIO.input(ECHO) == 0:
        inicio_pulso = time.time()

    # Esperar a que el ECHO se desactive
    while GPIO.input(ECHO) == 1:
        fin_pulso = time.time()

    # Calcular la duración del pulso
    duracion_pulso = fin_pulso - inicio_pulso

    # Calcular la distancia (velocidad del sonido: 34300 cm/s)
    distancia = (duracion_pulso * 34300) / 2

    return distancia

try:
    while True:
        distancia = medir_distancia()
        print(f"Distancia: {distancia:.2f} cm")
        time.sleep(1)

except KeyboardInterrupt:
    print("Medición detenida por el usuario")
    GPIO.cleanup()
