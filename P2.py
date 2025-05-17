#comentario prueba edtar
   #DAVOR BUTTON
import os
import re
import ipaddress
import csv
from datetime import datetime


#MI MODIFICACION ---------------------------------------------------------------------------------+

# registro de uso / historial ＞﹏＜
ARCHIVO_REGISTRO = "registros_red.csv"

def iniciar_registro():
    #se Crea el archivo de registro si es que no llega a existie
    if not os.path.exists(ARCHIVO_REGISTRO):
        with open(ARCHIVO_REGISTRO, mode='w', newline='', encoding='utf-8') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["Fecha", "Hora", "Usuario", "Acción", "Detalles"])

def registrar_evento(usuario, accion, detalles=""):
    """Guarda un evento en el registro"""
    try:
        with open(ARCHIVO_REGISTRO, mode='a', newline='', encoding='utf-8') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow([
                datetime.now().strftime("%d-%m-%Y"),#formatode la fecha
                datetime.now().strftime("%H:%M:%S"),#formato de la hora
                usuario,
                accion,
                str(detalles)
            ])
    except Exception as e:
        print(f"⚠️ Error en registro: {e}")
#ELOY MODIFICACION ---------------------------------------------------------------------------------+

# aqui se inicia el registro
iniciar_registro()
# ================================================================

# ASCII art para una presentacion mas fixita
print("""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~ ____  _____ ____  _____ ____          ___     __ __ ~
~|  _ \| ____|  _ \| ____/ ___|        / \ \   / //_ |~
~| |_) |  _| | | | |  _| \___ \ _____ / _ \ \ / /  | |~
~|  _ <| |___| |_| | |___ ___) |_____/ ___ \ V /   | |~
~|_| \_\_____|____/|_____|____/     /_/   \_\_/    |_|~
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
    MAX_INTENTOS = 3
if intentos >= MAX_INTENTOS:
    print("🔒 Demasiados intentos. Cuenta bloqueada temporalmente.")
    registrar_evento(usuario, "BLOQUEO_POR_INTENTOS")
    time.sleep(60)  # Bloqueo temporal
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

#validacion de la mascara 
def validar_mascara(mascara):
    patron = re.compile(r"^(255|254|252|248|240|224|192|128|0)\."
                        r"(255|254|252|248|240|224|192|128|0)\."
                        r"(255|254|252|248|240|224|192|128|0)\."
                        r"(255|254|252|248|240|224|192|128|0)$")
    return patron.match(mascara)

#ELOY MODIFICACION ---------------------------------------------------------------------------------+

# yo kcho que esta wa hay que borrarla , puro cacho
# Comprobar si IP está en rango privado válido , los deje como comentario para no borrar pero que no se ejecuten

def ip_en_rango(ip):
    try:
        ip_obj = ipaddress.IPv4Address(ip)
        # Solo permite IPs desde 1.0.0.0 hasta 223.255.255.255 (clase A, B, C)
        return ip_obj >= ipaddress.IPv4Address("1.0.0.0") and ip_obj <= ipaddress.IPv4Address("223.255.255.255")
    except ValueError:
        return False
#---------------------------------------------------------------------------------+

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

    while True:
        direccion_ip = input("Dirección IP: ").strip()
        if validar_ip(direccion_ip) and ip_en_rango(direccion_ip):
            break
        print("❌ IP inválida o fuera de rango permitido.")

    mascara = input("mascara: ").strip()
    vlans = input("VLAN(s): ").strip()
    servicios = input("Servicios: ").strip()
    capa = input("Capa: ").strip()
#ELOY MODIFICACION ---------------------------------------------------------------------------------+
    # Registrar en archivo
    with open(f"{campus[opcion]}.txt", "a") as archivo:
        archivo.write("\n" + "-"*30 + "\n")
        archivo.write(f"Dispositivo: {dispositivo}\n")
        archivo.write(f"Nombre: {nombre}\n")
        archivo.write(f"IP: {direccion_ip}\n")
        #------------
        archivo.write(f"mascara: {mascara}\n")
        #------------
        archivo.write(f"VLAN(s): {vlans}\n")
        archivo.write(f"Servicios: {servicios}\n")
        archivo.write(f"Capa: {capa}\n")
        archivo.write("-"*30 + "\n")

#ELOY MODIFICACION ---------------------------------------------------------------------------------+

    # registrando eventos
    registrar_evento(
        usuario_actual,
        "DISPOSITIVO_AGREGADO",
        f"Campus: {campus[opcion]}, Tipo: {dispositivo}, IP: {direccion_ip}, Mascara: {mascara}"
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


