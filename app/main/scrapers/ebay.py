
# coding: utf-8

# In[145]:

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
        
        title_elem = listing.xpath('.//h1[@id="itemTitle"]')[0]
        title = clean_str(title_elem.text_content())
        title = title.replace(u'Details about \xa0', '')
        
        if verbose:
            report('%s %s' % (listing_id, title))
        price_elem = listing.xpath('.//span[@id="prcIsum" or @id="prcIsum_bidPrice"]')[0]
        price = read_num(price_elem.text_content())
        location_elem = listing.xpath('.//div[@id="itemLocation"]')[0]
        location = re.sub('[\w ]+:', '', read_text(location_elem))
        condition_elem = listing.xpath('.//div[@class="u-flL condText  "]')[0]
        condition = read_text(condition_elem)
        
        img_src = None
        img_elem = listing.xpath('.//img[@id="icImg"]')
        if img_elem:
            img_src = img_elem[0].get('src')
        
        data = {
            'title': title,
            'price': price,
            'location': location,
            'condition': condition,
            'category': category,
            'image_source': img_src,
            'updated': today().strftime("%Y-%m-%d %X")
        }
        
        specifics_data = []
        specifics = listing.xpath('.//div[@class="itemAttr"]')[0]
        for key_elem in specifics.xpath('.//td[@class="attrLabels"]'):
            key = re.sub(':','', read_text(key_elem))
            value = read_text(key_elem.getnext())
            if key == 'Author':
                data['authors'] = value
            elif key == 'ISBN-13':
                data['isbn'] = value
            else:
                data[key.lower()] = value
            specifics_data.append(dict(listing_id=listing_id, key=key, value=value))

        shipping_costs = [read_num(read_text(span)) or 0.0 for span in listing.xpath('.//span[@id="fshippingCost"]')]
        shipping_types = [read_text(span) for span in listing.xpath('.//span[@id="fshippingSvc"]')]
        shipping_data = [dict(listing_id=listing_id, cost=cost, kind=kind) for cost, kind in zip(shipping_costs, shipping_types)]
        data['shipping'] = shipping_data
            
        detailed_data = []
        detailed = listing.xpath(".//div[@class='prodDetailDesc']")
        if detailed:
            detailed = detailed[0]
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
                        data['authors'] = v
                    elif k == 'ISBN-13':
                        data['isbn'] = v
                    else:
                        data[k.lower()] = v
        return data
    
    def scrape(self, listing_id):
        return self.read(self.get(listing_id))
    
def scrape(listing_id):
    return EbayScraper().scrape(listing_id)

