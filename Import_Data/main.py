import import_, create_tables

if __name__ == "__main__":
    try:
        create_tables.create_tables()
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        
    import_.import_games()