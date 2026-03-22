from flask import Flask, render_template, request, redirect, url_for
import pymysql as db

app = Flask(__name__)

conn = db.connect(
    host="mysql-3122869c-abdourahmanbarry7-9e3e.b.aivencloud.com",
    user="avnadmin",
    port= 18787,
    password="",      # put your password here if any
    database="defaultdb",
    ssl={"ssl": {}}
)

@app.route("/<name>")
def person(name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {name};")
    out = cursor.fetchall()

    result = "<h1>Persons:</h1>"
    for row in out:
        result += "<p>" + ", ".join([str(i) for i in row]) + "</p>"

    cursor.close()
    return result


@app.route("/")
def home():
    return render_template("connection.html")

# @app.route("/update")
# def home():
#     return render_template("update_doctor.html")

# @app.route("/delete")
# def home():
#     return render_template("delete_doctor.html")

# @app.route('/add_doctor')
# def add_doctor():
#     cursor = conn.cursor()
#     cursor.execute("SELECT dept_name FROM department")
#     departments = cursor.fetchall()
#     return render_template("add_doctor.html", departments=departments)

@app.route('/add_doctor',  methods=['POST'])
def add_doctor():
    cursor = conn.cursor()
    doctor_id = request.form['doctor_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    specialty = request.form['specialty']
    email = request.form['email']
    department_name = request.form['department_name']

    cursor.execute("""
        INSERT INTO doctor (doctor_id, first_name, last_name, specialty, email, dept_name)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (doctor_id, first_name, last_name, specialty, email, department_name))

    conn.commit()

    cursor = conn.cursor()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    return render_template("add_doctor.html", departments=departments, success=True)
 


@app.route('/add')
def add():
    cursor = conn.cursor()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    return render_template("add_doctor.html", departments=departments, success=False)


@app.route('/delete_doctor_form')
def delete_doctor_form():
    cursor = conn.cursor()
    cursor.execute("SELECT doctor_id, first_name, last_name FROM doctor")
    doctors = cursor.fetchall()
    cursor.close()
    return render_template("delete_doctor.html", doctors=doctors)

@app.route('/delete_doctor', methods=['POST'])
def delete_doctor():
    doctor_id = request.form['doctor_id']
    cursor = conn.cursor()
    cursor.execute("DELETE FROM doctor WHERE doctor_id = %s", (doctor_id,))
    conn.commit()
    cursor.close()
    return f"Doctor with ID {doctor_id} has been deleted successfully!"


@app.route('/update_doctor_form')
def update_doctor_form():
    cursor = conn.cursor()
    cursor.execute("SELECT doctor_id, first_name, last_name FROM doctor") 
    doctors = cursor.fetchall()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("update_doctor.html", doctors=doctors, departments=departments)

@app.route('/update_doctor', methods=['POST'])
def update_doctor():
    doctor_id = request.form['doctor_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    specialty = request.form['specialty']
    email = request.form['email']
    department_name = request.form['department_name']

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE doctor 
        SET first_name = %s,last_name = %s, specialty = %s, email= %s, dept_name=%s 
        WHERE doctor_id = %s
    """, (first_name, last_name, specialty, email, department_name, doctor_id))
    conn.commit()
    cursor.close()
    return f"Doctor {first_name} updated successfully!"


if __name__ == "__main__":
    app.run(debug=True)
