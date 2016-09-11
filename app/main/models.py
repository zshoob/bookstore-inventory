# -*- coding: utf-8 -*-
import django
from django.db import models
from django.conf import settings
import datetime

from . import managers
from .scrapers.ebay import EbayScraper

# class BoilerPlate(models.Model):
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

class Author(models.Model):
    # Relations

    # Attributes - Mandatory
    name = models.CharField(max_length=40)

    # Attributes - Optional
    # Object Manager
    objects = managers.AuthorManager

    # Custom Properties

    @property
    def books(self):
        return self.book_set

    # Methods

    # Meta and String
    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"
        # ordering = ("last_name",)

    def __str__(self):
        return self.name

class Book(models.Model):
    # Relations
    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
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

class EbayListing(models.Model):
    # Relations
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    # Attributes - Mandatory
    listing_id = models.BigIntegerField(primary_key=True)

    # Attributes - Optional
    # Object Manager
    objects = managers.EbayListingManager()

    # Custom Properties
    @property
    def url(self):
        return 'http://www.ebay.com/itm/%i' % self.listing_id

    # Methods
    # Meta and String

class EbayPrice(models.Model):
    # Relations
    listing = models.ForeignKey(EbayListing, on_delete=models.CASCADE)
    # Attributes - Mandatory
    date = models.DateField(default=django.utils.timezone.now)
    price = models.FloatField()
    # Attributes - Optional

    # Object Manager

    # Custom Properties

    # Methods

    # Meta and String
    def __str__(self):
        return "$%f.2" % price

def scrape_ebay(listing_id):
    data = EbayScraper().scrape(listing_id)
    author = Author(name=data['Overview']['author'])
    author.save()
    book = Book(
        isbn=data['Overview']['isbn'],
        author=author
    )
    book.save()
    listing = EbayListing(
        book=book,
        listing_id=listing_id
    )
    listing.save()
    for p in data['Prices']:
        price = EbayPrice(listing=listing, price=p['price'])
        price.save()
    return listing

from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, created, instance, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()
