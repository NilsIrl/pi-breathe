
# Pollution data
```sql
CREATE TABLE pollution (id integer primary key asc autoincrement, src text, lat
real NOT NULL, lng real NOT NULL, time integer, pollution real NOT NULL);
```

# User data
```sql
CREATE TABLE users (id integer primary key asc autoincrement, username text NOT
NULL, password text)
```

