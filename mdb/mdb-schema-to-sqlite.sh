mdb-schema -S $1 | perl -wpe 's%^DROP TABLE %DROP TABLE IF EXISTS %i;
  s%(Memo/Hyperlink|DateTime( \(Short\))?)%TEXT%i;
  s%(Boolean|Byte|Byte|Numeric|Replication ID|(\w+ )?Integer)%INTEGER%i;
  s%(BINARY|OLE|Unknown ([0-9a-fx]+)?)%BLOB%i;
  s%\s*\(\d+\)\s*(,?[ \t]*)$%${1}%;'
 
