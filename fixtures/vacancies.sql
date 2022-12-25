create table vacancies (
    id serial,
    user_id int8 not null,
    url varchar not null,
    content text null,
    title varchar null,
    salary varchar null,
    percentage float null,
    parsed bool not null default false,
    constraint vacancies_pkey primary key (id),
    constraint user_pkey foreign key (user_id) references users(id) deferrable initially deferred
);