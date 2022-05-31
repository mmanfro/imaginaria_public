from django.urls import path

from contest import views as v

app_name = "contest"
urlpatterns = [
    path("", v.index, name="index"),
    path("list/", v.contest_list, name="contest_list"),
    path("<int:contest_id>/", v.contest_view, name="contest_view"),
    path(
        "<int:contest_id>/participants/",
        v.participant_list,
        name="participant_list",
    ),
    path(
        "<int:contest_id>/participant/<int:participant_id>",
        v.participant_view,
        name="participant_view",
    ),
    path("vote/", v.vote, name="vote"),
]
