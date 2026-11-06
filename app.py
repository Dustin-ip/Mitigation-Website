
import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/')
def index():
    if 'role' in session:
        if session['role'] == 'student': return redirect('/student')
        if session['role'] == 'department': return redirect('/department')
        if session['role'] == 'admin': return redirect('/admin')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    session['username'] = request.form['username']
    session['role'] = request.form['role']
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/student', methods=['GET', 'POST'])
def student():
    db = get_db()
    if request.method == 'POST':
        category = request.form['category']
        location = request.form['location']
        person = request.form['person_involved']
        db.execute('INSERT INTO incidents (category, location, person_involved, status) VALUES (?, ?, ?, ?)',
                   (category, location, person, 'Pending'))
        db.commit()
        return redirect('/student')
    
    incidents = db.execute('SELECT * FROM incidents').fetchall()
    return render_template('student.html', incidents=incidents)
    
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    db = get_db()
    if request.method == 'POST':
        incident_id = request.form['incident_id']
        department = request.form['department']
        db.execute('UPDATE incidents SET assigned_dept = ?, status = ? WHERE id = ?', (department, 'Assigned', incident_id))
        db.commit()
        return redirect('/admin')
        
    incidents = db.execute('SELECT * FROM incidents').fetchall()
    return render_template('admin.html', incidents=incidents)

@app.route('/department', methods=['GET', 'POST'])
def department():
    db = get_db()
    if request.method == 'POST':
        incident_id = request.form['incident_id']
        file = request.files.get('photo')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.execute('UPDATE incidents SET status = ?, resolution_photo = ? WHERE id = ?', ('Resolved', filename, incident_id))
            db.commit()
        return redirect('/department')
        
    incidents = db.execute('SELECT * FROM incidents WHERE assigned_dept IS NOT NULL').fetchall()
    return render_template('department.html', incidents=incidents)

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
