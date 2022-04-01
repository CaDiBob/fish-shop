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


def get_product_detail(access_token, product_id):
    url = f'https://api.moltin.com/v2/products/{product_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    answer = response.json()['data']
    price = answer['meta']['display_price']['with_tax']['formatted']
    title = answer['name']
    amount = answer['meta']['stock']['level']
    availability = answer['meta']['stock']['availability']
    description = answer['description']
    return f'''{title}
    {price} per piece 
    {amount} {availability} 
    {description}
    '''


# if __name__ == '__main__':
#     env = Env()
#     env.read_env()
#     client_id = env('MOLTIN_CLIENT_ID')
#     access_token = get_moltin_access_token(client_id)
#     products = get_products(access_token)
#     for product in products['data']:
#         product_id = product['id']
#         print(get_product_detail(access_token, product_id))
#         exit()

