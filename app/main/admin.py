# -*- coding: utf-8 -*-
from django.contrib import admin
from . import models


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = ("username", "interaction")

    search_fields = ["user__username"]

@admin.register(models.Book)
class Book(admin.ModelAdmin):
    list_display = ("isbn", "title", "authors_string")

    search_fields = ["book__authors"]
