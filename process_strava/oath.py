"""A module with helper functions to process data."""

import os
import pickle
import time
import webbrowser

from stravalib.client import Client
from stravalib.util import limiter


def get_token(client, client_id, client_secret, code):
    """A one time authentication to get a user token"""
    # Should I instantiate a new client or just pass one in?

    return client.exchange_code_for_token(client_id=client_id,
                                          client_secret=client_secret,
                                          code=code)


def save_token(access_token, path_to_save):
    """Function to save the token somewhere. For now i'm using a
    pickle to do it. Don't laugh at pickles."""

    with open(path_to_save, 'wb') as f:
        pickle.dump(access_token, f)

    print("Token saved - hooray!")


def get_code(client,
             client_id):
    """ Get the access code from the user. Only needs to be performed once."""

    # Generate the URL
    print("Authenticating with Strava. Be sure you are logged into Strava before running this!")
    print("I am launching a web browser. Please return the code following code= in the resulting url.")

    # NOTE - this allows access to a lot of profile info AND private activities. we could scope this back to read all easily
    url = client.authorization_url(client_id=client_id,
                                   redirect_uri='http://127.0.0.1:5000/authorization',
                                   scope=['read_all', 'profile:read_all', 'activity:read_all'])
    webbrowser.open(url)
    print("""You will see a url that looks like this. """,
          """http://127.0.0.1:5000/authorization?state=&code=45fe4353d6f8d04fd6033a00923dd04972760550&scope=read,activity:read_all,profile:read_all,read_all")""",
          """copy the code after code= in the url. do not include the & in this """)

    code = input("Please enter the code that you received: ")
    print("Great! Your code is ", code, "Next I will exchange that code for a token.\n"
                                        "I only have to do this once.")
    return code


def authenticate_save_token(client,
                            client_id,
                            client_secret,
                            path_to_save="access_token.pickle"):
    code = get_code(client,
                    client_id)

    # Once we have the code,we can exchange the code for a token
    path_to_save = os.path.join("access_token.pickle")

    access_token = get_token(client, client_id, client_secret, code=code)
    save_token(access_token, path_to_save)



def authenticate(secrets,
                 client, verbose=True):
    """A function that sets up authentication with strava

    Parameters
    ----------
    secrets : string
        Path to secrets file with client id and client secret in it

    client : a stravalib client object

    Returns
    -------
    authentication

    """


    client_id, client_secret = open(
        'strava-secrets.txt').read().strip().split(',')

    client = Client(rate_limiter=limiter.DefaultRateLimiter())
    # ****This only needs to happen once. Once we have the token we can simply refresh ****

    path_to_save = os.path.join("access_token.pickle")

    # If the token doesn't exist, create it
    # else refresh if it does exist
    if not os.path.exists(path_to_save):
        authenticate_save_token(client,
                                client_id,
                                client_secret)

    else:
        if os.path.exists(path_to_save):
            refresh_token(client,
                          client_id,
                          client_secret,
                          token_path_pickle=path_to_save,
                          verbose=verbose)

    return client



def refresh_token(client, client_id, client_secret, token_path_pickle=None, code=None, verbose=True):

    """A function that refreshes the users token once it has been
    created. The tokens expire every 6 hours."""

    # Here i'm using a saved pickle
    try:
        with open(token_path_pickle, 'rb') as f:
            access_token = pickle.load(f)
    except FileNotFoundError:
        print("Oops - looks like you haven't created an access token yet. Aborting.")

    if time.time() > access_token['expires_at']:
        if verbose:
            print('Oops! Your token has expired. No worries - I will refresh it for you.')
        refresh_response = client.refresh_access_token(client_id=client_id,
                                                       client_secret=client_secret,
                                                       refresh_token=access_token['refresh_token'])
        access_token = refresh_response
        with open(token_path_pickle, 'wb') as f:
            pickle.dump(refresh_response, f)
        if verbose:
            print("I've refreshed your token and saved it to a file. Aren't I the best?")

        client.access_token = refresh_response['access_token']
        client.refresh_token = refresh_response['refresh_token']
        client.token_expires_at = refresh_response['expires_at']

    else:
        if verbose:
            print('Token still valid, expires at {}'
                  .format(time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(access_token['expires_at']))))

        client.access_token = access_token['access_token']
        client.refresh_token = access_token['refresh_token']
        client.token_expires_at = access_token['expires_at']

        return client
