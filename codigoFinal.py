import RPi.GPIO as GPIO
import time

# Configuración de pines
LDR_PIN = 17  # Pin del sensor de luz LDR
TRIG1 = 23    # Pin TRIG del sensor de distancia 1
ECHO1 = 24    # Pin ECHO del sensor de distancia 1
TRIG2 = 27    # Pin TRIG del sensor de distancia 2
ECHO2 = 22    # Pin ECHO del sensor de distancia 2
IN1 = 5       # Pin IN1 del puente H
IN2 = 6       # Pin IN2 del puente H

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LDR_PIN, GPIO.IN)
GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(ECHO1, GPIO.IN)
GPIO.setup(TRIG2, GPIO.OUT)
GPIO.setup(ECHO2, GPIO.IN)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

def medir_distancia(TRIG, ECHO):
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        inicio_pulso = time.time()

    while GPIO.input(ECHO) == 1:
        fin_pulso = time.time()

    duracion_pulso = fin_pulso - inicio_pulso
    distancia = duracion_pulso * 17150
    return distancia

def motor_girar_sentido1():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)

def motor_girar_sentido2():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)

def motor_detener():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)

try:
    while True:
        if GPIO.input(LDR_PIN) == GPIO.HIGH:  # Detecta luz
            motor_girar_sentido1()
            distancia = medir_distancia(TRIG1, ECHO1)
            if distancia > 20:
                motor_detener()
        else:  # No detecta luz
            motor_girar_sentido2()
            distancia = medir_distancia(TRIG2, ECHO2)
            if distancia <= 20:
                motor_detener()

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Programa terminado")
    GPIO.cleanup()
