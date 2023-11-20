import sys
import requests
import json
import logging
from os import environ
import base64
import urllib3
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# NOTE For now disable HTTPS certificate check
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
POLUS_LOG = getattr(logging, environ.get("POLUS_LOG", "DEBUG"))
logger = logging.getLogger("polus.plugins.token_service")
logger.setLevel(POLUS_LOG)

def _b64_decode(data):
    data += '=' * (4 - len(data) % 4)
    return base64.b64decode(data).decode('utf-8')

def _jwt_payload_decode(jwt):
    _, payload, _ = jwt.split('.')
    return json.loads(_b64_decode(payload))

def decode_access_token(access_token):
    ''' Transform base64 encoded token into unicode.'''
    return _jwt_payload_decode(access_token)

def get_access_token():
    """
    Obtain a new OAuth 2.0 token from the authentication server.
    """
    COMPUTE_CLIENT_ID = environ.get("COMPUTE_CLIENT_ID")
    COMPUTE_CLIENT_SECRET = environ.get("COMPUTE_CLIENT_SECRET")
    TOKEN_URL = environ.get("TOKEN_URL")

    if TOKEN_URL == None:
        raise Exception("you need to set env variable TOKEN_URL")
    if COMPUTE_CLIENT_ID == None: 
        raise Exception("you need to set env variable COMPUTE_CLIENT_ID")
    if COMPUTE_CLIENT_SECRET == None:
        raise Exception("you need to set env variable COMPUTE_CLIENT_SECRET")

    token_req_payload = {'grant_type': 'client_credentials'}
    auth = (COMPUTE_CLIENT_ID, COMPUTE_CLIENT_SECRET)
    token_response = requests.post(TOKEN_URL,data=token_req_payload, verify=False, allow_redirects=False,auth=auth)

    if token_response.status_code !=200:
        raise Exception("Failed to obtain token from the OAuth 2.0 server", token_response)
    else:
        token_json = token_response.json()  
        return token_json["access_token"]
