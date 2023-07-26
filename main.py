# Realizado por ################ en Bogota colombia
# Programa diseñado para Hidrosense
#-----------------[Modulos y Clases]--------------------

from Paquete import hilo1, hilo2, conectaWifi
import network, time
from _thread import start_new_thread
import _thread as thread
from utime import sleep, sleep_ms
import json
import urequests

def main():
    red = "Altea Admon"  # Reemplaza "nombre_de_red" con el nombre real de tu red WiFi
    password = "ConjuntoAlteaAdministracion"  # Reemplaza "contraseña_de_red" con la contraseña real de tu red WiFi
    if conectaWifi(red, password):
        print("Conectado!")
        # Iniciar los hilos
        semaforo = thread.allocate_lock()
        start_new_thread(hilo1, (semaforo,))
        while True:
            hilo2(semaforo)
    else:
        print("No se pudo conectar a la red WiFi.")

# Iniciar el programa
if __name__ == '__main__':
    main()

