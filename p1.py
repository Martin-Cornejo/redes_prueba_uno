import os
import re

def validar_ip(ip):
    patron = re.compile(r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
                        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
                        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
                        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    return patron.match(ip)

def mostrar_menu():
    print("\n¿Qué desea hacer?")
    print("1. Ver dispositivos")
    print("2. Ver campus")
    print("3. Añadir dispositivo")
    print("4. Añadir campus")
    print("5. Salir")

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
            print("No hay dispositivos registrados aún.")

def ver_campus(campus):
    print("\n--- Lista de Campus ---")
    for i, c in enumerate(campus):
        print(f"{i+1}. {c}")

def añadir_dispositivo(campus):
    for i, c in enumerate(campus):
        print(f"{i+1}. {c}")
    opcion = int(input("\nSeleccione un campus para agregar un dispositivo: ")) - 1
    if 0 <= opcion < len(campus):
        dispositivo = input("Ingrese tipo de dispositivo (Router/Switch/Switch Multicapa): ")
        nombre = input("Nombre del dispositivo: ")

        while True:
            direccion_ip = input("Dirección IP (formato xxx.xxx.xxx.xxx): ")
            if validar_ip(direccion_ip):
                break
            else:
                print("❌ IP no válida. Intente nuevamente.")

        vlans = input("VLAN(s) (separadas por coma): ")
        servicios = input("Servicios (Datos, VLAN, Trunking, Enrutamiento): ")
        capa = input("Capa (Núcleo, Distribución, Acceso): ")

        with open(f"{campus[opcion]}.txt", "a") as archivo:
            archivo.write("\n-----------------------------\n")
            archivo.write(f"Dispositivo: {dispositivo}\n")
            archivo.write(f"Nombre: {nombre}\n")
            archivo.write(f"IP: {direccion_ip}\n")
            archivo.write(f"VLAN(s): {vlans}\n")
            archivo.write(f"Servicios: {servicios}\n")
            archivo.write(f"Capa: {capa}\n")
            archivo.write("-----------------------------\n")

        print("✅ Dispositivo agregado correctamente.")

def añadir_campus(campus):
    nuevo = input("Nombre del nuevo campus: ")
    if nuevo not in campus:
        campus.append(nuevo)
        print(f"Campus '{nuevo}' agregado.")
    else:
        print("El campus ya existe.")

def main():
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
            print("👋 Saliendo del programa.")
            break
        else:
            print("❌ Opción inválida.")

if __name__ == "__main__":
    main()