from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.timezone import now


# Token for the e-mail activation
class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(now)
        )

register_email_token = TokenGenerator()
