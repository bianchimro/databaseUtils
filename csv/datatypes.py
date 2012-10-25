from helpers import * 
import datetime

BASE_DATE_FORMATS = ["%d/%m/%Y", "%d/%m/%y"]
BOOLEAN_MAPPINGS = { 'yes' : True, 'no': False, 'true' : True, 'False': False, 'y': True, 'n': False }


def date(value, formats=BASE_DATE_FORMATS):
    for format in formats:
        try:
            out = datetime.datetime.strptime(value, format) 
            return out
        except:
            pass

    raise ValueError("Could not convert date %s" % value)
    

def date2sql(value):
    if value is not None:
        return datetime.datetime.strftime(value, "%Y-%m-%d")
    return ''
    
    
    
def get_bool(value):
    found = False
    try:
        x = int(value)
        if x in [0,1]:
            found= True
            out = bool(x)
    except:
        pass
        
    try:
        x = str(x)
        mappings = BOOLEAN_MAPPINGS
        x = x.rstrip().lstrip()
        if x in BOOLEAN_MAPPINGS:
            found= True
            out = BOOLEAN_MAPPINGS[x]
    except:
        pass
    
    if not found:
        raise ValueError("Could not convert to boolean %s", value)
    return out
    
    


BASE_TYPES = { 'string' : {'checker': dummy},
               'integer' : { 'checker': int, 'overrides':['string'], 'converter': dummy },
               'float' : { 'checker': float, 'overrides':['integer'], 'converter': dummy },
               'date' : { 'checker': date, 'overrides':['string'], 'converter': date2sql },
               'boolean' : { 'checker': get_bool, 'overrides':['string'], 'converter': int },
             }


SQLITE_TYPES = { 'TEXT' : {'checker': dummy},
                 'INTEGER' : { 'checker': int, 'overrides':['TEXT'], 'converter': dummy },
                 'REAL' : { 'checker': float, 'overrides':['INTEGER'], 'converter': dummy },
                 'DATE' : { 'checker': date, 'overrides':['TEXT'], 'converter': date2sql },
                 'BOOLEAN' : { 'checker': get_bool, 'overrides':['TEXT'], 'converter': int },
             }