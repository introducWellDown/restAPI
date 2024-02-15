import psycopg2
from psycopg2 import OperationalError
import ssl
import os
import dotenv
dotenv.load_dotenv()
from function import *

git_token = os.environ.get("git_token")
dbname = os.environ.get("dbname")
user = os.environ.get("user")
password = os.environ.get("password")
host = os.environ.get("host")
port = os.environ.get("port")
sslmode = os.environ.get("sslmode")
sslrootcert = os.environ.get("sslrootcert")


def connect_to_bd(dbname,user,password,host,port,sslmode,sslrootcert):
    # Указание параметров подключения
    try:
        db_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port,
            'sslmode': sslmode,  # Использовать SSL
            'sslrootcert': sslrootcert,  # Путь к корневому SSL сертификату (опционально)
            'sslcert': " ",  # Путь к клиентскому SSL сертификату (опционально)
            'sslkey': " "  # Путь к приватному ключу клиентского SSL сертификата (опционально)
        }

        # Подключение к базе данных
        conn = psycopg2.connect(**db_params)

        # Если подключение прошло успешно, выведите сообщение
        print("Успешное подключение к базе данных!")
        return conn
    except OperationalError as e:
        # Если произошла ошибка подключения, выведите сообщение об ошибке
        print(f"Ошибка подключения к базе данных: {e}")
        conn.close()

conn = connect_to_bd(dbname,user,password,host,port,sslmode,sslrootcert)

def create_table_top100(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS top100 (
                position SERIAL PRIMARY KEY,
                repo TEXT,
                owner TEXT,
                stars INTEGER,
                watchers INTEGER,
                forks INTEGER,
                open_issues INTEGER,
                language TEXT
            )
        """)
        conn.commit()
    except OperationalError as e:
        print(f"Ошибка создания таблицы 'top100': {e}")

def insert_repositories(conn, top_repos_list):
    cursor = conn.cursor()
    try:
        for repo in top_repos_list:
            # Проверка наличия репозитория с таким же именем
            cursor.execute("SELECT repo FROM top100 WHERE repo = %s", (repo['name'],))
            existing_repo = cursor.fetchone()
            if existing_repo:
                # Обновление существующего репозитория
                cursor.execute("""
                    UPDATE top100
                    SET owner = %s, stars = %s, watchers = %s, forks = %s, open_issues = %s, language = %s
                    WHERE repo = %s
                """, (repo['owner'], repo['stars'], repo['watchers'], repo['forks'], repo['open_issues'], repo['lang'], repo['name']))
            else:
                # Вставка нового репозитория
                cursor.execute("""
                    INSERT INTO top100 (repo, owner, stars, watchers, forks, open_issues, language)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (repo['name'], repo['owner'], repo['stars'], repo['watchers'], repo['forks'], repo['open_issues'], repo['lang']))
        conn.commit()
        print("Данные успешно загружены в базу данных!")
    except Exception as e:
        print(f"Ошибка при вставке/изменении данных в базу данных: {e}")
        conn.rollback()
    finally:
        cursor.close()

def export_repositories(conn,sort):
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM top100 ORDER BY {sort} DESC;")
        # Получаем результаты запроса
        rows = cursor.fetchall()
        
        # Преобразуем данные в список
        data_list = []
        for row in rows:
            data_list.append(row)
        
        print("Данные успешно экспортированы в список")
        
        if sort == "language":
            data_list.reverse()
        
        return data_list
    
    except Exception as e:
        print(f"Ошибка при экспорте данных: {e}")
        return None
    
    finally:
        # Закрываем курсор и коммитим транзакцию
        cursor.close()
        conn.commit()
        