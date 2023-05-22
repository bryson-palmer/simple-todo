import sqlite3
import uuid
from flask import Flask, request
import json
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

dirname = os.path.dirname(__file__)  # removes filename from path to just get directory
filename = os.path.join(dirname, '../client/mockData/db.json')


@app.route('/')
def home():
	return 'Flask app is running!!!'

def create_note(request):
    # read in existing notes
    try:
        with open(filename, 'r') as f:
            db = json.load(f)
    except Exception as err:  # catch general exception with either file or json
        print(err)
        db = {'notes': []}
        
    # verify new note has an ID
    note = request.json
    id = note['id']
    if id is None or id == '':
        id = uuid.uuid4().hex # a 32-character lowercase hexadecimal string
        note['id'] = id

    # add note to our notes json, and write back to file
    db['notes'].append(note)
    with open(filename, 'w') as f:
        json.dump(db, f)

    return id

@app.route('/notes', methods=['GET', 'POST'])
def notes():
  if request.method == 'POST':
    # rather than fetching notes, we are creating a new one
    return create_note(request)

  # if we get here, we are fetching all notes
  with open(filename, 'r') as f:
    try:
      db = json.load(f)
    except json.decoder.JSONDecodeError:
      return []
  return db['notes'] if 'notes' in db else db

@app.route('/notes/<id>')
def note(id):
	with open(filename, 'r') as f:
		db = json.load(f)
		notes = db['notes']

		for note in notes:
			if note['id'] == id:
				return note

	return {}

@app.route('/notes/<id>', methods=['DELETE'])
def note_delete(id):
	with open(filename, 'r') as f:
		db = json.load(f)
		notes = db['notes']

	for i, note in enumerate(notes):
		if note['id'] == id:
			del notes[i]
			with open(filename, 'w') as f:
				json.dump(db, f)

			return 'Delete success'

	return 'Delete success'

app.run()