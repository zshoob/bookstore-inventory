# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-18 19:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_auto_20160918_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebaylisting',
            name='img_src',
            field=models.CharField(max_length=100, null=True),
        ),
    ]