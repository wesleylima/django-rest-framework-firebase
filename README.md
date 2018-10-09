# Django Rest Framework Firebase Auth

## Installation

```
pip install djangorestframework-firebase
```

On your project's `settings.py` add this to the `REST_FRAMEWORK` configuration

```
REST_FRAMEWORK = {
  ...
  'DEFAULT_AUTHENTICATION_CLASSES': (
    'rest_framework_firebase.authentication.FirebaseAuthentication',
  )
  ...
}
```

Get admin credentials `.json` from the Firebase SDK and add them to your project

Also in your project's `settings.py` :

```
FIREBASE_AUTH = {
    'FIREBASE_ACCOUNT_KEY_FILE': 'path_to_your_credentials.json',
}
```

Alternatively, you can configure the Firebase credentials directly, like so:

```
FIREBASE_AUTH = {
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
    }
}
```

## Publishing

`python setup.py sdist`

`twine upload dist/*`
