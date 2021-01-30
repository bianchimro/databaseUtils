#!/usr/bin/env python

"""
this scripts correct sqlite dates to iso format (not datetimes)
Mauro Bianchi 2012

usage:
    python sqlitedatecast.py sqlitefile tablename columnslist
    
for example:
    python sqlitedatecast.py a.sqlite table_a "start_date,end_date,middle_date"

"""

import sqlite3
import sys
import re
import datetime

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


CANDIDATE_FORMATS = ["%d/%m/%Y", "%d-%m-%Y", '%Y-%m-%d',
                     "%d/%m/%y", "%d-%m-%y",
                    ]
SQLITE_DATE_FORMAT = '%Y-%m-%d'


class Corrector(object):
    def __init__(self, db):
        self.db = db
        self.conn = None
        self.tables = []
        
        
    def connect(self):
        self.conn = sqlite3.connect(self.db)
        self.conn.row_factory = dict_factory
    
    def disconnect(self):
        self.conn.close()
        
        
    def inspectTables(self):
        self.connect()
        c = self.conn.cursor()
        q = "SELECT * FROM sqlite_master WHERE type='table';"
        c.execute(q)
        for row in c:
            self.tables.append(row['tbl_name'])
        self.disconnect()
    
        print self.tables
        

    def guessFormat(self, formatsDict):
        selected = []
        numEntries = reduce(lambda x,y:int(x)+int(y), formatsDict.values(), 0)
        for x in formatsDict:
            if formatsDict[x] > 0:
                selected.append((x, float(formatsDict[x]) / numEntries))
            
        return selected

    
    def correctTableForColumnsList(self,tbl, colList):
        for c in colList:
            self.correctTable(tbl, c.strip())
    
    def correctTable(self, tbl, col):
        print "correcting", tbl, col
        self.connect()
        records = []
        c = self.conn.cursor()
        q = "SELECT %s FROM %s" % (col, tbl)
        c.execute(q)
        
        formats = {}
        for f in CANDIDATE_FORMATS:
            formats[f] = 0
        
        for row in c:
            datePiece = row[col]
            records.append(row)
            for f in CANDIDATE_FORMATS:
                try:
                    convertedDate = datetime.datetime.strptime(datePiece, f)
                    formats[f] += 1
                except:
                    pass
                    
        selectedFormats = self.guessFormat(formats)
        print selectedFormats
        
        if len(selectedFormats) != 1:
            print "ambiguous, skipping"
            self.disconnect()
            return
            
        print "no doubt: ", selectedFormats[0][0]
        choosenFormat = selectedFormats[0][0]

        if choosenFormat == SQLITE_DATE_FORMAT:
            print "no need to convert"
        
        else:
            #altering table
            for r in records:
                if r[col] is not None and r[col]:
                    print "row", r
                    originalDate = r[col]
                    try:
                        correctDate = datetime.datetime.strptime(originalDate, choosenFormat )
                        sqliteDate = datetime.datetime.strftime(correctDate, SQLITE_DATE_FORMAT)
                    except:
                        sqliteDate = None
                    
                    q = "UPDATE %s set %s=? WHERE %s=?" % (tbl, col, col)
                    self.conn.execute(q, (sqliteDate, originalDate))
            
            self.conn.commit()
            
        self.disconnect()
        
    

if __name__ == '__main__':

    target = sys.argv[1]
    table = sys.argv[2]
    cols = sys.argv[3]
    worker = Corrector(target)
    cols = cols.split(",")
    worker.correctTableForColumnsList(table, cols)