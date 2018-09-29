import argparse
import os
from typing import List, Optional

import requests

from errors import Unavailable, VkMethodError
from models import User

VK_API_ACCESS_TOKEN = os.environ['VK_API_ACCESS_TOKEN']
VK_API_VERSION = os.environ.get('VK_API_VERSION', '5.85')


def create_parser():
    parser = argparse.ArgumentParser(description='Vk Friends Online')
    parser.add_argument('-id', type=int, dest='user_id',
                        help='show friends of the user with this id')
    return parser, parser.parse_args()


def make_vk_request(method_name: str, parameters: dict = {}):
    try:
        response = requests.get(f'https://api.vk.com/method/{method_name}', params={
            'access_token': VK_API_ACCESS_TOKEN,
            'v': VK_API_VERSION,
            **parameters
        })
    except Exception:
        raise Unavailable()

    response_content = response.json()

    error = response_content.get('error')
    if error is not None:
        raise VkMethodError(error['error_code'], error['error_msg'])

    return response_content.get('response')


def normalize_user_ids(user_ids: List[int] = None) -> Optional[str]:
    if not user_ids:
        return None
    return ','.join(str(user_id) for user_id in user_ids)


def get_users(user_ids: List[int] = None) -> List[User]:
    normalized_user_ids = normalize_user_ids(user_ids)
    users_data = make_vk_request('users.get', parameters={
        'user_ids': normalized_user_ids
    })
    return [
        User(
            id=user_data.get('id'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
        )
        for user_data in users_data
    ]


def get_user(user_id: int) -> User:
    users = get_users([user_id])
    return users[0]


def get_current_user() -> User:
    users = get_users()
    return users[0]


def get_friends_online(user_id: int) -> List[User]:
    friends_online_ids = make_vk_request('friends.getOnline', parameters={
        'user_id': user_id
    })
    friends_online = get_users(friends_online_ids)
    return friends_online


def main():
    _, args = create_parser()

    if args.user_id:
        user = get_user(args.user_id)
    else:
        user = get_current_user()
    friends = get_friends_online(user.id)

    print('User:')
    print(f'- {user}')

    print('Friends:')
    for friend in friends:
        print(f'- {friend}')


if __name__ == '__main__':
    main()
