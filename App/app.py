from flask import Flask, render_template, request, redirect, url_for
import pymysql as db

app = Flask(__name__)

conn = db.connect(
    host="mysql-3122869c-abdourahmanbarry7-9e3e.b.aivencloud.com",
    user="avnadmin",
    port=18787,
    password="",
    database="defaultdb",
    ssl={"ssl": {}}
)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/favicon.ico")
def favicon():
    return "", 204


@app.route("/table/<name>")
def person(name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {name};")
    out = cursor.fetchall()

    result = "<h1>Table Data</h1>"
    for row in out:
        result += "<p>" + ", ".join([str(i) for i in row]) + "</p>"

    cursor.close()
    return result


# DOCTOR ROUTES

@app.route("/add_doctor_form")
def add_doctor_form():
    cursor = conn.cursor()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("add_doctor.html", departments=departments, success=False)


@app.route("/add_doctor", methods=["POST"])
def add_doctor():
    doctor_id = request.form["doctor_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    specialty = request.form["specialty"]
    email = request.form["email"]
    department_name = request.form["department_name"]

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO doctor (doctor_id, first_name, last_name, specialty, email, dept_name)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (doctor_id, first_name, last_name, specialty, email, department_name))
    conn.commit()

    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("add_doctor.html", departments=departments, success=True)


@app.route("/delete_doctor_form")
def delete_doctor_form():
    cursor = conn.cursor()
    cursor.execute("SELECT doctor_id, first_name, last_name FROM doctor")
    doctors = cursor.fetchall()
    cursor.close()
    return render_template("delete_doctor.html", doctors=doctors)


@app.route("/delete_doctor", methods=["POST"])
def delete_doctor():
    doctor_id = request.form["doctor_id"]
    cursor = conn.cursor()
    cursor.execute("DELETE FROM doctor WHERE doctor_id = %s", (doctor_id,))
    conn.commit()
    cursor.close()
    return redirect(url_for("delete_doctor_form"))


@app.route("/update_doctor_form")
def update_doctor_form():
    cursor = conn.cursor()
    cursor.execute("SELECT doctor_id, first_name, last_name FROM doctor")
    doctors = cursor.fetchall()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("update_doctor.html", doctors=doctors, departments=departments, success=False)


@app.route("/update_doctor", methods=["POST"])
def update_doctor():
    doctor_id = request.form["doctor_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    specialty = request.form["specialty"]
    email = request.form["email"]
    department_name = request.form["department_name"]

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE doctor
        SET first_name = %s, last_name = %s, specialty = %s, email = %s, dept_name = %s
        WHERE doctor_id = %s
    """, (first_name, last_name, specialty, email, department_name, doctor_id))
    conn.commit()

    cursor.execute("SELECT doctor_id, first_name, last_name FROM doctor")
    doctors = cursor.fetchall()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("update_doctor.html", doctors=doctors, departments=departments, success=True)


# PATIENT ROUTES

@app.route("/add_patient_form")
def add_patient_form():
    cursor = conn.cursor()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("add_patient.html", departments=departments, success=False)


@app.route("/add_patient", methods=["POST"])
def add_patient():
    patient_id = request.form["patient_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    dob = request.form["dob"]
    gender = request.form["gender"]
    address = request.form["address"]
    phone = request.form["phone"]
    email = request.form["email"]
    department_name = request.form["department_name"]

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patient (patient_id, first_name, last_name, dob, gender, address, phone, email, dept_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (patient_id, first_name, last_name, dob, gender, address, phone, email, department_name))
    conn.commit()

    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("add_patient.html", departments=departments, success=True)


@app.route("/delete_patient_form")
def delete_patient_form():
    cursor = conn.cursor()
    cursor.execute("SELECT patient_id, first_name, last_name FROM patient")
    patients = cursor.fetchall()
    cursor.close()
    return render_template("delete_patient.html", patients=patients)


@app.route("/delete_patient", methods=["POST"])
def delete_patient():
    patient_id = request.form["patient_id"]
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patient WHERE patient_id = %s", (patient_id,))
    conn.commit()
    cursor.close()
    return redirect(url_for("delete_patient_form"))


@app.route("/update_patient_form")
def update_patient_form():
    cursor = conn.cursor()
    cursor.execute("SELECT patient_id, first_name, last_name FROM patient")
    patients = cursor.fetchall()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("update_patient.html", patients=patients, departments=departments, success=False)


@app.route("/update_patient", methods=["POST"])
def update_patient():
    patient_id = request.form["patient_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    dob = request.form["dob"]
    gender = request.form["gender"]
    address = request.form["address"]
    phone = request.form["phone"]
    email = request.form["email"]
    department_name = request.form["department_name"]

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE patient
        SET first_name = %s, last_name = %s, dob = %s, gender = %s,
            address = %s, phone = %s, email = %s, dept_name = %s
        WHERE patient_id = %s
    """, (first_name, last_name, dob, gender, address, phone, email, department_name, patient_id))
    conn.commit()

    cursor.execute("SELECT patient_id, first_name, last_name FROM patient")
    patients = cursor.fetchall()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("update_patient.html", patients=patients, departments=departments, success=True)


# NURSE ROUTES

@app.route("/add_nurse_form")
def add_nurse_form():
    cursor = conn.cursor()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("add_nurse.html", departments=departments, success=False)


@app.route("/add_nurse", methods=["POST"])
def add_nurse():
    nurse_id = request.form["nurse_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    phone = request.form["phone"]
    email = request.form["email"]
    department_name = request.form["department_name"]

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO nurse (nurse_id, first_name, last_name, phone, email, dept_name)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nurse_id, first_name, last_name, phone, email, department_name))
    conn.commit()

    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("add_nurse.html", departments=departments, success=True)


