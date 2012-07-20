#!/bin/bash
export MDB_ICONV=utf-8
export MDB_JET_CHARSET=utf-8

mdb-schema $1 postgres | sed 's/Char/Varchar/g' | sed 's/Postgres_Unknown 0x0c/text/g' | sed 's/Postgres_Unknown 0x10/text/g' > $2


for i in `mdb-tables $1`
do
    echo $i
    echo "CREATE SEQUENCE "$i"_id_seq;" >> $2
    echo "ALTER TABLE "$i" ADD COLUMN id INTEGER;" >> $2
    echo "ALTER TABLE "$i" ALTER COLUMN id SET DEFAULT nextval('"$i"_id_seq');" >> $2
    echo "ALTER TABLE "$i" ADD CONSTRAINT "$i"_pkey PRIMARY KEY (id );" >> $2

    #mdb-export -q '"' -R '\n'  $1 $i | iconv -f ISO-8859-1 -t UTF-8  > $i.csv
    #echo "\COPY $i from './$i.csv' WITH CSV HEADER QUOTE '\"';" >> $2
    
    mdb-export -I -q "'" -R ';\n'  $1 $i | iconv -f ISO-8859-1 -t UTF-8 >> $2
    
done