Student Management System Documentation
README

This documentation explains how to use and customize the Student Management System. 
The application is built using Flask (a Python framework), MySQL, and HTML/CSS/JavaScript. 
It is designed to manage student registrations, class assignments, performance tracking, and more.

1. Environment Setup

1. Install Python and MySQL on your computer.
2. Create a virtual environment for the project:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install necessary Python dependencies:
   ```
   pip install flask mysql-connector-python flask-cors pandas matplotlib
   ```
5. Set up the database using the provided SQL file (see Database Section below).
6. Start the application:
   ```
   python app.py
   ```
7. Open the app in your browser at `http://127.0.0.1:5000`.

2. Key Features and How They Work

The Student Management System consists of several key features. Here's how they work step by step:


2.1 Admin Login

The admin can log in using hardcoded credentials (`admin/admin123`). 

If the login is successful, the admin is redirected to their dashboard. 
The session keeps the admin logged in while using the app.

2.2 Student Registration

Admins can register new students by filling out a form.
 A unique PEN (Personal Enrollment Number) is 
automatically generated for each student and stored in the database along with their details.

2.3 Class Assignment

Admins can assign students to classes. They select a student using the PEN and choose the class and 
instructor. The database ensures no duplicate assignments are created.

2.4 Student Dashboard

Students can log in using their PEN and view their assigned classes, grades, and attendance records. 
Performance data is fetched from the database dynamically and displayed in an easy-to-read format.

2.5 Performance Chart

Students can download a performance chart as an image. This is generated using Matplotlib and 
visualizes grades for all their enrolled classes.

3. Customizing the Database

You can modify specific parts of the database to fit your needs. Here’s how you can do it:\

3.1 Updating Student Details

To update a student's name or details, use the following SQL command:
```
UPDATE students
SET student_name = 'New Name'
WHERE pen = 'abc123';
```

3.2 Adding or Removing Classes

Add a new class:
```
INSERT INTO classes (class_id, class_name)
VALUES (4, 'Physics');
```
Remove a class (ensure no students are linked):
```
DELETE FROM classes
WHERE class_id = 3;
```

3.3 Assigning Students to Classes

Change the class assigned to a student:
```
UPDATE enrollments
SET class_id = 2
WHERE pen = 'abc123';
```

3.4 Updating Grades and Performance

Record or update grades for a student in a class:
```
UPDATE performance
SET grade = 'A'
WHERE pen = 'abc123' AND class_id = 2;
```

4. Step-by-Step Explanation of app.py

This section explains the Python code in `app.py` step by step.

4.1 Flask App Setup

The application starts by importing necessary modules like Flask, MySQL connector, and libraries for creating charts.

- `Flask`: Framework to build web applications.
- `mysql.connector`: Connects Python to the MySQL database.
- `pandas` and `matplotlib`: Used to generate and display performance charts.

Code snippet:
```python

from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_cors import CORS
import mysql.connector
import secrets
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)
```
**Explanation**:
- `app = Flask(__name__)`: This creates the Flask app instance.
- `app.secret_key`: Ensures sessions are secure.
- `CORS(app)`: Enables cross-origin requests for security.





4.2 Database Connection

The app connects to the MySQL database using `mysql.connector`. 
Update the credentials in the code to match your setup.

Code snippet:
```python
db = mysql.connector.connect(
    host="localhost",
    user="your_username",
    password="your_password",
    database="PENmanagement"
)
```

1. Starting the App (Flask Setup)
Code:
python

from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_cors import CORS
import mysql.connector
import secrets
import pandas as pd
import matplotlib.pyplot as plt
What’s Happening?
We import Flask, the main tool for building the web app.
render_template: Displays HTML pages.
request: Reads user input (like forms).
redirect and url_for: Move the user to different pages.
session: Keeps users logged in.
mysql.connector: Connects Python to the MySQL database.
pandas and matplotlib: Used for creating performance charts.

Code:
python

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)
What’s Happening?
app = Flask(__name__): Creates the Flask app.
app.secret_key: A secret password to secure user sessions.
CORS(app): Allows the app to communicate with other tools securely (not always necessary but helpful).

2. Connecting to the Database
Code:
python
Copy code
db = mysql.connector.connect(
    host="localhost",
    user="your_username",  # Replace with your MySQL username
    password="your_password",  # Replace with your MySQL password
    database="PENmanagement"  # Replace with your database name
)
What’s Happening?
This connects your app to the MySQL database.
Replace "your_username", "your_password", and "PENmanagement" with your database details.



