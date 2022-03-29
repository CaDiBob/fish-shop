import requests
from environs import Env
from pprint import pprint


def add_to_cart(access_token):
    url = 'https://api.moltin.com/v2/carts/:reference/items'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    json_data = {
        'data': {
            'id': 'a08f9596-ec79-4663-bce7-c25e55df66de',
            'type': 'cart_item',
            'quantity': 1,
        },
    }
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()
    answer = response.json()
    return answer


def get_moltin_access_token(client_id):
    url = 'https://api.moltin.com/oauth/access_token'
    data = {
        'client_id': client_id,
        'grant_type': 'implicit',
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    answer = response.json()
    return answer['access_token']


def get_products(access_token):
    url = 'https://api.moltin.com/v2/products'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    answer = response.json()
    return answer


def main():
    env = Env()
    env.read_env()
    client_id = env('MOLTIN_CLIENT_ID')
    access_token = get_moltin_access_token(client_id)
    pprint(add_to_cart(access_token))


if __name__ == '__main__':
    main()
