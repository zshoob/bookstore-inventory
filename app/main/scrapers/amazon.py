
# coding: utf-8

# In[212]:

import requests
from urllib import urlencode
from datetime import datetime
import hashlib
import hmac
import base64
import pytz
import xmltodict
import pandas as pd
from main.common import *
import numpy as np
from numpy import atleast_1d
import collections

def traverse(xml, path, default=''):
    for node in path.split('/'):
        try:
            node = int(node)
        except ValueError:
            pass
        try:
            xml = xml[node]
        except (KeyError, TypeError):
            return default
    return xml

class AmazonEndpoint:
    api = 'Products'
    universal_params = {
        'AWSAccessKeyId': 'AKIAIR3XDAZOXFNE2WMA',
        'SellerId': 'A2QZBXE6ZQI12C',
        'MarketplaceId': 'ATVPDKIKX0DER',
        'Version': '2011-10-01',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
    }
    secret_key = bytes('zvqE0L6YkYfE1kpcaD6OIIDaX9Ttc1awIUrv7yoM').encode('utf-8')

    def get_params(self, *args):
        raise Exception

    def read(self, response):
        raise Exception

    def get(self, *args):
        params = self.get_params(*args)
        params['Timestamp'] = datetime.isoformat(datetime.now(pytz.timezone('US/Eastern')))
        params_str = '&'.join([urlencode({k:params[k]}) for k in sorted(params)])
        request = 'POST\nmws.amazonservices.com\n/%s/\n%s' % (self.api, params_str)
        message = bytes(request).encode('utf-8')
        params['Signature'] = base64.b64encode(hmac.new(self.secret_key, message, digestmod=hashlib.sha256).digest())
        response = requests.post('https://mws.amazonservices.com/%s/' % self.api, data=params)
        return response

    def fetch(self, *args):
        return self.read(self.get(*args))

class ProductFundamentals(AmazonEndpoint):
    action = 'GetMatchingProductForId'

    def get_params(self, isbns):
        params = self.universal_params.copy()
        params['Action'] = self.action
        params['IdType'] = 'ASIN'
        for ix, isbn in enumerate(atleast_1d(isbns)):
            params['IdList.Id.%s' % str(ix+1)] = isbn
        return params

    def read_product(self, product):
        asin = traverse(product, 'Identifiers/MarketplaceASIN/ASIN')
        attributes = traverse(product, 'AttributeSets/ns2:ItemAttributes')
        authors = atleast_1d(traverse(attributes, 'ns2:Author'))
        height, length, width, weight = [traverse(attributes, 'ns2:ItemDimensions/ns2:%s' % key) for key in ['Height','Length','Width','Weight']]
        height, length, width, weight = ['%s %s' % (traverse(dim,'#text'), traverse(dim,'@Units')) if dim else '' for dim in [height, length, width, weight]]
        languages = atleast_1d(traverse(attributes, 'ns2:Languages/ns2:Language'))
        language = [l['ns2:Name'] for l in languages if traverse(l,'ns2:Type') == 'Published']
        if language:
            language = language[0]
        list_price = traverse(attributes, 'ns2:ListPrice/ns2:Amount')
        flats = ['ns2:NumberOfPages', 'ns2:PublicationDate', 'ns2:Publisher', 'ns2:ReleaseDate', 'ns2:Title', 'ns2:Binding', 'ns2:Edition']
        pages, published, publisher, released, title, binding, edition = [traverse(attributes, path) for path in flats]
        sales_rank = traverse(product, 'SalesRankings/SalesRank')
        if sales_rank:
            sales_rank = atleast_1d(sales_rank)
        else:
            sales_rank = []
        for ix in range(len(sales_rank)):
            if sales_rank[ix].get('ProductCategoryId') == 'book_display_on_website':
                sales_rank[ix]['ProductCategoryId'] = 'Books'            
        image_source = traverse(attributes, 'ns2:SmallImage/ns2:URL')
        resized = re.sub('\._.*\.jpg','._SX331_BO1,204,203,200_.jpg',image_source)
        data = dict(
            asin=asin,
            authors=authors,
            height=height,
            length=length,
            width=width,
            weight=weight,
            language=language,
            list_price=list_price,
            pages=pages,
            published=published,
            released=released,
            publisher=publisher,
            title=title,
            binding=binding,
            edition=edition,
            sales_rank=sales_rank,
            image_source=resized
        )
        return data

    def read(self, response, raw=False):
        xml = xmltodict.parse(response.text)
        xml = traverse(xml, '%sResponse/%sResult' % (self.action, self.action))
        status = traverse(xml, '@status')
        error = traverse(xml, 'Error/Message')
        if error:
            return [dict(last_status=status, error=error)]
        if raw:
            return atleast_1d(traverse(xml, 'Products/Product'))
        return [self.read_product(product) for product in atleast_1d(traverse(xml, 'Products/Product'))]

