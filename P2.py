
import re
import ipaddress
from datetime import datetime

ARCHIVO = "dispositivos_guardados.txt"

def validar_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def ingresar_dispositivo():
    print("\n🆕 Ingrese los datos del nuevo dispositivo:")

    nombre = input("Nombre del dispositivo: ").strip()
    while not nombre:
        nombre = input("⚠️ Nombre vacío. Intente de nuevo: ").strip()

    tipo = input("Tipo (Switch, Router, Access Point): ").strip()
    while tipo.lower() not in ["switch", "router", "access point"]:
        tipo = input("⚠️ Tipo no válido. Ingrese Switch, Router o Access Point: ").strip()

    ip = input("Dirección IP: ").strip()
    while not validar_ip(ip):
        ip = input("⚠️ IP inválida. Ejemplo válido: 192.168.1.1 ➤ ").strip()

    ubicacion = input("Ubicación física: ").strip()
    while not ubicacion:
        ubicacion = input("⚠️ Ubicación vacía. Intente de nuevo: ").strip()

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    dispositivo = {
        "Nombre": nombre,
        "Tipo": tipo,
        "IP": ip,
        "Ubicación": ubicacion,
        "Fecha": fecha
    }

    guardar_dispositivo(dispositivo)
    print("✅ Dispositivo guardado correctamente.")

def guardar_dispositivo(dispositivo):
    with open(ARCHIVO, "a") as archivo:
        archivo.write(f"Nombre: {dispositivo['Nombre']}\n")
        archivo.write(f"Tipo: {dispositivo['Tipo']}\n")
        archivo.write(f"IP: {dispositivo['IP']}\n")
        archivo.write(f"Ubicación: {dispositivo['Ubicación']}\n")
        archivo.write(f"Fecha de Registro: {dispositivo['Fecha']}\n")
        archivo.write("-" * 40 + "\n")

def buscar_dispositivo():
    if not verificar_existencia_archivo():
        return
    criterio = input("🔍 Buscar por Nombre o IP: ").strip().lower()
    encontrado = False
    with open(ARCHIVO, "r") as archivo:
        bloque = ""
        for linea in archivo:
            bloque += linea
            if linea.strip() == "-" * 40:
                if criterio in bloque.lower():
                    print("\n📄 Resultado encontrado:\n" + bloque)
                    encontrado = True
                bloque = ""
    if not encontrado:
        print("❌ No se encontró ningún dispositivo con ese criterio.")

def limpiar_registros():
    confirmacion = input("⚠️ ¿Seguro que quieres borrar todos los registros? (s/n): ").lower()
    if confirmacion == "s":
        open(ARCHIVO, "w").close()
        print("🧹 Todos los registros han sido eliminados.")
    else:
        print("❌ Operación cancelada.")

def mostrar_menu():
    while True:
        print("\n📋 MENÚ PRINCIPAL")
        print("1. Ingresar nuevo dispositivo")
        print("2. Buscar dispositivo")
        print("3. Limpiar todos los registros")
        print("4. Salir")

        opcion = input("Seleccione una opción (1-4): ").strip()
        if opcion == "1":
            ingresar_dispositivo()
        elif opcion == "2":
            buscar_dispositivo()
        elif opcion == "3":
            limpiar_registros()
        elif opcion == "4":
            print("👋 Saliendo del programa. ¡Hasta pronto!")
            break
        else:
            print("⚠️ Opción inválida. Intente de nuevo.")

def verificar_existencia_archivo():
    try:
        with open(ARCHIVO, "r") as f:
            contenido = f.read()
            if not contenido.strip():
                print("⚠️ No hay registros guardados.")
                return False
            return True
    except FileNotFoundError:
        print("⚠️ No existe el archivo de registros.")
        return False

if __name__ == "__main__":
    mostrar_menu()
1