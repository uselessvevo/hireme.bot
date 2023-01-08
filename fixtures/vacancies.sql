create table vacancies (
    id serial,
    user_id int8 not null,
    vacancy_id int8 not null,
    url varchar not null,
    content text null,
    title varchar null,
    salary varchar null,
    percentage float null,
    parsed bool not null default false,
    status varchar not null default 'RESPONSE',
    constraint vacancies_pkey primary key (id),
    constraint user_pkey foreign key (user_id) references users(id) deferrable initially deferred
);

select url, regexp_match(url, '\d+') as vacancy_id from vacancies;

-- update vacancies set vacancy_id = array_to_string(regexp_match(url, '\d+'), ',')::int8;

select * from vacancies