from django.urls import path

from .views import manifest, service_worker, offline


app_name = "pwa"
urlpatterns = [
    path("serviceworker.js", service_worker, name="serviceworker"),
    path("manifest.json", manifest, name="manifest"),
    path("offline", offline, name="offline"),
]
