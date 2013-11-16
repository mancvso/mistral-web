drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  name text not null,
  lastname text not null,
  rut text not null,
  email text not null,
  score integer not null default 0,
  elapsed integer not null default 0,
  played boolean not null default false,
  rewarded boolean not null default false
);
