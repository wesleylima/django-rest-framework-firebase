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

## Publishing

`python setup.py sdist`

`twine upload dist/*`
