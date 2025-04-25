import RPi.GPIO as GPIO
import time

# Configuración de pines
TRIG = 23  # Pin TRIG del sensor de distancia
ECHO = 24  # Pin ECHO del sensor de distancia
ENA = 12   # Pin ENA del puente H (control de velocidad)
IN1 = 16   # Pin IN1 del puente H (dirección)
IN2 = 18   # Pin IN2 del puente H (dirección)

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

# Configuración del PWM para el control del servo
pwm = GPIO.PWM(ENA, 1000)  # Frecuencia de 50Hz
pwm.start(0)

def medir_distancia():
    # Enviar pulso TRIG
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Medir el tiempo del pulso ECHO
    while GPIO.input(ECHO) == 0:
        inicio_pulso = time.time()
    while GPIO.input(ECHO) == 1:
        fin_pulso = time.time()

    duracion_pulso = fin_pulso - inicio_pulso
    distancia = duracion_pulso * 17150  # Convertir a cm
    return distancia

def girar_servo():
    GPIO.output(IN1, True)
    GPIO.output(IN2, False)
    pwm.ChangeDutyCycle(40)  # Ajustar velocidad del servo
    time.sleep(1)  # Girar por 1 segundo
    GPIO.output(IN1, False)
    GPIO.output(IN2, False)
    pwm.ChangeDutyCycle(0)

try:
    while True:
        distancia = medir_distancia()
        print(f"Distancia: {distancia:.2f} cm")
        if distancia > 10:
            girar_servo()
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Programa terminado")
    pwm.stop()
    GPIO.cleanup()
