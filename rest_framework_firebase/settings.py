import datetime

from django.conf import settings
from rest_framework.settings import APISettings


USER_SETTINGS = getattr(settings, 'FIREBASE_AUTH', None)

DEFAULTS = {
    'FIREBASE_ACCOUNT_KEY_FILE': '', # JSON formatted key file you get directly from firebase

    # The credentials if you want to enter them in manually (not implemented)
    'FIREBASE_PRIVATE_KEY': None,
    'FIREBASE_PUBLIC_KEY': None,
    'FIREBASE_CLIENT_EMAIL': None,
    'FIREBASE_CREATE_NEW_USER': True, # We'll make a new user if we get one that we don't have yet

    'FIREBASE_AUTH_HEADER_PREFIX': "JWT",
    'FIREBASE_UID_FIELD': 'username',
}

# List of settings that may be in string import notation.
IMPORT_STRINGS = (
)

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
