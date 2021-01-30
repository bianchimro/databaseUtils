def dummy(value):
    return value

def wrapEmptyValues(fun, value):
    if value == '' or value is None:
        return None
    return fun(value)


def escapeSQLValue(value):

    if value == '' or value is None:
        return 'NULL'

    out = str(value)
    esc=False    
    if out.find("'") > -1:
         out = out.replace("'", "\\'")
         esc = True
    out = "'" + out + "'"
    

    if esc:
        out = "r" + out

    return out
    
def sanitize(value):
    return value.lstrip().rstrip().replace(" ", "_").replace(".", "_")
    