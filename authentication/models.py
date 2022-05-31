from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _

from authentication.managers import UserManager


# Not using Django's own user class for 2 reasons:
# 1- I do not need a 'username'
# 2- I need the e-mail to be the auth token
# 3- Keeping it as simple as possible due to LGPD policy
class User(AbstractBaseUser, PermissionsMixin):
    email = models.CharField(
        _("e-mail"),
        primary_key=True,
        null=False,
        blank=False,
        unique=True,
        max_length=255,
    )
    date_joined = models.DateTimeField(
        _("date joined"), auto_now_add=True, editable=False
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether the user should be treated as active. Unselect this instead of deleting the account."
        ),
    )
    is_staff = models.BooleanField(
        _("staff"),
        default=False,
        help_text=_("Designates wheter the user has staff level access (admin panel)."),
    )
    date_last_forgotpassword_request = models.DateTimeField(
        _("última solicitação de redefinição de senha"), editable=False, null=True
    )
    date_last_activationemail_request = models.DateTimeField(
        _("última solicitação de e-mail de ativação"),
        editable=False,
        null=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def email_user(self, subject, from_email, html_message, **kwargs):
        send_mail(
            subject=subject,
            from_email=from_email,
            html_message=html_message,
            recipient_list=[self.email],
            message=None,
            **kwargs,
        )
