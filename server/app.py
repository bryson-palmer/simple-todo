import sqlite3
import uuid
from flask import Flask, request, session
import json
from flask_cors import CORS
import os
from pprint import pprint

app = Flask(__name__)
CORS(app, supports_credentials=True)

# load secret key from .env file (or create it and then load it)
SECRET_FILE = '.env.local'
if not os.path.exists(SECRET_FILE):
    with open(SECRET_FILE, 'w') as f:
       f.write(f'{os.urandom(24)}')
with open(SECRET_FILE, 'r') as f:
    app.secret_key = f.readline()

dirname = os.path.dirname(__file__)  # removes filename from path to just get directory
filename = os.path.join(dirname, '../client/mockData/db.json')

db_file = os.path.join(dirname, 'app.db')
connection = sqlite3.connect(db_file)

cursor = connection.cursor()
create_notes_table = """
  CREATE TABLE IF NOT EXISTS NOTES(id, title, body, user_id, folder_id)
"""
create_folders_table = """
  CREATE TABLE IF NOT EXISTS FOLDERS(id, folderName)
"""
cursor.execute(create_notes_table)
cursor.execute(create_folders_table)
connection.commit()

# adding folder_id to NOTES existing NOTES table
cursor.execute('PRAGMA user_version')
result = cursor.fetchone()
version = result[0]
print(version)
if version == 0:
   add_folder_to_notes_table = """
     ALTER TABLE NOTES ADD COLUMN folder_id
   """
   cursor.execute(add_folder_to_notes_table)
   cursor.execute(f'PRAGMA user_version = {version + 1}')
   connection.commit()

@app.route('/')
def home():
	return 'Flask app is running!!!'

def create_or_modify_note(request):
    # read in existing notes
    note = request.json
    is_new_note = False
    id = note.get('id') # ID from post request, if updating note
    if id is None or id == '':
        id = uuid.uuid4().hex # a 32-character lowercase hexadecimal string
        note['id'] = id
        is_new_note = True
    
    title = note['title']
    body = note['body']
    folder = note.get('folder')
        
    connection = sqlite3.connect('app.db')
    cursor = connection.cursor()
    if is_new_note:
        cursor.execute(f'INSERT INTO NOTES (id, title, body, user_id, folder_id) VALUES ("{id}", "{title}", "{body}", null, "{folder}")')
    if not is_new_note:
        cursor.execute('UPDATE NOTES SET title="%s", body="%s", folder_id="%s" where id="%s"' % (title, body, folder, id))
    connection.commit()

    return note  # returning full note so it doesn't have to get re-fetched

@app.route('/notes', methods=['GET', 'POST'])
def notes():
  if request.method == 'POST':
    # rather than fetching notes, we are creating a new one
    return create_or_modify_note(request)

  folder_id = request.args.get('folder')  # url just needs a ?folder=<id> appended
  print('folder_id', folder_id)
  # if we get here, we are fetching all notes
  connection = sqlite3.connect('app.db')
  connection.row_factory = sqlite3.Row  # results come back as dictionaries
  cursor = connection.cursor()
  if folder_id:
    cursor.execute('SELECT * FROM NOTES WHERE folder_id="%s"' % (folder_id,))
  else:
    cursor.execute('SELECT * FROM NOTES')
  results = cursor.fetchall()  # [['uadfsdf', 'title', 'body', None], []...]
  notes = []
  for result in results:
    note = dict(result)
    note['folder'] = note['folder_id']  # front end expects 'folder' instead of 'folder_id'
    del note['folder_id']  # unneccesary cleanup of variables
    notes.append(note)

  return notes

@app.route('/notes/<id>', methods=['GET', 'PUT'])
def note(id):
  if request.method == 'PUT':
    return create_or_modify_note(request)
  
  connection = sqlite3.connect('app.db')
  cursor = connection.cursor()
  cursor.execute(f'SELECT * FROM NOTES WHERE id = "{id}"')
  note = cursor.fetchone()
  if note is None:
     return {}  # if ID was invalid
  note_dict = dict(id=note[0], title=note[1], body=note[2], folder=note[4])

  return note_dict

@app.route('/notes/<id>', methods=['DELETE'])
def note_delete(id):
  tuple_ids = tuple(id.split(','))

  connection = sqlite3.connect('app.db')
  cursor = connection.cursor()

  if len(tuple_ids) == 1:
    cursor.execute(f'DELETE FROM NOTES WHERE id = "{tuple_ids[0]}"')
  else:
    cursor.execute(f'DELETE FROM NOTES WHERE id IN {tuple_ids}')
  
  connection.commit()

  return 'Delete success'

@app.route('/folders', methods=['GET', 'POST'])
def folders():
    connection = sqlite3.connect('app.db')
    cursor = connection.cursor()
    if request.method == 'GET':
        cursor.execute('SELECT * FROM FOLDERS')
        results = cursor.fetchall()

        folders=[]
        for result in results:
          (id, folderName) = result
          folder = dict(id=id, folderName=folderName)
          folders.append(folder)
        
        return folders
    
    if request.method == 'POST':
        folder = request.json
        is_new_folder = False
        folder_name = folder['folderName']
        id = folder.get('id')

        if id is None or id == '':
            id = uuid.uuid4().hex # a 32-character lowercase hexadecimal string
            folder['id'] = id
            is_new_folder = True

        if is_new_folder:
            cursor.execute(f'INSERT INTO FOLDERS (id, folderName) VALUES ("{id}", "{folder_name}")')
        if not is_new_folder:
            cursor.execute('UPDATE FOLDERS SET folderName="%s" where id="%s"' % (folder_name, id))
        connection.commit()

        return id

@app.route('/folders/<id>', methods=['DELETE'])
def folder_delete(id):
  tuple_ids = tuple(id.split(','))

  connection = sqlite3.connect('app.db')
  cursor = connection.cursor()

  if len(tuple_ids) == 1:
    cursor.execute(f'DELETE FROM FOLDERS WHERE id = "{tuple_ids[0]}"')
  else:
    cursor.execute(f'DELETE FROM FOLDERS WHERE id IN {tuple_ids}')
  
  connection.commit()

  return 'Delete success'

app.run(debug=True)