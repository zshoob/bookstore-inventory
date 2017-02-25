
# coding: utf-8

# In[95]:

import requests
from lxml import html
import re
from scraper import read_num, report
import time
import pandas as pd

base_url = 'http://www.bookdepot.com'

def scrape_all(book_limit=None, pause=1, sort='relevant', ascending=False):
    assert sort in ['relevant', 'title', 'author', 'publisher', 'price', 'arrival']
    page_itr = book_itr = 0
    finished = False
    while not finished:
        page_itr += 1
        browse_page = get_nth_browse_page(page_itr)
        if pause:
            time.sleep(pause)
        isbns = read_browse_page_isbns(browse_page)
        finished = not isbns
        for isbn in read_browse_page_isbns(browse_page):
            book_itr += 1
            data = scrape_book(isbn)
            if data:
                report('%i %s' % (book_itr, data['title']))
                yield data                
            if book_itr == book_limit:
                finished = True
                break
            time.sleep(pause)

def request_nth_browse_page(n, sort='relevance', ascending=False):
    url = '%s/Store/Browse?page=%s&size=96&sort=%s_%i' % (base_url, n, sort, int(ascending))
    return requests.get(url)

def get_nth_browse_page(n, sort='relevance', ascending=False):
    response = request_nth_browse_page(n, sort=sort, ascending=ascending)
    return html.fromstring(response.text)
    
def read_browse_page_isbns(browse_page):
    links = browse_page.xpath('.//div[@class="grid-item"]/div[@class="grid-image"]/a')
    isbns = []
    for link in links:
        href = link.attrib['href']
        isbns.append(re.search('\d{10,13}', href).group(0))
    return isbns

def scrape_book(isbn):
    book_page = get_book_page(isbn)
    if book_is_unavailable(book_page):
        return None
    data = {}
    data['title'] = read_title(book_page)
    data['binding'] = read_binding(book_page)
    isbn_10, isbn_13 = read_isbns(book_page)
    data['isbn_10'] = isbn_10
    data['isbn_13'] = isbn_13
    data['book_depot_list_price'] = read_list_price(book_page)
    data['book_depot_our_price'] = read_book_depot_price(book_page)
    return data
    
def request_book_page(isbn):
    url = '%s/Store/Details/%sB' % (base_url, isbn)
    return requests.get(url)

def get_book_page(isbn):
    return html.fromstring(request_book_page(isbn).text)

def book_is_unavailable(book_page):
    return 'Sorry, this book is not available.' in book_page.text_content()

def read_title(book_page):
    title = book_page.xpath('.//h2[@itemprop="name"]')[0]
    return title.text_content()

def read_isbns(book_page):
    isbns = book_page.xpath('.//span[@itemprop="isbn"]')
    isbn_10 = isbn_13 = ''
    for isbn in isbns:
        isbn = isbn.text
        if len(isbn) == 13:
            isbn_13 = isbn
        elif len(isbn) == 10:
            isbn_10 = isbn
    return isbn_10, isbn_13

def read_binding(book_page):
    binding = book_page.xpath('.//span[@itemprop="bookFormat"]')[0]
    return binding.text_content()

def read_dt(page, search_text):
    try:
        dt = next(dt for dt in page.xpath('.//dt') if search_text in dt.text)
        dd = dt.getnext()
        return dd.text_content()
    except StopIteration:
        return ''
    
def read_list_price(book_page):
    return read_num(read_dt(book_page, 'List Price'))

def read_book_depot_price(book_page):
    return read_num(read_dt(book_page, 'Our Price'))

