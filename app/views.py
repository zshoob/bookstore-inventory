# -*- coding: utf-8 -*-
import main.common as cmn
from django.shortcuts import render
from django import http, forms
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.conf.urls import url, include
import json
from main import models
import numpy as np
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
    template_name = 'app/new_amazon_detail.html'
    list_display = ('title','authors','binding','edition','pages','published','released')

    def get_context_data(self, **kwargs):
        context = super(AmazonProductDetail, self).get_context_data(**kwargs)
        context.update({
            'sales_rankings': self.model.sales_rankings
        })
        return context

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
            asins = models.AmazonProduct.fetch(term)
            if asins:
                if len(asins) == 1:
                    return http.HttpResponseRedirect('/amazonproducts/%s' % asins[0])
                asins = ["asin%i=%s" % (ix, asin) for ix, asin in enumerate(asins)]
                return http.HttpResponseRedirect('/amazonproducts/?%s' % '&'.join(asins))
            return http.HttpResponseRedirect('/amazonproducts/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SearchForm()

    return render(request, 'app/search.html', {'form': form})

class XAmazonOfferList(ListView, BookStoreViewMixin):
    # model = models.AmazonOffer
    # queryset = models.AmazonOffer.objects.filter(product_id=)
    template_name = "generic_list.html"
    list_display = ('condition', 'price', 'shipping', 'is_fba', 'seller_rating', 'feedback_count')
    table_name = "Offers"

    def get_queryset(self):
        pid = self.request.GET.get('product_id')
        if pid:
            return models.AmazonOffer.objects.filter(product_id=pid)
        return models.AmazonOffer.objects.all()


class ProfitCalculatorForm(forms.Form):
    asin = forms.CharField(initial='', widget=forms.HiddenInput())
    price = forms.FloatField(label='', initial=10.00)

def calculate_profits(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProfitCalculatorForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            price = form.cleaned_data['price']
            data = form.cleaned_data
            pd = request.POST
            asin = request.POST.get('asin')
            # asin = models.AmazonProduct.fetch(term)
            from main.scrapers.amazon import GetMyFeesEstimate
            amount = GetMyFeesEstimate().fetch(asin, float(price))
            profit = price - (amount + 2.09)
            return render(request, 'app/profitcalculator.html', {'form': form, 'price': price, 'asin': asin, 'profit': profit})
            # return http.HttpResponseRedirect('/amazonproducts/%s' % asin)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProfitCalculatorForm(request.GET)

    price = request.GET.get('price')
    asin = request.GET.get('asin')
    return render(request, 'app/profitcalculator.html', {'form': form, 'price': price, 'asin': asin})


class NewAmazonProductDetail(DetailView):
    model = models.AmazonProduct
    template_name = 'app/new_amazon_detail.html'
    list_display = ('title','authors','binding','edition','pages','published')
    calculator_form = ProfitCalculatorForm()

    def fees(self):
        try:
            return self.foo
        except Exception as e:
            return str(e)

    def header(self):
        obj = self.get_object()
        h = "%s by %s" % (obj.title, obj.authors)
        if obj.edition or obj.binding:
            h += ', %s' % ' '.join([obj.edition, obj.binding])
        return h

    def rank(self):
        r = self.get_object().rank
        return "{:,.0f}".format(r) if r else '--'

    def offer_headers(self):
        return models.AmazonOffer.list_display

    def offers(self):
        return models.AmazonOffer.objects.filter(product=self.get_object())

    def offers_pivot(self):
        from django_pandas.io import read_frame
        qs = models.AmazonOffer.objects.filter(product=self.get_object())
        df = read_frame(qs)[['condition','is_fba','price','date']]
        # columns = ['new fba', 'new fbm', 'like new fba', 'like new fbm', 'very good fba', 'very good fbm', 'good fba', 'good fbm', 'acceptable fba', 'acceptable fbm']
        columns = ['acceptable fba', 'acceptable fbm', 'good fba', 'good fbm', 'very good fba', 'very good fbm', 'like new fba', 'like new fbm', 'new fba', 'new fbm']
        if df.empty:
            data = []
            as_of = '--'
        else:
            df['is_fba'] = df.is_fba.map(lambda s: 'fba' if s else 'fbm')
            as_of = df.date.max()
            df = df[df.date == as_of].drop('date', axis=1)
            df['price'] = df.price.astype(np.float)
            df['price_rank'] = df.groupby(['condition','is_fba']).rank(method='first')
            piv = df.set_index(['price_rank','condition','is_fba']).unstack(['condition','is_fba'])['price']
            # conditions = ['new','like new','very good','good','acceptable']
            conditions = ['acceptable', 'good', 'very good', 'like new', 'new']
            channels = ['fba','fbm']
            piv.columns = [' '.join(levels) for levels in piv.columns.values]
            for cond in conditions:
                for chan in channels:
                    col = '%s %s' % (cond, chan)
                    if col not in piv:
                        piv[col] = np.nan
            piv = piv[columns].applymap(cmn.money_f)
            data = piv.as_matrix()
        return {'headers': columns, 'data': data, 'as_of': as_of}

    def min_price(self):
        offers = self.offers()
        if not offers:
            return '--'
        return "${:,.2f}".format(min([o.price for o in offers]))

    def meta(self):
        return self.model._meta



import django_tables2 as tables

class AmazonOffersList(tables.Table):
    class Meta:
        model = models.AmazonOffer

class AmazonOffersPivot(tables.Table):
    class Meta:
        model = models.AmazonOfferPivot
        fields = ['new', 'like_new', 'very_good', 'good', 'acceptable']

def offers_list(request):
    pid = request.GET.get('product_id')
    if pid:
        queryset = models.AmazonOfferPivot.objects.filter(product_id=pid)
    else:
        queryset = models.AmazonOfferPivot.objects.all()
    # queryset = models.AmazonSalesRank.objects.all()
    table = AmazonOffersPivot(queryset)
    tables.RequestConfig(request, paginate=False).configure(table)
    return render(request, 'simple_list.html', {'table': table, 'verbose_name': table.Meta.model._meta.verbose_name_plural})


class AmazonSalesRankList(tables.Table):
    class Meta:
        model = models.AmazonSalesRank
        fields = ('rank', 'product_category',)

def sales_rank_list(request):
    pid = request.GET.get('product_id')
    if pid:
        queryset = models.AmazonSalesRank.objects.filter(product_id=pid)
    else:
        queryset = models.AmazonSalesRank.objects.all()
    table = AmazonSalesRankList(queryset)
    tables.RequestConfig(request, paginate=False).configure(table)
    return render(request, 'simple_list.html', {'table': table, 'verbose_name': table.Meta.model._meta.verbose_name_plural})

class NewAmazonProductList(tables.Table):
    asin = tables.TemplateColumn('<a href="/amazonproducts/{{record.asin}}">{{record.asin}}</a>')
    class Meta:
        model = models.AmazonProduct
        fields = ('asin','title','authors','binding',)


def amazon_products(request):
    asins = [request.GET.get('asin%i' % i) for i in range(100) if request.GET.get('asin%i' % i)]
    if asins:
        queryset = models.AmazonProduct.objects.filter(pk__in=asins)
    else:
        queryset = models.AmazonProduct.objects.all()
    table = NewAmazonProductList(queryset)
    tables.RequestConfig(request, paginate=False).configure(table)
    return render(request, 'list2.html', {'table': table, 'verbose_name': table.Meta.model._meta.verbose_name_plural})
