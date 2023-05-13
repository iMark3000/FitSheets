from os import getenv
import json

from requests_oauthlib import OAuth2Session

with open('credentials.json', 'r') as cred_file:
    creds = json.load(cred_file)

scope = ['activity',
        'heartrate',
        'nutrition',
        'location',
        'oxygen_saturation',
        'respiratory_rate',
        'settings',
        'sleep',
        'weight'
        ]

oauth = OAuth2Session(creds["client id"], redirect_uri='http:.www.fitbit.com', scope=scope)

authorization_url, state = oauth.authorization_url('https://www.fitbit.com/oauth2/authorize', access_type="offline",
                                                   propmpt="select_account")

print(f'Go to {authorization_url}')
auth_response = input("Enter Callback")

token = oauth.fetch_token(creds['access token uri'], client_secret=creds['client secret'],
                          authorization_response=auth_response)

r = oauth.get('/1.2/user/-/sleep/date/2022-07-30.json')
print(r)