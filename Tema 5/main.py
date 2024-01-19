import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DATABASE = "notes.db"

def create_table():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS notes (noteid INTEGER PRIMARY KEY AUTOINCREMENT, note TEXT NOT NULL)")
    connection.commit()
    connection.close()

create_table()

@app.route('/')
def index():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()
    connection.close()
    return render_template('index.html', notes=notes)

@app.route('/create', methods=['POST'])
def create():
    content = request.form.get('content')
    if content:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO notes (note) VALUES (?)", (content,))
        connection.commit()
        connection.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:noteid>', methods=['GET', 'POST'])
def edit(noteid):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    if request.method == 'POST':
        new_content = request.form.get('content')
        cursor.execute("UPDATE notes SET note = ? WHERE noteid = ?", (new_content, noteid))
        connection.commit()
        connection.close()
        return redirect(url_for('index'))
    else:
        cursor.execute("SELECT * FROM notes WHERE noteid = ?", (noteid,))
        note = cursor.fetchone()
        connection.close()
        return render_template('edit.html', note=note)

@app.route('/delete/<int:noteid>')
def delete(noteid):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM notes WHERE noteid = ?", (noteid,))
    connection.commit()
    connection.close()
    return redirect(url_for('index'))

@app.route('/view/<int:noteid>')
def view(noteid):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM notes WHERE noteid = ?", (noteid,))
    note = cursor.fetchone()
    connection.close()
    return render_template('view.html', note=note)

if __name__ == '__main__':
    app.run(debug=True)
