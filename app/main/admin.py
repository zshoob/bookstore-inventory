# -*- coding: utf-8 -*-
from django.contrib import admin
from . import models

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = ("username", "interaction")

    search_fields = ["user__username"]

# @admin.register(models.Book)
# class Book(admin.ModelAdmin):
#
#     list_display = ("isbn", "title", 'authors_string')
#
#     search_fields = ["authors__last_name", "authors__first_name"]

@admin.register(models.Author)
class Author(admin.ModelAdmin):
    list_display = ("first_name", "last_name")

    search_fields = ("first_name", "last_name")

@admin.register(models.EbayListing)
class EbayListing(admin.ModelAdmin):
    list_display = ("listing_id", "title", "authors")

    def update(self, obj):
        models.EbayListing.scrape(obj.listing_id)

# @admin.register(models.AmazonProduct)
# class AmazonProduct(admin.ModelAdmin):
#     list_display = ("asin", "title")
