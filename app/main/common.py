import dateutil
import re

def clean_date(x, default=None):
    try:
        return dateutil.parser.parse(x)
    except:
        return default

def clean_str(s):
    if s is None:
        return ''
    return re.sub(r'[\s]+',' ', unicode(s)).strip()

def read_num(s):
    n = re.findall('[0-9\.]+', clean_str(s))
    try:
        return float(n[0])
    except IndexError, ValueError:
        return None
