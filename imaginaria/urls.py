from django.views.i18n import JavaScriptCatalog
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path


from imaginaria import views as v

urlpatterns = [
    # path("", include("pwa.urls", namespace="pwa")),
]

urlpatterns += i18n_patterns(
    path(
        "jsi18n/",
        JavaScriptCatalog.as_view(),
        name="javascript-catalog",
    ),
    path("admin/", admin.site.urls),
    path("", v.index),
    path(
        "authentication/",
        include("authentication.urls", namespace="authentication"),
    ),
    path("contest/", include("contest.urls", namespace="contest")),
)


handler500 = "imaginaria.views.handler500"
handler404 = "imaginaria.views.handler404"
handler403 = "imaginaria.views.handler403"
handler400 = "imaginaria.views.handler400"
