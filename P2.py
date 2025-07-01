
# Fusion del sistema de red con RESTCONF y Subinterfaces

import os
import re
import ipaddress
import csv
import json
import requests
import urllib3
from datetime import datetime
from requests.auth import HTTPBasicAuth

# Configuracion general
ARCHIVO_REGISTRO = "registros_red.csv"
IP_ROUTER = "192.168.56.104"
USUARIO_ROUTER = "admin"
CONTRASENA_ROUTER = "admin123"

urllib3.disable_warnings()  # Ignora advertencias por certificado SSL

# Inicializa archivo de registro
def iniciar_registro():
    if not os.path.exists(ARCHIVO_REGISTRO):
        with open(ARCHIVO_REGISTRO, mode='w', newline='', encoding='utf-8') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["Fecha", "Hora", "Usuario", "Acción", "Detalles"])

def registrar_evento(usuario, accion, detalles=""):
    try:
        with open(ARCHIVO_REGISTRO, mode='a', newline='', encoding='utf-8') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow([
                datetime.now().strftime("%d-%m-%Y"),
                datetime.now().strftime("%H:%M:%S"),
                usuario,
                accion,
                str(detalles)
            ])

        datos = {
            "fecha": datetime.now().strftime("%d-%m-%Y"),
            "hora": datetime.now().strftime("%H:%M:%S"),
            "usuario": usuario,
            "accion": accion,
            "detalles": detalles
        }
        guardar_configuracion_en_json(datos, prefijo="evento")

    except Exception as e:
        print(f"⚠ Error en registro: {e}")

# Guardar configuraciones en JSON
def guardar_configuracion_en_json(datos, prefijo="backup"):
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    nombre_archivo = f"{prefijo}_{timestamp}.json"
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4)
        print(f"📁 Configuración guardada en '{nombre_archivo}'")
    except Exception as e:
        print(f"❌ Error al guardar configuración: {e}")

