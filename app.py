from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from pymongo import MongoClient
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()
def get_db_connection():
    username = os.getenv('MONGO_USERNAME')
    password = os.getenv('MONGO_PASSWORD')
    client = MongoClient(f"mongodb+srv://{username}:{password}@cluster0.71tvv.mongodb.net/")
    return client['formdata']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.secret_key = 'your_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

# Test credentials
USERNAME = "root"
PASSWORD = "1234"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if 'username' in session:
        return render_template('form.html')
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['username'] = username
            session.permanent = True
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'username' not in session:
        flash('Please log in to continue.', 'error')
        return redirect(url_for('login'))

    db = get_db_connection()
    collection = db['education_background']
    error_found = False

    for i in range(1, 7):
        if not request.form.get(f'na{i}'):
            name = request.form.get(f'name{i}', '')
            institute = request.form.get(f'institute{i}', '')
            gpa_grade = request.form.get(f'gpa{i}', '')
            from_date = request.form.get(f'from_date{i}', '')
            to_date = request.form.get(f'to_date{i}', '')
            majors = request.form.get(f'majors{i}', '')

            if not institute or not gpa_grade or not from_date or not to_date or not majors:
                flash(f"Please fill out all required fields for row {i}.", 'error')
                error_found = True
                break

            # Comment out or remove file processing
            # files = request.files.getlist(f'file{i}')
            # file_paths = []
            # for file in files:
            #     if file and file.filename != '' and allowed_file(file.filename):
            #         file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            #         file.save(file_path)
            #         file_paths.append(file_path)
            #     elif file.filename != '':
            #         flash('Invalid file format. Only PDF, JPG, JPEG, PNG files are allowed.', 'error')
            #         error_found = True
            #         break

            # if error_found:
            #     break

            # Insert data into MongoDB without file paths
            collection.insert_one({
                'name': name,
                'institute': institute,
                'gpa_grade': gpa_grade,
                'from_date': from_date,
                'to_date': to_date,
                'majors': majors,
                'file_paths': 'trial',  # Commented out
                'na': False
            })

    if not error_found:
        flash('Form submitted successfully!', 'success')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port = 5000)
