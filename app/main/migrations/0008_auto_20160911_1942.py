# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-11 19:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_ebayprice'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ebaylisting',
            old_name='key',
            new_name='listing_id',
        ),
        migrations.RenameField(
            model_name='ebayprice',
            old_name='listing',
            new_name='listing_id',
        ),
    ]
