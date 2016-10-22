# # -*- coding: utf-8 -*-
# from django.shortcuts import render
# from django import http
# import json
# from main import models
# import re
# import sys
#
#
# def home(request):
#     return render(request, "app/index.html", {})
#
# def home_files(request, filename):
#     return render(request, filename, {}, content_type="text/plain")
#
# def scrape(request, listing_id):
#     assert int(listing_id)
#     listing = EbayListing.scrape(listing_id)
#     response = http.HttpResponse(listing.title, content_type='application/json')
#     return response
#
# def registerModel(model):
#     meta = model._meta
#     def make_view(view):
#         def wrapped(request):
#             return render(request, "app/%s.html" % meta.verbose_name_plural, {'data': model.objects.all(), 'list_display': view.list_display })
#         return wrapped
#     return make_view
#
# # def books(request):
# #     return render(request, "app/books.html", {'data': Book.objects.all()})
#
# @registerModel(models.Book)
# class Books:
#     list_display = ("isbn", "title", 'authors_string')
