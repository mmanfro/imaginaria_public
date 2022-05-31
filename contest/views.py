import time

from authentication.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import (
    F,
    Prefetch,
    Q,
    Sum,
    ExpressionWrapper,
    IntegerField,
    Case,
    When,
)
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from contest.models import Contest, Participant, Vote


def index(request):
    context = {}

    present_contests = Contest.objects.filter(
        start_date__lt=now(), end_date__gt=now(), is_active=True
    ).prefetch_related(
        Prefetch(
            "participant_set",
            queryset=Participant.objects.annotate(
                rating_sum=Coalesce(Sum("vote__vote"), 0)
            ),
        )
    )
    context["present_contests"] = present_contests

    future_contests = Contest.objects.filter(start_date__gt=now(), is_active=True)
    context["future_contests"] = future_contests

    past_contests = Contest.objects.filter(
        end_date__lt=now(), is_active=True
    ).prefetch_related(
        Prefetch(
            "participant_set",
            queryset=Participant.objects.annotate(
                rating_sum=Coalesce(Sum("vote__vote"), 0)
            ),
        )
    )
    context["past_contests"] = past_contests

    return render(request, "contest/index.html", context=context)


@login_required
def contest_list(request):
    context = {}

    contests = Contest.objects.filter(
        start_date__lt=now(), end_date__gt=now(), is_active=True
    )
    context["contests"] = contests

    participants = (
        Participant.objects.filter(contest__in=contests)
        .annotate(rating_sum=Coalesce(Sum("vote__vote"), 0))
        .order_by("-rating_sum")
    )[:9]

    context["participants"] = participants

    return render(request, "contest/contest/list.html", context=context)


def contest_view(request, contest_id):
    context = {}

    contest = Contest.objects.filter(pk=contest_id)[0]
    context["contest"] = contest

    participants = (
        Participant.objects.filter(contest=contest)
        .annotate(rating_sum=Coalesce(Sum("vote__vote"), 0))
        .order_by("-rating_sum")
    )
    context["participants"] = participants

    return render(request, "contest/contest/view.html", context=context)


def participant_list(request, contest_id):
    context = {}

    page = request.GET.get("page", 1)

    user = None
    if request.user.is_authenticated:
        user = request.user

    contest = Contest.objects.get(pk=contest_id)
    context["contest"] = contest

    participants = (
        Participant.objects.filter(contest=contest)
        .annotate(
            rating=Coalesce(
                Sum(
                    Case(
                        When(
                            Q(vote__registered_by__in=F("contest__judges")),
                            then=F("vote__vote") * F("contest__judge_vote_weight"),
                        ),
                        default=F("vote__vote"),
                        output_field=IntegerField(),
                    )
                ),
                0,
            )
        )
        .prefetch_related(
            Prefetch("vote_set", queryset=Vote.objects.filter(registered_by=user))
        )
        .order_by("name")
    )

    print(participants)

    if "search" in request.GET:
        participants = participants.filter(
            Q(name__icontains=request.GET.get("search"))
            | Q(work__icontains=request.GET.get("search"))
        )
        context["search"] = request.GET.get("search")

    context["pagination"] = request.GET.get("pagination", 6)
    participants = Paginator(participants, context["pagination"])
    participants_page = participants.page(page)
    context["participants"] = participants_page

    context["ongoing"] = (
        contest.start_date <= now() and contest.end_date >= now() and contest.is_active
    )

    return render(request, "contest/participant/list.html", context=context)


def participant_view(request, contest_id, participant_id):
    context = {}

    user = request.user if request.user.is_authenticated else None

    participant = (
        Participant.objects.annotate(
            rating=Coalesce(
                Sum(
                    Case(
                        When(
                            Q(vote__registered_by__in=F("contest__judges")),
                            then=F("vote__vote") * F("contest__judge_vote_weight"),
                        ),
                        default=F("vote__vote"),
                        output_field=IntegerField(),
                    )
                ),
                0,
            )
        )
        .prefetch_related(
            Prefetch(
                "contest",
                queryset=Contest.objects.filter(id=contest_id),
            ),
        )
        .prefetch_related(
            Prefetch("vote_set", queryset=Vote.objects.filter(registered_by=user))
        )
        .get(pk=participant_id)
    )

    context["participant"] = participant
    context["pagination"] = "1"
    context["ongoing"] = (
        participant.contest.start_date <= now()
        and participant.contest.end_date >= now()
        and participant.contest.is_active
    )

    return render(request, "contest/participant/view.html", context=context)


@login_required
def vote(request):
    context = {}

    vote, created = Vote.objects.update_or_create(
        registered_by=request.user,
        participant_id=request.POST.get("participant_id"),
        defaults={"vote": request.POST.get("vote")},
    )

    participant = (
        Participant.objects.annotate(
            rating=Coalesce(
                Sum(
                    Case(
                        When(
                            Q(vote__registered_by__in=F("contest__judges")),
                            then=F("vote__vote") * F("contest__judge_vote_weight"),
                        ),
                        default=F("vote__vote"),
                        output_field=IntegerField(),
                    )
                ),
                0,
            )
        )
        .prefetch_related(
            Prefetch(
                "vote_set",
                queryset=Vote.objects.filter(
                    registered_by=request.user,
                    participant__id=request.POST.get("participant_id"),
                ),
            )
        )
        .get(pk=request.POST.get("participant_id"))
    )
    context["participant"] = participant

    context["ongoing"] = (
        participant.contest.start_date <= now()
        and participant.contest.end_date >= now()
        and participant.contest.is_active
    )

    time.sleep(1)

    return render(request, "contest/participant/_participant.html", context)
