import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape product listing page
def scrape_product_listing(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('div', {'data-component-type': 's-search-result'})

    data = []
    for product in products:
        try:
            product_url = 'https://www.amazon.in' + product.find('a', {'class': 'a-link-normal'})['href']
            product_name = product.find('span', {'class': 'a-size-medium'}).text.strip()
            product_price = product.find('span', {'class': 'a-price-whole'}).text.strip()
            product_rating = product.find('span', {'class': 'a-icon-alt'}).text.strip().split()[0]
            product_reviews = product.find('span', {'class': 'a-size-base'}).text.strip().replace(',', '')

            data.append({
                'Product URL': product_url,
                'Product Name': product_name,
                'Product Price': product_price,
                'Rating': product_rating,
                'Number of Reviews': product_reviews
            })
        except:
            continue

    return data

# Function to scrape individual product page
def scrape_product_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            description = soup.find('div', {'id': 'productDescription'}).get_text(strip=True)
        except:
            description = ''
        try:
            asin = soup.find('th', string='ASIN').find_next('td').get_text(strip=True)
        except:
            asin = ''
        try:
            product_description = soup.find('h2', string='Product Description').find_next('div').get_text(strip=True)
        except:
            product_description = ''
        try:
            manufacturer = soup.find('th', string='Manufacturer').find_next('td').get_text(strip=True)
        except:
            manufacturer = ''

        data = {
            'Product URL': url,
            'Description': description,
            'ASIN': asin,
            'Product Description': product_description,
            'Manufacturer': manufacturer
        }

        return data
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while scraping {url}: {e}") 
        return None

# Scrape product listing pages
base_url = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{}'
total_pages = 20
all_data = []

for page in range(1, total_pages + 1):
    url = base_url.format(page)
    data = scrape_product_listing(url)
    all_data.extend(data)

## Scrape individual product pages
product_data = []
total_urls = 200

for i, data in enumerate(all_data[:total_urls]):
    print(f"Scraping product {i+1}/{total_urls}...")
    product_url = data['Product URL']
    product_info = scrape_product_page(product_url)
    if product_info:
        product_data.append({**data, **product_info})

# Convert data to DataFrame
df = pd.DataFrame(product_data)

# Save DataFrame to CSV|
df.to_csv('amazon_products.csv', index=False)

print("CSV file 'amazon_products.csv' downloaded successfully.")
