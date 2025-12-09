-- CASO VOCÊ TENHA IMPORTADO A VERSÃO ANTERIOR DAS TABELAS: FAÇA ESSE PROCEDIMENTO.
-- Caso nunca tenha importado, descosiderar tudo abaixo.
-- Set de segurança antes de alterar as tabelas.
UPDATE detalhes SET owners_min = 0 WHERE owners_min IS NULL;
UPDATE detalhes SET owners_max = 0 WHERE owners_max IS NULL;
UPDATE detalhes SET peak_ccu = 0 WHERE peak_ccu IS NULL;
UPDATE detalhes SET dlc_count = 0 WHERE dlc_count IS NULL;
UPDATE detalhes SET average_playtime_forever = 0 WHERE average_playtime_forever IS NULL;
UPDATE detalhes SET average_playtime_2weeks = 0 WHERE average_playtime_2weeks IS NULL;
UPDATE detalhes SET median_playtime_forever = 0 WHERE median_playtime_forever IS NULL;
UPDATE detalhes SET median_playtime_2weeks = 0 WHERE median_playtime_2weeks IS NULL;
UPDATE detalhes SET recommendations = 0 WHERE recommendations IS NULL;
UPDATE detalhes SET achievements = 0 WHERE achievements IS NULL;
UPDATE detalhes SET positive = 0 WHERE positive IS NULL;
UPDATE detalhes SET negative = 0 WHERE negative IS NULL;

-------------------------------------------------------
-- Agora, aplicar DEFAULT 0 + NOT NULL
-------------------------------------------------------
ALTER TABLE detalhes ALTER COLUMN owners_min SET DEFAULT 0;
ALTER TABLE detalhes ALTER COLUMN owners_min SET NOT NULL;

ALTER TABLE detalhes ALTER COLUMN owners_max SET DEFAULT 0;
ALTER TABLE detalhes ALTER COLUMN owners_max SET NOT NULL;

ALTER TABLE detalhes ALTER COLUMN peak_ccu SET DEFAULT 0;
ALTER TABLE detalhes ALTER COLUMN peak_ccu SET NOT NULL;

ALTER TABLE detalhes ALTER COLUMN dlc_count SET DEFAULT 0;
ALTER TABLE detalhes ALTER COLUMN dlc_count SET NOT NULL;

ALTER TABLE detalhes ALTER COLUMN average_playtime_forever SET DEFAULT 0;
ALTER TABLE detalhes ALTER COLUMN average_playtime_forever SET NOT NULL;

ALTER TABLE detalhes ALTER COLUMN average_playtime_2weeks SET DEFAULT 0;
ALTER TABLE detalhes ALTER COLUMN average_playtime_2weeks SET NOT NULL;

ALTER TABLE detalhes ALTER COLUMN median_playtime_forever SET DEFAULT 0;
ALTER TABLE detalhes ALTER COLUMN median_playtime_forever SET NOT NULL;

ALTER TABLE detalhes ALTER COLUMN median_playtime_2weeks SET DEFAULT 0;
ALTER TABLE detalhes ALTER COLUMN median_playtime_2weeks SET NOT NULL;

ALTER TABLE detalhes ALTER COLUMN recommendations SET DEFAULT 0;
ALTER TABLE detalhes ALTER COLUMN recommendations SET NOT NULL;

ALTER TABLE detalhes ALTER COLUMN achievements SET DEFAULT 0;
ALTER TABLE detalhes ALTER COLUMN achievements SET NOT NULL;

ALTER TABLE detalhes ALTER COLUMN positive SET DEFAULT 0;
ALTER TABLE detalhes ALTER COLUMN positive SET NOT NULL;

ALTER TABLE detalhes ALTER COLUMN negative SET DEFAULT 0;
ALTER TABLE detalhes ALTER COLUMN negative SET NOT NULL;

-- Nova constraint para estimeted_owners
ALTER TABLE detalhes
ADD CONSTRAINT chk_owners_min_max
CHECK (owners_min <= owners_max);

--Nova tabela para registro do histórico de preços
CREATE TABLE game_price_history (
            id SERIAL PRIMARY KEY,
            id_game INTEGER NOT NULL,
            old_price NUMERIC(10,2),
            new_price NUMERIC(10,2),
            changed_at TIMESTAMP DEFAULT NOW(),
            FOREIGN KEY(id_game) REFERENCES games(appid)
        );
