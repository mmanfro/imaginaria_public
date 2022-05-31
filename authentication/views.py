import re
from datetime import timedelta
from time import sleep

from django.contrib import messages
from django.contrib.auth import authenticate, get_user, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from authentication.forms import UserForgotPasswordForm, UserRegisterForm
from authentication.models import User
from authentication.tokens import register_email_token


def login_view(request):
    context = {}

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            return redirect("/")
        else:
            messages.error(request, _("Usuário e senha incorretos"))

    return render(request, "authentication/login.html", context)


def logout_view(request):
    logout(request)

    return redirect("/")


def register_user(request):
    context = {}

    form = UserRegisterForm()
    context["form"] = form

    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        email = form["email"].value()

        # Validates if there's already a user with the specified e-mail
        # If the user already exists AND has never logged in AND is not active AND was created MORE than X hours ago,
        #   deletes the existing user, allowing the creation of a user with the specified e-mail
        # If the user already exists AND has never logged in AND is not active AND was created LESS than X hours ago,
        #   shows a 'try again' message with the remaining time to complete the X hours so the current user can create a new account with the specified e-mail
        try:
            user = User.objects.get(email=email)

            date_difference = (now() - user.date_joined).total_seconds()

            # X # 1440 minutes = 24 hours; 720 minutes = 12 hours
            minutes_remaining = 720 - int(str(date_difference / 60).split(".")[0])

            if not user.last_login and not user.is_active:

                if minutes_remaining <= 0:
                    user.delete()
                else:
                    context["try_again"] = True
                    try_again_time = (
                        minutes_remaining // 60
                        if minutes_remaining // 60 > 0
                        else minutes_remaining
                    )
                    try_again_time_type = (
                        "horas" if minutes_remaining // 60 > 0 else "minutos"
                    )
                    context["failed"] = True
                    context["try_again_time"] = try_again_time
                    context["try_again_time_type"] = try_again_time_type
        except:
            pass

        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            send_activation_email(request, user)

            context["success"] = True

            messages.success(request, _("Conta criada com sucesso"))
        else:
            context["form"] = form

    return render(request, "authentication/register/form.html", context)


def send_activation_email(request, user):
    if user is not None:
        current_site = get_current_site(request)
        html_message = render_to_string(
            "authentication/register/email.html",
            {
                "user": user,
                "domain": current_site.domain,
                "user_id_b64": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": register_email_token.make_token(user),
            },
        )
        user.email_user(
            subject="Ative sua conta do Festival Imaginária",
            from_email="info@festivalimaginaria.com.br",
            html_message=html_message,
        )


def resend_activation_email(request):
    context = {}
    regex = re.compile(r"^[\w\-\.]+@([\w\-]+\.)+[\w\-]{2,4}$")

    if "email" in request.POST and re.fullmatch(regex, request.POST.get("email")):

        try:
            user = User.objects.get(pk=request.POST.get("email"), is_active=False)
            if (now() - user.date_joined > timedelta(hours=0, minutes=30)) and (
                not user.date_last_activationemail_request
                or now() - user.date_last_activationemail_request
                > timedelta(hours=0, minutes=30)
            ):
                send_activation_email(request, user)
                user.date_last_activationemail_request = now()
                user.save()

                messages.success(request, _("E-mail de ativação enviado"))
            else:
                date_difference = (
                    now() - user.date_last_activationemail_request
                ).total_seconds()
                minutes_remaining = 30 - int(str(date_difference / 60).split(".")[0])

                messages.error(
                    request,
                    _(
                        f"Necessário aguardar {minutes_remaining} minutos para solicitar novo e-mail de ativação"
                    ),
                )
                sleep(1)
        except User.DoesNotExist:
            messages.error(request, _("Usuário não existe ou já está ativo"))
            sleep(1)
    else:
        messages.error(request, _("E-mail inválido"))
        sleep(1)

    return render(request, "authentication/login.html", context)


def activate_user(request, user_id_b64, token):
    context = {}

    try:
        user_id = force_str(urlsafe_base64_decode(user_id_b64))
        user = User.objects.get(pk=user_id, is_active=False)

        if register_email_token.check_token(user, token):
            user.is_active = True
            user.save()

            messages.success(
                request, _("Conta ativada com sucesso, você pode fazer login agora")
            )
        else:
            messages.error(
                request, _("Token inválido, solicite um novo link de ativação")
            )
    except User.DoesNotExist:
        messages.info(request, _("Usuário já está ativo"))

    return render(request, "authentication/login.html", context)


def send_forgot_password_mail(request):
    context = {}

    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST.get("email"))
        except:
            user = None

        if user is not None and user.is_active:
            if (
                not user.date_last_forgotpassword_request
                or now() - user.date_last_forgotpassword_request
                > timedelta(hours=0, minutes=30)
            ):
                current_site = get_current_site(request)
                html_message = render_to_string(
                    "authentication/forgotpassword/email.html",
                    {
                        "user": user,
                        "domain": current_site.domain,
                        "user_id_b64": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": default_token_generator.make_token(user),
                    },
                )

                user.date_last_forgotpassword_request = now()
                user.save()

                user.email_user(
                    subject="Esqueci minha senha - Festival Imaginária",
                    from_email="info@festivalimaginaria.com.br",
                    html_message=html_message,
                )

                context["POST"] = True
            else:
                date_difference = (
                    now() - user.date_last_forgotpassword_request
                ).total_seconds()

                minutes_remaining = 30 - int(str(date_difference / 60).split(".")[0])

                messages.error(
                    request,
                    _(
                        f"Necessário aguardar {minutes_remaining} minutos para solicitar nova senha"
                    ),
                )
        else:
            messages.error(request, _("E-mail não encontrado"))

    return render(request, "authentication/forgotpassword/request.html", context)


def forgot_password_form(request, user_id_b64, token):
    context = {}

    # Pass the <user_id> and <token> parameters back to the template
    #   to be used again if the the form is saved (method == 'POST')
    context["user_id_b64"] = user_id_b64
    context["token"] = token

    try:
        user_id = force_str(urlsafe_base64_decode(user_id_b64))
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = UserForgotPasswordForm(request.POST)

            if form.is_valid():
                user = form.save(user, commit=False)
                user.save()

                messages.success(
                    request,
                    _(
                        "Senha alterada com sucesso. Você pode fazer login com a nova senha"
                    ),
                )

                return render(request, "authentication/login.html", context)
            else:
                context["form"] = form

                return render(
                    request, "authentication/forgotpassword/form.html", context
                )
        else:
            if default_token_generator.check_token(user, token):
                form = UserForgotPasswordForm(instance=user)
                context["form"] = form

                return render(
                    request, "authentication/forgotpassword/form.html", context
                )
    else:
        messages.error(
            request, _("O link que você tentou acessar expirou ou é inválido")
        )

        return render(request, "authentication/login.html", context)
