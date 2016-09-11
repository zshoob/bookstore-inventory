# -*- coding: utf-8 -*-
from django.test import TestCase

from django.contrib.auth import get_user_model
from . import models
from .scrapers.ebay import EbayScraper

class TestProfileModel(TestCase):
    def test_profile_creation(self):
        User = get_user_model()
        # New user created
        user = User.objects.create(
            username="taskbuster", password="django-tutorial")
        # Check that a Profile instance has been crated
        self.assertIsInstance(user.profile, models.Profile)
        # Call the save method of the user to activate the signal
        # again, and check that it doesn't try to create another
        # profile instace
        user.save()
        self.assertIsInstance(user.profile, models.Profile)

# class TestBookModel(TestCase):
#     def test_book_creation(self):
#         author = models.Author(first_name='Isaac', last_name='Asimov')
#         author.save()
#         book = models.Book(
#             isbn=9780553293357,
#             title='Foundation',
#             author=author
#         )
#         book.save()
#         self.assertIsInstance(book.author, models.Author)
#         self.assertIsInstance(author.books.first(), models.Book)
#         self.assertEqual(book.author.name, 'Asimov, Isaac')

class TestEbayScraper(TestCase):
    def test_listing_creation(self):
        # ebay = EbayScraper()
        # data = ebay.scrape(311459830589)
        # self.assertTrue('Prices' in data)
        # price = data['Prices'][0]['price']
        # self.assertEqual(price, 19.61)
        listing = models.scrape_ebay(311459830589)
        self.assertEqual(listing.listing_id, 311459830589)
        update = models.scrape_ebay(311459830589)
        self.assertEqual(listing.listing_id, update.listing_id)
