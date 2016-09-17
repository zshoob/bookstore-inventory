# -*- coding: utf-8 -*-
from django.shortcuts import render
from django import http
import json
from .main.models import EbayListing, Book
import re

def home(request):
    return render(request, "app/index.html", {})

def home_files(request, filename):
    return render(request, filename, {}, content_type="text/plain")

def scrape(request, listing_id):
    assert int(listing_id)
    listing = EbayListing.scrape(listing_id)
    response = http.HttpResponse(listing.title, content_type='application/json')
    return response

def books(request):
    return render(request, "app/books.html", {'books': Book.objects.all()})
