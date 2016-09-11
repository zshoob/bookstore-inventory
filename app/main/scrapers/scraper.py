from lxml import html
import requests
import re
import sys
import datetime
import pandas as pd
import time
import dateutil
import traceback
from nameparser.parser import HumanName

def parse_authors(s):
    names = [HumanName(n) for n in s.split(',')]
    # format must be Stein, Clifford
    if len(names) == 2 and not names[0].last:
        names = HumanName(s)
    return [dict(first_name=name.first, middle_name=name.middle, last_name=name.last) for name in names]

def today():
    return datetime.date.today()

def now():
    return datetime.datetime.now()

def report(s):
    print '%s: %s' % (now(), s)

def clean_str(s):
    if s is None:
        return None
    return re.sub(r'[\s]+',' ', unicode(s)).strip()

def read_num(s):
    n = re.findall('[0-9\.]+', clean_str(s))
    try:
        return float(n[0])
    except IndexError, ValueError:
        return None

def read_text(elem, clean=True):
    if hasattr(elem, 'text_content'):
        return clean_str(elem.text_content()) if clean else elem.text_content()
    return None

def read_date(s):
    return dateutil.parser.parse(s)

class Scraper(object):
    pass
