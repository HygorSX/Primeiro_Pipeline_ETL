import pandas as pd
import numpy as np
import requests
import json
import os

limit = 10

def extract_data(endpoint):
    response = requests.get(endpoint)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erros ao extrair dados da API: {response.status_code}")
        return None

def load_data(data, path):
    id = data["id"]

    os.makedirs(os.path.dirname(f"{path}/"), exist_ok=True)

    with open(f"{path}/{id}.json", "w") as file:
        json.dump(data, file)

def loop_load_data(endpoint):
    url = 'https://dummyjson.com/' + endpoint
    i = 1

    while True:
        data = extract_data(url + "/" + str(i))
        if data and i <= limit:
            load_data(data, "raw/" + endpoint)
        elif i > limit:
            break
        else:
            print(f"Erros ao extrair dados da API: {data}")
            break
        i += 1

def transform_data_json_to_csv(endpoint, i):
    os.makedirs(f"curated/{endpoint}", exist_ok=True)

    with open(f"raw/{endpoint}/{i}.json", "r") as file:
        data = json.load(file)

    if endpoint == "user":
        df = pd.DataFrame([data])
    elif endpoint == "products":
        if isinstance(data, dict):
            products = [data]
        elif isinstance(data, list):
            products = data
        else:
            raise ValueError(f"Formato inesperado para produtos: {type(data)}")

        selected_data = []
        for product in products:
            if not isinstance(product, dict):
                print(f"Produto {i} não é um dicionário: {product}")
                continue

            selected_data.append({
                "id": product.get("id"),
                "title": product.get("title"),
                "description": product.get("description"),
                "category": product.get("category"),
                "price": product.get("price"),
                "brand": product.get("brand"),
                "thumbnail": product.get("thumbnail")
            })
        df = pd.DataFrame(selected_data)

    df.to_csv(f"curated/{endpoint}/{i}.csv", index=False)

endpoints = ["user", "products"]

try:
    for endpoint in endpoints:
        print(f"Carregando dados para {endpoint}...")
        loop_load_data(endpoint)

    for endpoint in endpoints:
        print(f"Convertendo {endpoint} para CSV...")
        for i in range(1, limit + 1):
            transform_data_json_to_csv(endpoint, i)
finally:
    print("\nExtração e conversão concluídos com sucesso!")


