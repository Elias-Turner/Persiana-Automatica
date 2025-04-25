import RPi.GPIO as GPIO
import time
from datetime import datetime

# Configuración de pines
boton_bajar = 0  # Reemplaza con el número real de pin GPIO
boton_subir = 1
rele_baja = 8
rele_sube = 9
sensor_luz_pin = 2  # Este es un ejemplo. Para lectura analógica necesitas un ADC como MCP3008

# Estado de la persiana
INDETERMINADO = 0
CERRADA = 1
ABIERTA = 2
estado_persiana = INDETERMINADO

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(rele_baja, GPIO.OUT)
GPIO.setup(rele_sube, GPIO.OUT)
GPIO.setup(boton_bajar, GPIO.IN)
GPIO.setup(boton_subir, GPIO.IN)

# Estado inicial de relés (desactivados)
GPIO.output(rele_baja, GPIO.HIGH)
GPIO.output(rele_sube, GPIO.HIGH)

# Simulación de lectura analógica (reemplaza esto si usás MCP3008)
def leer_luz():
    # Por ahora devuelve un valor simulado
    return 100  # Cambiá esto por una función real si usás ADC

def bajar_persiana():
    GPIO.output(rele_baja, GPIO.LOW)
    time.sleep(5)
    GPIO.output(rele_baja, GPIO.HIGH)
    print("Persiana parada")

def subir_persiana():
    GPIO.output(rele_sube, GPIO.LOW)
    time.sleep(5)
    GPIO.output(rele_sube, GPIO.HIGH)
    print("Persiana parada")

try:
    while True:
        valor_luz = leer_luz()
        print(f"Valor de luz: {valor_luz}")
        time.sleep(0.5)

        if valor_luz <= 95 and estado_persiana != CERRADA:
            print("Bajando persiana")
            time.sleep(0.5)
            bajar_persiana()
            estado_persiana = CERRADA
        elif valor_luz >= 120 and estado_persiana != ABIERTA:
            print("Subiendo persiana")
            time.sleep(0.5)
            subir_persiana()
            estado_persiana = ABIERTA

        # Controles manuales (opcional)
        if GPIO.input(boton_bajar) == GPIO.LOW:
            GPIO.output(rele_baja, GPIO.LOW)
        else:
            GPIO.output(rele_baja, GPIO.HIGH)

        if GPIO.input(boton_subir) == GPIO.LOW:
            GPIO.output(rele_sube, GPIO.LOW)
        else:
            GPIO.output(rele_sube, GPIO.HIGH)

except KeyboardInterrupt:
    print("Deteniendo programa")
    GPIO.cleanup()
