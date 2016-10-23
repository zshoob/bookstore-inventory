# -*- coding: utf-8 -*-
from django.shortcuts import render
from django import http, forms
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.conf.urls import url, include
import json
from main import models
import re
import sys


def home(request):
    return render(request, "app/index.html", {})

def home_files(request, filename):
    return render(request, filename, {}, content_type="text/plain")

def scrape(request, listing_id):
    assert int(listing_id)
    listing = models.EbayListing.scrape(listing_id)
    response = http.HttpResponse(listing.title, content_type='application/json')
    return response


class ModelView:
    def __init__(self, model):
        self.model = model
        self.meta = model._meta
        self.singular_name = self.meta.object_name.lower().replace(' ','')
        self.plural_name = self.meta.verbose_name_plural.lower().replace(' ','')

    def plural_view(self):
        def view(request):
            return render(request, "app/%s.html" % self.plural_name, {
                'meta': self.meta,
                'data': self.model.objects.all(),
                'list_display': self.plural_display_columns,
            })
        return view

    def singular_view(self):
        def view(request, pk):
            return render(request, "app/%s.html" % (self.singular_name), {
                'meta': self.meta,
                'data': self.model.objects.filter(pk=pk),
                'list_display': self.singular_display_columns,
            })
        return view

def register_model(model):
    def make_view(options):
        view = ModelView(model)
        view.plural_display_columns = options.plural_display_columns
        view.singular_display_columns = options.singular_display_columns
        return view
    return make_view

@register_model(models.Book)
class Book:
    plural_display_columns = ('title', 'authors_display')
    singular_display_columns = ('title',)

# @register_model(models.EbayListing)
# class EbayListing:
#     plural_display_columns = ('book','title','authors')
#     singular_display_columns = ('title','authors','condition','book_format','publication_date','language','synopsis')

urlpatterns = []

class BookStoreViewMixin:
    def get_path_from_name(self, name):
        return re.sub('[\s\_]+','',name).lower()

    def get_bookstore_context(self):
        context = {
            'list_display': self.list_display,
            'pk_name': self.model._meta.pk.name,
            'detail_name': self.model._meta.verbose_name,
            'list_name': self.model._meta.verbose_name_plural,
            'detail_path': self.get_path_from_name(self.model._meta.verbose_name),
            'list_path': self.get_path_from_name(self.model._meta.verbose_name_plural),
        }
        if hasattr(self, 'tools'):
            context['tools'] = self.tools

        return context

class BookStoreDetailView(DetailView):
    def get_context_data(self, **kwargs):
        context = super(BookStoreDetailView, self).get_context_data(**kwargs)
        context['pk'] = self.model._meta.pk
        context.update(self.get_bookstore_context())
        return context

class BookStoreListView(ListView):
    template_name = 'list.html'
    def get_context_data(self, **kwargs):
        context = super(BookStoreListView, self).get_context_data(**kwargs)
        context['detail_name'] = self.model._meta.verbose_name.lower().replace(' ','')
        context.update(self.get_bookstore_context())
        return context

class EbayListingDetail(BookStoreDetailView, BookStoreViewMixin):
    model = models.EbayListing
    template_name = 'app/ebay_detail.html'
    list_display = ('title','authors','condition','synopsis','book_format')
    tools = {
        'update': scrape
    }

    def scrape(self, listing_id):
        data = models.EbayListing.scrape(listing_id)


class EbayListingList(BookStoreListView, BookStoreViewMixin):
    model = models.EbayListing
    list_display = ('title','authors','condition')

class AmazonProductList(BookStoreListView, BookStoreViewMixin):
    model = models.AmazonProduct
    list_display = ('title','authors','binding')


def fetch_from_amazon(request, asin):
    models.AmazonProduct.fetch(asin)
    return http.HttpResponseRedirect('/amazonproducts/%s' % asin)

class SearchForm(forms.Form):
    term = forms.CharField(label='Search', initial='', max_length=100)

class AmazonProductDetail(BookStoreDetailView, BookStoreViewMixin):
    model = models.AmazonProduct
    template_name = 'app/amazon_detail.html'
    list_display = ('title','authors','binding','edition','pages','published','released')


def search_amazon(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            term = form.cleaned_data['term']
            asin = models.AmazonProduct.fetch(term)
            return http.HttpResponseRedirect('/amazonproducts/%s' % asin)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SearchForm()

    return render(request, 'app/search.html', {'form': form})
