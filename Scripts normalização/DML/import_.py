import psycopg2
import ijson
from DML.config import DB_CONFIG, PATH_ROOT
from DML.util import *

JSON_PATH = PATH_ROOT / "games.json"

def treat_str(value, can_be_null=True):
    """
    Se can_be_null=True: Retorna None se a string for vazia (vira NULL no banco).
    Se can_be_null=False: Retorna string vazia ou string tratada (evita NULL constraint violation).
    """
    if value is None:
        return None if can_be_null else ""
    
    s_value = str(value).strip()
    
    if s_value == "":
        return None if can_be_null else ""
    
    return s_value

def safe_int_nullable(value):
    """Retorna None se falhar (para campos como score_rank que podem ser NULL)"""
    if not value or value == "":
        return None
    try:
        return int(float(value))
    except:
        return None
    
def insert_enums(cur):
    os_lista = ['windows', 'mac', 'linux']

    for os_name in os_lista:
        cur.execute(
            """
            INSERT INTO operation_systems (so_name)
            VALUES (%s)
            ON CONFLICT (so_name) DO NOTHING
            """,
            (os_name,)
        )
# =====================================================================
# INSERT PRINCIPAL (tabela games) 
# =====================================================================
def insert_game(cur, game):
    
    # Tratamentos Prévios
    # release_date: Se falhar a conversão, retornamos None
    data_lancamento = string_to_postgres_date(game.get("release_date", ""))
    
    own_min, own_max = parse_owners(game.get("estimated_owners"))

    pos = safe_int(game.get("positive"), default=0)
    neg = safe_int(game.get("negative"), default=0)
    
    if game.get("user_score") == 0 and (pos + neg) > 0:
        user_score = (pos / (pos + neg)) * 100
    else:
        user_score = safe_int_nullable(game.get("user_score"))

    # Montagem do Dicionário com a Lógica de NULL
    clean_data = {
        # === TABELA GAMES (NOT NULL estritos) ===
        "name": treat_str(game.get("name"), can_be_null=False), # Nunca será NULL
        "release_date": data_lancamento, 
        "required_age": safe_int(game.get("required_age"), default=0),
        "price": safe_float(game.get("price"), default=0.0),
        
        # about_the_game:se vier vazio, mandamos string vazia ou "No description"
        "about_the_game": treat_str(game.get("about_the_game"), can_be_null=False) or "No description available",
        
        "header_image": treat_str(game.get("header_image"), can_be_null=False),
        
        # website: Pode ser NULL
        "website": treat_str(game.get("website"), can_be_null=True), 

        # === TABELA DETALHES (Maioria Nullable) ===
        "owners_min": own_min,
        "owners_max": own_max,
        "peak_ccu": safe_int(game.get("peak_ccu"), default=0),
        "dlc_count": safe_int(game.get("dlc_count"), default=0),
        
        # Tempos de jogo: 0 faz mais sentido que NULL se não tiver dados
        "average_playtime_forever": safe_int(game.get("average_playtime_forever"), default=0),
        "average_playtime_2weeks": safe_int(game.get("average_playtime_2weeks"), default=0),
        "median_playtime_forever": safe_int(game.get("median_playtime_forever"), default=0),
        "median_playtime_2weeks": safe_int(game.get("median_playtime_2weeks"), default=0),
        
        # Campos de Texto Opcionais (Viram NULL se vazios)
        "notes": treat_str(game.get("notes"), can_be_null=True),
        "support_url": treat_str(game.get("support_url"), can_be_null=True),
        "support_email": treat_str(game.get("support_email"), can_be_null=True),
        "metacritic_url": treat_str(game.get("metacritic_url"), can_be_null=True),
        
        # Scores e Ranks (Devem ser NULL se não existirem)
        # Use safe_int_nullable aqui, pois 0 mudaria a média estatística
        "metacritic_score": safe_int_nullable(game.get("metacritic_score")),
        "score_rank": safe_int_nullable(game.get("score_rank")),
        "user_score": user_score,

        # Contadores (0 é ok)
        "recommendations": safe_int(game.get("recommendations"), default=0),
        "achievements": safe_int(game.get("achievements"), default=0),
        "positive": safe_int(game.get("positive"), default=0),
        "negative": safe_int(game.get("negative"), default=0),
    }

    # Definição das colunas
    cols_games = ["name", "release_date", "required_age", "price", 
                  "about_the_game", "header_image", "website"]
    
    cols_details = ["id_game", "owners_min", "owners_max", "peak_ccu", "dlc_count",
                    "average_playtime_forever", "average_playtime_2weeks", 
                    "median_playtime_forever", "median_playtime_2weeks", "notes", 
                    "recommendations", "achievements", "support_url", "support_email", 
                    "metacritic_score", "metacritic_url", "positive", "negative", 
                    "user_score", "score_rank"]

    # Extraindo valores na ordem correta
    vals_games = [clean_data[c] for c in cols_games]

    # SQL Insert
    sql_games = f"""
        INSERT INTO games ({",".join(cols_games)})
        VALUES ({",".join(["%s"] * len(vals_games))})
        ON CONFLICT (appid) DO NOTHING
        RETURNING appid;
    """
    cur.execute(sql_games, vals_games)

    row = cur.fetchone()

    if row:
        id_game = row[0]
        vals_details = [id_game] + [
            clean_data[c] 
            for c in cols_details 
            if c != "id_game"
        ]
        sql_details = f"""
            INSERT INTO detalhes ({",".join(cols_details)})
            VALUES ({",".join(["%s"] * len(vals_details))})
            ON CONFLICT (id_game) DO NOTHING;
        """
        cur.execute(sql_details, vals_details)

    return id_game
