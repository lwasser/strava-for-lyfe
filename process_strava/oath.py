"""A module with helper functions to process data."""

import pickle
import time

from stravalib.client import Client

def get_token(token_path_pickle, client_id, client_secret):
    """A function """
    
    client = Client()
    
    try:
        with open('../access_token.pickle', 'rb') as f:
            access_token = pickle.load(f)
    except FileNotFoundError:
        print("Oops - looks like the access token pickle file doesn't exist.")
    
    if time.time() > access_token['expires_at']:
        print('Oops! Your token has expired. No worries - I will refresh it for you.')
        refresh_response = client.refresh_access_token(client_id=client_id,
                                                       client_secret=client_secret,
                                                       refresh_token=access_token['refresh_token'])
        access_token = refresh_response
        with open(token_path_pickle, 'wb') as f:
            pickle.dump(refresh_response, f)
        print("I've refreshed your token and saved it to a file. Aren't I the best?")

        client.access_token = refresh_response['access_token']
        client.refresh_token = refresh_response['refresh_token']
        client.token_expires_at = refresh_response['expires_at']

    else:
        print('Token still valid, expires at {}'
              .format(time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(access_token['expires_at']))))

        client.access_token = access_token['access_token']
        client.refresh_token = access_token['refresh_token']
        client.token_expires_at = access_token['expires_at']
        
        return client