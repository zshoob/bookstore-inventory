# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-18 15:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_auto_20160918_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ebaylisting',
            name='book_format',
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]