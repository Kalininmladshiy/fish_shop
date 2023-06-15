import requests
from environs import Env


def get_access_token():
    client_id = env.str('CLIENT_ID')
    client_secret = env.str('CLIENT_SECRET')
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
    access_token = response.json()['access_token']
    return access_token


def create_a_customer(name, email):

    access_token = get_access_token()
    create_customer = 'https://useast.api.elasticpath.com/v2/customers'
    headers = {
        "Authorization": f"Bearer {access_token}",
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
        create_customer,
        headers=headers,
        json=payload,
    )
    response.raise_for_status()


def add_to_cart(quantity, product_id, cart_id):

    access_token = get_access_token()
    add_to_cart = f'https://useast.api.elasticpath.com/v2/carts/{cart_id}/items'
    headers = {
        "Authorization": f"Bearer {access_token}",
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
        add_to_cart,
        headers=headers,
        json=payload,
    )
    response.raise_for_status()


def delete_from_cart(product_id, cart_id):

    access_token = get_access_token()
    delete_from_cart = f'https://useast.api.elasticpath.com/v2/carts/{cart_id}/items/{product_id}'
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.delete(
        delete_from_cart,
        headers=headers,
    )
    response.raise_for_status()


def get_cart(cart_id):

    access_token = get_access_token()
    get_cart = f'https://useast.api.elasticpath.com/v2/carts/{cart_id}/items'
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    payload = {}
    response = requests.get(
        get_cart,
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    cart = response.json()

    return cart


def get_products():

    access_token = get_access_token()
    get_products = 'https://useast.api.elasticpath.com/pcm/products'
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    payload = {}
    response = requests.get(
        get_products,
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    products = response.json()['data']

    return products


def get_product(product_id):

    access_token = get_access_token()
    get_product = f'https://useast.api.elasticpath.com/pcm/products/{product_id}'
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    payload = {}
    response = requests.get(
        get_product,
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    product = response.json()['data']

    return product


def get_price(sku):

    access_token = get_access_token()
    price_book_id = env.str('PRICE_BOOK_ID')
    get_prices = f'https://useast.api.elasticpath.com/pcm/pricebooks/{price_book_id}/prices'
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    payload = {}
    response = requests.get(
        get_prices,
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    prices = response.json()['data']
    for price in prices:
        if price['attributes']['sku'] == sku:
            return price['attributes']['currencies']['USD']['amount'] / 100
    return 'Цена не найдена'


def get_product_photo_link(photo_id):

    access_token = get_access_token()
    get_product_photo = f'https://useast.api.elasticpath.com/v2/files/{photo_id}'
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    payload = {}
    response = requests.get(
        get_product_photo,
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    return response.json()['data']['link']['href']


if __name__ == '__main__':
    env = Env()
    env.read_env()
