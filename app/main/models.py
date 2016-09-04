# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings

from . import managers

# class Boiler(models.Model):
    # Relations
    # Attributes - Mandatory
    # Attributes - Optional
    # Object Manager
    # Custom Properties
    # Methods
    # Meta and String

class Profile(models.Model):
    # Relations
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile",
        verbose_name="user"
        )
    # Attributes - Mandatory
    interaction = models.PositiveIntegerField(
        default=0,
        verbose_name="interaction"
        )
    # Attributes - Optional
    # Object Manager
    objects = managers.ProfileManager()

    # Custom Properties
    @property
    def username(self):
        return self.user.username

    # Methods

    # Meta and String
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ("user",)

    def __str__(self):
        return self.user.username

class Book(models.Model):
    # Relations
    # Attributes - Mandatory
    isbn = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=100)

    # Attributes - Optional
    # Object Manager
    objects = managers.BookManager()
    # Custom Properties

    # Methods
    # Meta and String
    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ("title",)

    def __str__(self):
        return self.title

class Author(models.Model):
    # Relations
    book = models.ManyToManyField(
        Book,
        related_name="author",
        verbose_name="author"
    )

    # Attributes - Mandatory
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    # Attributes - Optional
    # Object Manager
    objects = managers.AuthorManager
    # Custom Properties
    @property
    def name(self):
        return '%s, %s' % (self.last_name, self.first_name)
    # Methods
    # Meta and String
    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"
        ordering = ("last_name",)

    def __str__(self):
        return self.name

from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, created, instance, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()
