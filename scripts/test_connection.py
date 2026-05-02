from src.db import get_cursor, close_pool

def main() -> None:
    print("Testando conexão com o Supabase")

    with get_cursor() as cur:
        cur.execute("select version()")
        version = cur.fetchone()
        print(f"\n Conectado ao: {version['version'][:60]}")

        cur.execute("""
            select table_name
            from information_schema.tables
            where table_schema = 'public'
            order by table_name
        """)
        tables = cur.fetchall()

        print(f"\n Tabelas encontradas ({len(tables)}):")
        for t in tables:
            print(f"   - {t['table_name']}")

        
        cur.execute("""
            select column_name, data_type 
            from information_schema.columns
            where table_name = 'subjects'
            order by ordinal_position
        """)
        cols = cur.fetchall()
        print(f"\n Colunas de 'subjects':")
        for c in cols:
            print(f"   - {c['column_name']}: {c['data_type']}")

    close_pool()
    print("\n Tudo certo!")


if __name__ == "__main__":
    main()