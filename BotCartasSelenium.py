from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import json
import csv
from datetime import datetime
import os

# URLs de categorías
URLS = {
    "coreanas": "https://www.pokemillon.com/collections/pokemon-cartas-coreano",
    "mega-evolution": "https://www.pokemillon.com/collections/mega-evolution",
    "destined-rivals": "https://www.pokemillon.com/collections/destined-rivals",
    "juntos-aventuras": "https://www.pokemillon.com/collections/juntos-de-aventuras-journey-together",
    "surging-spark": "https://www.pokemillon.com/collections/surging-spark"
}

def obtener_cartas(url, categoria=""):
    print(f"🔍 Accediendo a: {url}")
    service = Service("D:/WebDrivers/chromedriver.exe")
  # Ajusta si tienes otro nombre/ruta
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    time.sleep(5)  # Esperar carga de JS

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    productos = soup.select(".grid-product__content")
    if not productos:
        print("⚠️ No se encontraron productos.")
        return {}

    cartas = {}
    for p in productos:
        try:
            nombre = p.select_one(".grid-product__title").get_text(strip=True)
            precio_raw = p.select_one(".grid-product__price").get_text(strip=True)
            precio = float(precio_raw.replace("€", "").replace(",", ".").strip())
            enlace = "https://www.pokemillon.com" + p.find_parent("a")["href"]
            stock = "sold out" not in p.get_text(strip=True).lower()
            cartas[nombre] = {
                "nombre": nombre,
                "categoria": categoria,
                "precio": precio,
                "url": enlace,
                "stock": stock,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"❌ Error procesando producto: {e}")
            continue
    return cartas

def exportar_a_json(cartas, filename="cartas_exportadas.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cartas, f, ensure_ascii=False, indent=4)

def exportar_a_csv(cartas, filename="cartas_exportadas.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["nombre", "categoria", "precio", "url", "stock", "fecha"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for carta in cartas.values():
            writer.writerow(carta)

# Recolectar datos
cartas_totales = {}
for categoria, url in URLS.items():
    cartas = obtener_cartas(url, categoria)
    if cartas:
        cartas_totales.update(cartas)

# Exportar con marca de tiempo
os.makedirs("exportaciones", exist_ok=True)
fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
json_path = f"exportaciones/cartas_{fecha_hora}.json"
csv_path = f"exportaciones/cartas_{fecha_hora}.csv"

exportar_a_json(cartas_totales, json_path)
exportar_a_csv(cartas_totales, csv_path)

print(f"\n✅ Exportación completada:\nJSON: {json_path}\nCSV:  {csv_path}")
