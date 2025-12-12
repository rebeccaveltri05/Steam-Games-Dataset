/* Muitos usuário pesquisam pelo nome do jogo, portanto foi criado um índice para
 essa busca recorrente. Obs: o lower() é para atender o padrão case-sensitive para 
 não diferenciar o modo de escrita do usuário.
 */
CREATE INDEX idx_games_name_lower ON games (lower(name));

/* Muitos usuário filtram jogos pelo preço, por exemplo: jogos acima de 10 reais/dolares, jogos entre 50 a 100 reais, etc.
 Portanto, um índices  na coluna price seria de bom grado para otimizar essas buscas que envolvem preços.
 */
CREATE INDEX idx_games_price ON games (price);

/* Esses índices  tem bons casos de usos para criaçao de dashboards/relatórios e filtragem de jogos mais bem avaliados.
 Evita a demora na busca ordenada também, pois já vem ordenado do maior para o menor.
 */
CREATE INDEX idx_detalhes_metacritic ON detalhes (metacritic_score DESC);
CREATE INDEX idx_detalhes_user_score ON detalhes (user_score DESC);

/*
Como o Postgre não cria índice automaticamente em FK (apenas na PK), 
criamos um índice para cada coluna FK das tabelas com relação (1:N)
,assim melhorando a perfomance dos JOINS.
*/
CREATE INDEX idx_reviews_id_game ON reviews_game (id_game);
CREATE INDEX idx_screenshots_appid ON screenshots (appid);
CREATE INDEX idx_movies_appid ON movies (appid);

/*
Esses são índices inversos nas tabelas associativas. Como a PK composta dessas tabelas
já cobre a busca começando pelo primeiro ID, por exemplo id_tag, esses índices são 
importantes para o cenário oposto: carregar todas as tags, gêneros ou desenvolvedores de 
um determinado jogo buscado pelo seu ID.
Sem eles, carregar a página de detalhes de um jogo seria lento.
*/
CREATE INDEX idx_tags_game_id_game ON tags_game (id_game);
CREATE INDEX idx_genres_game_id_game ON genres_game (id_game);
CREATE INDEX idx_categories_game_id_game ON categories_game (id_game);
CREATE INDEX idx_developers_game_id_game ON developers_game (id_game);
CREATE INDEX idx_publishers_game_id_game ON publishers_game (id_game);
CREATE INDEX idx_languages_game_id_game ON languages_game (id_game);
CREATE INDEX idx_audio_languages_game_id_game ON audio_languages_game (id_game);
CREATE INDEX idx_operation_systems_games_id_game ON operation_systems_games (id_game);

/*
Facilita a busca textual e filtros por entidades específicas (ex: clicar no nome 
da "Ubisoft" e ver todos os jogos dela, ou filtrar por gênero RPG).
Novamente, o lower() garante que a busca funcione independente da maneira escrita.
*/
CREATE INDEX idx_developers_name_lower ON developers (lower(developer_name));
CREATE INDEX idx_publishers_name_lower ON publishers (lower(publisher_name));
CREATE INDEX idx_categories_name_lower ON categories (lower(category_name));
CREATE INDEX idx_genres_name_lower ON genres (lower(genre_name));
CREATE INDEX idx_tags_name_lower ON tags (lower(tag_name));
CREATE INDEX idx_author_name_lower ON author (lower(author_name));

/*
Tabelas de histórico crescem indefinidamente. O índice no id_game é essencial 
para traçar a evolução de preço de um jogo específico sem varrer o histórico inteiro.
O índice na data (changed_at) ajuda em relatórios datados.
*/
CREATE INDEX idx_price_history_id_game ON game_price_history (id_game);
CREATE INDEX idx_price_history_date ON game_price_history (changed_at DESC);


/*
 Criado index para as tabelas de languages e audio_language_game buscando pelo nome do idioma, assim facilitando 
 a busca através dos nomes do idioma.
 */
CREATE INDEX idx_language_name_lower ON languages (lower(language_name));
CREATE INDEX idx_audio_language_name_lower ON audio_languages (lower(audio_language_name));

-- Não foi criado para tabela operation_systems devido ela ter somente 3 registros.