3. Homepage Route
Code:
python

@app.route("/", methods=["GET"])def home():
    return render_template("base.html")
What’s Happening?
@app.route("/"): The app listens for users visiting the homepage (/).
return render_template("base.html"): It shows the base.html file (the homepage).

4. Admin Login
Code:
python

@app.route("/login_admin", methods=["GET", "POST"])def login_admin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("login_admin.html", error="Invalid credentials")
    return render_template("login_admin.html")
What’s Happening?
The login_admin route handles admin login.
request.method: Checks if the user is sending data (POST) or just viewing the page (GET).
Admin credentials are hardcoded: admin/admin123.
If login is successful:
oIt creates a session for the admin (session["admin"] = True).
oRedirects to the admin dashboard.
If login fails:
oReloads the login page and shows an error.

5. Admin Dashboard
Code:
python

@app.route("/admin_dashboard", methods=["GET"])def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("login_admin"))
    return render_template("admin_dashboard.html")
What’s Happening?
Only admins can access this page.
session.get("admin"): Checks if the admin is logged in.
If not logged in, it sends them back to the login page.
If logged in, it shows the admin_dashboard.html file.

6. Registering Students
Code:
python


@app.route("/register_student", methods=["GET", "POST"])def register_student():
    if request.method == "POST":
        data = request.form
        pen = secrets.token_hex(5)
        student_name = data.get("student_name")
        gender = data.get("gender")
        address = data.get("address")
        dob = data.get("dob")
        phone = data.get("phone")

        cursor = db.cursor()
        query = """
            INSERT INTO students (pen, student_name, gender, address, dob, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (pen, student_name, gender, address, dob, phone))
        db.commit()
        return render_template("register_student.html", pen=pen, success="Student registered successfully!")
    return render_template("register_student.html")
What’s Happening?
POST Method: When the admin fills out the form, the app:
oReads the input (e.g., student name, address).
oGenerates a unique PEN (like a student ID) using secrets.token_hex.
oSaves the data into the students table in the database.
If registration is successful, it shows the PEN on the page.

7. Assigning Classes
Code:
python

@app.route("/assign_class", methods=["GET", "POST"])def assign_class():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT class_id, class_name FROM classes")
    classes = cursor.fetchall()
    cursor.execute("SELECT instructor_id, instructor_name FROM instructors")
    instructors = cursor.fetchall()

    if request.method == "POST":
        pen = request.form.get("pen")
        class_id = request.form.get("class_id")
        instructor_id = request.form.get("instructor_id")
        instructor_name = request.form.get("instructor_name")
        
        # Check if the student exists
        check_query = "SELECT * FROM students WHERE pen = %s"
        cursor.execute(check_query, (pen,))
        student = cursor.fetchone()
        if not student:
            return render_template("assign_class.html", classes=classes, instructors=instructors, error="The provided PEN does not exist!")
        
        # Assign the student and instructor to the class
        insert_query = "INSERT INTO enrollments (pen, class_id, enrollment_date) VALUES (%s, %s, CURDATE())"
        cursor.execute(insert_query, (pen, class_id))
        db.commit()
        return render_template("assign_class.html", success="Class assigned successfully!", classes=classes, instructors=instructors)
    return render_template("assign_class.html", classes=classes, instructors=instructors)
What’s Happening?
Admin assigns a class to a student by:
oSelecting a class and instructor.
oEntering the student’s PEN.
The app checks if the student exists.
It saves the assignment into the enrollments table.

8. Student Login and Dashboard
Code:
python

@app.route("/login_student", methods=["GET", "POST"])def login_student():
    if request.method == "POST":
        username = request.form.get("username")
        pen = request.form.get("pen")
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM students WHERE pen = %s"
        cursor.execute(query, (pen,))
        student = cursor.fetchone()
        if student:
            session["student"] = student["pen"]
            return redirect(url_for("student_dashboard"))
        else:
            return render_template("login_student.html", error="Invalid PEN or username")
    return render_template("login_student.html")
What’s Happening?
Students log in using their PEN.
If the PEN exists in the database:
oThe app creates a session for the student and redirects them to their dashboard.
If not, it shows an error.

This is how the main features work
