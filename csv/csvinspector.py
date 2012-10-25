import csv
import copy

from helpers import *    
from datatypes import BASE_TYPES, SQLITE_TYPES


class CSVInspector(object):

    def __init__(self, filename, types= BASE_TYPES):
    
        self.filename = filename
        self.types = types
        self.dialect = None
        self.names=[]
        self.meta={}
        
        
    def getDialect(self):
        with open(self.filename, 'rb') as csvfile:
            self.dialect = csv.Sniffer().sniff(csvfile.read(1024))
            
    
    def explainDialect(self):
        
        if not self.dialect:
            self.getDialect()
            
        print "delimiter:", self.dialect.delimiter
        print "quotechar:", self.dialect.quotechar
    


    def analyze(self):

        if not self.dialect:
            self.getDialect()
    
        with open(self.filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, self.dialect)
            #assuming header
            firstline = reader.next()
            self.names = [sanitize(x) for x in firstline]
            tempMeta = [{'fieldName': x, 'candidates' : copy.copy(self.types) } for x in self.names]
            
            for row in reader:
                self.checkRow(row, tempMeta)
                
            self.checkOverrides(tempMeta)
            self.meta = self.convertMeta(tempMeta)
            
            
    def buildInserts(self, tablename):
        with open(self.filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, self.dialect)
            #assuming header
            firstline = reader.next()
            for row in reader:
                values = self.row2python(row)
                insert = "INSERT INTO %s "
                insert += "(" + ','.join(self.names) +")"
                insert += " VALUES("
                pieces = [escapeSQLValue(v) for v in values]
                pi = ','.join(pieces)
                insert += pi
                insert += ");"
                
                insert = insert % tablename
                
                yield insert
    

    def createTable(self,tablename="TABLE_1"):
        sql = "CREATE TABLE IF NOT EXISTS \""+tablename+"\" (\n"
        sql = sql+"  id INTEGER PRIMARY KEY, \n"
        for field in self.names:
            meta = self.meta[field]
            sql = sql+"  "+field+" \t "+ meta[0] + ",\n"
        sql = sql[:-2]
        sql += "\n);"
        print sql
        

    def insert(self, tablename="TABLE_1"):
        for statement in self.buildInserts(tablename=tablename):
            print statement
            
            
    
                
    def checkRow(self, row, tempMeta):
        for i, x in enumerate(row):
            meta = tempMeta[i]
            toRemove = []
            candidates = meta['candidates']
            for typeName in candidates:
                candidate = candidates[typeName]
                typeCheck =  candidate['checker']
                try:
                    value = wrapEmptyValues(typeCheck,x)
                except ValueError:
                    toRemove.append(typeName)
                except:
                    raise
                    
            for r in toRemove: 
                del candidates[r]
                
                
    def row2python(self, row):
        out = []
        for i, name in enumerate(self.names):
            typeName = self.meta[name][0]
            item = row[i]
            fun = self.types[typeName]['checker']
            converter = self.types[typeName]['converter']
            value = wrapEmptyValues(fun, item)
            value = converter(value)
            out.append(value)
        return out
            
            
        
                    
    def checkOverrides(self, meta):
        for metaItem in meta:
            toRemove = []
            candidates =  metaItem['candidates']
            for typeName in candidates:
                candidate = candidates[typeName]
                if 'overrides' in candidate:
                    toRemove.extend(candidate['overrides'])
                    #recursive removal
                    for ov in candidate['overrides']:
                        if 'overrides' in self.types[ov]:
                            toRemove.extend(self.types[ov]['overrides'])
                        
            toRemove = list(set(toRemove))
            for r in toRemove: 
                try:
                    del candidates[r]
                except:
                    pass
        
    
    def convertMeta(self, tempMeta):
        out = {}
        for metaItem in tempMeta:
            candidates =  metaItem['candidates']
            out[ metaItem['fieldName']] = candidates.keys()
        return out
        
        

if __name__ == '__main__':
    import sys
    fn = sys.argv[1]
    inspector = CSVInspector(fn, types=SQLITE_TYPES)
    inspector.analyze()
    #inspector.insert(tablename='test1')
    if '--create' in sys.argv:
        inspector.createTable(tablename='test1')
    if '--insert' in sys.argv:
        inspector.insert(tablename='test1')
        

        
        