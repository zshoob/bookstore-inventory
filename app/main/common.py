import dateutil
import re
import numpy as np

def today():
    import datetime
    return datetime.date.today()

def now():
    import datetime
    return datetime.datetime.now()

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

def money_f(f):
    if (f is np.nan) or not read_num(f):
        return '--'
    return "${:,.2f}".format(read_num(f))

def parse_authors(s):
    from nameparser.parser import HumanName
    names = [HumanName(n) for n in s.split(',')]
    # format must be Stein, Clifford
    if len(names) == 2 and not names[0].last:
        names = [HumanName(s)]
    return [name.as_dict() for name in names]
