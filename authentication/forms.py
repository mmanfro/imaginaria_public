from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UsernameField
from django.utils.translation import gettext_lazy as _

from .models import User


class UserRegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")
        field_classes = {"email": UsernameField}

    error_messages = {
        "password_mismatch": _("As senhas digitadas não são iguais."),
        "email_domain_invalid": _("O domínio do e-mail não é aceito."),
    }

    email = forms.EmailField(
        label=_(""),
        widget=forms.EmailInput(
            attrs={
                "class": "input",
                "autocomplete": "off",
                "placeholder": _("E-mail"),
                "maxlength": "64",
                "required": "required",
            }
        ),
    )

    password1 = forms.CharField(
        label=_(""),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "input",
                "autocomplete": "new-password",
                "placeholder": _("Senha"),
                "required": "required",
            }
        ),
    )

    password2 = forms.CharField(
        label=_(""),
        widget=forms.PasswordInput(
            attrs={
                "class": "input",
                "autocomplete": "new-password",
                "placeholder": _("Repetir a senha"),
                "required": "required",
            }
        ),
        strip=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs[
                "autofocus"
            ] = True

    def clean_email(self):
        email = self.cleaned_data.get("email")

        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error("password2", error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserForgotPasswordForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("password1", "password2")

    error_messages = {
        "password_mismatch": _("As senhas digitadas não são iguais."),
    }

    password1 = forms.CharField(
        label=_(""),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "input",
                "autocomplete": "new-password",
                "placeholder": _("Senha"),
                "required": "required",
            }
        ),
    )

    password2 = forms.CharField(
        label=_(""),
        widget=forms.PasswordInput(
            attrs={
                "class": "input",
                "autocomplete": "new-password",
                "placeholder": _("Repetir a senha"),
                "required": "required",
            }
        ),
        strip=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error("password2", error)

    # Must pass the user to update the password to
    def save(self, user, commit=True):
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
