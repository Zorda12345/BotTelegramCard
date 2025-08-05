# Este codigo no funciona, lo usaremos como referencia 
import requests
from bs4 import BeautifulSoup
import json
import telebot
import time
import threading
import os
import csv
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================

# 🔐 Telegram
TOKEN_TELEGRAM = "8247777433:AAGLIlTGV6FwqrPEWhMuVimr3g2fI-jHIiQ"
MI_CHAT_ID = 1326048001
CANAL_CARTAS = -4905992224
CANAL_VIDEOJUEGOS = -4950809772 

bot = telebot.TeleBot(TOKEN_TELEGRAM)

#URLs que queremos scrapear (puedes seguir añadiendo más)
URLS = [
    "https://www.pokemillon.com/collections/pokemon-cartas-coreano",
    "https://www.pokemillon.com/collections/mega-evolution",
    "https://www.pokemillon.com/collections/destined-rivals",
    "https://www.pokemillon.com/collections/juntos-de-aventuras-journey-together",
    "https://www.pokemillon.com/collections/surging-spark"
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
}

# 📦 Archivo donde se guardan los datos antiguos
DATA_FILE = "cartas_pokemillon.json"

# ==============================
# FUNCIONES
# ==============================

def cargar_datos_anteriores():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_datos_nuevos(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def obtener_cartas(url):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "lxml")
    productos = soup.select(".productgrid--item")

    cartas = {}
    categoria = url.split("/")[-1]  # Ej: mega-evolution

    for p in productos:
        nombre_tag = p.select_one(".productitem--title")
        enlace_tag = p.select_one("a")
        precio_tag = p.select_one(".price")
        img_tag = p.select_one("img")

        # Validamos que existen todos los campos
        if not all([nombre_tag, enlace_tag, precio_tag, img_tag]):
            continue

        nombre = nombre_tag.text.strip()
        enlace = "https://www.pokemillon.com" + enlace_tag["href"]
        precio_texto = precio_tag.text.strip().replace("\n", "").replace("€", "").replace(",", ".")
        try:
            precio = float(precio_texto)
        except ValueError:
            continue  # precio inválido, lo ignoramos

        img = img_tag["src"]
        en_stock = "agotado" not in p.text.lower()

        clave = f"{nombre} ({categoria})"
        cartas[clave] = {
            "nombre": nombre,
            "categoria": categoria,
            "url": enlace,
            "precio": precio,
            "img": "https:" + img,
            "stock": en_stock
        }

    if not cartas:
        print(f"⚠️ No se encontraron productos válidos en {url}")

    return cartas

def comparar_y_enviar(cartas_actuales, cartas_anteriores):
    for clave, datos in cartas_actuales.items():
        nombre = datos["nombre"]
        url = datos["url"]
        precio = datos["precio"]
        stock = datos["stock"]
        img = datos["img"]
        categoria = datos["categoria"]

        carta_ant = cartas_anteriores.get(clave)

        nueva = carta_ant is None
        cambio_precio = carta_ant and precio < carta_ant["precio"]
        vuelve_stock = carta_ant and not carta_ant["stock"] and stock

        if nueva or cambio_precio or vuelve_stock:
            mensaje = f"🃏 <b>{nombre}</b>\n"
            mensaje += f"📂 Categoría: <i>{categoria.replace('-', ' ').title()}</i>\n"
            mensaje += f"💶 Precio: <b>{precio:.2f}€</b>\n"
            if cambio_precio:
                mensaje += f"🔻 <i>¡Ha bajado de precio!</i>\n"
            if vuelve_stock:
                mensaje += f"✅ <i>¡Vuelve a estar en stock!</i>\n"
            if nueva:
                mensaje += f"🆕 <i>Nueva carta detectada</i>\n"
            mensaje += f"🔗 <a href='{url}'>Ver producto</a>"

            bot.send_photo(CANAL_CARTAS, img, caption=mensaje, parse_mode="HTML")

def exportar_a_csv(cartas, carpeta="exportaciones_csv"):
    os.makedirs(carpeta, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    archivo = os.path.join(carpeta, f"cartas_pokemillon_{timestamp}.csv")

    with open(archivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Nombre", "Categoría", "Precio (€)", "Enlace", "En stock"])
        for datos in cartas.values():
            writer.writerow([
                datos["nombre"],
                datos["categoria"],
                f"{datos['precio']:.2f}",
                datos["url"],
                "Sí" if datos["stock"] else "No"
            ])
    print(f"📁 CSV guardado: {archivo}")

def revisar():
    print("🔍 Revisando Pokemillon...")
    cartas_anteriores = cargar_datos_anteriores()
    cartas_actuales = {}

    for url in URLS:
        cartas = obtener_cartas(url)
        cartas_actuales.update(cartas)

    comparar_y_enviar(cartas_actuales, cartas_anteriores)
    guardar_datos_nuevos(cartas_actuales)
    exportar_a_csv(cartas_actuales)
    print("✅ Revisión completada.\n")

# ==============================
# BUCLE INFINITO
# ==============================

def bucle():
    while True:
        revisar()
        time.sleep(1800)  # Cada 30 minutos

# ==============================
# MAIN
# ==============================

if __name__ == "__main__":
    hilo = threading.Thread(target=bucle)
    hilo.start()
    print("Bot de Pokemillon iniciado.")
    bot.send_message(MI_CHAT_ID,"Bot incializado")
