from django.contrib.auth.backends import ModelBackend

from authentication.models import User


class UserBackend(ModelBackend):

    def authenticate(self, request, **kwargs):
        
        # In Django admin page the form field is 'username'
        # In my login form, the field is 'email'
        email = kwargs['email'] if 'email' in kwargs else kwargs['username']

        password = kwargs['password']

        try:
            user = User.objects.get(email=email)
            if user.check_password(password) and user.is_active:
                return user
        except User.DoesNotExist:
            return None
