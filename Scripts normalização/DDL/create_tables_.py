import psycopg2
from DML.config import DB_CONFIG
 
def create_tables():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
 
    cur.execute("""
        CREATE TABLE games (
            appid              INTEGER PRIMARY KEY,
            name               TEXT not null,
            release_date       DATE not null,
            required_age       INTEGER not null,
            price              NUMERIC not null,
	        about_the_game       TEXT not null,
            header_image         TEXT not null,
            website              TEXT
        );
	
        CREATE TABLE detalhes (
            id_game                  int primary key,
            owners_min               INTEGER,
            owners_max               INTEGER,   
            peak_ccu                 INTEGER,
            dlc_count                INTEGER,
            average_playtime_forever INTEGER,
            average_playtime_2weeks  INTEGER,
            median_playtime_forever  INTEGER,
            median_playtime_2weeks   INTEGER,
            notes                    TEXT,
            recommendations          INTEGER,
            achievements             INTEGER,
            support_url              TEXT,
            support_email            TEXT,
            metacritic_score         INTEGER,
            metacritic_url           TEXT,
            positive		         INTEGER,
            negative                 INTEGER,
            user_score               INTEGER, 
            score_rank               INTEGER,
            FOREIGN KEY (id_game) REFERENCES games(appid) ON UPDATE CASCADE ON DELETE CASCADE
        );

        CREATE TYPE os_enum AS ENUM ('windows', 'mac', 'linux');

        CREATE TABLE operation_systems (
            id serial PRIMARY KEY,
            so_name os_enum UNIQUE NOT NULL
        );

        CREATE TABLE operation_systems_games (
            id_so int,
            id_game int,
            PRIMARY KEY (id_so, id_game),
            FOREIGN KEY (id_so) REFERENCES operation_systems (id),
            FOREIGN KEY (id_game) REFERENCES games (appid)
        );

        CREATE TABLE author (
            id SERIAL PRIMARY KEY,
            author_name TEXT UNIQUE NOT NULL
        );
                        
        CREATE TABLE reviews_game (
            id SERIAL PRIMARY KEY,
            id_author      INT NOT NULL,
            id_game        INT NOT NULL,
            review_text    TEXT NOT NULL,
            FOREIGN KEY (id_author) REFERENCES author (id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (id_game) REFERENCES games (appid) ON UPDATE CASCADE ON DELETE CASCADE
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
            publisher_name TEXT unique not null
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
            category_name TEXT unique not NULL
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
            genre_name TEXT unique not NULL
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
            screenshot_url TEXT not null
        );


        CREATE TABLE movies (
            id SERIAL PRIMARY key,
            appid INTEGER REFERENCES games(appid) ON DELETE CASCADE,
            movie_url TEXT not null
        );


        CREATE TABLE tags (
            id SERIAL PRIMARY KEY,
            tag_name TEXT unique not null
        );

        create table tags_game (
            id_tag int,
            id_game int,
            primary key (id_tag, id_game),
            foreign KEY (id_tag) references tags (id) on delete cascade,
            FOREIGN KEY (id_game) REFERENCES games (appid) ON DELETE cascade
        );
        
        CREATE TABLE languages (
            id SERIAL PRIMARY KEY,
            language_name TEXT UNIQUE NOT NULL
        );
                
        CREATE TABLE languages_game (
            id_language INT,
            id_game INT,
            PRIMARY KEY (id_language, id_game),
            FOREIGN KEY (id_language) REFERENCES languages(id) ON DELETE CASCADE,
            FOREIGN KEY (id_game) REFERENCES games(appid) ON DELETE CASCADE
        );
        
        CREATE TABLE audio_languages (
            id SERIAL PRIMARY KEY,
            audio_language_name TEXT UNIQUE NOT NULL
        );
                
        CREATE TABLE audio_languages_game (
            id_audio INT,
            id_game INT,
            PRIMARY KEY (id_audio, id_game),
            FOREIGN KEY (id_audio) REFERENCES audio_languages(id) ON DELETE CASCADE,
            FOREIGN KEY (id_game) REFERENCES games(appid) ON DELETE CASCADE
        );
        """
    )
 
    conn.commit()
    cur.close()
    conn.close()
    print("Tabelas criadas com sucesso.")
 
 