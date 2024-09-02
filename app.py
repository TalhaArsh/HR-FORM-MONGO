from flask import Flask, render_template, request, redirect, url_for, flash
import os
from pymongo import MongoClient

def get_db_connection():
    client = MongoClient("mongodb+srv://talhaarshad901:mongowongo@cluster0.71tvv.mongodb.net/")
    return client['formdata']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'your_secret_key'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
#mongowongo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/upload', methods=['POST'])
def upload():
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
            # Debugging: print form data
            print(f'Row {i}: name={name}, institute={institute}, gpa_grade={gpa_grade}, from_date={from_date}, to_date={to_date}, majors={majors}')

            # Validate required fields
            if not institute or not gpa_grade or not from_date or not to_date or not majors:
                flash(f"Please fill out all required fields for row {i}.", 'error')
                error_found = True
                break

            # Handle file upload
            files = request.files.getlist(f'file{i}')
            file_paths = []
            for file in files:
                if file and file.filename != '' and allowed_file(file.filename):
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(file_path)
                    file_paths.append(file_path)
                elif file.filename != '':
                    flash('Invalid file format. Only PDF, JPG, JPEG, PNG files are allowed.', 'error')
                    error_found = True
                    break

            if error_found:
                break

            # Insert the document into MongoDB
            collection.insert_one({
                'name': name,
                'institute': institute,
                'gpa_grade': gpa_grade,
                'from_date': from_date,
                'to_date': to_date,
                'majors': majors,
                'file_paths': file_paths,
                'na': False
            })

    if not error_found:
        flash('Form submitted successfully!', 'success')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port = 5000)
