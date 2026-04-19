import os

from flask import Flask, render_template, request, redirect, url_for, jsonify
import pymysql as db
from datetime import date

app = Flask(__name__)

conn = db.connect(
    host="mysql-3122869c-abdourahmanbarry7-9e3e.b.aivencloud.com",
    user="avnadmin",
    port=18787,
    password=os.environ.get("DB_PASSWORD"),
    database="defaultdb",
    ssl={"ssl": {}}
)


@app.route("/patients")
def patients():
    cursor = conn.cursor()
    cursor.execute(f"SELECT patient_id, first_name, last_name, dob, gender, phone, gender FROM patient;")
    out = cursor.fetchall()
    return render_template("patients.html", patients=out)

@app.route("/view_patient/<int:patient_id>")
def view_patient(patient_id):
    pass

@app.route("/delete_patient/<int:patient_id>")
def delete_patient(patient_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patient WHERE patient_id = %s", (patient_id,))
    conn.commit()
    cursor.close()
    return jsonify({"success":True, "message":"Works"})

@app.route("/edit_patient/<int:patient_id>")
def edit_patient(patient_id):
    pass

@app.route("/doctors")
def doctors():
    cursor = conn.cursor()
    cursor.execute(f"SELECT doctor_id, first_name, last_name, specialty, email, dept_name FROM doctor;")
    out = cursor.fetchall()
    return render_template("doctors.html", doctors=out)

@app.route("/view_doctor/<int:doctor_id>")
def view_doctor(doctor_id):
    cursor = conn.cursor()
    cursor.execute(f"SELECT doctor_id, first_name, last_name, specialty, email, dept_name FROM doctor WHERE doctor_id={doctor_id};")
    doctor = cursor.fetchone()
    cursor.execute(f"SELECT COUNT(*) FROM patient;")
    total_patients = cursor.fetchone()
    cursor.execute(f"SELECT COUNT(*) FROM appointment WHERE DATE(ap_datetime)=CURDATE();")
    appointments_today = cursor.fetchone()
    cursor.execute(f"SELECT COUNT(*)  FROM admission WHERE doctor_id={doctor_id} AND status='Active';")
    active_admissions = cursor.fetchone()
    cursor.execute(f""" SELECT CONCAT(p.first_name, p.last_name) AS patient_name,
                        DATE(a.ap_datetime) AS date,
                        TIME(ap_datetime) AS time,
                        status
                        FROM patient as p join appointment as a
                        ON p.patient_id=a.patient_id order by ap_datetime;""")
    upcoming_appointments = cursor.fetchall()
    cursor.execute(f"""SELECT CONCAT(p.first_name, p.last_name), ward, room, bed_no, admit_datetime
                       FROM admission AS a join patient AS  p join beds AS b
                       WHERE a.patient_id=p.patient_id and b.admit_id = a.admit_id;""")
    admissions = cursor.fetchall()

    return render_template(
    "doctor_profile.html",
    doctor=doctor,
    total_patients=total_patients,
    appointments_today=appointments_today,
    active_admissions=active_admissions,
    doctor_status="Active",
    on_call_status="No",
    next_available_slot="2026-04-12 10:30 AM",
    upcoming_appointments=upcoming_appointments,
    patients=[],
    admissions=admissions,
    recent_activity=[]
)

@app.route("/delete_doctor/<int:doctor_id>", methods=["POST", "GET"])
def delete_doctor(doctor_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM doctor WHERE doctor_id = %s", (doctor_id,))
    conn.commit()
    cursor.close()
    return jsonify({"success":True, "message":"Works"})

@app.route("/edit_doctor/<int:doctor_id>")
def edit_doctor(doctor_id):
    return render_template("doctors.html")


@app.route("/appointments")
def appointments():
    selected_date = request.args.get("date", date.today().isoformat())
    search = request.args.get("search", "").strip()
    gender = request.args.get("gender", "").strip()
    status = request.args.get("status", "").strip()
    page = max(int(request.args.get("page", 1)), 1)
    per_page = 10
    offset = (page - 1) * per_page
    cursor = conn.cursor(db.cursors.DictCursor)

    doctor_id=2
    where_clauses = ["a.patient_id = p.patient_id", "a.doctor_id = %s"]
    params = [doctor_id]

    if selected_date:
        where_clauses.append("DATE(a.ap_datetime) = %s")
        params.append(selected_date)

    if search:
        where_clauses.append("(p.first_name LIKE %s OR p.last_name LIKE %s OR p.phone LIKE %s)")
        like_value = f"%{search}%"
        params.extend([like_value, like_value, like_value])

    if gender:
        where_clauses.append("p.gender = %s")
        params.append(gender)

    if status:
        where_clauses.append("a.status = %s")
        params.append(status)

    where_sql = " AND ".join(where_clauses)

    # count query for pagination
    count_sql = f"""
        SELECT COUNT(*) AS total_rows
        FROM patient AS p
        JOIN appointment AS a
        WHERE {where_sql}
    """
    cursor.execute(count_sql, params)
    count_result = cursor.fetchone()
    total_rows = count_result["total_rows"] or 0

    total_pages = max((total_rows + per_page - 1) // per_page, 1)


    if page > total_pages:
        page = total_pages
        offset = (page - 1) * per_page

 
    appointments_sql = f"""
        SELECT
            p.first_name,
            p.last_name,
            p.gender,
            p.dob,
            TIME(a.ap_datetime) AS time,
            p.phone,
            a.status
        FROM patient AS p
        JOIN appointment AS a
        WHERE {where_sql}
        ORDER BY a.ap_datetime ASC
        LIMIT %s OFFSET %s
    """
    cursor.execute(appointments_sql, params + [per_page, offset])
    appointments = cursor.fetchall()

    # stats
    cursor.execute(
        "SELECT COUNT(*) AS total_appointments FROM appointment WHERE doctor_id = %s",
        (doctor_id,)
    )
    stats1 = cursor.fetchone()

    cursor.execute(
        "SELECT COUNT(*) AS completed_appointments FROM appointment WHERE doctor_id = %s AND status = 'Completed'",
        (doctor_id,)
    )
    stats2 = cursor.fetchone()

    cursor.execute(
        "SELECT COUNT(*) AS pending_appointments FROM appointment WHERE doctor_id = %s AND status = 'Pending'",
        (doctor_id,)
    )
    stats3 = cursor.fetchone()

    cursor.execute(
        "SELECT COUNT(*) AS cancelled_appointments FROM appointment WHERE doctor_id = %s AND status = 'Cancelled'",
        (doctor_id,)
    )
    stats4 = cursor.fetchone()

    cursor.close()

    start_row = 0 if total_rows == 0 else offset + 1
    end_row = min(offset + per_page, total_rows)
    return render_template(
        "appointments.html",
        appointments=appointments,
        selected_date=selected_date,
        total_appointments=stats1["total_appointments"] or 0,
        completed_appointments=stats2["completed_appointments"] or 0,
        pending_appointments=stats3["pending_appointments"] or 0,
        cancelled_appointments=stats4["cancelled_appointments"] or 0,
        current_search=search,
        current_gender=gender,
        current_status=status,
        current_page=page,
        per_page=per_page,
        total_rows=total_rows,
        total_pages=total_pages,
        start_row=start_row,
        end_row=end_row,
        doctor_id=doctor_id
    )




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


# @app.route("/delete_doctor", methods=["POST"])
# def delete_doctor():
#     doctor_id = request.form["doctor_id"]
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM doctor WHERE doctor_id = %s", (doctor_id,))
#     conn.commit()
#     cursor.close()
#     return redirect(url_for("delete_doctor_form"))


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


# @app.route("/delete_patient", methods=["POST"])
# def delete_patient():
#     patient_id = request.form["patient_id"]
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM patient WHERE patient_id = %s", (patient_id,))
#     conn.commit()
#     cursor.close()
#     return redirect(url_for("delete_patient_form"))


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

@app.route("/doctor_menu")
def doctor_menu():
    return render_template(
        "role_menu.html",
        role_name="Doctor",
        add_url="/add_doctor_form",
        update_url="/update_doctor_form",
        delete_url="/delete_doctor_form"
    )


@app.route("/patient_menu")
def patient_menu():
    return render_template(
        "role_menu.html",
        role_name="Patient",
        add_url="/add_patient_form",
        update_url="/update_patient_form",
        delete_url="/delete_patient_form"
    )


@app.route("/nurse_menu")
def nurse_menu():
    return render_template(
        "role_menu.html",
        role_name="Nurse",
        add_url="/add_nurse_form",
        update_url="/update_nurse_form",
        delete_url="/delete_nurse_form"
    )


@app.route("/admin_menu")
def admin_menu():
    return render_template(
        "role_menu.html",
        role_name="Administrator",
        add_url="/add_admin_form",
        update_url="/update_admin_form",
        delete_url="/delete_admin_form"
    )
if __name__ == "__main__":
    app.run(debug=True)
