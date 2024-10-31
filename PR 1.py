import socket
from bs4 import BeautifulSoup
from functools import reduce
from datetime import datetime

EURS_TO_MDL = 20.22
MDL_MIN_PRICE = 100
MDL_MAX_PRICE = 1000

def http_get(url):
    host = url.split("//")[-1].split("/")[0]
    path = "/" + "/".join(url.split("//")[-1].split("/")[1:])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, 80))
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        s.send(request.encode())
        response = b""
        while True:
            part = s.recv(4096)
            if not part:
                break
            response += part
    return response.decode().split("\r\n\r\n", 1)[1]

def validate_product(name, price):
    return isinstance(name, str) and isinstance(price, int) and price > 0

def convert_price_to_eur(price):
    return price / EURS_TO_MDL

def filter_products(products):
    return [product for product in products if MDL_MIN_PRICE <= product['price'] <= MDL_MAX_PRICE]

def scrape_product_details(product_link):
    response = http_get(product_link)
    soup = BeautifulSoup(response, 'html.parser')
    additional_info = soup.find('div', class_='product-info')
    color = additional_info.find('span', class_='color').text if additional_info else "N/A"
    return color

def main():
    url = 'https://999.md'
    response = http_get(url)
    soup = BeautifulSoup(response, 'html.parser')
    products = []
    for item in soup.select('.product-item'):
        name = item.find('h2', class_='product-title').text.strip()
        price = int(item.find('span', class_='product-price').text.strip().replace(' MDL', ''))
        if validate_product(name, price):
            link = item.find('a', class_='product-link')['href']
            additional_data = scrape_product_details(link)
            products.append({'name': name, 'price': price, 'link': link, 'color': additional_data})
    prices_in_eur = list(map(convert_price_to_eur, [product['price'] for product in products]))
    filtered_products = filter_products(products)
    total_price = reduce(lambda x, y: x + y, [product['price'] for product in filtered_products])
    timestamp = datetime.utcnow().isoformat()
    result = {
        'timestamp': timestamp,
        'total_price': total_price,
        'filtered_products': filtered_products
    }
    print(result)

if __name__ == "__main__":
    main()