# =====================================================================
# INSERTS RELACIONADOS
# =====================================================================
def insert_related(cur, appid, game):

    game_plataform = {
        'windows': game.get("windows", None),
        'mac': game.get("mac", None),
        'linux': game.get("linux", None)
    }

    for plataform, value in game_plataform.items():
        if value == True:
            cur.execute(
                """
                SELECT id
                FROM operation_systems
                WHERE so_name = %s
                """,(plataform,)
            )

            result = cur.fetchone()
            if result:
                so_id = result[0]
                cur.execute(
                    """
                    INSERT INTO operation_systems_games
                    VALUES(%s, %s)
                    ON CONFLICT DO NOTHING;
                    """, (so_id, appid)
                )

    reviews = game.get("reviews", "")
    reviews_separadas = parse_reviews(reviews)

    if reviews_separadas == "":
        pass
    else:
        for review in reviews_separadas:
            author_name = review["author"]
            review_text = review["review"]

            cur.execute(
                """INSERT INTO author (author_name) VALUES (%s)
                    ON CONFLICT (author_name) 
                    DO UPDATE SET author_name = EXCLUDED.author_name
                    RETURNING id;""",
                (author_name,)
            )

            author_id = cur.fetchone()[0]

            cur.execute(
                """INSERT INTO reviews_game (id_author, id_game, review_text) 
                    VALUES (%s, %s, %s) 
                    ON CONFLICT DO NOTHING;""",
                (author_id, appid, review_text)
            )
        
    # DEVELOPERS
    for dev in game.get("developers", []):
        cur.execute(
            """INSERT INTO developers (developer_name) VALUES (%s)
                ON CONFLICT (developer_name) 
                DO UPDATE SET developer_name = EXCLUDED.developer_name 
                RETURNING id;""",
            (dev,)
        )

        dev_id = cur.fetchone()[0]

        cur.execute(
            """INSERT INTO developers_game (id_developer, id_game) 
                VALUES (%s, %s) 
                ON CONFLICT DO NOTHING;""",
            (dev_id, appid)
        )

    # PUBLISHERS
    for pub in game.get("publishers", []):
        cur.execute(
            """INSERT INTO publishers (publisher_name) VALUES (%s)
            ON CONFLICT (publisher_name) 
            DO UPDATE SET publisher_name = EXCLUDED.publisher_name 
            RETURNING id;""",
            (pub,)
        )

        pub_id = cur.fetchone()[0]
        
        cur.execute(
            """INSERT INTO publishers_game (id_publisher, id_game) VALUES (%s, %s)
            ON CONFLICT DO NOTHING;""",
            (pub_id, appid)
        )

    # CATEGORIES
    for cat in game.get("categories", []):
        cur.execute(
            """INSERT INTO categories (category_name) VALUES (%s) 
            on conflict (category_name)
            DO UPDATE SET category_name = EXCLUDED.category_name 
            RETURNING id;""",
            (cat,)
        )
        
        cat_id = cur.fetchone()[0]

        cur.execute(
            """INSERT INTO categories_game (id_category, id_game) VALUES (%s, %s)
            ON CONFLICT DO NOTHING;""",
            (cat_id, appid)
        )

    # GENRES
    for gen in game.get("genres", []):
        cur.execute(
            """INSERT INTO genres (genre_name) VALUES (%s) 
            ON CONFLICT (genre_name) 
            DO UPDATE SET genre_name = EXCLUDED.genre_name 
            RETURNING id;""",
            (gen,)
        )
        
        gen_id = cur.fetchone()[0]

        cur.execute(
            """INSERT INTO genres_game (id_genre, id_game) VALUES (%s, %s)
            ON CONFLICT DO NOTHING;""",
            (gen_id, appid)
        )

    # SCREENSHOTS
    screenshot_list = game.get("scrennshots") or game.get("screenshots") or []

    for shot in screenshot_list:
        cur.execute(
            "INSERT INTO screenshots (appid, screenshot_url) VALUES (%s, %s);",
            (appid, shot)
        )

    # MOVIES
    for movie in game.get("movies", []):
        cur.execute(
            "INSERT INTO movies (appid, movie_url) VALUES (%s, %s);",
            (appid, movie)
        )

    # TAGS
    tag_dict = dict(game.get("tags", {}))
    if(tag_dict):
        for tag_name, tag_score in tag_dict.items():
            cur.execute(
                """INSERT INTO tags (tag_name) VALUES (%s) 
                ON CONFLICT (tag_name) 
                DO UPDATE SET tag_name = EXCLUDED.tag_name
                RETURNING id;""",
                (str(tag_name),)
            )

            tag_id = cur.fetchone()[0]

            cur.execute(
                """INSERT INTO tags_game (id_tag, id_game) VALUES (%s, %s)
                ON CONFLICT DO NOTHING;""",
                (tag_id, appid)
            )

    for lang in game.get("supported_languages", []):
        cur.execute(
            """INSERT INTO languages (language_name) VALUES (%s) 
            ON CONFLICT (language_name) 
            DO UPDATE SET language_name = EXCLUDED.language_name
            RETURNING id;""",
            (lang,)
        )

        lang_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO languages_game (id_language, id_game) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
            (lang_id, appid)
        )
    
    for audio_lang in game.get("full_audio_languages", []):
        cur.execute(
            """INSERT INTO audio_languages (audio_language_name) VALUES (%s) 
            ON CONFLICT (audio_language_name) 
            DO UPDATE SET audio_language_name = EXCLUDED.audio_language_name
            RETURNING id;""",
            (audio_lang,)
        )

        audio_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO audio_languages_game (id_audio, id_game) VALUES (%s, %s) ON CONFLICT  DO NOTHING;",
            (audio_id, appid)
        )

# =====================================================================
# IMPORT PRINCIPAL
# =====================================================================
def import_games():
    print("\nLendo arquivo JSON...")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SET search_path TO public;")
    conn.commit()
    # Carregando JSON
    f = open(JSON_PATH, "rb")

    parser = ijson.kvitems(f, "")

    count = 0

    insert_enums(cur)

    for appid, game in parser:

        # INSERIR NA TABELA PRINCIPAL
        id_game = insert_game(cur, game)

        # INSERIR NAS TABELAS RELACIONADAS
        insert_related(cur, id_game, game)

        count += 1

        # Commit a cada 1000 jogos
        if count % 1000 == 0:
            conn.commit()
            print(f"✔ {count} jogos importados...")

    conn.commit()
    cur.close()
    conn.close()
    f.close()

    print("\nImportação finalizada com sucesso!")
    print(f"Total importado: {count} jogos.\n")


if __name__ == "__main__":
    import_games()
    