# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-11 20:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_remove_ebaylisting_author'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ebayprice',
            old_name='listing_id',
            new_name='listing',
        ),
    ]
