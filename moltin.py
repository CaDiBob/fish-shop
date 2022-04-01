import requests
from environs import Env


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
    return answer


def get_img(access_token, product_detail):
    image_id = product_detail['relationships']['main_image']['data']['id']
    url = f'https://api.moltin.com/v2/files/{image_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    answer = response.json()
    image_url = answer['data']['link']['href']
    return image_url


def get_product_info(product_detail):
    price = product_detail['meta']['display_price']['with_tax']['formatted']
    title = product_detail['name']
    amount = product_detail['meta']['stock']['level']
    availability = product_detail['meta']['stock']['availability']
    description = product_detail['description']
    return f'{title} {price} per piece'\
        f'{amount} {availability} '\
        f'{description}'


# if __name__ == '__main__':
#     env = Env()
#     env.read_env()
#     client_id = env('MOLTIN_CLIENT_ID')
#     access_token = get_moltin_access_token(client_id)
#     products = get_products(access_token)
#     for product in products['data']:
#         product_id = product['id']
#         print(get_img(access_token, get_product_detail(access_token, product_id)))
#         print(get_product_info(access_token, get_product_detail(access_token, product_id)))
#         exit()

