
# coding: utf-8

# In[192]:

from scraper import *
import itertools

class EbayScraper(Scraper):
    def __init__(self):
        super(EbayScraper, self).__init__()
        self.cache = {}

    def get(self, url, nocache=False):
        if isinstance(url, int) or re.match('\d{12}', url):
            url = 'http://www.ebay.com/itm/%s' % url
        cached = not nocache and self.cache.get(url)
        response = cached or requests.get(url)
        if not nocache:
            self.cache[url] = response
        return response

    def read(self, page, listing_id=None, verbose=0):
        listing_id = listing_id or int(re.search('itm[/=](\d+)',page.url).group(1))
        listing = html.fromstring(page.text)

        category = re.findall("Books\s?>\s*(.*?)\s*>", read_text(listing))
        title = re.sub('Details about','', clean_str(listing.xpath('.//h1[@id="itemTitle"]')[0].text_content()))
        if verbose:
            report('%s %s' % (listing_id, title))
        price_elem = listing.xpath('.//span[@id="prcIsum"]')[0]
        price = read_num(price_elem.text_content())
        location_elem = listing.xpath('.//div[@id="itemLocation"]')[0]
        location = re.sub('[\w ]+:', '', read_text(location_elem))
        condition_elem = listing.xpath('.//div[@class="u-flL condText  "]')[0]
        condition = read_text(condition_elem)

        authors = ''
        isbn = None

        specifics_data = []
        specifics = listing.xpath('.//div[@class="itemAttr"]')[0]
        for key_elem in specifics.xpath('.//td[@class="attrLabels"]'):
            key = re.sub(':','', read_text(key_elem))
            value = read_text(key_elem.getnext())
            if key == 'Author':
                authors = value
            elif key == 'ISBN-13':
                isbn = value
            specifics_data.append(dict(listing_id=listing_id, key=key, value=value))

        detailed_data = []
        detailed = listing.xpath(".//div[@class='prodDetailDesc']")
        if detailed:
            detailed = detailed[0]
            detailed_data = []
            pairs = []
            category = ''
            for row in detailed.xpath(".//tr"):
                cat_elem = row.xpath("./td/font/b")
                if cat_elem:
                    category = clean_str(cat_elem[0].text_content())
                elif category > '':
                    tds = [clean_str(td.text_content()) for td in row.xpath("./td")]
                    if len(tds) == 2:
                        k, v = [clean_str(td.text_content()) for td in row.xpath("./td")]
                    else:
                        k, v = category, tds[0]
                    if v:
                        detailed_data.append(dict(listing_id=listing_id, category=category, key=k, value=v))
                    if k == 'Author':
                        authors = v
                    elif k == 'ISBN-13':
                        isbn = v

        shipping_costs = [read_num(read_text(span)) or 0.0 for span in listing.xpath('.//span[@id="fshippingCost"]')]
        shipping_types = [read_text(span) for span in listing.xpath('.//span[@id="fshippingSvc"]')]
        shipping_data = [dict(listing_id=listing_id, cost=cost, kind=kind) for cost, kind in zip(shipping_costs, shipping_types)]

        return {
            'title': title,
            'isbn': isbn,
            'authors': authors,
            'price': price,
            'location': location,
            'condition': condition,
            'category': category,
            'specifics': specifics_data,
            'details': detailed_data,
            'shipping': shipping_data,
            'updated': today().strftime("%Y-%m-%d %X")
        }

    def scrape(self, listing_id):
        return self.read(self.get(listing_id))

def scrape(listing_id):
    return EbayScraper().scrape(listing_id)
