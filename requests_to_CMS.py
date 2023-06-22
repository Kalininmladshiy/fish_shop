import requests


def get_access_token(client_id, client_secret):

    new_access_token = 'https://useast.api.elasticpath.com/oauth/access_token'
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }
    response = requests.get(
        new_access_token,
        data=payload,
    )
    response.raise_for_status()
    access_token = response.json()

    return access_token


def create_a_customer(name, email, access_token):

    url = 'https://useast.api.elasticpath.com/v2/customers'
    headers = {
        "Authorization": f"Bearer {access_token['access_token']}",
        "Content-Type": "application/json",
    }
    payload = {
        "data": {
            "type": 'customer',
            "name": name,
            "email": email,
        }
    }
    response = requests.post(
        url,
        headers=headers,
        json=payload,
    )
    response.raise_for_status()


def add_to_cart(quantity, product_id, cart_id, access_token):

    url = f'https://useast.api.elasticpath.com/v2/carts/{cart_id}/items'
    headers = {
        "Authorization": f"Bearer {access_token['access_token']}",
        "Content-Type": "application/json",
    }
    payload = {
        "data": {
            "id": product_id,
            "type": "cart_item",
            "quantity": quantity,
        }
    }
    response = requests.post(
        url,
        headers=headers,
        json=payload,
    )
    response.raise_for_status()


def delete_from_cart(product_id, cart_id, access_token):

    url = f'https://useast.api.elasticpath.com/v2/carts/{cart_id}/items/{product_id}'
    headers = {
        "Authorization": f"Bearer {access_token['access_token']}",
    }

    response = requests.delete(
        url,
        headers=headers,
    )
    response.raise_for_status()


def get_cart(cart_id, access_token):

    url = f'https://useast.api.elasticpath.com/v2/carts/{cart_id}/items'
    headers = {
        "Authorization": f"Bearer {access_token['access_token']}",
    }
    payload = {}
    response = requests.get(
        url,
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    cart = response.json()

    return cart


def get_products(access_token):

    url = 'https://useast.api.elasticpath.com/pcm/products'
    headers = {
        "Authorization": f"Bearer {access_token['access_token']}",
    }
    payload = {}
    response = requests.get(
        url,
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    products = response.json()['data']

    return products


def get_product(product_id, access_token):

    url = f'https://useast.api.elasticpath.com/pcm/products/{product_id}'
    headers = {
        "Authorization": f"Bearer {access_token['access_token']}",
    }
    payload = {}
    response = requests.get(
        url,
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    product = response.json()['data']

    return product


def get_price(sku, price_book_id, access_token):

    url = f'https://useast.api.elasticpath.com/pcm/pricebooks/{price_book_id}/prices'
    headers = {
        "Authorization": f"Bearer {access_token['access_token']}",
    }
    payload = {}
    response = requests.get(
        url,
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    prices = response.json()['data']
    for price in prices:
        if price['attributes']['sku'] == sku:
            return price['attributes']['currencies']['USD']['amount'] / 100
    return 'Цена не найдена'


def get_product_photo_link(photo_id, access_token):

    url = f'https://useast.api.elasticpath.com/v2/files/{photo_id}'
    headers = {
        "Authorization": f"Bearer {access_token['access_token']}",
    }
    payload = {}
    response = requests.get(
        url,
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    return response.json()['data']['link']['href']
