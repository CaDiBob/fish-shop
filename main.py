import requests
from environs import Env
from pprint import pprint


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
    pprint(get_products(access_token))


if __name__ == '__main__':
    main()
