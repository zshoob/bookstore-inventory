# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-29 21:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20161029_2025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amazonproductcategory',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
