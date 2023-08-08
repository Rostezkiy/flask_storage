# flask_storage
Simple File storage with http access. 
Using basic authentication and Flask.
Sample files included, default users credentials (user/pass): {"admin:admin", "test:test"}. 
Start application: 
  - pip install -r requirements.txt
  - python app.py
*It is assumed that postgres is running.

Docker no tested, but should work.

Examples of cURL:

**upload:** 
curl -X POST -u admin:admin -F 'file=@file1.txt' http://localhost:5000/upload

**download:**
curl -o output_file.txt -u admin:admin http://localhost:5000/download?file_hash=a28dbd7a011cfefcf54edebd969a6c23

**delete:**
curl -X DELETE -u admin:admin "http://localhost:5000/delete?file_hash=a28dbd7a011cfefcf54edebd969a6c23"
