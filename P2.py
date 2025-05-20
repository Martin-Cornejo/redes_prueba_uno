#comentario prueba edtar
   #DAVOR BUTTON
import os
import re
import ipaddress
import csv
from datetime import datetime

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

# aqui se inicia el registro
iniciar_registro()
# ================================================================

# ASCII art para una presentacion mas fixita
print("""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~  ____  _____ ____   _____ ____           __ ___      ___ ___     ~
~ |  _ \ | ____|  _ \| ____/  __|         /  \   \    /  //_  |    ~
~ | |_) || |_  | | | | |_  | |__  _____  / /\ \   \  /  /   | |    ~             
~ |  _ < |  _| | | | |  _| \___ \ \___/ / /__\ \   \/  /    | |    ~
~ | | | || |___| |_| | |___ ___) |     /  ___   \     /    _| |_   ~
~ |_| \_|\_____|____/|_____|____/     /__/   \___\___/    |_____|  ~
~                      - Redes Avanzadas 1 -                       ~
~                                                                  ~
~                    - Eloy , Martin , Davor -                     ~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
    print('''
+-------------------------+
| 📋 MENÚ PRINCIPAL       |
| 1. Ver dispositivos     |
| 2. Ver campus           |
| 3. Añadir dispositivo   |
| 4. Añadir campus        |
| 5. Salir                |
| 6. Eliminar dispositivo |
+-------------------------+
          ''')

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

    vlans = input("VLAN(s): ").strip()
    servicios = input("Servicios: ").strip()
    capa = input("Capa: ").strip()

    # Registrar en archivo
    with open(f"{campus[opcion]}.txt", "a") as archivo:
        archivo.write("\n" + "-"*30 + "\n")
        archivo.write(f"Dispositivo: {dispositivo}\n")
        archivo.write(f"Nombre: {nombre}\n")
        archivo.write(f"IP: {direccion_ip}\n")
        archivo.write(f"VLAN(s): {vlans}\n")
        archivo.write(f"Servicios: {servicios}\n")
        archivo.write(f"Capa: {capa}\n")
        archivo.write("-"*30 + "\n")

    # registrando eventos
    registrar_evento(
        usuario_actual,
        "DISPOSITIVO_AGREGADO",
        f"Campus: {campus[opcion]}, Tipo: {dispositivo}, IP: {direccion_ip}"
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
       
 # Eliminar dispositivo
def eliminar_dispositivo(campus, usuario_actual):
    ver_campus(campus, usuario_actual)
    try:
        opcion = int(input("\nSeleccione un campus: ")) - 1
        if not 0 <= opcion < len(campus):
            print("❌ Campus inválido")
            return
    except ValueError:
        print("❌ Ingrese un número válido")
        return

    archivo_nombre = f"{campus[opcion]}.txt"
    if not os.path.exists(archivo_nombre):
        print("⚠️ No hay dispositivos en este campus.")
        return

    with open(archivo_nombre, "r") as archivo:
        contenido = archivo.read()

    bloques = contenido.strip().split("-" * 30)
    dispositivos = [b.strip() for b in bloques if b.strip()]

    if not dispositivos:
        print("⚠️ No hay dispositivos registrados.")
        return

    print("\n--- Dispositivos ---")
    for i, d in enumerate(dispositivos):
        nombre = re.search(r"Nombre:\s*(.*)", d)
        print(f"{i+1}. {nombre.group(1) if nombre else 'Sin nombre'}")

    try:
        eliminar_idx = int(input("Seleccione número del dispositivo a eliminar: ")) - 1
        if not 0 <= eliminar_idx < len(dispositivos):
            print("❌ Opción inválida.")
            return
    except ValueError:
        print("❌ Ingrese un número válido.")
        return

    eliminado = dispositivos.pop(eliminar_idx)
    nuevo_contenido = ("\n" + "-" * 30 + "\n").join(dispositivos)

    with open(archivo_nombre, "w") as archivo:
        archivo.write(nuevo_contenido.strip() + "\n" if dispositivos else "")

    registrar_evento(usuario_actual, "DISPOSITIVO_ELIMINADO", f"Campus: {campus[opcion]}, Detalles: {eliminado.splitlines()[0]}")
    print("🗑️ Dispositivo eliminado correctamente.")

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
        elif opcion == "6":
            eliminar_dispositivo(campus, usuario_actual)

            break
        else:
            print("❌ Opción inválida.")
        
        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()

    #profe sadro rajese con un 7 porfa UWU

