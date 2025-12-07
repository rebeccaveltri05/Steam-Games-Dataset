# Explicação da Normalização

A tabela games, que antes da normalização era uma tabela única com todas as informações
em suas colunas, foi desmembrada. Atributos vinculados à tabela games se tornaram tabelas
próprias, e algumas foram conectadas conforme as necessidades de cada atributo através de
IDs (relacionamentos). Após o processo, o banco de dados passou a ter 21 tabelas.

Regras Aplicadas:
- Normalização de colunas multivaloradas;
- Criação de tabela 1:1 para detalhamento dos games;
- Criação de tabelas associativas com relacionamento M:N;
- Criação de tabelas associativas com relacionamento 1:N;

## Tabelas criadas e funções relacionais

### Tabelas Entidades (Entidades Forte)
 - games
 - operation_systems
 - author
 - developers
 - publisher
 - category
 - genres
 - tags
 - languages
 - audio_languages
 - screenshots 
 - movies 
### Tabelas associativas (Tabelas de Junção, M:N)

- developers_game
- publishers_game
- categories_game
- genres_game
- tags_game
- languages_game
- audio_languages_game
- operation_systems_games
- reviews_game

### Tabelas associativas (Relacionamentos 1:1 )
- detalhes

## Motivos para criação das tabelas

#### Tabelas: author, developers, publisher, category, genres, tags, languages, audio_languages, screenshots, movies
- Essas tabelas foram criadas porque apresentavam valores multivalorados na tabela base.

#### Tabelas: developers_game, publishers_game, categories_game, genres_game, tags_game, languages_game, audio_languages_game, operation_systems_games, reviews_game 
- Essas tabelas foram criadas para permitir a relação entre duas tabelas fortes.

#### Tabela: detalhe
- Essa tabela foi criada para extender colunas da tabela games (base), apresentando métricas e informações secundárias sobre o game.

### Colunas modificadas
- Na tabela detalhes: 
estimated_owners foi renomeada e dividida em owners_min e owners_max por ser uma coluna multivalorada com valores máximos e mínimos de usuários, o que dificultaria o select.

score_rank - alterado o tipo de dado de TEXT para INTEGER.

- Na tabela games:

release_date - alterado o tipo de dado de TEXT para DATE.

- Nas colunas em que a constrain NOT NULL foi removida, a ausência de valores não alterava a integridade dos dados.

- Nas tabelas associativas, a constrain UNIQUE foi acrescentada pois determinados valores deveriam existir uma única vez na tabela, sem duplicidade.

- 