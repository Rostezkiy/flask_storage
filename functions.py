import configparser
import psycopg2
import logging

config = configparser.ConfigParser()
config.read('config.ini')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def get_owner(file_hash):
    try:
        postgres_config = get_postgres_config()
        conn = psycopg2.connect(**postgres_config)
        cursor = conn.cursor()
        cursor.execute('SELECT owner FROM files WHERE file_hash = %s;', (file_hash,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return result[0]
        return None
    except Exception as e:
        logging.error(f'An error occurred in get_owner function: {str(e)}')


def add_user(username, password):
    try:
        postgres_config = get_postgres_config()
        conn = psycopg2.connect(**postgres_config)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = %s;", (username,))
        exists = cursor.fetchone()
        if not exists:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s);", (username, password))
            conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f'An error occurred in add_user function: {str(e)}')


def get_postgres_config():
    try:
        postgres_config = {
            'host': config.get('DB', 'host'),
            'port': config.get('DB', 'port'),
            'user': config.get('DB', 'user'),
            'password': config.get('DB', 'password'),
            'dbname': config.get('DB', 'database')
        }
        return postgres_config
    except Exception as e:
        logging.error(f'An error occurred in get_postgres_config function: {str(e)}')


def get_default_postgres_config():
    try:
        postgres_config = {
            'host': config.get('default', 'host'),
            'port': config.get('default', 'port'),
            'user': config.get('default', 'user'),
            'password': config.get('default', 'password'),
            'dbname': config.get('default', 'database')
        }
        return postgres_config
    except Exception as e:
        logging.error(f'An error occurred in get_default_postgres_config function: {str(e)}')


def create_files_table():
    try:
        postgres_config = get_postgres_config()
        conn = psycopg2.connect(**postgres_config)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS files (
                   id SERIAL PRIMARY KEY,
                   file_hash VARCHAR(32) NOT NULL,
                   filename VARCHAR(255) NOT NULL,
                   owner VARCHAR(50) NOT NULL);''')
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f'An error occurred in create_files_table function: {str(e)}')


def create_users_table():
    try:
        postgres_config = get_postgres_config()
        conn = psycopg2.connect(**postgres_config)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                   id SERIAL PRIMARY KEY,
                   username VARCHAR(50) NOT NULL,
                   password VARCHAR(100) NOT NULL);''')
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f'An error occurred in create_users_table function: {str(e)}')

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql

def create_database(database_name):
    try:
        database = config.get('DB', 'database')
        conn = psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host=config.get('DB', 'host'),
                                port=config.get('DB', 'port'))
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        # Check if database exists and create it if not
        cursor.execute("SELECT datname FROM pg_database;")
        list_database = [item[0] for item in cursor.fetchall()]
        if database not in list_database:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database)))
            logging.debug("Creating DB.")
        else:
            logging.debug("DB already created.")
        cursor.close()
        conn.close()
        conn = psycopg2.connect(host=config.get('DB', 'host'),
                                port=config.get('DB', 'port'),
                                dbname=config.get('DB', 'database'),
                                user=config.get('DB', 'user'),
                                password=config.get('DB', 'password'))
        return conn

    except Exception as e:
        logging.error(f'An error occurred in create_database function: {str(e)}')


def get_filename(file_hash):
    try:
        conn = psycopg2.connect(**get_postgres_config())
        cursor = conn.cursor()
        cursor.execute("SELECT filename FROM files WHERE file_hash = %s", (file_hash,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        logging.error(f'An error occurred in get_filename function: {str(e)}')


def check_auth(username, password):
    try:
        postgres_config = get_postgres_config()
        conn = psycopg2.connect(**postgres_config)
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE username = %s;', (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            stored_password = result[0]
            return stored_password == password
        return False
    except Exception as e:
        logging.error(f'An error occurred in check_auth function: {str(e)}')
