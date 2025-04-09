import requests
from bs4 import BeautifulSoup
import argparse
import unicodedata
from functions import fixear_nombre
import os
from dotenv import load_dotenv

load_dotenv()

# Configurar argparse para leer la URL desde la línea de comandos
parser = argparse.ArgumentParser(description="Extraer nombres de estudiantes desde una tabla web")
parser.add_argument("url", help="URL de la página con la tabla")
args = parser.parse_args()

# Obtener la URL pasada como argumento
url = args.url

mis_estudiantes = os.getenv("ESTUDIANTES").split("|")
#LOS ESTUDIANTES EN .env DEBEN DEBEN VENIR SEPARADOS POR UN | PARA GENERAR UN ARRAY CORRECTAMENTE
#cookies
cookies = {
    
    "wordpress_sec_ce9867109f826f6031a2b7fcd3213f1b":  os.getenv("COOKIE_WORDPRESS_SEC"),
    "wordpress_logged_in_ce9867109f826f6031a2b7fcd3213f1b": os.getenv("COOKIE_WORDPRESS_LOGGED_IN")
}

# Hacer la solicitud HTTP
response = requests.get(url, cookies=cookies)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    filas = soup.select("table.tutor-table tbody tr")

    nombres = []

    for fila in filas:
        columnas = fila.find_all("td")
        if len(columnas) > 1:
            nombre_div = columnas[1].find_all("div")[-1]
            nombre = nombre_div.contents[0].strip()
            nombres.append(nombre)
    
    #fixear nombres
    entregados_fix = set(fixear_nombre(nombre) for nombre in nombres)
    print(entregados_fix)
    mis_estudiantes_fix = [(e, fixear_nombre(e)) for e in mis_estudiantes]
    print(mis_estudiantes_fix)
    pendientes = [original for original, norm in mis_estudiantes_fix if norm not in entregados_fix]


    # Guardar en archivo
    with open("estudiantes_no_entregaron.txt", "w", encoding="utf-8") as f:
        for nombre in pendientes:
            f.write(nombre + "\n")
            print(f"❌ No entregó: {nombre}")
        

    print("✅ Nombres guardados en 'nombres_estudiantes.txt'")
else:
    print(f"❌ Error al acceder a la URL: {response.status_code}")

print(f"\nResumen:")
print(f"📥 Entregaron: {len(entregados_fix)}")
print(f"📤 No entregaron: {len(pendientes)} de {len(mis_estudiantes)}")