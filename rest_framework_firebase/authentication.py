import firebase_admin
from firebase_admin import credentials
from rest_framework_firebase.settings import api_settings
from django.utils.encoding import smart_text
from rest_framework import exceptions
from firebase_admin import auth
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model


from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header
)

# TODO: Support entering the keys individually later
cred = credentials.Certificate(api_settings.FIREBASE_ACCOUNT_KEY_FILE)
firebase = firebase_admin.initialize_app(cred)

class BaseFirebaseuthentication(BaseAuthentication):
    """
    Token based authentication using firebase.
    """

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

        user = self.authenticate_credentials(payload)

        return (user, payload)

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        User = get_user_model()
        uid_field = api_settings.FIREBASE_UID_FIELD
        uid = payload['uid']
        if not uid:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(**{uid_field: uid})
        except User.DoesNotExist:
            if not api_settings.FIREBASE_CREATE_NEW_USER:
                msg = _('Invalid signature.')
                raise exceptions.AuthenticationFailed(msg)

            # Make a new user here!
            user = auth.get_user(uid)
            # TODO: This assumes emails are unique. Factor this out as an option
            try:
                user = User.objects.get(email=user.email)
                setattr(user, uid_field, uid)
                user.save()
            except User.DoesNotExist:
                fields = {
                    uid_field : uid,
                    'email':user.email
                }
                u = User(**fields)
                u.save()
                return u

        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.AuthenticationFailed(msg)

        return user


class Firebaseuthentication(BaseFirebaseuthentication):
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
