import requests
import json

url = "https://dummyjson.com/products"

response = requests.get(url)
data = response.json()

# Get all products
products = data['products']

total_price = 0
product_lines = []
high_rating_titles = []

for product in products:
    title = product['title']
    price = product['price']
    
    if price > 15:
        total_price += price
        product_lines.append(f"{title}: {price}")

    for review in product['reviews']:
        if review['rating'] == 5:
            high_rating_titles.append(title)
            break 

file_path = 'products_over_15.txt'
with open(file_path, 'w') as file:
    for line in product_lines:
        file.write(line + "\n")
    file.write(f"\nTotal price of products with price greater than 15: {total_price:.2f}")

print(f"Total price of products with price greater than 15: {total_price:.2f}")

print("Products with at least one review rating of 5:")
for title in high_rating_titles:
    print(title)
