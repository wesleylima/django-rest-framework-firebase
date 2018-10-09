import datetime

from django.conf import settings
from rest_framework.settings import APISettings


USER_SETTINGS = getattr(settings, 'FIREBASE_AUTH', None)

DEFAULTS = {
    'FIREBASE_ACCOUNT_KEY_FILE': '', # JSON formatted key file you get directly from firebase
    'FIREBASE_CREDENTIALS': {
        'type': "service_account",
        'project_id': "",
        'private_key_id': "",
        'private_key': "",
        'client_email': "",
        'client_id': "",
        'auth_uri': "https://accounts.google.com/o/oauth2/auth",
        'token_uri': "https://accounts.google.com/o/oauth2/token",
        'auth_provider_x509_cert_url': "https://www.googleapis.com/oauth2/v1/certs",
        'client_x509_cert_url': ""
    }, # the credentials in raw json form
    
    'FIREBASE_CREATE_NEW_USER': True, # We'll make a new user if we get one that we don't have yet

    'FIREBASE_AUTH_HEADER_PREFIX': "JWT",
    'FIREBASE_UID_FIELD': 'username',
}

# List of settings that may be in string import notation.
IMPORT_STRINGS = (
)

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
