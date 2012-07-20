for i in $(mdb-tables $1); do (
  echo "BEGIN TRANSACTION;";
  MDB_JET3_CHARSET=cp1256 mdb-export -S -R ";\n" -I $1 $i;
  echo "END TRANSACTION;" ); done