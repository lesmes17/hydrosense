import network, time
from machine import Pin, ADC, PWM
from _thread import start_new_thread
from utime import sleep, sleep_ms
from dht import DHT11
from hcsr04 import HCSR04
import json
import urequests

# ----------------------------Variables globales ------------------------------------
conver = 90.0
conver2 = 180.0
conver3 = 90.0
tem = 0
hum = 0
distance = 0
#api_key = "1fe91ac602ccc71425bf06c671c212ea"
#city = "Soacha,co"
#url = "https://api.openweathermap.org/data/2.5/weather?q=Soacha,co&appid=1fe91ac602ccc71425bf06c671c212ea"
    #---------------------[CONECTAR WIFI]------------------
def conectaWifi(red, password):
    global miRed
    miRed = network.WLAN(network.STA_IF)
    if not miRed.isconnected():          # Si no está conectado…!
        miRed.active(True)               # Activa la interfaz
        miRed.connect(red, password)     # Intenta conectar con la red
        print('Conectando a la red', red + "…")
        timeout = time.time()
        while not miRed.isconnected():           # Mientras no se conecte..
            if (time.time() - timeout) > 10:
                return False
    return True

    if conectaWifi("Altea Admon", "ConjuntoAlteaAdministracion"):
        print("Conexión exitosa!")
        print('Datos de la red (IP/netmask/gw/DNS):', miRed.ifconfig()) 
        sleep(1)
        print("Conectado!")
# Función para controlar el servo motor
def controlar_servo(servo_motor, angulo):
    if angulo < 0:
        angulo = 0
    elif angulo > 180:
        anguelo = 180
    duty = int(25 + angulo * 100 / 180)  # Ajustar los valores según el rango del servo
    servo_motor.duty(duty)       
        #url= "https://api.thingspeak.com/update?api_key=EZ40ZZRKPOGK4U9B"

#-------------------------- Función para ejecutar en el primer hilo ----------------------------------
def hilo1(semaforo):
    servo_sg90 = PWM(Pin(21), freq=50)
    s_dht = DHT11(Pin(15))
    ledN = Pin(5, Pin.OUT)
    releA = Pin(13, Pin.OUT)
    ledR = Pin(2, Pin.OUT)
    sensor_luz = ADC(Pin(35))
    ledF = Pin(22, Pin.OUT)
    ledv = Pin(26, Pin.OUT)
    sensorMq7 = ADC (Pin(34))
    sensorMq7.width(ADC.WIDTH_10BIT)
    sensorMq7.atten(ADC.ATTN_11DB)
    url_api = "https://api.thingspeak.com/update?api_key=EZ40ZZRKPOGK4U9B"
    url = "https://maker.ifttt.com/trigger/telegram/with/key/cWAlO2MkKkngRkS8fhiwoF5he3mTefuVGo1gXoABb3q?"
    while True:
# Medir temperatura y humedad con el sensor DHT22 ----------------------------------------
        s_dht.measure()
        tem = s_dht.temperature()
        hum = s_dht.humidity()
        print("Temperatura: {}°C, Humedad: {}%".format(tem, hum))
        respuesta = urequests.get(url_api+"&field1="+str(tem)+"&field2="+str(hum))# para thingspeak
        respuesta.close ()
        time.sleep(10)
# Enviar una notificación si la temperatura es alta
        if tem >= 25:
            #url = "https://maker.ifttt.com/trigger/telegram/with/key/cWAlO2MkKkngRkS8fhiwoF5he3mTefuVGo1gXoABb3q?"
            ledR.value(1)
            releA.value(1)
            try:
                semaforo.acquire()
                res = urequests.get(url+"&value1="+str(tem)+"&value2="+str(hum)+"&value3="+str("tempe_elevada")) # Alerta Telegram
                print(res.text)
                print(res.status_code)
                print(res.json)
                semaforo.release()
            except Exception as e:
                print(e)
                sleep(4)
        else:
            ledR.value(0)
            releA.value(0)
        sleep(4)

        lec = int(sensorMq7.read())

        ppm = 1200 / 1023
        co = ppm * lec
        print("Monoxido de carbono:", co, "ppm")
        sleep(4)
        
        if co > 550:
            ledv.value(1)
            print("Hay presencia de Monoxido de carbono")
            sleep(3)
        else:
           ledv.value(0)
           sleep(4)
        

#------------------- Función para ejecutar en el segundo hilo ---------------------------------
def hilo2(semaforo):
    sensor_distancia = HCSR04(trigger_pin=19, echo_pin=4)
    servo_sg90 = PWM(Pin(21), freq=50)
    releb = Pin(32, Pin.OUT)
    ledR = Pin(2, Pin.OUT)
    ledF = Pin(22, Pin.OUT)
    ledN = Pin(5, Pin.OUT)
    sensor_luz = ADC(Pin(35))
    sensor_Humedad = ADC(Pin(33))
    sensor_Humedad.atten(ADC.ATTN_11DB)
    sensor_Humedad.width(ADC.WIDTH_12BIT)
    url_api = "https://api.thingspeak.com/update?api_key=EZ40ZZRKPOGK4U9B"
    url = "https://maker.ifttt.com/trigger/telegram/with/key/cWAlO2MkKkngRkS8fhiwoF5he3mTefuVGo1gXoABb3q?"
    while True:
        # Medir la distancia con el sensor ultrasónico HC-SR04
        global distance
        distance = sensor_distancia.distance_cm()
        print("Distancia: {} cm".format(distance))
        respuesta = urequests.get(url_api+"&field3="+str(distance))
        respuesta.close ()
        time.sleep(4)
        
        semaforo.acquire()
        # Encender el LED si el nivel de agua es bajo
        if distance >= 55:
            ledN.value(1)
            res = urequests.get(url+"&value1="+str(distance)+"&value2="+str("NivelBajo")) #Alerta a Telegram
            print(res.status_code)
            print(res.json)
            print("Nivel bajo de agua")
            sleep(6)
        else:
            ledN.value(0)
            sleep(3)

        # Medir la intensidad de luz con el sensor de luz
        lectura = sensor_luz.read_u16()
        intensidad = lectura * (100 / 65535)
        print("Intensidad: {:.2f} %".format(intensidad))
        sleep(2)

        # Encender el LED si la intensidad de luz es baja
        if intensidad >=45 and intensidad <= 50:
            ledF.value(1)
            print("Nivel bajo de Luminosidad")
            sleep(2)
        else:
            ledF.value(0)
            sleep(4)

        medicion = float(sensor_Humedad.read())
        conversion = round(medicion * 98 / 4096, 2)
        print("Humedad Suelo:", conversion)
        sleep(2)
        
        if conversion >=24:
            releb.value(1)
            print("Humedad baja")
            for i in range (0 , 360, 30):
                controlar_servo(servo_sg90, i)
                sleep(2)
            else:
                releb.value(0)
                sleep(4)
        
        semaforo.release()

