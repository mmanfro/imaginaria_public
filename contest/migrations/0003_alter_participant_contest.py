# Generated by Django 4.0.4 on 2022-04-20 18:12

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0002_alter_participant_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='contest',
            field=models.ForeignKey(limit_choices_to=models.Q(('is_active', True), ('end_date__gt', datetime.datetime(2022, 4, 20, 18, 12, 20, 102842, tzinfo=utc))), on_delete=django.db.models.deletion.CASCADE, to='contest.contest', verbose_name='concurso'),
        ),
    ]
