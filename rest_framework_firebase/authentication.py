import abc

import firebase_admin
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from firebase_admin import auth, credentials
from rest_framework import exceptions
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header
)

from rest_framework_firebase.settings import api_settings


if api_settings.FIREBASE_ACCOUNT_KEY_FILE:
    creds = credentials.Certificate(api_settings.FIREBASE_ACCOUNT_KEY_FILE)
elif api_settings.FIREBASE_CREDENTIALS:
    creds = credentials.Certificate(api_settings.FIREBASE_CREDENTIALS)
else:
    creds = None
firebase = firebase_admin.initialize_app(creds)


class BaseFirebaseAuthentication(BaseAuthentication):
    """
    Token based authentication using firebase.
    """

    @abc.abstractmethod
    def get_token(self, request):
        ...

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using Firebase authentication.  Otherwise returns `None`.
        """
        firebase_token = self.get_token(request)
        if firebase_token is None:
            return None

        try:
            payload = auth.verify_id_token(firebase_token)
        except ValueError:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except auth.AuthError:
            msg = _('Could not log in.')
            raise exceptions.AuthenticationFailed(msg)

        user = self._authenticate_credentials(payload)

        return (user, payload)

    def _authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        User = get_user_model()
        uid_field = api_settings.FIREBASE_UID_FIELD
        uid = payload['uid']
        anon_auth = False
        user = None
        if not uid:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)
        try:
            if payload.get('email', None):
                # a non-anon user
                if 'email_verified' not in payload or ('email_verified' in payload and not payload['email_verified']):
                    msg = _('User email not yet confirmed.')
                    raise exceptions.AuthenticationFailed(msg)
            elif payload["firebase"]["sign_in_provider"] == "anonymous":
                anon_auth = True
            else:
                msg = _('Unknown auth method')
                raise exceptions.AuthenticationFailed(msg)
            user = User.objects.get(**{uid_field: uid})
        except User.DoesNotExist:
            if not api_settings.FIREBASE_CREATE_NEW_USER:
                msg = _('Invalid signature.')
                raise exceptions.AuthenticationFailed(msg)

            # Try get user by email rather than uid
            fb_user = auth.get_user(uid)
            try:
                # NOTE: we only have the FB uid to id a django user in the anon case
                if anon_auth:
                    raise User.DoesNotExist()
                if api_settings.FIREBASE_UNIQUE_EMAIL:
                    user = User.objects.get(email=fb_user.email)
                else:
                    # get the lastest user using the email (assuming has the larger PK)
                    user = User.objects.last(email=fb_user.email)
                setattr(user, uid_field, uid)
                user.save()
            except User.DoesNotExist:
                # User absolutely doesn't exist - create atomically
                user = self._create(User, uid, uid_field, fb_user)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.AuthenticationFailed(msg)

        return user

    @transaction.atomic
    def _create(self, User, uid, uid_field, fb_user):
        """Create user atomically"""
        fields = {
            uid_field: uid,
            'email': fb_user.email or ''
        }
        (user, created) = User.objects.select_for_update().get_or_create(**fields)
        if created:
            user.is_active = True
            user.save()
        return user


class FirebaseAuthentication(BaseFirebaseAuthentication):
    """
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    """
    www_authenticate_realm = 'api'

    def get_token(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = api_settings.FIREBASE_AUTH_HEADER_PREFIX.lower()

        if not auth:
            return None

        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        if smart_text(auth[0].lower()) != auth_header_prefix:
            return None

        return auth[1]

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        auth_header_prefix = api_settings.FIREBASE_AUTH_HEADER_PREFIX.lower()
        return '{0} realm="{1}"'.format(auth_header_prefix, self.www_authenticate_realm)
