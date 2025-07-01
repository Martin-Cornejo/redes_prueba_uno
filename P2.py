import os
import ipaddress
import csv
import json
import requests
import urllib3
from datetime import datetime
from requests.auth import HTTPBasicAuth


# ================================================================
# ASCII art para una presentacion mas fixita
# Colores ANSI
RED = "\033[91m"
WHITE = "\033[97m"
YELLOW = "\033[93m"
RESET = "\033[0m"

ascii_art = f"""
{RED}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{RESET}
{RED}|{WHITE}                                                                   {RED}|{RESET}
{RED}|{WHITE}  ____  _____ ____   _____ ____           __  ____      ___ ___    {RED}|{RESET}
{RED}|{WHITE} |  _ \ | ____|  _ \| ____/  __|         /  \ \   \    /  //_  |   {RED}|{RESET}
{RED}|{WHITE} | |_) || |_  | | | | |_  | |__  _____  / /\ \ \   \  /  /   | |   {RED}|{RESET}
{RED}|{WHITE} |  _ < |  _| | | | |  _| \___ \ \___/ / /__\ \ \   \/  /    | |   {RED}|{RESET}
{RED}|{WHITE} | | | || |___| |_| | |___ ___) |     /  ___   \ \     /    _| |_  {RED}|{RESET}
{RED}|{WHITE} |_| \_|\_____|____/|_____|____/     /__/   \___\ \___/    |_____| {RED}|{RESET}
{RED}|{WHITE}  -.-.-.-.-.-.-.-.-.-.-.-.-.-.-     -.-.-.-.-.-.-.-.-.-.-.-.-.-.-  {RED}|{RESET}
{RED}|{WHITE}                                                                   {RED}|{RESET}
{RED}|{YELLOW}                       - Redes Avanzadas 1 -                       {RED}|{RESET}
{RED}|{WHITE}                                                                   {RED}|{RESET}
{RED}|{YELLOW}                     - Eloy , Martin , Davor -                     {RED}|{RESET}
{RED}|{WHITE}                                                                   {RED}|{RESET}
{RED}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{RESET}
"""

print(ascii_art)



# Configuración general
ARCHIVO_REGISTRO = "registros_red.csv"
IP_ROUTER = "192.168.56.104"
USUARIO_ROUTER = "cisco"
CONTRASENA_ROUTER = "cisco123!"

# Deshabilita las credenciales SSL
urllib3.disable_warnings()

# ==============================================
# Funciones de Registro y Utilidades
# ==============================================

def iniciar_registro():
    """Inicializa el archivo de registro si no existe"""
    if not os.path.exists(ARCHIVO_REGISTRO):
        try:
            with open(ARCHIVO_REGISTRO, mode='w', newline='', encoding='utf-8') as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(["Fecha", "Hora", "Usuario", "Acción", "Detalles"])
                archivo.close()
        except Exception as e:
            print(f"😭 Error al crear archivo de registro: {e}")

#aqui se registran los eventos en un archivo CSV
#se usa para registrar los eventos importantes durante la sesion

def registrar_evento(usuario, accion, detalles=""):
    """Registra un evento en el archivo CSV"""
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
            archivo.close()
    except Exception as e:


        print(f"( ˘︹˘ ) Error en registro: {e}")

def guardar_configuracion_en_json(datos, prefijo="backup"):
    """Guarda configuración en archivo JSON"""
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    nombre_archivo = f"{prefijo}_{timestamp}.json"
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4)
            archivo.close()
        print(f" ConfiguraciOn guardada en '{nombre_archivo}'")
    except Exception as e:
        print(f" Error al guardar configuraciOn: {e}")

# ==============================================
# Funciones de Validación
# ==============================================

#ipv4
def validar_ip(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ValueError:
        return False


#ipv6
def validar_ipv6(ip):
    """Valida una dirección IPv6"""
    try:
        ipaddress.IPv6Address(ip)
        return True
    except ValueError:
        return False

# ==============================================
# Funcion para validar Máscaras

def validar_mascara(mascara):
    try:
        # Verificar si ya está en formato CIDR (ej: "24")
        if mascara.isdigit() and 0 <= int(mascara) <= 32:
            return str(ipaddress.IPv4Network(f'0.0.0.0/{mascara}').netmask)
        
        # Verificar formato decimal (ej: "255.255.255.0")
        partes = mascara.split('.')
        if len(partes) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in partes):
            # Convertir a formato de red para validación
            mascara_obj = ipaddress.IPv4Address(mascara)
            mascara_bin = ''.join(f'{int(octeto):08b}' for octeto in map(int, partes))
            
            # Validar que sea una máscara contigua
            if '01' in mascara_bin:
                return None
                
            return str(mascara_obj)
            
        return None
    except ValueError:
        return None

