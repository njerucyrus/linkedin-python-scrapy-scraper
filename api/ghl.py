import json
import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()
GHL_API_KEY = os.getenv("GHL_API_KEY")
GHL_LOCATION_ID = os.getenv("GHL_LOCATION_ID")


class ApiClient(object):
    def __init__(self):

        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {GHL_API_KEY}'})
        self.base_url = 'https://rest.gohighlevel.com'

    def list_users(self):
        endpoint = f"{self.base_url}/v1/users/"
        response = self.session.get(url=endpoint)
        return response.json()

    def create_user(self, user_data: dict) -> Any:
        endpoint = f"{self.base_url}/v1/users/"

        response = self.session.post(url=endpoint, json=user_data)
        if 200 <= response.status_code <= 201:
            user = response.json()
            return {'status': 'success', 'user': user, 'errors': None}
        else:
            with open('highlevel_error.json', 'w+') as f:
                f.write(json.dumps(response.json()))
            errors = response.json()
            error_messages = []

            for key, value in errors.items():
                error_message = value['message']
                error_messages.append(error_message)

            return {'status': 'failed', 'user': None, 'errors': error_messages}

    def retrieve_user(self, user_id: str) -> Any:
        endpoint = f"{self.base_url}/v1/users/{user_id}"

        response = self.session.get(url=endpoint)
        if response.status_code == 200:
            user = response.json()

            return user
        else:
            return None

    def update_user(self, user_id, user_data: dict) -> Any:
        endpoint = f"{self.base_url}/v1/users/{user_id}"

        response = self.session.put(url=endpoint, json=user_data)
        if response.status_code == 200:
            user = response.json()
            return user
        else:
            return response.json()

    def delete_user(self, user_id):
        endpoint = f"{self.base_url}/v1/users/{user_id}"
        response = self.session.delete(url=endpoint)
        return response.json()

    def list_locations(self):
        endpoint = f"{self.base_url}/v1/locations"
        response = self.session.get(url=endpoint)
        return response.json()

    def get_default_permissions(self):
        return {
            "campaignsEnabled": False,
            "campaignsReadOnly": True,
            "contactsEnabled": False,
            "workflowsEnabled": False,
            "workflowsReadOnly": True,
            "triggersEnabled": False,
            "funnelsEnabled": False,
            "websitesEnabled": False,
            "opportunitiesEnabled": False,
            "dashboardStatsEnabled": True,
            "bulkRequestsEnabled": False,
            "appointmentsEnabled": False,
            "reviewsEnabled": True,
            "onlineListingsEnabled": True,
            "phoneCallEnabled": False,
            "conversationsEnabled": False,
            "assignedDataOnly": False,
            "adwordsReportingEnabled": False,
            "membershipEnabled": False,
            "facebookAdsReportingEnabled": False,
            "attributionsReportingEnabled": False,
            "settingsEnabled": False,
            "tagsEnabled": False,
            "leadValueEnabled": False,
            "marketingEnabled": False,
            "agentReportingEnabled": False,
            "botService": False,
            "socialPlanner": False,
            "bloggingEnabled": True,
            "invoiceEnabled": False
        }

    def create_contact(self, contact_details: dict) -> Any:
        try:
            endpoint = f"{self.base_url}/v1/contacts/"
            response = self.session.post(url=endpoint, json=contact_details)
            if 200 <= response.status_code <= 201:
                contact =  response.json()
                return {'status': 'success', 'contact': contact, 'errors': None}
            else:
                return {'status': 'failed', 'contact': None, 'errors': response.json()}
        except Exception as e:
            print(e)
            return {'status': 'failed', 'error': str(e)}

    def list_contacts(self):
        try:
            endpoint = f"{self.base_url}/v1/contacts"
            response = self.session.get(url=endpoint)
            return response.json()
        except Exception as e:
            print(e)
            return {'status': 'failed', 'error': str(e)}

if __name__ == '__main__':
    api = ApiClient()
    users = api.list_users()
    print(json.dumps(users, indent=2))