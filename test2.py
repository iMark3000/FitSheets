import base64
import hashlib
import secrets
import random
from typing import Tuple

from requests_oauthlib.oauth2_session import OAuth2Session


def generate_code_verifier(length: int = 128) -> str:
    """Return a random PKCE-compliant code verifier.
    Parameters
    ----------
    length : int
        Code verifier length. Must verify `43 <= length <= 128`.
    Returns
    -------
    code_verifier : str
        Code verifier.
    Raises
    ------
    ValueError
        When `43 <= length <= 128` is not verified.
    """
    if not 43 <= length <= 128:
        msg = 'Parameter `length` must verify `43 <= length <= 128`.'
        raise ValueError(msg)
    code_verifier = secrets.token_urlsafe(96)[:length]
    return code_verifier


def generate_pkce_pair(code_verifier_length: int = 128) -> Tuple[str, str]:
    """Return random PKCE-compliant code verifier and code challenge.
    Parameters
    ----------
    code_verifier_length : int
        Code verifier length. Must verify
        `43 <= code_verifier_length <= 128`.
    Returns

    """
    if not 43 <= code_verifier_length <= 128:
        msg = 'Parameter `code_verifier_length` must verify '
        msg += '`43 <= code_verifier_length <= 128`.'
        raise ValueError(msg)
    code_verifier = generate_code_verifier(code_verifier_length)
    code_challenge = get_code_challenge(code_verifier)
    return code_verifier, code_challenge


def get_code_challenge(code_verifier: str) -> str:
    """Return the PKCE-compliant code challenge for a given verifier.
    Parameters
    ----------
    ValueError
        When `43 <= len(code_verifier) <= 128` is not verified.
    """
    if not 43 <= len(code_verifier) <= 128:
        msg = 'Parameter `code_verifier` must verify '
        msg += '`43 <= len(code_verifier) <= 128`.'
        raise ValueError(msg)
    hashed = hashlib.sha256(code_verifier.encode('ascii')).digest()
    encoded = base64.urlsafe_b64encode(hashed)
    code_challenge = encoded.decode('ascii')[:-1]
    return code_challenge


def main():
    client_id = "238H5R"
    redirect_uri = 'http://localhost/foobar'

    code_verifier_len = random.randrange(43, 128)
    code_verifier, code_challenge = generate_pkce_pair(code_verifier_len)

    # Need to figure out scope
    scope = []

    oauth = OAuth2Session(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
        code_challenge=code_challenge,
        code_challenge_method='S256',
        response_type='code')

    authorization_url, state = oauth.authorization_url('https://www.fitbit.com/oauth2/authorize?')

    print(f'Please go to {authorization_url} and authorize access.')
    # authorization_response = raw_input('Enter the full callback URL')

    token = oauth.fetch_token('https://accounts.google.com/o/oauth2/token', authorization_response=authorization_response)

    r = oauth.get('INSERT API URL HERE')
