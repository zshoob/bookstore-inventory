# -*- coding: utf-8 -*-
import django
from django.db import models
from django.conf import settings
from django.db.models import Avg, Max, Min
import datetime
import dateutil
import main.common as cmn
import pandas as pd

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
        for a_dict in cmn.parse_authors(data.get('authors','')):
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

class AmazonProductCategory(models.Model):
    product_category_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    parent = models.BigIntegerField(null=True)

    @staticmethod
    def fetch(asin):
        from scrapers.amazon import ProductCategoriesForASIN
        loader = ProductCategoriesForASIN()
        data = loader.fetch(asin)
        for row in data:
            category = AmazonProductCategory(
                product_category_id = row.get('ProductCategoryId'),
                name = row.get('ProductCategoryName'),
                parent = row.get('Parent')
            )
            category.save()

    def inheritance_str(self):
        node = self
        s = self.name
        while True:
            try:
                node = AmazonProductCategory.objects.get(product_category_id=node.parent)
                if node.name == 'Subjects':
                    return s
                # s = '%s < %s' % (s, node.name)
                s = '%s > %s' % (node.name, s)
            except django.core.exceptions.ObjectDoesNotExist:
                return s

    def __str__(self):
        return self.inheritance_str()

class AmazonProduct(models.Model):
    # Relations
    author_set = models.ManyToManyField(Author, blank=True)
    # Attributes - Mandatory
    asin = models.CharField(primary_key=True, max_length=10)
    title = models.CharField(max_length=255)
    binding = models.CharField(max_length=100, null=True, blank=True)
    edition = models.CharField(max_length=100, null=True, blank=True)
    height = models.CharField(max_length=100, null=True, blank=True)
    width = models.CharField(max_length=100, null=True, blank=True)
    length = models.CharField(max_length=100, null=True, blank=True)
    weight = models.CharField(max_length=100, null=True, blank=True)
    pages = models.IntegerField(null=True, blank=True)
    published = models.DateField(null=True, blank=True)
    released = models.DateField(null=True, blank=True)
    image_source = models.CharField(max_length=100, null=True)

    @staticmethod
    def fetch(query):
        from scrapers.amazon import ProductFundamentals, ListMatchingProducts
        # asin = asin.strip().split('-')[-1]
        # if len(asin) == 13 and asin.startswith('978'):
        #     asin = asin[3:]
        asins = []
        results = ListMatchingProducts().fetch(query)
        for result in results:
            asin = result.get('asin')
            if asin:
                asins.append(asin)
            product = AmazonProduct(
                asin=result.get('asin'),
                title=result.get('title'),
                binding=result.get('binding'),
                edition=result.get('edition'),
                width=result.get('width'),
                height=result.get('height'),
                length=result.get('length'),
                pages=result.get('pages') or None,
                published=cmn.clean_date(result.get('published')),
                released=cmn.clean_date(result.get('released')),
                image_source=result.get('image_source')
            )
            product.save()
            for rank_item in result['sales_rank']:
                category_id = rank_item.get('ProductCategoryId')
                if category_id == 'Books':
                    category = AmazonProductCategory.objects.get_or_create(product_category_id=1, name='Books')[0]
                    category.save()
                    rank = AmazonSalesRank.objects.get_or_create(
                        product=product,
                        product_category=category,
                        date=cmn.today(),
                    )[0]
                    rank.rank = rank_item.get('Rank')
                    rank.save()
                    rank.save()
                # else:
                #     category_id = cmn.read_num(category_id)
                #     try:
                #         category = AmazonProductCategory.objects.get(product_category_id=category_id)
                #     except django.core.exceptions.ObjectDoesNotExist:
                #         AmazonProductCategory.fetch(asin)
                #         category = AmazonProductCategory.objects.get(product_category_id=category_id)
                # rank = AmazonSalesRank.objects.get_or_create(
                #     product=product,
                #     product_category=category,
                #     date=cmn.today(),
                # )[0]
                # rank.rank = rank_item.get('Rank')
                # rank.save()
                # rank.save()
            for author_str in result.get('authors'):
                author_dict = cmn.parse_authors(author_str)[0]
                author, _ = Author.objects.get_or_create(
                    first_name=author_dict['first'],
                    middle_name=author_dict['middle'],
                    last_name=author_dict['last']
                )
                product.author_set.add(author)
        if asins:
            AmazonOffer.fetch(asins[0])
        return asins


    def __str__(self):
        return self.title

    @property
    def authors(self):
        return ', '.join([a.name for a in self.author_set.all()])

    @property
    def sales_rankings(self):
        return [(r.rank, r.product_category.inheritance_str()) for r in AmazonSalesRank.objects.filter(product=self)]

    @property
    def rank(self):
        hist = AmazonSalesRank.objects.filter(product=self, product_category_id=1)
        if hist:
            return hist[0].rank
        return None

    @property
    def min_price(self):
        prices = AmazonOffer.objects.filter(product=self, used=True).aggregate(Min('price'))

    @property
    def camel_price(self):
        return "http://charts.camelcamelcamel.com/us/%s/used.png?force=1&zero=0&w=725&h=440&desired=false&legend=1&ilt=1&tp=all&fo=0&lang=en" % self.asin

    @property
    def camel_rank(self):

        import requests
        from lxml import html
        page = requests.get('https://secure.camelcamelcamel.com/login?return_to=http%3A%2F%2Fcamelcamelcamel%2Ecom%2F')
        doc = html.fromstring(page.text)
        form = doc.xpath(".//form[@id='loginform']")[0]
        page2 = requests.post(form.action, data={'login': 'schubert.zach@gmail.com', 'password':'VM7R2#b7$Ost'})
        return "http://charts.camelcamelcamel.com/us/%s/sales-rank.png?force=1&zero=0&w=725&h=440&desired=false&legend=1&ilt=1&tp=all&fo=0&lang=en" % self.asin

    class Meta:
        verbose_name = "Amazon Product"
        verbose_name_plural = "Amazon Products"
        ordering = ("title", )

