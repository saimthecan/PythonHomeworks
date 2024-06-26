import requests
import json

url = "https://dummyjson.com/products"

response = requests.get(url)
data = response.json()

# Get the first 10 products
products = data['products'][:10]

total_price = 0
product_lines = []

for product in products:
    title = product['title']
    price = product['price']
    total_price += price
    product_lines.append(f"{title}: {price}")

# Format the total price to 2 decimal places
total_price_formatted = f"{total_price:.2f}"

file_path = 'first_10_products.txt'
with open(file_path, 'w') as file:
    for line in product_lines:
        file.write(line + "\n")
    file.write(f"\nTotal price of first 10 products: {total_price_formatted}")

print(f"Total price of first 10 products: {total_price_formatted}")

print("Products and their prices:")
for line in product_lines:
    print(line)
