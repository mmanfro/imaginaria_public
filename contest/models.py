from authentication.models import User
from django.db.models import Q
from django.db import models
from django.db.models.signals import pre_save
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class Contest(models.Model):
    name = models.CharField(
        _("name"), null=False, blank=False, unique=True, max_length=255
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
    )
    start_date = models.DateTimeField(_("início"), default=now)
    end_date = models.DateTimeField(
        _("término"),
    )
    judges = models.ManyToManyField(
        User, blank=True, verbose_name="jurados", related_name="judges"
    )
    judge_vote_weight = models.IntegerField(
        _("peso do voto dos jurados"),
        help_text=_(
            'Exemplo: se especificado "3" e o jurado votar "5", o voto será computado como 15.'
        ),
        null=False,
        blank=False,
        validators=[MinValueValidator(1)],
        default=1,
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        null=False,
        editable=False,
    )
    created_date = models.DateTimeField(_("created date"), auto_now_add=True)

    class Meta:
        verbose_name = _("concurso")
        verbose_name_plural = _("concursos")

    def __str__(self):
        return self.name


class Participant(models.Model):
    name = models.CharField(_("nome"), null=False, blank=False, max_length=255)
    work = models.CharField(_("trabalho"), null=False, blank=False, max_length=255)
    description = models.TextField(_("descrição"), null=True, blank=True)
    video_url = models.URLField(_("URL do vídeo"), null=False, blank=False)
    contest = models.ForeignKey(
        Contest,
        verbose_name="concurso",
        on_delete=models.CASCADE,
        null=False,
        limit_choices_to=Q(is_active=True) & Q(end_date__gt=now()),
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        null=False,
        editable=False,
    )
    created_date = models.DateTimeField(_("created date"), auto_now_add=True)

    class Meta:
        verbose_name = _("participante")
        verbose_name_plural = _("participantes")
        unique_together = ("name", "contest")

    def __str__(self):
        return self.name


class Vote(models.Model):
    vote = models.IntegerField(validators=[MinValueValidator(1)], default=0)
    registered_by = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        null=False,
    )
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        null=False,
    )
    created_date = models.DateTimeField(
        _("created date"), auto_now_add=True, editable=False
    )

    class Meta:
        verbose_name = _("voto")
        verbose_name_plural = _("votos")
        unique_together = ("registered_by", "participant")


def check_vote(sender, instance, *args, **kwargs):
    vote = int(instance.vote)
    if vote > 5:
        raise ValueError(_("O voto máximo é 5"))

    if (
        instance.participant.contest.start_date >= now()
        or instance.participant.contest.end_date <= now()
    ):
        raise ValueError(_("Só é possível votar em concursos em andamento"))


def check_dates(sender, instance, *args, **kwargs):
    if instance.start_date > instance.end_date:
        raise ValueError(_("Data de término deve ser maior que a data de início."))


pre_save.connect(check_vote, sender=Vote)
pre_save.connect(check_dates, sender=Contest)
