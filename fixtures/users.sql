create table users (
    -- ids
    id serial, -- use only for employees; someday it will cause seq error
    curator_id int8 null, -- use only when register new users

    -- user main info
    firstname varchar not null,
    middlename varchar not null,
    patronymic varchar null,

    -- resource info
    resume_url varchar not null,
    email varchar not null,
    password varchar not null,

    -- flags
    is_admin bool not null default false,
    is_employee bool not null default false,

    constraint user_pkey primary key (id),
    constraint curator_pkey foreign key (curator_id) references users (id) deferrable initially deferred
);

create table letters (
    id int8 not null generated by default as identity,
    user_id int8 not null,
    content text not null,

    constraint resumes_pkey primary key (id),
    constraint resumes_user_id foreign key (user_id) references users (id) deferrable initially deferred
);


create unlogged table employee_requests (
    id int8 not null generated by default as identity,
    user_id int8 not null,
    username varchar not null,

    constraint employee_requests_pkey primary key (id)
);