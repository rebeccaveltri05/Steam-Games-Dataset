import psycopg2
from util import DB_CONFIG

def create_tables():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE games (
            appid              INTEGER PRIMARY KEY,
            name               TEXT,
            release_date       TEXT,
            estimated_owners   TEXT,
            peak_ccu           INTEGER,
            required_age       INTEGER,
            price              NUMERIC,
            dlc_count          INTEGER,
            detailed_description TEXT,
            short_description  TEXT,
            supported_languages TEXT,
            full_audio_languages TEXT,
            reviews            TEXT,
            header_image       TEXT,
            website            TEXT,
            support_url        TEXT,
            support_email      TEXT,
            windows            BOOLEAN,
            mac                BOOLEAN,
            linux              BOOLEAN,
            metacritic_score   INTEGER,
            metacritic_url     TEXT,
            user_score         INTEGER,
            positive           INTEGER,
            negative           INTEGER,
            score_rank         TEXT,
            achievements       INTEGER,
            recommendations    INTEGER,
            notes              TEXT,
            average_playtime_forever INTEGER,
            average_playtime_2weeks  INTEGER,
            median_playtime_forever  INTEGER,
            median_playtime_2weeks   INTEGER
        );


        CREATE TABLE packages (
            id SERIAL PRIMARY KEY,
            appid INTEGER REFERENCES games(appid) ON DELETE CASCADE,
            title TEXT,
            description TEXT
        );


        CREATE TABLE subs (
            id SERIAL PRIMARY KEY,
            package_id INTEGER REFERENCES packages(id) ON DELETE CASCADE,
            text TEXT,
            description TEXT,
            price NUMERIC
        );


        CREATE TABLE developers (
            id SERIAL PRIMARY KEY,
            developer_name TEXT unique not null
        );

        create table developers_game (
            id_developer int,
            id_game int,
            primary key (id_developer, id_game),
            foreign key (id_developer) references  developers (id) on delete cascade,
            FOREIGN KEY (id_game) REFERENCES games (appid) ON DELETE cascade
        );


        CREATE TABLE publishers (
            id SERIAL PRIMARY KEY,
            publisher_name TEXT not null
        );

        create table publishers_game (
            id_publisher int,
            id_game int,
            primary key (id_publisher, id_game),
            foreign key (id_publisher) references publishers (id) on delete cascade,
            FOREIGN KEY (id_game) REFERENCES games (appid) ON DELETE cascade 
        );


        CREATE TABLE categories (
            id SERIAL primary key,
            category_name TEXT not NULL
        );

        create table categories_game (
            id_category int,
            id_game int,
            PRIMARY KEY (id_category, id_game),
            FOREIGN KEY (id_category) REFERENCES categories (id) ON DELETE CASCADE,
            FOREIGN KEY (id_game) REFERENCES games (appid) ON DELETE cascade 
        );


        CREATE TABLE genres (
            id SERIAL PRIMARY KEY,
            genre_name TEXT not NULL
        );

        create table genres_game (
            id_genre int,
            id_game int,
            primary key (id_genre, id_game),
            foreign key (id_genre) references genres (id) on delete cascade,
            FOREIGN KEY (id_game) REFERENCES games (appid) ON DELETE cascade 
        );

        CREATE TABLE screenshots (
            id SERIAL PRIMARY KEY,
            appid INTEGER REFERENCES games(appid) ON DELETE CASCADE,
            screenshot_url TEXT
        );


        CREATE TABLE movies (
            id SERIAL PRIMARY key,
            appid INTEGER REFERENCES games(appid) ON DELETE CASCADE,
            movie_url TEXT
        );


        CREATE TABLE tags (
            id SERIAL PRIMARY KEY,
            tag_name TEXT unique not null
        );

        create table tags_game (
            id_tag int,
            id_game int,
            tag_score int,
            primary key (id_tag, id_game),
            foreign KEY (id_tag) references tags (id) on delete cascade,
            FOREIGN KEY (id_game) REFERENCES games (appid) ON DELETE cascade
        );
        """
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Tabelas criadas com sucesso.")