from django.urls import path

from authentication import views as v

app_name = "authentication"
urlpatterns = [
    path("login/", v.login_view, name="login"),
    path("logout/", v.logout_view, name="logout"),
    path("register/", v.register_user, name="register_user"),
    path(
        "activate/<str:user_id_b64>/<str:token>/", v.activate_user, name="activate_user"
    ),
    path(
        "resend_activation_email/",
        v.resend_activation_email,
        name="resend_activation_email",
    ),
    path(
        "forgot-password/",
        v.send_forgot_password_mail,
        name="send_forgot_password_mail",
    ),
    path(
        "forgot-password/<user_id_b64>/<token>/",
        v.forgot_password_form,
        name="forgot_password_form",
    ),
]
