from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_cors import CORS
import mysql.connector
import secrets
import pandas as pd  # Import pandas for data handling
import matplotlib.pyplot as plt  # Import matplotlib for generating charts

# Flask app setup
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Enable CORS
CORS(app)

# MySQL Database Configuration
db = mysql.connector.connect(
    host="localhost",
    user="harukidhruv",  # Replace with your MySQL username
    password="My$QLr00t#2024",  # Replace with your MySQL password
    database="PENmanagement"  # Replace with your database name
)

# Routes

@app.route("/", methods=["GET"])
def home():
    return render_template("base.html")  # Base login page (choose Admin/Student)

# Admin Login
@app.route("/login_admin", methods=["GET", "POST"])
def login_admin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Hardcoded admin credentials
        if username == "admin" and password == "admin123":
            session["admin"] = True  # Set admin session
            return redirect(url_for("admin_dashboard"))  # Redirect to admin dashboard
        else:
            return render_template("login_admin.html", error="Invalid credentials")
    
    return render_template("login_admin.html")  # Show login page

# Admin Dashboard
@app.route("/admin_dashboard", methods=["GET"])
def admin_dashboard():
    if not session.get("admin"):  # Check if admin is logged in
        return redirect(url_for("login_admin"))  # Redirect to login page
    return render_template("admin_dashboard.html")  # Render admin dashboard

# Student Login
@app.route("/login_student", methods=["GET", "POST"])
def login_student():
    if request.method == "POST":
        username = request.form.get("username")
        pen = request.form.get("pen")

        # Check if the student exists in the database
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM students WHERE pen = %s"
        cursor.execute(query, (pen,))
        student = cursor.fetchone()

        if student:
            session["student"] = student["pen"]
            return redirect(url_for("student_dashboard"))  # Redirect to student dashboard
        else:
            return render_template("login_student.html", error="Invalid PEN or username")
    return render_template("login_student.html")  # Show student login form

# Register Student
@app.route("/register_student", methods=["GET", "POST"])
def register_student():
    pen = None  # Initialize PEN as None in case the form has not been submitted yet
    if request.method == "POST":
        data = request.form
        pen = secrets.token_hex(5)  # Generate unique PEN
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

        # Return success message along with the PEN generated
        return render_template("register_student.html", pen=pen, success="Student registered successfully!")

    return render_template("register_student.html", pen=pen)

# Assign Class to Students
@app.route("/assign_class", methods=["GET", "POST"])
def assign_class():
    cursor = db.cursor(dictionary=True)

    # Fetch all available classes and instructors
    cursor.execute("SELECT class_id, class_name FROM classes")
    classes = cursor.fetchall()

    cursor.execute("SELECT instructor_id, instructor_name FROM instructors")
    instructors = cursor.fetchall()

    if request.method == "POST":
        data = request.form
        pen = data.get("pen")
        class_id = data.get("class_id")
        instructor_id = data.get("instructor_id")
        instructor_name = data.get("instructor_name")

        # Check if the student exists in the students table
        check_student_query = """
            SELECT * FROM students WHERE pen = %s
        """
        cursor.execute(check_student_query, (pen,))
        student = cursor.fetchone()

        if not student:
            # Return error if the student does not exist
            return render_template("assign_class.html", classes=classes, instructors=instructors, error="The provided PEN does not exist in the student records!")

        # If the instructor is not selected from the list, add a new instructor
        if not instructor_id and instructor_name:
            # Insert the new instructor into the instructors table
            cursor.execute("INSERT INTO instructors (instructor_name) VALUES (%s)", (instructor_name,))
            db.commit()

            # Fetch the newly added instructor_id
            cursor.execute("SELECT instructor_id FROM instructors WHERE instructor_name = %s", (instructor_name,))
            instructor_id = cursor.fetchone()['instructor_id']

        # Check if the student is already enrolled in this class
        check_query = """
            SELECT * FROM enrollments WHERE pen = %s AND class_id = %s
        """
        cursor.execute(check_query, (pen, class_id))
        existing_enrollment = cursor.fetchone()

        if existing_enrollment:
            # Return error if the student is already enrolled in this class
            return render_template("assign_class.html", classes=classes, instructors=instructors, error="This student is already enrolled in the selected class!")

        # Insert the student into the class
        insert_query = """
            INSERT INTO enrollments (pen, class_id, enrollment_date)
            VALUES (%s, %s, CURDATE())
        """
        cursor.execute(insert_query, (pen, class_id))
        db.commit()

        # Insert the instructor into the class_instructors table
        insert_instructor_query = """
            INSERT INTO class_instructors (class_id, instructor_id)
            VALUES (%s, %s)
        """
        cursor.execute(insert_instructor_query, (class_id, instructor_id))
        db.commit()

        # Return success message
        return render_template("assign_class.html", classes=classes, instructors=instructors, success="Student successfully assigned to the class with instructor!")

    return render_template("assign_class.html", classes=classes, instructors=instructors)

