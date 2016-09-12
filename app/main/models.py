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
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)

    # Attributes - Optional
    middle_name = models.CharField(max_length=20, null=True, blank=True)

    # Object Manager
    objects = managers.AuthorManager

    # Custom Properties

    @property
    def books(self):
        return self.book_set

    @property
    def name(self):
        middle = ' %s' % self.middle_name if self.middle_name else ''
        return '%s%s %s' % (self.first_name, self.middle_name, self.last_name)

    @property
    def search_name(self):
        middle = ' %s' % self.middle_name if self.middle_name else ''
        return '%s, %s%s' % (self.last_name, self.first_name, middle)

    # Methods

    # Meta and String
    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"
        ordering = ("last_name",)

    def __str__(self):
        return self.name

class Book(models.Model):
    # Relations
    authors = models.ManyToManyField(Author, blank=True)
    # Attributes - Mandatory
    isbn = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=100)

    # Attributes - Optional

    # Object Manager
    objects = managers.BookManager()

    # Custom Properties
    @property
    def authors_string(self):
        return ', '.join(self.authors.all())


    # Methods

    # Meta and String
    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ("title",)

    def __str__(self):
        return self.title

def parse_authors(s):
    from nameparser.parser import HumanName
    names = [HumanName(n) for n in s.split(',')]
    # format must be Stein, Clifford
    if len(names) == 2 and not names[0].last:
        names = HumanName(s)
    return [dict(first_name=name.first, middle_name=name.middle, last_name=name.last) for name in names]

class EbayListing(models.Model):
    # Relations
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    # Attributes - Mandatory
    listing_id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=100, blank=True)

    # Attributes - Optional
    # Object Manager
    objects = managers.EbayListingManager()

    # Custom Properties
    @property
    def url(self):
        return 'http://www.ebay.com/itm/%i' % self.listing_id

    @staticmethod
    def scrape(listing_id):
        data = EbayScraper().scrape(listing_id)
        book = Book(
            isbn=data['isbn']
        )
        book.save()
        for a_dict in parse_authors(data['authors']):
            author = Author(**a_dict)
            author.save()
            book.authors.add(author)
        listing = EbayListing(
            book=book,
            listing_id=listing_id,
            title=data.get('title', '')
        )
        listing.save()
        current_price = EbayPrice(listing=listing, price=data['price'])
        current_price.save()
        return listing

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


from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, created, instance, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()
