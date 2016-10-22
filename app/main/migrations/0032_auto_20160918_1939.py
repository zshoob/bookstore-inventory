# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-18 19:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_auto_20160918_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ebaylisting',
            name='book_format',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='ebaylisting',
            name='condition',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='ebaylisting',
            name='language',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='ebaylisting',
            name='synopsis',
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
    ]