# Record Academic Performance
@app.route("/record_performance", methods=["GET", "POST"])
def record_performance():
    cursor = db.cursor(dictionary=True)

    # Fetch all available classes
    cursor.execute("SELECT class_id, class_name FROM classes")
    classes = cursor.fetchall()

    if request.method == "POST":
        data = request.form
        pen = data.get("pen")
        class_id = data.get("class_id")
        grade = data.get("grade")
        attendance = data.get("attendance")

        try:
            query = """
                INSERT INTO performance (pen, class_id, grade, attendance)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (pen, class_id, grade, attendance))
            db.commit()
            return render_template("record_performance.html", classes=classes, success=True)
        except Exception as e:
            return render_template("record_performance.html", classes=classes, error=str(e))

    return render_template("record_performance.html", classes=classes)

# View Student Records
@app.route("/view_student_records", methods=["GET", "POST"])
def view_student_records():
    if request.method == "POST":
        pen = request.form.get("pen")
        if not pen:
            return render_template("view_student_records.html", error="PEN is required.")

        try:
            cursor = db.cursor(dictionary=True)
            print(f"Searching for PEN: {pen}")  # Log the PEN value

            # Modify the query to ensure no duplicates, we can use DISTINCT if needed
            query = """
                SELECT DISTINCT s.student_name, c.class_name, p.grade, p.attendance, i.instructor_name
                FROM students s
                LEFT JOIN enrollments e ON s.pen = e.pen
                LEFT JOIN classes c ON e.class_id = c.class_id
                LEFT JOIN performance p ON e.pen = p.pen AND e.class_id = p.class_id
                LEFT JOIN class_instructors ci ON ci.class_id = c.class_id
                LEFT JOIN instructors i ON ci.instructor_id = i.instructor_id
                WHERE s.pen = %s
            """
            cursor.execute(query, (pen,))
            student_data = cursor.fetchall()
            print(f"Student data fetched: {student_data}")  # Log the query result

            if not student_data:
                return render_template("view_student_records.html", error="No records found for this PEN.")

            return render_template("view_student_records.html", student_data=student_data)

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return render_template("view_student_records.html", error="An error occurred while fetching data.")

    return render_template("view_student_records.html")

# Student Dashboard
@app.route("/student_dashboard", methods=["GET"])
def student_dashboard():
    if "student" not in session:  # Check if the student is logged in
        return redirect(url_for("login_student"))  # Redirect to student login if not authenticated
    
    # Fetch student data (e.g., assigned classes, grades, attendance)
    pen = session["student"]
    cursor = db.cursor(dictionary=True)

    # Fetch basic student info
    query = "SELECT student_name, dob, gender, pen FROM students WHERE pen = %s"
    cursor.execute(query, (pen,))
    student_info = cursor.fetchone()
    print(f"Student Info: {student_info}")  # Debugging the student info

    # Fetch classes and performance using DISTINCT
    query = """
        SELECT DISTINCT c.class_name, p.grade, p.attendance, i.instructor_name
        FROM performance p
        JOIN classes c ON p.class_id = c.class_id
        LEFT JOIN class_instructors ci ON ci.class_id = c.class_id
        LEFT JOIN instructors i ON ci.instructor_id = i.instructor_id
        WHERE p.pen = %s
    """
    cursor.execute(query, (pen,))
    performance_data = cursor.fetchall()
    print(f"Performance Data: {performance_data}")  # Debugging the performance data

    return render_template(
        "student_dashboard.html",  # Ensure this template exists in the templates folder
        student_info=student_info,
        performance_data=performance_data,
    )

# Download Performance Chart
@app.route("/download_performance_chart", methods=["GET"])
def download_performance_chart():
    if "student" not in session:
        return redirect(url_for("login_student"))  # Ensure the student is logged in

    pen = session["student"]
    cursor = db.cursor(dictionary=True)

    # Fetch data for the chart
    query = """
        SELECT c.class_name, p.grade
        FROM performance p
        JOIN classes c ON p.class_id = c.class_id
        WHERE pen = %s
    """
    cursor.execute(query, (pen,))
    performance_data = cursor.fetchall()

    # Use Pandas to handle the performance data
    df = pd.DataFrame(performance_data)

    # Map grades to numeric values using Pandas
    grade_map = {'A': 90, 'B': 80, 'C': 70, 'D': 60, 'F': 50}
    df['grade_numeric'] = df['grade'].map(grade_map)

    # Generate Matplotlib chart
    plt.figure(figsize=(8, 6))
    plt.bar(df['class_name'], df['grade_numeric'], color='skyblue')
    plt.title('Performance Chart')
    plt.xlabel('Classes')
    plt.ylabel('Grades')
    plt.tight_layout()

    # Save the chart to the static folder
    chart_path = "static/performance_chart.png"
    plt.savefig(chart_path)
    plt.close()

    return send_file(chart_path, as_attachment=True)

# Logout
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()  # Clear the session
    return redirect(url_for("home"))  # Redirect to home page

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
