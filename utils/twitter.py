import json
import requests
from requests_oauthlib import OAuth1Session


class TwitterAuth(OAuth1Session):
    def __init__(self, consumer_key, consumer_secret, token, token_secret):
        super(TwitterAuth, self).__init__(consumer_key, consumer_secret, resource_owner_key=token,
                                          resource_owner_secret=token_secret)

    @staticmethod
    def create_payload(text):
        return json.dumps({"text": text})

    def perform_request(self, url, payload):
        headers = {'Content-Type': 'application/json'}
        try:
            response = self.post(url, headers=headers, data=payload)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as http_err:
            raise ValueError(f'HTTP error occurred: {http_err}')
        except requests.exceptions.RequestException as req_err:
            raise ValueError(f'Request error occurred: {req_err}')
        except Exception as e:
            raise ValueError(f'An unexpected error occurred: {str(e)}')

    def post_tweet(self, text):
        url = "https://api.twitter.com/2/tweets"
        payload = self.create_payload(text)
        self.perform_request(url, payload)
