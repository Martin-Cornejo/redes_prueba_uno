import os
import re
import ipaddress
import csv
from datetime import datetime
import platform

# ===================== [SISTEMA DE LOGS] =====================
LOG_FILE = os.path.join(os.path.dirname(__file__), "logs_red.csv")

def init_log():
    """Inicializa el archivo de logs con encabezados"""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Usuario", "Fecha", "Hora", "Acción", "Detalles", "SO"])

def log_accion(usuario, accion, detalles=""):
    """Registra una acción en el archivo de logs"""
    try:
        with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                usuario,
                datetime.now().strftime("%d-%m-%Y"),
                datetime.now().strftime("%H:%M:%S"),
                accion,
                str(detalles),
                platform.system()
            ])
    except Exception as e:
        print(f"⚠️ Error en logs: {e}")

# ============================================
# ASCII art
print("""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~ ____  _____ ____  _____ ____          ___     __ __ ~
|  _ \| ___|  _ \| ____/ ___|        / \ \   / // |
| |) |  _| | | | |  _| \__ \ _____ / _ \ \ / /  | |
|  _ <| || || | |___ __) |/ ___ \ V /   | |
|| \|/||/     //   \/    ||
~                                                     ~
~              Eloy , Martin , Davor                  ~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
""")

# Sesión predefinida
def sesion():
    usuarios = {
        "admin": "admin",
        "eloy": "eloy",
        "davor": "davor",
        "martin": "martin",
        "administrador": "administrador"
    }
    while True:
        print("\nInicio de sesión")
        usuario = input("Escriba nombre del usuario: ").strip()
        if usuario in usuarios:
            contrasena = input("Escriba la contraseña: ").strip()
            if contrasena == usuarios[usuario]:
                print("✅ Bienvenido " + usuario)
                break
            else:
                print("❌ Contraseña incorrecta")
        else:
            print(f"❌ Usuario incorrecto: {usuario}")

# Validación de IP
def validar_ip(ip):
    patron = re.compile(r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
                        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
                        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
                        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    return patron.match(ip)

# Comprobar si IP está en rango privado válido
def ip_en_rango(ip):
    rangos_validos = [
        ipaddress.ip_network('192.168.0.0/16'),
        ipaddress.ip_network('10.0.0.0/8'),
        ipaddress.ip_network('172.16.0.0/12')
    ]
    try:
        ip_obj = ipaddress.ip_address(ip)
        return any(ip_obj in rango for rango in rangos_validos)
    except ValueError:
        return False

# Mostrar menú
def mostrar_menu():
    print("\n📋 MENÚ PRINCIPAL")
    print("1. Ver dispositivos")
    print("2. Ver campus")
    print("3. Añadir dispositivo")
    print("4. Añadir campus")
    print("5. Salir")

# Ver dispositivos por campus
def ver_dispositivos(campus):
    os.system("cls" if os.name == "nt" else "clear")
    for i, c in enumerate(campus):
        print(f"{i+1}. {c}")
    opcion = int(input("\nSeleccione un campus: ")) - 1
    if 0 <= opcion < len(campus):
        try:
            with open(f"{campus[opcion]}.txt", "r") as archivo:
                print("\n--- Dispositivos Registrados ---")
                print(archivo.read())
        except FileNotFoundError:
            print("⚠️ No hay dispositivos registrados aún.")

# Ver lista de campus
def ver_campus(campus):
    print("\n--- Lista de Campus ---")
    for i, c in enumerate(campus):
        print(f"{i+1}. {c}")

# Añadir nuevo dispositivo
def añadir_dispositivo(campus):
    for i, c in enumerate(campus):
        print(f"{i+1}. {c}")
    opcion = int(input("\nSeleccione un campus: ")) - 1
    if 0 <= opcion < len(campus):
        dispositivo = input("Tipo de dispositivo: ")
        nombre = input("Nombre del dispositivo: ")

        while True:
            direccion_ip = input("Dirección IP: ")
            if validar_ip(direccion_ip) and ip_en_rango(direccion_ip):
                break
            else:
                print("❌ IP inválida o fuera de rango permitido.")

        vlans = input("VLAN(s): ")
        servicios = input("Servicios: ")
        capa = input("Capa: ")

        with open(f"{campus[opcion]}.txt", "a") as archivo:
            archivo.write("\n-----------------------------\n")
            archivo.write(f"Dispositivo: {dispositivo}\n")
            archivo.write(f"Nombre: {nombre}\n")
            archivo.write(f"IP: {direccion_ip}\n")
            archivo.write(f"VLAN(s): {vlans}\n")
            archivo.write(f"Servicios: {servicios}\n")
            archivo.write(f"Capa: {capa}\n")
            archivo.write("-----------------------------\n")
        print("✅ Dispositivo agregado.")

# Añadir nuevo campus
def añadir_campus(campus):
    nuevo = input("Nombre del nuevo campus: ")
    if nuevo not in campus:
        campus.append(nuevo)
        print(f"🏫 Campus '{nuevo}' agregado.")
    else:
        print("⚠️ El campus ya existe.")

# Programa principal
def main():
    sesion()
    campus = ["Zona Core", "Campus Uno", "Campus Matriz", "Sector Outsourcing"]
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")
        if opcion == "1":
            ver_dispositivos(campus)
        elif opcion == "2":
            ver_campus(campus)
        elif opcion == "3":
            añadir_dispositivo(campus)
        elif opcion == "4":
            añadir_campus(campus)
        elif opcion == "5":
            print("👋 Hasta luego.")
            break
        else:
            print("❌ Opción inválida.")

if __name__ == "__main__":
    main()

