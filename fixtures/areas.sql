create table areas (
    id int8 not null,
    parent_id int8 null,
    name varchar not null,
    constraint area_id primary key (id),
    constraint parent_pkey foreign key (parent_id) references areas(id) deferrable initially deferred
);
