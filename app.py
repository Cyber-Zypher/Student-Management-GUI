from flask import Flask, render_template, request, redirect, url_for
import os
import uuid  # to generate unique filenames
import mysql.connector

app = Flask(__name__)

# Replace these values with your MySQL database credentials
db_host = "localhost"
db_user = "root"
db_password ="Database_Password"
db_name = "STUDENT_MANAGEMENT"

# Connect to MySQL
db = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)

cursor = db.cursor()

# Create a 'students' table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        class VARCHAR(50) NOT NULL,
        image_path VARCHAR(255)
    )
""")
db.commit()

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the 'uploads' directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    # Fetch all students from the database
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    return render_template('index.html', students=students)

@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    student_class = request.form['class']

    # Check if the post request has the file part
    if 'image' not in request.files:
        return redirect(request.url)

    image = request.files['image']

    # If the user does not select a file, the browser submits an empty file
    if image.filename == '':
        return redirect(request.url)

    # Generate a unique filename to avoid overwriting existing files
    image_filename = str(uuid.uuid4()) + os.path.splitext(image.filename)[1]
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)

    # Save the uploaded image to the 'uploads' folder
    image.save(image_path.replace('\\', '/'))

    # Insert the new student into the database
    cursor.execute("INSERT INTO students (name, class, image_path) VALUES (%s, %s, %s)", (name, student_class, image_path))
    db.commit()

    return redirect(url_for('index'))

# New route to handle student deletion
@app.route('/delete_student/<int:id>', methods=['POST'])
def delete_student(id):
    cursor.execute("SELECT * FROM students WHERE id = %s", (id,))
    student = cursor.fetchone()

    if student:
        cursor.execute("DELETE FROM students WHERE id = %s", (id,))
        db.commit()

        if os.path.exists(student[3]):
            os.remove(student[3])

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
