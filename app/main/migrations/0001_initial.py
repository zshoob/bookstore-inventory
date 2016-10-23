# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-23 20:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AmazonPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(max_length=10)),
                ('price', models.FloatField()),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='AmazonProduct',
            fields=[
                ('asin', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('binding', models.CharField(blank=True, max_length=100, null=True)),
                ('edition', models.CharField(blank=True, max_length=100, null=True)),
                ('height', models.CharField(blank=True, max_length=100, null=True)),
                ('width', models.CharField(blank=True, max_length=100, null=True)),
                ('length', models.CharField(blank=True, max_length=100, null=True)),
                ('weight', models.CharField(blank=True, max_length=100, null=True)),
                ('pages', models.IntegerField(blank=True, null=True)),
                ('published', models.DateField(blank=True, null=True)),
                ('released', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'Amazon Product',
                'verbose_name_plural': 'Amazon Products',
            },
        ),
        migrations.CreateModel(
            name='AmazonSalesRank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_id', models.IntegerField(null=True)),
                ('rank', models.IntegerField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.AmazonProduct')),
            ],
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
                ('middle_name', models.CharField(blank=True, default=b'', max_length=20)),
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
                ('authors', models.ManyToManyField(blank=True, to='main.Author')),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'Book',
                'verbose_name_plural': 'Books',
            },
        ),
        migrations.CreateModel(
            name='EbayListing',
            fields=[
                ('listing_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=100)),
                ('condition', models.CharField(blank=True, max_length=1000, null=True)),
                ('book_format', models.CharField(blank=True, max_length=100, null=True)),
                ('publication_date', models.DateField(blank=True, null=True)),
                ('language', models.CharField(blank=True, max_length=20, null=True)),
                ('synopsis', models.CharField(blank=True, max_length=5000, null=True)),
                ('image_source', models.CharField(max_length=100, null=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Book')),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'Ebay Listing',
                'verbose_name_plural': 'Ebay Listings',
            },
        ),
        migrations.CreateModel(
            name='EbayPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('price', models.FloatField()),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.EbayListing')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interaction', models.PositiveIntegerField(default=0, verbose_name=b'interaction')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name=b'user')),
            ],
            options={
                'ordering': ('user',),
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
            },
        ),
        migrations.AlterUniqueTogether(
            name='author',
            unique_together=set([('first_name', 'last_name')]),
        ),
        migrations.AddField(
            model_name='amazonproduct',
            name='authors',
            field=models.ManyToManyField(blank=True, to='main.Author'),
        ),
        migrations.AddField(
            model_name='amazonprice',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.AmazonProduct'),
        ),
    ]
