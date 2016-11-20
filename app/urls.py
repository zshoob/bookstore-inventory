"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.contrib import admin
import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),
    url(r'^(?P<filename>(robots.txt)|(humans.txt))$',
            views.home_files, name='home-files'),
    url(r'^scrape/.*(?P<listing_id>\d{12})', views.scrape, name='scrape'),
    url(r'^books/', views.Book.plural_view(), name='books'),
    url(r'^book/(?P<pk>\d+)', views.Book.singular_view(), name='book'),
    url(r'^ebaylistings/(?P<pk>\d+)', views.EbayListingDetail.as_view(), name='ebay-listing'),
    url(r'^ebaylistings/', views.EbayListingList.as_view(), name='ebay-listings'),
    # url(r'^amazonproducts/fetch/(?P<asin>\w+)', views.fetch_from_amazon),
    url(r'^amazonproducts/(?P<pk>\w+)', views.NewAmazonProductDetail.as_view(), name='amazon-product'),
    url(r'^amazonproducts/', views.amazon_products, name='amazon-products'),
    url(r'^amazonoffers/', views.offers_list, name='amazon-offers'),
    url(r'^salesranks/', views.sales_rank_list, name='sales-ranks'),
    url(r'^accounts/', include('allauth.urls')),
    url('search/', views.search_amazon, name='search'),
    url('profitcalculator/', views.calculate_profits, name='profitcalculator'),
]
