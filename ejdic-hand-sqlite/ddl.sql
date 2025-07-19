create table main.items
(
    item_id INTEGER
        primary key,
    word    TEXT
        unique,
    mean    TEXT,
    level   INTEGER default 0
);

create index main.word_index
    on main.items (word);