# Validación de IP y máscara
def validar_ip(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ValueError:
        return False

def validar_mascara(mascara):
    try:
        ip_obj = ipaddress.IPv4Address(mascara)
        return ip_obj > ipaddress.IPv4Address("0.0.0.0") and ip_obj <= ipaddress.IPv4Address("255.255.255.255")
    except ValueError:
        return False

# RESTCONF - Cambiar hostname
def configurar_hostname_restconf(nuevo_hostname, usuario_actual):
    url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native/hostname"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }
    payload = {
        "Cisco-IOS-XE-native:hostname": nuevo_hostname
    }
    try:
        response = requests.put(
            url,
            headers=headers,
            auth=HTTPBasicAuth(USUARIO_ROUTER, CONTRASENA_ROUTER),
            json=payload,
            verify=False
        )
        if response.status_code in [200, 204]:
            print(f"✅ Hostname cambiado a '{nuevo_hostname}' exitosamente.")
            registrar_evento(usuario_actual, "CAMBIO_HOSTNAME", nuevo_hostname)
        else:
            print(f"❌ Error ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en RESTCONF: {e}")

# Función para activar/desactivar interfaz
def activar_interfaz(nombre_interfaz, usuario_actual, activar=True):
    """Función para activar/desactivar interfaces usando el parámetro 'shutdown'"""
    url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet={nombre_interfaz}/shutdown"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }
    payload = {"Cisco-IOS-XE-native:shutdown": not activar}  # True=desactivada, False=activada
    
    try:
        response = requests.patch(
            url,
            headers=headers,
            auth=HTTPBasicAuth(USUARIO_ROUTER, CONTRASENA_ROUTER),
            json=payload,
            verify=False
        )
        
        if response.status_code in [200, 204]:
            estado = "activada" if activar else "desactivada"
            print(f"✅ Interfaz {nombre_interfaz} {estado} exitosamente")
            registrar_evento(usuario_actual, f"INTERFAZ_{estado.upper()}", nombre_interfaz)
        else:
            print(f"❌ Error al cambiar estado de interfaz ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en RESTCONF: {e}")

# RESTCONF - Crear subinterfaz (versión corregida)
def crear_subinterfaz(nombre_subif, vlan_id, ip, mascara, usuario_actual):
    if not validar_ip(ip):
        print("❌ Dirección IP inválida")
        return
    if not validar_mascara(mascara):
        print("❌ Máscara inválida")
        return

    # Extraemos el número de interfaz principal (ej: "1" de "1.10")
    try:
        interfaz_principal = nombre_subif.split('.')[0]
    except IndexError:
        print("❌ Formato de subinterfaz incorrecto. Use formato como '1.10'")
        return

    url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet={nombre_subif}"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }
    
    payload = {
        "Cisco-IOS-XE-native:GigabitEthernet": {
            "name": nombre_subif,
            "description": f"Subinterfaz VLAN {vlan_id}",
            "vrf": {"forwarding": "default"},  # Asegura que está en VRF por defecto
            "encapsulation": {
                "dot1Q": {
                    "vlan-id": int(vlan_id)
                }
            },
            "ip": {
                "address": {
                    "primary": {
                        "address": ip,
                        "mask": mascara
                    }
                },
                "arp": {
                    "timeout": 14400  # Tiempo de espera ARP estándar
                }
            }
        }
    }

    try:
        # Primero verificamos si la interfaz principal existe
        check_url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet={interfaz_principal}"
        check_response = requests.get(
            check_url,
            headers=headers,
            auth=HTTPBasicAuth(USUARIO_ROUTER, CONTRASENA_ROUTER),
            verify=False
        )

        if check_response.status_code != 200:
            print(f"❌ La interfaz principal GigabitEthernet {interfaz_principal} no existe")
            return

        # Configuramos la subinterfaz
        response = requests.put(
            url,
            headers=headers,
            auth=HTTPBasicAuth(USUARIO_ROUTER, CONTRASENA_ROUTER),
            json=payload,
            verify=False
        )

        if response.status_code in [200, 204]:
            print(f"✅ Subinterfaz {nombre_subif} configurada exitosamente para VLAN {vlan_id} con IP {ip}/{mascara}")
            registrar_evento(usuario_actual, "SUBINTERFAZ_CREADA", f"{nombre_subif} - VLAN {vlan_id} - {ip}/{mascara}")
            
            # Activamos la interfaz por defecto
            activar_interfaz(nombre_subif, usuario_actual, activar=True)
        else:
            print(f"❌ Error al configurar subinterfaz ({response.status_code}): {response.text}")
            registrar_evento(usuario_actual, "ERROR_CONFIGURACION", f"{response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión RESTCONF: {e}")
        registrar_evento(usuario_actual, "ERROR_CONEXION", str(e))

# Autenticacion exclusiva para usuario admin
def sesion():
    print("\nInicio de sesión - Solo admin autorizado")
    while True:
        usuario = input("Nombre de usuario: ").strip()
        if usuario == "admin":
            contrasena = input("Contraseña: ").strip()
            if contrasena == "admin123":
                print("✅ Bienvenido admin")
                registrar_evento(usuario, "INICIO_SESION_EXITOSO")
                return usuario
            else:
                print("❌ Contraseña incorrecta")
                registrar_evento(usuario, "INTENTO_FALLIDO", "Contraseña incorrecta")
        else:
            print("❌ Acceso denegado. Solo se permite el usuario 'admin'")
            registrar_evento("DESCONOCIDO", "INTENTO_USUARIO", f"Intento de acceso con usuario: {usuario}")

# Mostrar hostname actual
def ver_hostname_actual():
    url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native/hostname"
    headers = {
        "Accept": "application/yang-data+json"
    }
    try:
        response = requests.get(
            url,
            headers=headers,
            auth=HTTPBasicAuth(USUARIO_ROUTER, CONTRASENA_ROUTER),
            verify=False
        )
        if response.status_code == 200:
            data = response.json()
            hostname = data.get("Cisco-IOS-XE-native:hostname", "Desconocido")
            print(f"🔎 Hostname actual del router: {hostname}")
        else:
            print(f"❌ Error al obtener hostname ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en RESTCONF: {e}")

# Menú RESTCONF
def menu_configuracion_restconf(usuario):
    while True:
        print("""
--- Configuración RESTCONF ---
1. Ver hostname actual
2. Cambiar hostname
3. Crear subinterfaz
4. Activar/Desactivar interfaz
5. Volver al menú principal
""")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == "1":
            ver_hostname_actual()
            registrar_evento(usuario, "VER_HOSTNAME")
        elif opcion == "2":
            nuevo_hostname = input("Nuevo hostname: ").strip()
            configurar_hostname_restconf(nuevo_hostname, usuario)
        elif opcion == "3":
            subif = input("Nombre de subinterfaz (ej: 1.10): ").strip()
            vlan = input("VLAN ID: ").strip()
            ip = input("Dirección IP: ").strip()
            mascara = input("Máscara de subred: ").strip()
            crear_subinterfaz(subif, vlan, ip, mascara, usuario)
        elif opcion == "4":
            interfaz = input("Nombre de interfaz (ej: 1.10): ").strip()
            accion = input("¿Activar (1) o Desactivar (2)? ").strip()
            if accion == "1":
                activar_interfaz(interfaz, usuario, activar=True)
            elif accion == "2":
                activar_interfaz(interfaz, usuario, activar=False)
            else:
                print("❌ Opción no válida")
        elif opcion == "5":
            break
        else:
            print("❌ Opción no válida")

# Menú principal
def menu_principal():
    iniciar_registro()
    usuario_actual = sesion()

    while True:
        print("""
+-----------------------------+
| 🚀 MENÚ RED Y RESTCONF       |
| 1. Configuración RESTCONF     |
| 2. Salir                     |
+-----------------------------+
""")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == "1":
            menu_configuracion_restconf(usuario_actual)
        elif opcion == "2":
            registrar_evento(usuario_actual, "SESION_CERRADA")
            print("👋 Sesión finalizada. Hasta pronto.")
            break
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    menu_principal()
    
