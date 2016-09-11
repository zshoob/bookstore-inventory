# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-04 03:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
            ],
            options={
                'ordering': ('last_name',),
                'verbose_name': 'Author',
                'verbose_name_plural': 'Authors',
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('isbn', models.BigIntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'Book',
                'verbose_name_plural': 'Books',
            },
        ),
        migrations.AddField(
            model_name='author',
            name='book',
            field=models.ManyToManyField(related_name='author', to='main.Book', verbose_name=b'author'),
        ),
    ]