from django.contrib.auth.backends import ModelBackend

from simpleoncall.models import User


def find_users(username, with_valid_password=True):
    """
    Return a list of users that match a username
    and falling back to email
    """
    qs = User.objects
    if with_valid_password:
        qs = qs.exclude(password='!')

    try:
        # First, assume username is an iexact match for username
        user = qs.get(username__iexact=username)
        return [user]
    except User.DoesNotExist:
        # If not, we can take a stab at guessing it's an email address
        if '@' in username:
            # email isn't guaranteed unique
            return list(qs.filter(email__iexact=username))
    return None


class EmailAuthBackend(ModelBackend):
    """
    Authenticate against django.contrib.auth.models.User.
    Supports authenticating via an email address or a username.
    """
    def authenticate(self, username=None, password=None):
        users = find_users(username)
        if users:
            for user in users:
                try:
                    if user.password and user.check_password(password):
                        return user
                except ValueError:
                    continue
        return None
