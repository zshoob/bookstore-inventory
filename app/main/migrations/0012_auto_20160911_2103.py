# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-11 21:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20160911_2001'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='author',
            options={'ordering': ('last_name',), 'verbose_name': 'Author', 'verbose_name_plural': 'Authors'},
        ),
        migrations.RemoveField(
            model_name='author',
            name='name',
        ),
        migrations.RemoveField(
            model_name='book',
            name='author',
        ),
        migrations.AddField(
            model_name='author',
            name='first_name',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='author',
            name='last_name',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='author',
            name='middle_name',
            field=models.CharField(default=b'', max_length=20),
        ),
        migrations.AddField(
            model_name='book',
            name='authors',
            field=models.ManyToManyField(to='main.Author'),
        ),
    ]
