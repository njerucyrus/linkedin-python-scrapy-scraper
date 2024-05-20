import json
import os

from api.ghl import ApiClient
from dotenv import load_dotenv

load_dotenv()
GHL_LOCATION_ID = os.getenv('GHL_LOCATION_ID')
api = ApiClient()


def create_user(user_data: dict):
    ghl_user_data = {
        'firstName': user_data.get('first_name', ''),
        'lastName': user_data.get('last_name', ''),
        'email': user_data.get('email', ''),
        'password': user_data.get('password', ''),
        'type': 'account',
        'role': 'user',
        "permissions": api.get_default_permissions(),
        "locationIds": [
            f"{GHL_LOCATION_ID}"
        ]
    }

    return api.create_user(ghl_user_data)


def create_contact(contact_details: dict):
    ghl_contact_data = {
        'firstName': contact_details.get('first_name', ''),
        'lastName': contact_details.get('last_name', ''),
        'email': contact_details.get('email', ''),
        'phone': contact_details.get('phone', ''),
        'tags': ['LinkedIn-Contacts']
    }
    return api.create_contact(ghl_contact_data)


if __name__ == '__main__':
    with open('sample-data.json', 'r') as f:
        data = json.load(f)
        for item in data[1:]:
            contact = create_contact(item)
            print(f'Created contact {contact}')
