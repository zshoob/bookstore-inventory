# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-12 03:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_auto_20160912_0222'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebaylisting',
            name='authors',
            field=models.ManyToManyField(blank=True, to='main.Author'),
        ),
    ]
