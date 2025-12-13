from DML.import_ import import_games
from DDL.create_tables_ import create_tables
from DDL.create_dw_tables_ import create_dw_tables
from CODE.create_functions import create_functions
from CODE.create_procedures import create_procedures
from CODE.create_indexes import create_indexes
from CODE.create_views import create_views
from CODE.create_triggers import create_triggers


if __name__ == "__main__":
    try:
        create_tables()
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
    
    try:
        create_functions()
    except Exception as e:
        print(f"Erro ao criar funções: {e}")
        
    try:
        create_procedures()
    except Exception as e:
        print(f"Erro ao criar procedures: {e}")
        
    try:
        create_indexes()
    except Exception as e:
        print(f"Erro ao criar índices: {e}")
    import_games()

    try:
        create_views()
    except Exception as e:
        print(f"Erro ao criar views: {e}")

    try:
        create_triggers()
    except Exception as e:
        print(f"Erro ao criar triggers: {e}")

    try:
        create_dw_tables()
    except Exception as e:
        print(f"Erro ao criar dw tables: {e}")