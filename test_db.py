from database import Database

def testar_conexao():
    try:
        # Tentar criar uma instância do banco de dados
        db = Database()
        print("✅ Conexão com o banco de dados estabelecida com sucesso!")
        
        # Testar uma consulta simples
        with db.conn.cursor() as cursor:
            cursor.execute("SELECT NOW();")
            result = cursor.fetchone()
            print(f"✅ Hora atual do servidor: {result[0]}")
            
        # Testar a criação das tabelas
        print("\nVerificando tabelas...")
        with db.conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tabelas = cursor.fetchall()
            print("✅ Tabelas encontradas:")
            for tabela in tabelas:
                print(f"  - {tabela[0]}")
                
        print("\n🎉 Todos os testes passaram com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco de dados: {str(e)}")

if __name__ == "__main__":
    testar_conexao() 