class LowestPricedOffers(AmazonEndpoint):
    def get_params(self, asin, condition):
        params = self.universal_params.copy()
        params['Action'] = 'GetLowestPricedOffersForASIN'
        params['ASIN'] = asin
        params['ItemCondition'] = condition
        return params

    def read_offer(self, xml):
        offer = xml.copy()
        if 'ShipsFromCountry' in offer.keys(): # already flattened
            offer['ShipsFromCountry'] = offer['ShipsFromCountry'] or ''
            return offer

        offer['SubCondition'] = re.sub('_',' ', traverse(offer, 'SubCondition'))
        feedback = offer.pop('SellerFeedbackRating')
        offer['SellerFeedbackRating'] = feedback[u'SellerPositiveFeedbackRating']
        offer['FeedbackCount'] = feedback['FeedbackCount']
        price = offer.pop('ListingPrice')
        offer['Price'] = price['Amount']
        shipping_price = offer.pop('Shipping')
        offer['ShippingPrice'] = shipping_price['Amount']
        shipping_time = offer.pop('ShippingTime')
        offer['ShippingMinimumHours'] = shipping_time['@minimumHours']
        offer['ShippingMaximumHours'] = shipping_time['@maximumHours']
        offer['ShippingAvailability'] = shipping_time['@availabilityType']
        ships_from = offer.pop('ShipsFrom', {})
        offer['ShipsFromCountry'] = traverse(ships_from, 'Country') or ''
        offer['ShipsFromState'] = traverse(ships_from, 'State')

        return offer

    def read_summary(self, xml):
        summary = traverse(xml, 'Summary') or xml
        list_price = traverse(summary, 'ListPrice/Amount')
        total_offer_count = traverse(summary, 'TotalOfferCount')

        number_of_offers = traverse(summary, 'NumberOfOffers/OfferCount', [])
        if number_of_offers:
            number_of_offers = pd.DataFrame(number_of_offers, index=range(len(number_of_offers)))
            number_of_offers.rename(columns={
                '#text': 'NumberOfOffers',
                '@condition': 'Condition',
                '@fulfillmentChannel': 'FulfillmentChannel'
            }, inplace=True)
            number_of_offers = number_of_offers.to_dict(orient='records')

        lowest_prices = traverse(summary, 'LowestPrices/LowestPrice', [])
        if lowest_prices:
            if isinstance(lowest_prices, collections.OrderedDict):
                lowest_prices = [lowest_prices]
            lowest_prices = pd.DataFrame(lowest_prices, index=range(len(lowest_prices)))
            lowest_prices.rename(columns={
                '@condition': 'Condition',
                '@fulfillmentChannel': 'FulfillmentChannel'
            }, inplace=True)
            lowest_prices[['LandedPrice','ListingPrice','Shipping']] = lowest_prices[['LandedPrice','ListingPrice','Shipping']].applymap(lambda d: d['Amount'])
            lowest_prices = lowest_prices.to_dict(orient='records')

        buybox_prices = traverse(summary, 'BuyBoxPrices/BuyBoxPrice', [])
        if buybox_prices:
            if isinstance(buybox_prices, collections.OrderedDict):
                buybox_prices = [buybox_prices]
            buybox_prices = pd.DataFrame(buybox_prices, index=range(len(buybox_prices)))
            buybox_prices.rename(columns={'@condition':'Condition'}, inplace=True)
            try:
                buybox_prices = buybox_prices.ix['Amount']
                buybox_prices = [buybox_prices.to_dict()]
            except KeyError: # more annoying JSON variation
                buybox_prices[['LandedPrice','ListingPrice','Shipping']] = buybox_prices[['LandedPrice','ListingPrice','Shipping']].applymap(lambda d: d['Amount'])
                buybox_prices = buybox_prices.to_dict(orient='records')
                
        buybox_eligible_offers = traverse(summary, 'BuyBoxEligibleOffers/OfferCount', [])
        if buybox_eligible_offers:
            if isinstance(buybox_eligible_offers, collections.OrderedDict):
                buybox_eligible_offers = [buybox_eligible_offers]
            buybox_eligible_offers = pd.DataFrame(buybox_eligible_offers, index=range(len(buybox_eligible_offers)))
            buybox_eligible_offers.rename(columns={
                '#text': 'NumberOfOffers',
                '@condition': 'Condition',
                '@fulfillmentChannel': 'FulfillmentChannel'
            }, inplace=True)
            buybox_eligible_offers = buybox_eligible_offers.to_dict(orient='records')
                
        data = dict(
            list_price=list_price,
            total_offer_count=total_offer_count,
            number_of_offers=number_of_offers,
            lowest_prices=lowest_prices,
            buybox_prices=buybox_prices,
            buybox_eligible_offers=buybox_eligible_offers
        )

        return data
    
    def read(self, response, raw=False):
        xml = xmltodict.parse(response.text)
        xml = traverse(xml, 'GetLowestPricedOffersForASINResponse/GetLowestPricedOffersForASINResult')
        offers = traverse(xml, 'Offers/Offer', [])
        if not raw:
            offers = [self.read_offer(o) for o in offers]
        summary = traverse(xml, 'Summary')
        if not raw:
            summary = self.read_summary(summary)
        return dict(offers=offers, summary=summary)

    def fetch(self, asin):
        data = self.read(self.get(asin, 'used'))
        new = self.read(self.get(asin, 'new'))
        data['offers'].extend(new['offers'])
        return data
    
