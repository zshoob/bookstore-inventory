
# coding: utf-8

# In[14]:

from scraper import read_num, report
from amazon import LowestPricedOffers, ProductFundamentals, traverse
import book_depot
import dataset
import pandas as pd


amazon_fundamentals = ProductFundamentals()
amazon_offers = LowestPricedOffers()

def scrape(book_limit=None, pause=1, sort='relevant', ascending=False, to_csv=''):
    db = dataset.connect('sqlite:///:memory:')
    table = db['data']
    book_depot_data = book_depot.scrape_all(book_limit=book_limit, pause=pause, sort=sort, ascending=ascending)
    for itr, row in enumerate(book_depot_data):
        row['error'] = None
        try:
            isbn_10 = row['isbn_10']
            row.update(fetch_amazon_data(isbn_10))
        except Exception as e:
            row['error'] = str(e)
        table.insert(row)
        if to_csv and itr % 1000 == 0:
            df = pd.DataFrame(list(table.all())).set_index('id')
            df.to_csv(to_csv)        
    df = pd.DataFrame(list(table.all())).set_index('id')
    if to_csv:
        df.to_csv(to_csv)
    return df

def fetch_amazon_data(isbn_10):
    data = {}
    data['amazon_sales_rank'] = fetch_amazon_sales_rank(isbn_10)
    best_offer, condition, is_fba = fetch_best_amazon_offer(isbn_10)
    data['amazon_best_offer'] = best_offer
    data['amazon_best_offer_condition'] = condition
    data['amazon_best_offer_is_fba'] = is_fba
    return data

def fetch_amazon_sales_rank(isbn_10):
    if not isbn_10:
        return None
    fundamentals = amazon_fundamentals.fetch(isbn_10)
    fundamentals[0]['sales_rank']
    sales_rank = traverse(fundamentals, '0/sales_rank/0/Rank')
    return read_num(sales_rank)

def fetch_best_amazon_offer(isbn_10):
    if not isbn_10:
        return None, None, None
    offers = amazon_offers.fetch(isbn_10)['offers']
    for is_fba in [True, False]:
        for condition in ['like new', 'very good', 'good', 'acceptable']:
            offer = best_offer_for_criteria(offers, condition, is_fba)
            if offer:
                return offer, condition, is_fba
    return None, None, None

def best_offer_for_criteria(all_offers, condition, is_fba):
    fba_str = 'true' if is_fba else 'false'
    matching_offers = [read_num(o['Price']) for o in all_offers if o['SubCondition']==condition and o['IsFulfilledByAmazon']==fba_str]
    if matching_offers:
        return min(matching_offers)
    return 0

if __name__ == '__main__':
    scrape(to_csv='book_depot_vs_amazon.csv')