@app.route("/delete_nurse_form")
def delete_nurse_form():
    cursor = conn.cursor()
    cursor.execute("SELECT nurse_id, first_name, last_name FROM nurse")
    nurses = cursor.fetchall()
    cursor.close()
    return render_template("delete_nurse.html", nurses=nurses)


@app.route("/delete_nurse", methods=["POST"])
def delete_nurse():
    nurse_id = request.form["nurse_id"]
    cursor = conn.cursor()
    cursor.execute("DELETE FROM nurse WHERE nurse_id = %s", (nurse_id,))
    conn.commit()
    cursor.close()
    return redirect(url_for("delete_nurse_form"))


@app.route("/update_nurse_form")
def update_nurse_form():
    cursor = conn.cursor()
    cursor.execute("SELECT nurse_id, first_name, last_name FROM nurse")
    nurses = cursor.fetchall()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("update_nurse.html", nurses=nurses, departments=departments, success=False)


@app.route("/update_nurse", methods=["POST"])
def update_nurse():
    nurse_id = request.form["nurse_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    phone = request.form["phone"]
    email = request.form["email"]
    department_name = request.form["department_name"]

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE nurse
        SET first_name = %s, last_name = %s, phone = %s, email = %s, dept_name = %s
        WHERE nurse_id = %s
    """, (first_name, last_name, phone, email, department_name, nurse_id))
    conn.commit()

    cursor.execute("SELECT nurse_id, first_name, last_name FROM nurse")
    nurses = cursor.fetchall()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("update_nurse.html", nurses=nurses, departments=departments, success=True)


# HOSPITAL ADMINISTRATOR ROUTES

@app.route("/add_admin_form")
def add_admin_form():
    cursor = conn.cursor()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("add_admin.html", departments=departments, success=False)


@app.route("/add_admin", methods=["POST"])
def add_admin():
    admin_id = request.form["admin_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    phone = request.form["phone"]
    email = request.form["email"]
    role_name = request.form["role_name"]
    department_name = request.form["department_name"]

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO hospital_administrator
        (admin_id, first_name, last_name, phone, email, role_name, dept_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (admin_id, first_name, last_name, phone, email, role_name, department_name))
    conn.commit()

    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("add_admin.html", departments=departments, success=True)


@app.route("/delete_admin_form")
def delete_admin_form():
    cursor = conn.cursor()
    cursor.execute("SELECT admin_id, first_name, last_name FROM hospital_administrator")
    admins = cursor.fetchall()
    cursor.close()
    return render_template("delete_admin.html", admins=admins)


@app.route("/delete_admin", methods=["POST"])
def delete_admin():
    admin_id = request.form["admin_id"]
    cursor = conn.cursor()
    cursor.execute("DELETE FROM hospital_administrator WHERE admin_id = %s", (admin_id,))
    conn.commit()
    cursor.close()
    return redirect(url_for("delete_admin_form"))


@app.route("/update_admin_form")
def update_admin_form():
    cursor = conn.cursor()
    cursor.execute("SELECT admin_id, first_name, last_name FROM hospital_administrator")
    admins = cursor.fetchall()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("update_admin.html", admins=admins, departments=departments, success=False)


@app.route("/update_admin", methods=["POST"])
def update_admin():
    admin_id = request.form["admin_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    phone = request.form["phone"]
    email = request.form["email"]
    role_name = request.form["role_name"]
    department_name = request.form["department_name"]

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE hospital_administrator
        SET first_name = %s, last_name = %s, phone = %s, email = %s,
            role_name = %s, dept_name = %s
        WHERE admin_id = %s
    """, (first_name, last_name, phone, email, role_name, department_name, admin_id))
    conn.commit()

    cursor.execute("SELECT admin_id, first_name, last_name FROM hospital_administrator")
    admins = cursor.fetchall()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("update_admin.html", admins=admins, departments=departments, success=True)


if __name__ == "__main__":
    app.run(debug=True)