def obtener_ips_asignadas():
    """Obtiene todas las IPs asignadas a interfaces"""
    url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native/interface"
    headers = {"Accept": "application/yang-data+json"}
    ips_asignadas = {'ipv4': [], 'ipv6': []}
    
    try:
        response = requests.get(
            url,
            headers=headers,
            auth=HTTPBasicAuth(USUARIO_ROUTER, CONTRASENA_ROUTER),
            verify=False,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            interfaces = data.get("Cisco-IOS-XE-native:interface", {})
            
            for int_type in ["GigabitEthernet", "Loopback"]:
                if int_type in interfaces:
                    for interface in (interfaces[int_type] if isinstance(interfaces[int_type], list) else [interfaces[int_type]]):
                        # IPv4
                        ipv4 = interface.get("ip", {}).get("address", {}).get("primary", {}).get("address")
                        if ipv4:
                            ips_asignadas['ipv4'].append(ipv4)
                        
                        # IPv6
                        ipv6_prefixes = interface.get("ipv6", {}).get("address", {}).get("prefix-list", [])
                        if isinstance(ipv6_prefixes, dict):
                            ipv6_prefixes = [ipv6_prefixes]
                        for prefix in ipv6_prefixes:
                            ipv6 = prefix.get("prefix", "").split('/')[0]
                            if ipv6:
                                ips_asignadas['ipv6'].append(ipv6)
    
    except requests.exceptions.RequestException:
        pass
    
    return ips_asignadas

# ==============================================
# Funciones de Config del Router
# ==============================================

def activar_interfaz(interfaz, usuario_actual, activar=True):
    """Activa o desactiva una interfaz del router"""
    if interfaz == "1":
        print("❌ No se puede modificar GigabitEthernet1")
        return
        
    url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet={interfaz}"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }
    
    # Payload corregido para Cisco IOS XE
    payload = {
        "Cisco-IOS-XE-native:GigabitEthernet": {
            "name": interfaz,
            "shutdown": None if activar else {"#text": "true"}
        }
    }
    
    try:
        response = requests.patch(
            url,
            headers=headers,
            auth=HTTPBasicAuth(USUARIO_ROUTER, CONTRASENA_ROUTER),
            json=payload,
            verify=False,
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            estado = "activada" if activar else "desactivada"
            print(f"✅ Interfaz GigabitEthernet{interfaz} {estado} exitosamente")
            registrar_evento(usuario_actual, f"INTERFAZ_{estado.upper()}", f"GigabitEthernet{interfaz}")
        else:
            print(f"❌ Error al cambiar estado de interfaz ({response.status_code}): {response.text}")
            registrar_evento(usuario_actual, "ERROR_INTERFAZ", f"{response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en RESTCONF: {e}")
        registrar_evento(usuario_actual, "ERROR_CONEXION", str(e))

def configurar_ip_interfaz(interfaz, usuario_actual):
    """Configura dirección IP en una interfaz"""
    if interfaz == "1":
        print("❌ No se puede configurar GigabitEthernet1")
        return
    
    print("\n🔹 Configuración de IP para GigabitEthernet", interfaz)
    
    while True:
        tipo_ip = input("¿Configurar IPv4 (1) o IPv6 (2)? ").strip()
        if tipo_ip not in ["1", "2"]:
            os.system('cls' if os.name == 'nt' else 'clear')

            print("❌ Opcion invalida. Ingrese 1 para IPv4 o 2 para IPv6")
            continue
        break
    
    if tipo_ip == "1":  # IPv4
        while True:
            ip = input("Dirección IPv4: ").strip()
            if not validar_ip(ip):
                print("❌ Dirección IPv4 inválida")
                continue
                
            mascara = input("Máscara de subred (ej: 255.255.255.0 o 24): ").strip()
            mascara_validada = validar_mascara(mascara)
            if not mascara_validada:
                print("❌ Máscara inválida. Use formato como 255.255.255.0 o 24")
                continue
                
            # Verificar si la IP ya está asignada
            ips_asignadas = obtener_ips_asignadas()
            if ip in ips_asignadas['ipv4']:
                print(f"❌ La IP {ip} ya está asignada a otra interfaz")
                return
                
            break
            
        url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet={interfaz}"
        headers = {
            "Content-Type": "application/yang-data+json",
            "Accept": "application/yang-data+json"
        }
        
        payload = {
            "Cisco-IOS-XE-native:GigabitEthernet": {
                "name": interfaz,
                "ip": {
                    "address": {
                        "primary": {
                            "address": ip,
                            "mask": mascara_validada
                        }
                    }
                }
            }
        }
        
    else:  # IPv6
        while True:
            ipv6 = input("Dirección IPv6: ").strip()
            if not validar_ipv6(ipv6):
                print("❌ Dirección IPv6 inválida")
                continue
                
            prefijo = input("Longitud de prefijo (ej: 64): ").strip()
            if not prefijo.isdigit() or int(prefijo) < 1 or int(prefijo) > 128:
                print("❌ Prefijo IPv6 inválido (debe ser 1-128)")
                continue
                
            # Verificar si la IPv6 ya está asignada
            ips_asignadas = obtener_ips_asignadas()
            if ipv6 in ips_asignadas['ipv6']:
                print(f"❌ La IPv6 {ipv6} ya está asignada a otra interfaz")
                return
                
            break
            
        url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet={interfaz}"
        headers = {
            "Content-Type": "application/yang-data+json",
            "Accept": "application/yang-data+json"
        }
        
        payload = {
            "Cisco-IOS-XE-native:GigabitEthernet": {
                "name": interfaz,
                "ipv6": {
                    "address": {
                        "prefix-list": [
                            {
                                "prefix": f"{ipv6}/{prefijo}",
                                "eui-64": False
                            }
                        ]
                    }
                }
            }
        }
    
    try:
        response = requests.patch(
            url,
            headers=headers,
            auth=HTTPBasicAuth(USUARIO_ROUTER, CONTRASENA_ROUTER),
            json=payload,
            verify=False,
            timeout=15
        )
        
        if response.status_code in [200, 204]:
            if tipo_ip == "1":
                print(f"✅ IP {ip}/{mascara_validada} configurada en GigabitEthernet{interfaz}")
                registrar_evento(usuario_actual, "IP_CONFIGURADA", f"GigabitEthernet{interfaz} - {ip}/{mascara_validada}")
            else:
                print(f"✅ IPv6 {ipv6}/{prefijo} configurada en GigabitEthernet{interfaz}")
                registrar_evento(usuario_actual, "IPV6_CONFIGURADA", f"GigabitEthernet{interfaz} - {ipv6}/{prefijo}")
            
            # Activar la interfaz por defecto
            activar_interfaz(interfaz, usuario_actual, activar=True)
        else:
            print(f"❌ Error al configurar IP ({response.status_code}): {response.text}")
            registrar_evento(usuario_actual, "ERROR_CONFIGURACION", f"{response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión RESTCONF: {e}")
        registrar_evento(usuario_actual, "ERROR_CONEXION", str(e))

def configurar_descripcion_interfaz(interfaz, usuario_actual):
    """Configura la descripción de una interfaz"""
    if interfaz == "1":
        print("❌ No se puede configurar GigabitEthernet1")
        return
    
    descripcion = input("Descripción de la interfaz: ").strip()
    url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet={interfaz}"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }
    payload = {
        "Cisco-IOS-XE-native:GigabitEthernet": {
            "name": interfaz,
            "description": descripcion
        }
    }
    
    try:
        response = requests.patch(
            url,
            headers=headers,
            auth=HTTPBasicAuth(USUARIO_ROUTER, CONTRASENA_ROUTER),
            json=payload,
            verify=False,
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            print(f"✅ Descripción '{descripcion}' configurada en GigabitEthernet{interfaz}")
            registrar_evento(usuario_actual, "DESCRIPCION_CONFIGURADA", f"GigabitEthernet{interfaz} - {descripcion}")
        else:
            print(f"❌ Error al configurar descripción ({response.status_code}): {response.text}")
            registrar_evento(usuario_actual, "ERROR_DESCRIPCION", f"{response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión RESTCONF: {e}")
        registrar_evento(usuario_actual, "ERROR_CONEXION", str(e))

def configurar_hostname(nuevo_hostname, usuario_actual):
    """Configura el hostname del router"""
    url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native/hostname"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }
    payload = {"Cisco-IOS-XE-native:hostname": nuevo_hostname}
    
    try:
        response = requests.put(
            url,
            headers=headers,
            auth=HTTPBasicAuth(USUARIO_ROUTER, CONTRASENA_ROUTER),
            json=payload,
            verify=False,
            timeout=10
        )
        if response.status_code in [200, 204]:
            print(f"✅ Hostname cambiado a '{nuevo_hostname}' exitosamente.")
            registrar_evento(usuario_actual, "CAMBIO_HOSTNAME", nuevo_hostname)
        else:
            print(f"❌ Error ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en RESTCONF: {e}")

def configurar_banner(banner, usuario_actual):
    """Configura el banner del router"""
    url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native/banner/motd/banner"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }
    payload = {"Cisco-IOS-XE-native:banner": banner}
    
    try:
        response = requests.put(
            url,
            headers=headers,
            auth=HTTPBasicAuth(USUARIO_ROUTER, CONTRASENA_ROUTER),
            json=payload,
            verify=False,
            timeout=10
        )
        if response.status_code in [200, 204]:
            print("✅ Banner configurado exitosamente.")
            registrar_evento(usuario_actual, "CAMBIO_BANNER", banner)
        else:
            print(f"❌ Error ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en RESTCONF: {e}")

# ==============================================
# Funciones de Visualizacin
# ==============================================

def listar_interfaces(usuario_actual):
    """Lista todas las interfaces del router"""
    url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native/interface"
    headers = {"Accept": "application/yang-data+json"}
    
    try:
        response = requests.get(
            url,
            headers=headers,
            auth=HTTPBasicAuth(USUARIO_ROUTER, CONTRASENA_ROUTER),
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n📋 Interfaces Disponibles:")
            
            # GigabitEthernet
            gigas = data.get("Cisco-IOS-XE-native:interface", {}).get("GigabitEthernet", [])
            if isinstance(gigas, dict):
                gigas = [gigas]
                
            print("\n🔹 GigabitEthernet:")
            for giga in gigas:
                name = giga.get("name", "Desconocido")
                desc = giga.get("description", "Sin descripcion")
                ip_info = giga.get("ip", {}).get("address", {}).get("primary", {})
                ip = ip_info.get("address", "No configurada")
                mask = ip_info.get("mask", "")
                estado = "🟢 ACTIVA" if not giga.get("shutdown") else "🔴 INACTIVA"
                
                print(f"  {name}: {desc}")
                print(f"    IP: {ip}/{mask} - Estado: {estado}")
                
                # IPv6
                ipv6_prefixes = giga.get("ipv6", {}).get("address", {}).get("prefix-list", [])
                if isinstance(ipv6_prefixes, dict):
                    ipv6_prefixes = [ipv6_prefixes]
                for prefix in ipv6_prefixes:
                    ipv6 = prefix.get("prefix", "")
                    if ipv6:
                        print(f"    IPv6: {ipv6}")
            
            registrar_evento(usuario_actual, "LISTADO_INTERFACES")
        else:
            print(f"❌ Error al obtener interfaces ({response.status_code}): {response.text}")
            registrar_evento(usuario_actual, "ERROR_LISTADO", f"{response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión RESTCONF: {e}")
        registrar_evento(usuario_actual, "ERROR_CONEXION", str(e))

def mostrar_configuracion_completa(usuario_actual):
    """Muestra la configuración completa del router"""
    url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native"
    headers = {"Accept": "application/yang-data+json"}
    
    try:
        print("\n⏳ Obteniendo configuración completa...")
        response = requests.get(
            url,
            headers=headers,
            auth=HTTPBasicAuth(USUARIO_ROUTER, CONTRASENA_ROUTER),
            verify=False,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n🔧 Configuración Completa del Router:")
            print(json.dumps(data, indent=4))
            registrar_evento(usuario_actual, "CONFIGURACION_COMPLETA")
            
            guardar = input("\n¿Desea guardar esta configuración en un archivo? (s/n): ").lower()
            if guardar == 's':
                guardar_configuracion_en_json(data, prefijo="configuracion_completa")
        else:
            print(f"❌ Error al obtener configuración ({response.status_code}): {response.text}")
            registrar_evento(usuario_actual, "ERROR_CONFIGURACION", f"{response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión RESTCONF: {e}")
        registrar_evento(usuario_actual, "ERROR_CONEXION", str(e))

def mostrar_resumen_interfaces(usuario_actual):
    """Muestra un resumen del estado de las interfaces"""
    url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native/interface"
    headers = {"Accept": "application/yang-data+json"}
    
    try:
        response = requests.get(
            url,
            headers=headers,
            auth=HTTPBasicAuth(USUARIO_ROUTER, CONTRASENA_ROUTER),
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n📡 Resumen de Interfaces:")
            
            gigas = data.get("Cisco-IOS-XE-native:interface", {}).get("GigabitEthernet", [])
            if isinstance(gigas, dict):
                gigas = [gigas]
                
            print("\n🔹 GigabitEthernet:")
            for giga in gigas:
                name = giga.get("name", "Desconocido")
                estado = "🟢 ACTIVA" if not giga.get("shutdown") else "🔴 INACTIVA"
                print(f"  {name}: {estado}")
            
            registrar_evento(usuario_actual, "RESUMEN_INTERFACES")
        else:
            print(f"❌ Error al obtener interfaces ({response.status_code}): {response.text}")
            registrar_evento(usuario_actual, "ERROR_RESUMEN", f"{response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión RESTCONF: {e}")
        registrar_evento(usuario_actual, "ERROR_CONEXION", str(e))

def mostrar_configuracion_actual(usuario_actual):
    """Muestra la configuración actual del router"""
    url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native"
    headers = {"Accept": "application/yang-data+json"}
    
    try:
        response = requests.get(
            url,
            headers=headers,
            auth=HTTPBasicAuth(USUARIO_ROUTER, CONTRASENA_ROUTER),
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n🔧 Configuración Actual:")
            
            # Hostname
            hostname = data.get("Cisco-IOS-XE-native:native", {}).get("hostname", "Desconocido")
            print(f"\n🖥️ Hostname: {hostname}")
            
            # Banner
            banner = data.get("Cisco-IOS-XE-native:native", {}).get("banner", {}).get("motd", {}).get("banner", "No configurado")
            print(f"\n📜 Banner: {banner}")
            
            # Interfaces
            interfaces = data.get("Cisco-IOS-XE-native:native", {}).get("interface", {})
            print("\n📡 Interfaces:")
            for int_type in ["GigabitEthernet", "Loopback"]:
                if int_type in interfaces:
                    for interface in (interfaces[int_type] if isinstance(interfaces[int_type], list) else [interfaces[int_type]]):
                        name = interface.get("name", "Desconocido")
                        desc = interface.get("description", "Sin descripción")
                        estado = "🟢 ACTIVA" if not interface.get("shutdown") else "🔴 INACTIVA"
                        print(f"\n  {int_type}{name}: {desc} - {estado}")
                        
                        # IPv4
                        ip_info = interface.get("ip", {}).get("address", {}).get("primary", {})
                        ip = ip_info.get("address", "No configurada")
                        mask = ip_info.get("mask", "")
                        if ip != "No configurada":
                            print(f"    IPv4: {ip}/{mask}")
                        
                        # IPv6
                        ipv6_prefixes = interface.get("ipv6", {}).get("address", {}).get("prefix-list", [])
                        if isinstance(ipv6_prefixes, dict):
                            ipv6_prefixes = [ipv6_prefixes]
                        for prefix in ipv6_prefixes:
                            ipv6 = prefix.get("prefix", "")
                            if ipv6:
                                print(f"    IPv6: {ipv6}")
            
            registrar_evento(usuario_actual, "CONFIGURACION_ACTUAL")
        else:
            print(f"❌ Error al obtener configuración ({response.status_code}): {response.text}")
            registrar_evento(usuario_actual, "ERROR_CONFIGURACION", f"{response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión RESTCONF: {e}")
        registrar_evento(usuario_actual, "ERROR_CONEXION", str(e))

# ==============================================
# Funcion de Administracion
# ==============================================

def guardar_configuracion(usuario_actual):
    """Guarda la configuración actual en un archivo JSON"""
    url = f"https://{IP_ROUTER}/restconf/data/Cisco-IOS-XE-native:native"
    headers = {"Accept": "application/yang-data+json"}
    
    try:
        response = requests.get(
            url,
            headers=headers,
            auth=HTTPBasicAuth(USUARIO_ROUTER, CONTRASENA_ROUTER),
            verify=False,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            guardar_configuracion_en_json(data, prefijo="configuracion_guardada")
            registrar_evento(usuario_actual, "CONFIGURACION_GUARDADA")
        else:
            print(f"❌ Error al obtener configuración ({response.status_code}): {response.text}")
            registrar_evento(usuario_actual, "ERROR_GUARDAR", f"{response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión RESTCONF: {e}")
        registrar_evento(usuario_actual, "ERROR_CONEXION", str(e))

def mostrar_registros(usuario_actual):
    """Muestra los registros del sistema"""
    try:
        with open(ARCHIVO_REGISTRO, mode='r', encoding='utf-8') as archivo:
            lector = csv.reader(archivo)
            print("\n📜 Registros del Sistema:")
            print("-" * 80)
            for idx, fila in enumerate(lector):
                if idx == 0:  # Encabezados
                    print(f"{fila[0]:<12} {fila[1]:<10} {fila[2]:<10} {fila[3]:<20} {fila[4]}")
                    print("-" * 80)
                else:
                    print(f"{fila[0]:<12} {fila[1]:<10} {fila[2]:<10} {fila[3]:<20} {fila[4]}")
            archivo.close()
        registrar_evento(usuario_actual, "REGISTROS_CONSULTADOS")
    except FileNotFoundError:
        print("❌ No hay registros disponibles")
    except Exception as e:
        print(f"❌ Error al leer registros: {e}")

# ==============================================
# Menus del Sistema
# ==============================================

def menu_configurar_interfaz(interfaz, usuario):
    """Menú para configurar una interfaz específica"""
    while True:
        print(f"""
--- Configuración de GigabitEthernet{interfaz} ---
[1] Configurar Dirección IP (IPv4/IPv6)
[2] Configurar Descripción
[3] Volver al menú anterior
""")
        opcion = input("Seleccione una opcion: ").strip()
        
        if opcion == "1":
            configurar_ip_interfaz(interfaz, usuario)
        elif opcion == "2":
            configurar_descripcion_interfaz(interfaz, usuario)
        elif opcion == "3":
            break
        else:
            os.system('cls' if os.name == 'nt' else 'clear')

            print("❌ Opcion invalida")


# ==============================================

# submenu configuracion global

def menu_configuracion_global(usuario):
    """Menú de configuración global"""
    while True:
        print("""
--- Configuración Global ---
[1] Cambiar Hostname
[2] Configurar Banner
[3] Volver al menú principal
""")
        opcion = input("Seleccione una opcion: ").strip()
        
        if opcion == "1":
            nuevo_hostname = input("Nuevo hostname: ").strip()
            configurar_hostname(nuevo_hostname, usuario)
        elif opcion == "2":
            banner = input("Texto del banner: ").strip()
            configurar_banner(banner, usuario)
        elif opcion == "3":
            break
        else:
            print("❌ Opcion invalida")

# ==============================================
# submenu configuracion de las int

def menu_configuracion_interfaces(usuario):
    """Menú de configuración de interfaces"""
    while True:
        print("""
--- Configuración de Interfaces ---
[1] Listar Interfaces Disponibles
[2] Configurar Interface
[3] Activar/Desactivar Interface
[4] Volver al menú principal
""")
        opcion = input("Seleccione una opcion: ").strip()
        
        if opcion == "1":
            listar_interfaces(usuario)
        elif opcion == "2":
            while True:
                interfaz = input("Número de interfaz a configurar (ej: 2): ").strip()
                if not interfaz.isdigit():
                    print("❌ Debe ingresar un número de interfaz válido")
                    continue
                break
            menu_configurar_interfaz(interfaz, usuario)
        elif opcion == "3":
            while True:
                interfaz = input("Número de interfaz a activar/desactivar (ej: 2): ").strip()
                if not interfaz.isdigit():
                    print("❌ Debe ingresar un número de interfaz válido")
                    continue
                break
                
            while True:
                accion = input("¿Activar (1) o Desactivar (2)? ").strip()
                if accion == "1":
                    activar_interfaz(interfaz, usuario, activar=True)
                    break
                elif accion == "2":
                    activar_interfaz(interfaz, usuario, activar=False)
                    break
                else:
                    print("❌ Opcion invalida. Ingrese 1 para Activar o 2 para Desactivar")
        elif opcion == "4":
            break
        else:
            os.system('cls' if os.name == 'nt' else 'clear')

            print("❌ Opcion invalida")
# ==============================================
#submenu mostrar config

def menu_mostrar_configuracion(usuario):
    while True:
        print("""
--- Mostrar Configuracion ---
[1] Mostrar Configuracion Completa
[2] Mostrar Resumen de Interfaces
[3] Mostrar Configuracion Actual
[4] Volver al menu principal
""")
        opcion = input("Seleccione una opcion: ").strip()
        
        if opcion == "1":
            mostrar_configuracion_completa(usuario)
        elif opcion == "2":
            mostrar_resumen_interfaces(usuario)
        elif opcion == "3":
            mostrar_configuracion_actual(usuario)
        elif opcion == "4":
            break
        else:
            os.system('cls' if os.name == 'nt' else 'clear')

            print("❌ Opcion invalida")


#submenu de administracion
# sirve para que el usuario guarde la configuracion actual y para mostrar los registros del sistema
def menu_administracion(usuario):
    
    while True:
        print("""
--- Administración ---
[1] Guardar Configuracion
[2] Mostrar Registros del Sistema
[3] Volver al menú principal
""")
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            guardar_configuracion(usuario)
        elif opcion == "2":
            mostrar_registros(usuario)
        elif opcion == "3":
            break
        else:
            print("❌ Opcion invalida")
# ==============================================

#  Autenticacion        clave y contra : admin

def sesion():
    print("\nInicio de sesión - Solo usuarios autorizados")
    while True:
        usuario = input("Nombre de usuario: ").strip()
        if usuario == "admin":
            contrasena = input("Contraseña: ").strip()
            if contrasena == "admin":
                print("✅ Bienvenido Administrador   ;) ")
                registrar_evento(usuario, "INICIO_SESION_EXITOSO")
                return usuario
            else:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(ascii_art)

                print("ƪ(˘⌣˘)ʃ Contraseña incorrecta , intente de nuevo")
                print(" ")
                registrar_evento(usuario, "INTENTO_FALLIDO", "Contraseña incorrecta")
                print(" ")
        else:
            print(" ")
            os.system('cls' if os.name == 'nt' else 'clear')
            print(ascii_art)
            print("❌ Acceso denegado. Solo se permite acceso al ''ADMINISTRADOR'' ")
            print(" ")
            registrar_evento("DESCONOCIDO", "INTENTO_USUARIO", f"Intento de acceso con usuario: {usuario}")

# ==============================================
#menu pincipla

def menu_principal():

    iniciar_registro()
    usuario_actual = sesion()

    while True:
        print("""
+-----------------------------+
| 🚀 MENÚ PRINCIPAL            |
| [1] Configuración Global     |
| [2] Configuración de         |
|     Interfaces               |
| [3] Mostrar Configuración    |
| [4] Administración           |
| [5] Salir                    |
+-----------------------------+
""")
        opcion = input("Seleccione una opcion: ").strip()
        
        if opcion == "1":
            menu_configuracion_global(usuario_actual)
        elif opcion == "2":
            menu_configuracion_interfaces(usuario_actual)
        elif opcion == "3":
            menu_mostrar_configuracion(usuario_actual)
        elif opcion == "4":
            menu_administracion(usuario_actual)
        elif opcion == "5":
            registrar_evento(usuario_actual, "SESION_CERRADA")
            print("👋 Sesión finalizada. Hasta pronto.")
            break
        else:
            os.system('cls' if os.name == 'nt' else 'clear')

            print("❌ Opcion invalida")

# ==============================================
# Inicio del Programa
# ==============================================

if __name__ == "__main__":
    menu_principal()
