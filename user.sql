drop table if exists users;
create table users (
  id integer primary key autoincrement,
  name text not null,
  password text
);
insert into users (name, password) values ('admin', '');
