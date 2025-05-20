#comentario prueba edtar
   #DAVOR BUTTON
import os
import re
import ipaddress
import csv
from datetime import datetime

# ASCII art para una presentacion mas fixita
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
        #orden es "usuario":"contra"
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
                registrar_evento(usuario, "INICIO_SESION_EXITOSO")
                return usuario
            else:
                print("❌ Contraseña incorrecta")
                registrar_evento(usuario, "INTENTO_FALLIDO", "Contraseña incorrecta")
        else:
            print(f"❌ Usuario incorrecto: {usuario}")
            registrar_evento("DESCONOCIDO", "INTENTO_USUARIO", f"Usuario no existe: {usuario}")

# Validación de IP
def validar_ip(ip):
    patron = re.compile(r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
                        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
                        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
                        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    return patron.match(ip)
# yo kcho que esta wa hay que borrarla , puro cacho
# Comprobar si IP está en rango privado válido
def ip_en_rango(ip):
    rangos_validos = [
        ipaddress.ip_network('0.0.0.0'),
        ipaddress.ip_network('0.0.0.0'),
        ipaddress.ip_network('0.0.0.0')
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
def ver_dispositivos(campus, usuario_actual):
    os.system("cls" if os.name == "nt" else "clear")
    for i, c in enumerate(campus):
        print(f"{i+1}. {c}")
    try:
        opcion = int(input("\nSeleccione un campus: ")) - 1
        if 0 <= opcion < len(campus):
            try:
                with open(f"{campus[opcion]}.txt", "r") as archivo:
                    print("\n--- Dispositivos Registrados ---")
                    print(archivo.read())
                    registrar_evento(usuario_actual, "VER_DISPOSITIVOS", f"Campus: {campus[opcion]}")
            except FileNotFoundError:
                print("⚠️ No hay dispositivos registrados aún.")
                registrar_evento(usuario_actual, "VER_DISPOSITIVOS", "Sin dispositivos")
        else:
            print("❌ Opción inválida")
    except ValueError:
        print("❌ Ingrese un número válido")

# lista de los campus 
def ver_campus(campus, usuario_actual):
    print("\n--- Lista de Campus ---")
    for i, c in enumerate(campus):
        print(f"{i+1}. {c}")
    registrar_evento(usuario_actual, "VER_CAMPUS")

# Añadir nuevo dispositivo
def añadir_dispositivo(campus, usuario_actual):
    ver_campus(campus, usuario_actual)
    try:
        opcion = int(input("\nSeleccione un campus: ")) - 1
        if not 0 <= opcion < len(campus):
            print("❌ Campus inválido")
            return
    except ValueError:
        print("❌ Ingrese un número válido")
        return

    dispositivo = input("Tipo de dispositivo: ").title()
    nombre = input("Nombre del dispositivo: ").strip()

    # Submenú para tipo de IP
    while True:
        print("\n¿Tipo de IP que desea agregar?")
        print("1. IPv4")
        print("2. IPv6")
        tipo_ip = input("Seleccione una opción (1/2): ").strip()

        if tipo_ip == "1":
            while True:
                direccion_ip = input("Dirección IPv4 (ej: 192.168.1.1): ").strip()
                mascara = input("Máscara (ej: 24): ").strip()
                try:
                    red = ipaddress.IPv4Network(f"{direccion_ip}/{mascara}", strict=False)
                    if ip_en_rango(direccion_ip):
                        direccion_completa = f"{direccion_ip}/{mascara}"
                        break
                    else:
                        print("❌ IP fuera de rango privado permitido.")
                except Exception as e:
                    print(f"❌ IP o máscara inválida. {e}")
            break

        elif tipo_ip == "2":
            while True:
                direccion_ip = input("Dirección IPv6 (ej: 2001:db8::1): ").strip()
                mascara = input("Máscara (ej: 64): ").strip()
                try:
                    red = ipaddress.IPv6Network(f"{direccion_ip}/{mascara}", strict=False)
                    direccion_completa = f"{direccion_ip}/{mascara}"
                    break
                except Exception as e:
                    print(f"❌ IP o máscara inválida. {e}")
            break
        else:
            print("❌ Opción inválida. Intente nuevamente.")

    vlans = input("VLAN(s): ").strip()
    servicios = input("Servicios: ").strip()
    capa = input("Capa: ").strip()

    # Registrar en archivo
    with open(f"{campus[opcion]}.txt", "a") as archivo:
        archivo.write("\n" + "-"*30 + "\n")
        archivo.write(f"Dispositivo: {dispositivo}\n")
        archivo.write(f"Nombre: {nombre}\n")
        archivo.write(f"IP: {direccion_completa}\n")
        archivo.write(f"VLAN(s): {vlans}\n")
        archivo.write(f"Servicios: {servicios}\n")
        archivo.write(f"Capa: {capa}\n")
        archivo.write("-"*30 + "\n")

    # registrando eventos
    registrar_evento(
        usuario_actual,
        "DISPOSITIVO_AGREGADO",
        f"Campus: {campus[opcion]}, Tipo: {dispositivo}, IP: {direccion_completa}"
    )
    print("✅ Dispositivo agregado.")
#aqui se añade campus
def añadir_campus(campus, usuario_actual):
    nuevo = input("Nombre del nuevo campus: ").strip()
    if nuevo and nuevo not in campus:
        campus.append(nuevo)
        registrar_evento(usuario_actual, "CAMPUS_AGREGADO", f"Nombre: {nuevo}")
        print(f"🏫 Campus '{nuevo}' agregado.")
    else:
        print("⚠️ El campus ya existe o nombre inválido")

# Programa principal
def main():
    usuario_actual = sesion()
    campus = ["Zona Core", "Campus Uno", "Campus Matriz", "Sector Outsourcing"]
    
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            ver_dispositivos(campus, usuario_actual)
        elif opcion == "2":
            ver_campus(campus, usuario_actual)
        elif opcion == "3":
            añadir_dispositivo(campus, usuario_actual)
        elif opcion == "4":
            añadir_campus(campus, usuario_actual)
        elif opcion == "5":
            registrar_evento(usuario_actual, "SESION_CERRADA")
            print("👋 Hasta luego.")
            break
        else:
            print("❌ Opción inválida.")
        
        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()

