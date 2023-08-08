import logging

import psycopg2
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
import hashlib
import os

from functions import check_auth, get_postgres_config, get_owner, create_database, config, create_users_table, \
    create_files_table, add_user, get_filename

app = Flask(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return 'Unauthorized', 401
        file = request.files['file']
        file_hash = hashlib.md5(file.read()).hexdigest()
        directory = os.path.join('store', file_hash[:2])
        os.makedirs(directory, exist_ok=True)
        filename, ext = os.path.splitext(secure_filename(file.filename))
        new_filename = file_hash + ext
        file_path = os.path.join(directory, new_filename)
        file.seek(0)
        file.save(file_path)
        postgres_config = get_postgres_config()
        conn = psycopg2.connect(**postgres_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (file_hash, filename, owner) VALUES (%s, %s, %s);",
                       (file_hash, new_filename, auth.username))
        conn.commit()
        cursor.close()
        conn.close()
        logging.debug('File uploaded successfully')
        return file_hash
    except Exception as e:
        logging.error(f'An error occurred during file upload: {str(e)}')


def check_file_exists(file_hash):
    result = get_filename(file_hash)
    if not result:
        logging.warning('File not found')
        return 'File not found', 404
    filename = result[0]
    directory = os.path.join('store', file_hash[:2])
    file_path = os.path.join(directory, filename)
    if not os.path.exists(file_path):
        logging.warning('File not found')
        return 'File not found', 404
    return file_path


@app.route('/delete', methods=['DELETE'])
def delete_file():
    try:
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return 'Unauthorized', 401
        file_hash = request.args.get('file_hash')
        file_path = check_file_exists(file_hash)
        owner = get_owner(file_hash)
        if owner != auth.username:
            logging.warning('Permission denied')
            return 'Permission denied', 403
        os.remove(file_path)
        logging.debug('File deleted successfully')
        return 'File deleted successfully'
    except Exception as e:
        logging.error(f'An error occurred during file deletion: {str(e)}')


@app.route('/download', methods=['GET'])
def download_file():
    try:
        file_hash = request.args.get('file_hash')
        file_path = check_file_exists(file_hash)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logging.error(f'An error occurred during file download: {str(e)}')


if __name__ == '__main__':
    create_database(config.get('DB', 'database'))
    create_users_table()
    create_files_table()
    add_user("admin", "admin")
    add_user("user1", "qwerty")
    app.run(debug=False, host='0.0.0.0', port=5000)