class AmazonSalesRank(models.Model):
    product = models.ForeignKey(AmazonProduct, on_delete=models.CASCADE)
    product_category = models.ForeignKey(AmazonProductCategory, on_delete=models.CASCADE)
    date = models.DateField()
    rank = models.IntegerField(null=True)

    def inheritance_str(self):
        return self.product_category.inheritance_str()

    class Meta:
        unique_together = ('product', 'product_category', 'date')
        verbose_name = "Sales Rank"
        verbose_name_plural = "Sales Rankings"
        ordering = ('-date',)

class AmazonPrice(models.Model):
    # Relations
    product = models.ForeignKey(AmazonProduct, on_delete=models.CASCADE)
    # Attributes - Mandatory
    kind = models.CharField(max_length=10)
    price = models.FloatField()
    date = models.DateField()
    # Attributes - Optional
    # Object Manager
    # Custom Properties
    # Methods
    # Meta and String
    def __str__(self):
        return "$%f.2" % price

class AmazonOffer(models.Model):
    product = models.ForeignKey(AmazonProduct, on_delete=models.CASCADE)
    price = models.FloatField()
    shipping = models.FloatField()
    used = models.BooleanField()
    condition = models.CharField(max_length=10)
    is_fba = models.BooleanField()
    is_featured_merchant = models.BooleanField()
    seller_rating = models.IntegerField()
    feedback_count = models.IntegerField()
    date = models.DateField()
    list_display = ('condition', 'price', 'shipping', 'is_fba', 'seller_rating', 'feedback_count')

    @staticmethod
    def fetch(asin):
        from scrapers.amazon import LowestPricedOffers
        loader = LowestPricedOffers()
        data = loader.fetch(asin)
        product = AmazonProduct.objects.get(asin=asin)
        for row in data['offers']:
            offer = AmazonOffer.objects.get_or_create(
                product=product,
                price=cmn.read_num(row['Price']),
                shipping=cmn.read_num(row['ShippingPrice']),
                used=row['SubCondition'] == 'used',
                condition=row['SubCondition'],
                is_fba=row['IsFulfilledByAmazon'].lower() == 'true',
                is_featured_merchant=row['IsFeaturedMerchant'].lower() == 'true',
                seller_rating=cmn.read_num(row['SellerFeedbackRating']),
                feedback_count=cmn.read_num(row['FeedbackCount']),
                date=cmn.today()
            )[0]
            offer.save()

    class Meta:
        ordering = ('used','condition','price','shipping',)

class AmazonOfferPivot(models.Model):
    product = models.ForeignKey(AmazonProduct, on_delete=models.CASCADE)
    new = models.FloatField(null=True, blank=True)
    like_new = models.FloatField(null=True, blank=True)
    very_good = models.FloatField(null=True, blank=True)
    good = models.FloatField(null=True, blank=True)
    acceptable = models.FloatField(null=True, blank=True)
    date = models.DateField()

    @staticmethod
    def update(asin):
        from django_pandas.io import read_frame
        import numpy as np
        qs = AmazonOffer.objects.filter(product_id=asin, date=cmn.today())
        df = read_frame(qs)[['price','condition']]
        df['price_rank'] = df.groupby('condition').rank(method='dense')['price']
        df = df.drop_duplicates()
        piv = df.pivot(index='price_rank', columns='condition')['price'].fillna(0)
        for row in piv.to_dict(orient='records'):
            offer = AmazonOfferPivot.objects.get_or_create(
                new=row.get('new') or None,
                like_new=row.get('like new') or None,
                very_good=row.get('very good') or None,
                good = row.get('good') or None,
                acceptable = row.get('acceptable') or None,
                product_id = asin,
                date = cmn.today()
            )[0]
            offer.save()


# class AmazonOffer(models.Model):
    # Relations


    # Attributes - Mandatory
    # Attributes - Optional
    # Object Manager
    # Custom Properties
    # Methods
    # Meta and String

from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, created, instance, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()


if __name__ == '__main__':
    AmazonProductCategory.fetch('0553293354')