class ProductCategoriesForASIN(AmazonEndpoint):
    def get_params(self, asin):
        params = self.universal_params.copy()
        params['Action'] = 'GetProductCategoriesForASIN'
        params['ASIN'] = asin
        return params
    
    def read(self, response):
        xml = xmltodict.parse(response.text)
        categories = []
        lists = atleast_1d(traverse(xml, 'GetProductCategoriesForASINResponse/GetProductCategoriesForASINResult/Self'))
        for prev in lists:    
            node = traverse(prev, 'Parent')
            while node:
                prev['Parent'] = node['ProductCategoryId']
                categories.append(prev)
                prev = node
                node = traverse(node, 'Parent')
            prev['Parent'] = None
            categories.append(prev)
        return categories

class ListMatchingProducts(ProductFundamentals):
    action = 'ListMatchingProducts'
    def get_params(self, query):
        params = self.universal_params.copy()
        params['Action'] = 'ListMatchingProducts'
        params['QueryContextId'] = 'Books'
        params['Query'] = query
        return params
    
class GetMyFeesEstimate(AmazonEndpoint):
    def get_params(self, asin, price):
        params = self.universal_params.copy()
        params.pop('MarketplaceId')
        params.update({
            'Action': 'GetMyFeesEstimate',
            'FeesEstimateRequestList.FeesEstimateRequest.1.MarketplaceId': 'ATVPDKIKX0DER',
            'FeesEstimateRequestList.FeesEstimateRequest.1.IdType': 'ASIN',
            'FeesEstimateRequestList.FeesEstimateRequest.1.IdValue': asin,
            'FeesEstimateRequestList.FeesEstimateRequest.1.IsAmazonFulfilled': 'false',
            'FeesEstimateRequestList.FeesEstimateRequest.1.Identifier': 'request1',
            'FeesEstimateRequestList.FeesEstimateRequest.1.PriceToEstimateFees.ListingPrice.CurrencyCode': 'USD',
            'FeesEstimateRequestList.FeesEstimateRequest.1.PriceToEstimateFees.ListingPrice.Amount': price,
            'FeesEstimateRequestList.FeesEstimateRequest.1.PriceToEstimateFees.Shipping.CurrencyCode': 'USD',
            'FeesEstimateRequestList.FeesEstimateRequest.1.PriceToEstimateFees.Shipping.Amount': '0.00',
            'FeesEstimateRequestList.FeesEstimateRequest.1.PriceToEstimateFees.Points.PointsNumber': '0',
        })
        return params    
    
    def read(self, response):
        xml = xmltodict.parse(response.text)
        node = traverse(xml, 'GetMyFeesEstimateResponse/GetMyFeesEstimateResult/FeesEstimateResultList/FeesEstimateResult')
        amount = read_num(traverse(node, 'FeesEstimate/TotalFeesEstimate/Amount'))
        return amount
    
clrs = '0262033844'
three_body = '0765382032'
gott = '1594634025'
foundation = '0553293354'
chomsky = '0375714499'
pearls = '0201657880'

