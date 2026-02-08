# scraper.py
import requests
from bs4 import BeautifulSoup
import random
import logging
import re

logging.basicConfig(level=logging.INFO)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_products_by_categories(categories: list) -> list:
    """
    Para cada categoría:
        - Scrapea 10 productos
        - Selecciona 5 al azar
        - Añade la categoría
    Retorna lista total (5 por categoría).
    """
    base_url = "https://www.trolley.co.uk/search/?from=search&q="
    final_list = []

    for category in categories:
        formatted_query = category.replace(" ", "+")
        url = base_url + formatted_query

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                logging.error(f"Error HTTP {response.status_code} en {url}")
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            items = soup.find_all("div", class_="product-item")

            if not items:
                logging.warning(f"There are no productos for '{category}'")
                continue

            # Tomar solo 10
            items = items[:10]

            extracted = []
            for item in items:
                info = item.find("div", class_="_info")
                if not info:
                    continue

                brand = info.find("div", class_="_brand")
                title = info.find("div", class_="_desc")
                link = item.find("a")

                href = link["href"] if link and link.get("href") else None

                extracted.append({
                    #"brand": brand.get_text(strip=True) if brand else "Unknown",
                    "title": title.get_text(strip=True) if title else "No title",
                    "href": href,
                    "category": category
                })

            # Seleccionar 5 al azar
            selected = random.sample(extracted, min(5, len(extracted)))
            final_list.extend(selected)

        except Exception as e:
            logging.error(f"Error inesperado en categoría {category}: {str(e)}")
            continue

    return final_list


def get_best_store_info(products: list) -> list:
    """
    Va a cada href y obtiene la tienda con el precio más bajo.
    """
    base_url = "https://www.trolley.co.uk"

    for product in products:
        href = product.get("href")
        if not href:
            product["store"] = None
            product["best_price"] = None
            product["store_link"] = None
            continue

        product_url = base_url + href

        try:
            response = requests.get(product_url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.content, "html.parser")

            table = soup.find("div", class_="comparison-table")
            if not table:
                continue

            items = table.find_all("div", class_="_item")

            store_entries = []

            for it in items:
                # -------- STORE NAME ----------
                svg = it.find("svg")
                store_name = svg.get("title") if svg and svg.get("title") else "Unknown"

                # -------- PRICE ---------------
                price_box = it.find("div", class_="_price")
                if not price_box:
                    continue
                price_text = price_box.get_text(" ", strip=True)
                match = re.search(r"([0-9]+\.?[0-9]*)", price_text)
                if not match:
                    continue
                price_val = float(match.group(1))

                # -------- VISIT LINK ----------
                # Buscar cualquier botón con texto VISIT
                visit_btn = it.find("a", string=lambda t: t and "visit" in t.lower())
                visit_link = visit_btn["href"] if visit_btn and visit_btn.get("href") else None
                store_entries.append({
                    "store": store_name,
                    "price": price_val,
                    "link": visit_link
                })
            
            # Elegir el más barato
            if store_entries:
                best_item = min(store_entries, key=lambda x: x["price"])
                product["store"] = best_item["store"]
                product["best_price"] = best_item["price"]
                product["store_link"] = best_item["link"]
                product.pop("href", None)  # Limpiar href innecesario
            else:
                product["store"] = None
                product["best_price"] = None
                product["store_link"] = None

        except Exception as e:
            logging.error(f"Error procesando {product_url}: {str(e)}")
            continue

    return products


# categories = ["cleaning", "health+beauty", "groceries", "online+shopping", "others"]

# products = get_products_by_categories(categories)
# final_products = get_best_store_info(products)

# for p in final_products:
#     print(p)
