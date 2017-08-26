# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-23 08:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tpa', '0002_mychoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='year_in_school',
            field=models.CharField(choices=[('FR', 'Freshman'), ('SO', 'Sophomore'), ('JR', 'Junior'), ('SR', 'Senior')], default='FR', max_length=2),
        ),
    ]
