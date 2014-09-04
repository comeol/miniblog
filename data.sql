drop table if exists data;
create table data (
  id integer primary key autoincrement,
  title text not null,
  text text not null,
  name text not null,
  date text not null
);
