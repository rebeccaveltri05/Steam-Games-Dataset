import psycopg2
import ijson
from  util import DB_CONFIG
# =====================================================================
# INSERT PRINCIPAL (tabela games) – automátizado para evitar erros
# =====================================================================
def insert_game(cur, appid, game):

    columns = [
        "appid", "name", "release_date", "estimated_owners", "peak_ccu",
        "required_age", "price", "dlc_count", "detailed_description",
        "short_description", "supported_languages", "full_audio_languages",
        "reviews", "header_image", "website", "support_url", "support_email",
        "windows", "mac", "linux", "metacritic_score", "metacritic_url",
        "user_score", "positive", "negative", "score_rank", "achievements",
        "recommendations", "notes", "average_playtime_forever",
        "average_playtime_2weeks", "median_playtime_forever",
        "median_playtime_2weeks"
    ]

    values = [appid] + [game.get(col) for col in columns[1:]]

    placeholders = ",".join(["%s"] * len(values))
    colnames = ",".join(columns)

    sql = f"""
        INSERT INTO games ({colnames})
        VALUES ({placeholders})
        ON CONFLICT (appid) DO NOTHING;
    """

    cur.execute(sql, values)


# =====================================================================
# INSERTS RELACIONADOS
# =====================================================================
def insert_related(cur, appid, game):

    # PACKAGES
    for pack in game.get("packages", []):
        cur.execute(
            "INSERT INTO packages (appid, title, description) VALUES (%s, %s, %s) RETURNING id;",
            (appid, pack.get("title"), pack.get("description"))
        )
        package_id = cur.fetchone()[0]

        # SUBPACKAGES
        for sub in pack.get("subs", []):
            cur.execute(
                "INSERT INTO subs (package_id, text, description, price) VALUES (%s, %s, %s, %s);",
                (package_id, sub.get("text"), sub.get("description"), sub.get("price"))
            )

    # DEVELOPERS
    for dev in game.get("developers", []):
        cur.execute(
            """INSERT INTO developers (developer_name) VALUES (%s)
                ON CONFLICT (developer_name) DO NOTHING 
                RETURNING id;""",
            (dev,)
        )
        try:
            dev_id = cur.fetchone()[0]
        except:
            dev_id = None

        if dev_id is None:
            cur.execute(
                "SELECT id FROM developers WHERE developer_name = %s;",
                (dev,)
            )
            dev_id = cur.fetchone()[0]

        cur.execute(
            """INSERT INTO developers_game (id_developer, id_game) VALUES (%s, %s) 
                ON CONFLICT DO NOTHING;""",
            (dev_id, appid)
        )

    # PUBLISHERS
    for pub in game.get("publishers", []):
        cur.execute(
            "INSERT INTO publishers (publisher_name) VALUES (%s) RETURNING id;",
            (pub,)
        )
        pub_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO publishers_game (id_publisher, id_game) VALUES (%s, %s);",
            (pub_id, appid)
        )

    # CATEGORIES
    for cat in game.get("categories", []):
        cur.execute(
            "INSERT INTO categories (category_name) VALUES (%s) RETURNING id;",
            (cat,)
        )
        cat_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO categories_game (id_category, id_game) VALUES (%s, %s);",
            (cat_id, appid)
        )

    # GENRES
    for gen in game.get("genres", []):
        cur.execute(
            "INSERT INTO genres (genre_name) VALUES (%s) RETURNING id;",
            (gen,)
        )
        gen_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO genres_game (id_genre, id_game) VALUES (%s, %s);",
            (gen_id, appid)
        )
    # SCREENSHOTS (corrigindo erro scrennshots)
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
    tag_dict = game.get("tags", {})
    for tag_name, tag_score in tag_dict.items():
        cur.execute(
            "INSERT INTO tags (tag_name) VALUES (%s) ON CONFLICT (tag_name) DO NOTHING RETURNING id;",
            (str(tag_name),)
        )
        try:
            tag_id = cur.fetchone()[0]
        except:
            tag_id = None

        if tag_id is None:
            cur.execute(
                "SELECT id FROM tags WHERE tag_name = %s;",
                (str(tag_name),)
            )
            tag_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO tags_game (id_tag, id_game, tag_score) VALUES (%s, %s, %s);",
            (tag_id, appid, tag_score)
        )

    for lang in game.get("supported_languages", []):
        cur.execute(
            "INSERT INTO languages (language_name) VALUES (%s) ON CONFLICT (language_name) DO NOTHING RETURNING id;",
            (lang,)
        )
        try:
            lang_id = cur.fetchone()[0]
        except:
            lang_id = None

        if lang_id is None:
            cur.execute(
                "SELECT id FROM languages WHERE language_name = %s;",
                (lang,)
            )
            lang_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO languages_game (id_language, id_game) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
            (lang_id, appid)
        )
    
    for audio_lang in game.get("full_audio_languages", []):
        cur.execute(
            "INSERT INTO audio_languages (audio_language_name) VALUES (%s) ON CONFLICT (audio_language_name) DO NOTHING RETURNING id;",
            (audio_lang,)
        )
        try:
            audio_id = cur.fetchone()[0]
        except:
            audio_id = None

        if audio_id is None:
            cur.execute(
                "SELECT id FROM audio_languages WHERE audio_language_name = %s;",
                (audio_lang,)
            )
            audio_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO audio_languages_game (id_audio, id_game) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
            (audio_id, appid)
        )

# =====================================================================
# IMPORT PRINCIPAL
# =====================================================================
def import_games():
    print("\n📥 Lendo arquivo JSON com ijson...")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Carregando JSON de forma stream
    f = open("games.json", "rb")

    parser = ijson.kvitems(f, "")

    count = 0

    for appid, game in parser:

        try:
            appid = int(appid)
        except:
            continue  # pular erros inesperados

        # INSERIR NA TABELA PRINCIPAL
        insert_game(cur, appid, game)

        # INSERIR NAS TABELAS RELACIONADAS
        insert_related(cur, appid, game)

        count += 1

        # Commit a cada 1000 jogos (muito mais rápido)
        if count % 1000 == 0:
            conn.commit()
            print(f"✔ {count} jogos importados...")

    conn.commit()
    cur.close()
    conn.close()
    f.close()

    print("\n🎉 Importação finalizada com sucesso!")
    print(f"Total importado: {count} jogos.\n")


if __name__ == "__main__":
    import_games()
