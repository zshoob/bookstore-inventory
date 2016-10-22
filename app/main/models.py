# -*- coding: utf-8 -*-
import django
from django.db import models
from django.conf import settings
import datetime
import dateutil
import common as cmn

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
    middle_name = models.CharField(max_length=20, default='', blank=True)

    # Object Manager
    objects = managers.AuthorManager

    # Custom Properties

    @property
    def books(self):
        return self.book_set

    @property
    def name(self):
        middle = ' %s' % self.middle_name if self.middle_name else ''
        return '%s%s %s' % (self.first_name, middle, self.last_name)

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
        unique_together = (('first_name','last_name'))

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
    def authors_display(self):
        return ', '.join([a.name for a in self.authors.all()])


    # Methods

    # Meta and String
    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ("title",)

    def __str__(self):
        return self.title.encode('ascii', 'ignore')

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
    condition = models.CharField(max_length=1000, blank=True, null=True)
    book_format = models.CharField(max_length=100, blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    language = models.CharField(max_length=20, blank=True, null=True)
    synopsis = models.CharField(max_length=5000, blank=True, null=True)
    image_source = models.CharField(max_length=100, null=True)

    # Attributes - Optional
    # Object Manager
    objects = managers.EbayListingManager()

    # Custom Properties
    @property
    def url(self):
        return 'http://www.ebay.com/itm/%i' % self.listing_id

    @property
    def authors(self):
        return ', '.join([a.name for a in self.book.authors.all()])

    @staticmethod
    def scrape(listing_id):
        data = EbayScraper().scrape(listing_id)
        book = Book.objects.get_or_create(isbn=data['isbn'])[0]
        book.title = book.title or data.get('title')
        book.save()
        for a_dict in parse_authors(data.get('authors','')):
            author = Author.objects.get_or_create(**a_dict)[0]
            author.save()
            book.authors.add(author)
        listing = EbayListing(
            book=book,
            listing_id=listing_id,
            title=data.get('title', ''),
            condition=data.get('condition'),
            book_format=data.get('format'),
            publication_date=cmn.clean_date(data.get('publication date')),
            language=data.get('language'),
            synopsis=data.get('synopsis'),
            image_source=data.get('image_source')
        )
        listing.save()
        current_price = EbayPrice(listing=listing, price=data['price'])
        current_price.save()
        return listing

    # Methods
    # Meta and String
    class Meta:
        verbose_name = "Ebay Listing"
        verbose_name_plural = "Ebay Listings"
        ordering = ("title",)

    def __str__(self):
        return self.title.encode('ascii', 'ignore')

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
