from flask import Flask, render_template, request, redirect, flash, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Connect to the database
def get_db_connection():
    return mysql.connector.connect(
        user='root',
        password='@Pavi123',
        host='localhost',
        database='student_db'
    )

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        usn = request.form["usn"]
        name = request.form["name"]
        branch = request.form["branch"]
        section = request.form["section"]
        sem = request.form["sem"]
        marks = request.form["marks"]

        if len(usn) != 10:
            flash("USN must be 10 characters", "error")
            return redirect(url_for("index"))
        if not sem.isdigit() or not (1 <= int(sem) <= 8):
            flash("Semester must be between 1 and 8", "error")
            return redirect(url_for("index"))
        if not marks.isdigit() or int(marks) > 100:
            flash("Marks must be less than or equal to 100", "error")
            return redirect(url_for("index"))

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO student_info (usn, name, branch, section, sem, marks)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (usn, name, branch, section, sem, marks))
            conn.commit()
            flash("Student inserted successfully", "success")
        except mysql.connector.IntegrityError:
            flash("USN already exists", "error")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for("index"))

    return render_template("insert.html")

@app.route("/display", methods=["GET", "POST"])
def display():
    student = None
    if request.method == "POST":
        usn = request.form["usn"]
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student_info WHERE usn = %s", (usn,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()
        if not student:
            flash("USN not found", "error")
    return render_template("display.html", student=student)

@app.route("/update", methods=["GET", "POST"])
def update():
    if request.method == "POST":
        usn = request.form["usn"]
        field = request.form["field"]
        new_value = request.form["new_value"]

        allowed_fields = {"name", "branch", "section", "sem", "marks"}
        if field not in allowed_fields:
            flash("Invalid field selected", "error")
            return redirect(url_for("update"))

        if field == "sem" and (not new_value.isdigit() or not (1 <= int(new_value) <= 8)):
            flash("Semester must be between 1 and 8", "error")
            return redirect(url_for("update"))
        if field == "marks" and (not new_value.isdigit() or int(new_value) > 100):
            flash("Marks must be less than or equal to 100", "error")
            return redirect(url_for("update"))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM student_info WHERE usn = %s", (usn,))
        if cursor.fetchone():
            query = f"UPDATE student_info SET {field} = %s WHERE usn = %s"
            cursor.execute(query, (new_value, usn))
            conn.commit()
            flash("Student updated successfully", "success")
        else:
            flash("USN not found", "error")

        cursor.close()
        conn.close()
        return redirect(url_for("update"))

    return render_template("update.html")

@app.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        usn = request.form["usn"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM student_info WHERE usn = %s", (usn,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM student_info WHERE usn = %s", (usn,))
            conn.commit()
            flash(f"USN {usn} deleted", "success")
        else:
            flash("USN not found", "error")

        cursor.close()
        conn.close()
        return redirect(url_for("delete"))

    return render_template("delete.html")

if __name__ == "__main__":
    app.run(debug=True)
