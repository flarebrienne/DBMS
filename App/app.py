import os
from datetime import date

import pymysql as db
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from model.appointments import appointment_data
from model.patient_profile_data import *


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "thisismysecretkey")

conn = db.connect(
    host="mysql-3122869c-abdourahmanbarry7-9e3e.b.aivencloud.com",
    user="avnadmin",
    port=18787,
    password=os.environ.get("DB_PASSWORD"),
    database="defaultdb",
    ssl={"ssl": {}}
)


# @app.route("/view_patient/<int:patient_id>")
# def view_patient(patient_id):
#     pass

@app.route("/delete_patient/<int:patient_id>")
def delete_patient(patient_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patient WHERE patient_id = %s", (patient_id,))
    conn.commit()
    cursor.close()
    return jsonify({"success":True, "message":"Works"})

# @app.route("/edit_patient/<int:patient_id>")
# def edit_patient(patient_id):
#     pass

# @app.route("/doctors")
# def doctors():
#     cursor = conn.cursor()
#     cursor.execute(f"SELECT doctor_id, first_name, last_name, specialty, email, dept_name FROM doctor;")
#     out = cursor.fetchall()
#     return render_template("doctors.html", doctors=out)


# @app.route("/", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         role = request.form.get("role")
#         email = request.form.get("email")
#         password = request.form.get("password")

#         cursor = conn.cursor(db.cursors.DictCursor)

#         if role == "admin":
#             cursor.execute("""
#                 SELECT * FROM hospital_administrator
#                 WHERE email = %s
#             """, (email,))
#             user = cursor.fetchone()

#             if user:
#                 session["user_id"] = user["admin_id"]
#                 session["role"] = "Admin"
#                 user["first_name"] + " " + user["last_name"]
#                 return redirect(url_for("admin_dashboard"))

#         elif role == "doctor":
#             cursor.execute("""
#                 SELECT * FROM doctor
#                 WHERE email = %s
#             """, (email,))
#             user = cursor.fetchone()

#             if user:
#                 session["user_id"] = user["doctor_id"]
#                 session["role"] = "Doctor"
#                 session["username"] = user["first_name"] + " " + user["last_name"]
#                 return redirect(url_for("doctor_dashboard", doctor_id=user["doctor_id"]))

#         return "Invalid login"

#     return render_template("login.html")

@app.route("/delete_doctor/<int:doctor_id>", methods=["POST", "GET"])
def delete_doctor(doctor_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM doctor WHERE doctor_id = %s", (doctor_id,))
    conn.commit()
    cursor.close()
    return jsonify({"success":True, "message":"Works"})

# @app.route("/edit_doctor/<int:doctor_id>")
# def edit_doctor(doctor_id):
#     return render_template("doctors.html")

@app.route("/admitted-patients")
def admitted_patients():
    search = request.args.get("search", "")
    gender = request.args.get("gender", "")
    status = request.args.get("status", "")
    page = int(request.args.get("page", 1))
    per_page = 10
    offset = (page - 1) * per_page

    doctor_id = session["user_id"]

    query = f"""
        SELECT 
            a.admit_id,
            p.patient_id,
            p.first_name,
            p.last_name,
            p.gender,
            p.dob,
            p.phone,
            a.admit_datetime AS admission_date,
            a.status,
            d.first_name AS doctor_first_name,
            d.last_name AS doctor_last_name,
            dept.dept_name,
            b.bed_no
        FROM admission a
        JOIN patient p ON a.patient_id = p.patient_id
        JOIN doctor d ON a.doctor_id = d.doctor_id
        JOIN department dept ON d.dept_name = dept.dept_name
        JOIN beds b ON a.admit_id = b.admit_id
        WHERE d.doctor_id = {doctor_id}
    """

    count_query = """
        SELECT COUNT(*) AS total
        FROM admission a
        JOIN patient p ON a.patient_id = p.patient_id
        JOIN doctor d ON a.doctor_id = d.doctor_id
        JOIN department dept ON d.dept_name = dept.dept_name
        JOIN beds b ON a.admit_id = b.admit_id
        WHERE 1 = 1
    """

    params = []

    if search:
        query += " AND (p.first_name LIKE %s OR p.last_name LIKE %s OR p.phone LIKE %s)"
        count_query += " AND (p.first_name LIKE %s OR p.last_name LIKE %s OR p.phone LIKE %s)"
        search_value = f"%{search}%"
        params.extend([search_value, search_value, search_value])

    if gender:
        query += " AND p.gender = %s"
        count_query += " AND p.gender = %s"
        params.append(gender)

    if status:
        query += " AND a.status = %s"
        count_query += " AND a.status = %s"
        params.append(status)

    query += """
        ORDER BY a.admit_datetime DESC
        LIMIT %s OFFSET %s
    """

    cursor = conn.cursor(db.cursors.DictCursor)

    cursor.execute(count_query, params)
    total_rows = cursor.fetchone()["total"]

    cursor.execute(query, params + [per_page, offset])
    admitted_patients = cursor.fetchall()

    cursor.close()

    total_pages = (total_rows + per_page - 1) // per_page
    start_row = offset + 1 if total_rows > 0 else 0
    end_row = min(offset + per_page, total_rows)

    return render_template(
        "admitted_patients.html",
        admitted_patients=admitted_patients,
        current_search=search,
        current_gender=gender,
        current_status=status,
        current_page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_rows=total_rows,
        start_row=start_row,
        end_row=end_row,
        active_tab="admission",
        role=session["role"],
        username=session["username"]
    )


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
        doctor_id=doctor_id,
        role=session["role"],
        username=session["username"]
    )

@app.route("/patients")
def patients():
    search = request.args.get("search", "")
    gender = request.args.get("gender", "")
    page = int(request.args.get("page", 1))

    per_page = 10
    offset = (page - 1) * per_page

    cursor = conn.cursor(db.cursors.DictCursor)

    doctor_id = session["user_id"]

    doctor_query = """
        SELECT doctor_id, first_name, last_name
        FROM doctor
        WHERE doctor_id = %s
    """
    cursor.execute(doctor_query, (doctor_id,))
    doctor = cursor.fetchone()

    if not doctor:
        cursor.close()
        return "Doctor not found", 404

    base_query = """
        FROM patient
        WHERE 1 = 1
    """

    params = []

    if search:
        base_query += """
            AND (
                first_name LIKE %s
                OR last_name LIKE %s
                OR phone LIKE %s
                OR email LIKE %s
            )
        """
        search_value = f"%{search}%"
        params.extend([search_value, search_value, search_value, search_value])

    if gender:
        base_query += " AND gender = %s"
        params.append(gender)

    count_query = "SELECT COUNT(*) AS total " + base_query

    patients_query = """
        SELECT 
            patient_id,
            first_name,
            last_name,
            gender,
            dob,
            phone,
            email
    """ + base_query + """
        ORDER BY patient_id DESC
        LIMIT %s OFFSET %s
    """

    cursor.execute(count_query, params)
    total_rows = cursor.fetchone()["total"]

    cursor.execute(patients_query, params + [per_page, offset])
    patients = cursor.fetchall()

    stats_query = f"""
        SELECT
            COUNT(*) AS total_patients,

            (
                SELECT COUNT(DISTINCT patient_id)
                FROM doc_patients
                WHERE doctor_id = %s
            ) AS appointment_patients,

            (
                SELECT COUNT(DISTINCT patient_id)
                FROM admission
                WHERE doctor_id = %s
            ) AS admitted_patients_count
        FROM doc_patients WHERE doctor_id={doctor_id};
    """

    cursor.execute(stats_query, (doctor_id, doctor_id))
    stats = cursor.fetchone()

    upcoming_query = """
        SELECT COUNT(*) AS upcoming_appointments
        FROM appointment
        WHERE doctor_id = %s
        AND ap_datetime >= NOW() AND status='Pending'
    """

    cursor.execute(upcoming_query, (doctor_id,))
    upcoming_appointments = cursor.fetchone()["upcoming_appointments"]

    cursor.close()

    total_pages = (total_rows + per_page - 1) // per_page
    start_row = offset + 1 if total_rows > 0 else 0
    end_row = min(offset + per_page, total_rows)

    return render_template(
        "patients.html",
        doctor=doctor,
        patients=patients,
        current_search=search,
        current_gender=gender,
        current_page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_rows=total_rows,
        start_row=start_row,
        end_row=end_row,
        total_patients=stats["total_patients"],
        appointment_patients=stats["appointment_patients"],
        admitted_patients_count=stats["admitted_patients_count"],
        upcoming_appointments=upcoming_appointments,
        role=session["role"],
        username=session["username"]
    )

@app.route("/doctor-dashboard")
def doctor_dashboard():
    doctor_id = session["user_id"]
    cursor = conn.cursor(db.cursors.DictCursor)

    # stats: today's appointments
    cursor.execute("""
        SELECT COUNT(*) AS today_appointments
        FROM appointment
        WHERE doctor_id = %s
          AND DATE(ap_datetime) = CURDATE()
    """, (doctor_id,))
    today_appointments = cursor.fetchone()["today_appointments"]

    # stats: distinct patients seen by this doctor
    cursor.execute("""
        SELECT COUNT(DISTINCT patient_id) AS total_patients
        FROM appointment
        WHERE doctor_id = %s
    """, (doctor_id,))
    total_patients = cursor.fetchone()["total_patients"]

    # stats: prescriptions this month
    cursor.execute("""
        SELECT COUNT(*) AS month_prescriptions
        FROM prescription
        WHERE doctor_id = %s
          AND YEAR(prescribed_datetime) = YEAR(CURDATE())
          AND MONTH(prescribed_datetime) = MONTH(CURDATE())
    """, (doctor_id,))
    month_prescriptions = cursor.fetchone()["month_prescriptions"]

    # stats: lab tests this month
    cursor.execute("""
        SELECT COUNT(*) AS month_lab_tests
        FROM laboratory_test
        WHERE doctor_id = %s
          AND YEAR(ordered_datetime) = YEAR(CURDATE())
          AND MONTH(ordered_datetime) = MONTH(CURDATE())
    """, (doctor_id,))
    month_lab_tests = cursor.fetchone()["month_lab_tests"]

    # recent patients from latest appointments for this doctor
    cursor.execute("""
        SELECT
            p.patient_id,
            p.first_name,
            p.last_name,
            p.gender,
            TIMESTAMPDIFF(YEAR, p.dob, CURDATE()) AS age,
            p.phone,
            p.phone as dept_name,
            MAX(a.ap_datetime) AS last_seen
        FROM patient p
        JOIN appointment a ON a.patient_id = p.patient_id
        WHERE a.doctor_id = %s
        GROUP BY p.patient_id, p.first_name, p.last_name, p.gender, p.dob, p.phone, p.phone
        ORDER BY last_seen DESC
        LIMIT 4
    """, (doctor_id,))
    recent_patients = cursor.fetchall()

    # recent prescriptions
    cursor.execute("""
        SELECT
            CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
            DATE_FORMAT(pr.prescribed_datetime, '%%b %%d, %%Y') AS prescribed_date,
            CASE
                WHEN CHAR_LENGTH(pr.dosage_instruction) > 40
                THEN CONCAT(LEFT(pr.dosage_instruction, 40), '...')
                ELSE pr.dosage_instruction
            END AS dosage_preview
        FROM prescription pr
        JOIN patient p ON pr.patient_id = p.patient_id
        WHERE pr.doctor_id = %s
        ORDER BY pr.prescribed_datetime DESC
        LIMIT 4
    """, (doctor_id,))
    recent_prescriptions = cursor.fetchall()

    # today's schedule
    cursor.execute("""
        SELECT
            DATE_FORMAT(a.ap_datetime, '%%h:%%i %%p') AS time,
            CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
            a.reason,
            a.status
        FROM appointment a
        JOIN patient p ON a.patient_id = p.patient_id
        WHERE a.doctor_id = %s
          AND DATE(a.ap_datetime) = CURDATE()
        ORDER BY a.ap_datetime ASC
        LIMIT 5
    """, (doctor_id,))
    today_schedule = cursor.fetchall()

    cursor.close()

    stats = {
        "today_appointments": today_appointments or 0,
        "total_patients": total_patients or 0,
        "month_prescriptions": month_prescriptions or 0,
        "month_lab_tests": month_lab_tests or 0,
    }

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_patients=recent_patients,
        recent_prescriptions=recent_prescriptions,
        today_schedule=today_schedule,
        active_tab="dashboard",
        role=session["role"],
        username=session["username"]
    )




@app.route("/patient/<patient_id>/appointments")
def patient_appointments(patient_id):
    doctor_id = session["user_id"]
    appointment = appointment_data(db=db, conn=conn, patient_id=patient_id, doctor_id=doctor_id) 
    patients_profile = patient_profile_data(db, conn, patient_id)
    adm = admission(db, conn, patient_id);
    stats = patient_statistics(db, conn, patient_id)
    return render_template(
                "patient_appointments.html", 
                upcoming_appointments=appointment["upcoming_appointments"], 
                past_appointments = appointment["past_appointments"], 
                patient=patients_profile,
                stats=stats,
                active_tab="appointments",
                role=session["role"],
                username=session["username"]
        )


@app.route("/patient/<patient_id>/admissions")
def patient_admissions(patient_id):
    doctor_id = 2;
    patients_profile = patient_profile_data(db, conn, patient_id)
    adm = admission(db, conn, patient_id);
    return render_template("patient_admissions.html", admissions=adm, patient=patients_profile, role=session["role"],
                username=session["username"], active_tab="admissions")

@app.route("/patient/<patient_id>/medical-records")
def patient_medical_records(patient_id):
    doctor_id = 2;
    patients_profile = patient_profile_data(db, conn, patient_id)
    records = medical_record(db, conn, patient_id)
    return render_template("patient_medical_records.html", medical_records=records, patient=patients_profile, role=session["role"],
                username=session["username"], active_tab="medical_records")

@app.route("/patient/<int:patient_id>/add-note", methods=["POST"])
def add_note(patient_id):
    note_text = request.form.get("note_text", "").strip()
    note_type = request.form.get("note_type", "").strip()

    if not note_text:
        return redirect(url_for("patient_medical_records", patient_id=patient_id))

    nurse_id = 1  # replace later with logged-in nurse/admin ID

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO medical_record_notes
        (note_text, note_type, date_time, patient_id, nurse_id)
        VALUES (%s, %s, NOW(), %s, %s)
    """, (note_text, note_type, patient_id, nurse_id))

    conn.commit()
    cursor.close()

    return redirect(url_for("patient_medical_records", patient_id=patient_id))

@app.route("/patient/<int:patient_id>/add-appointment", methods=["POST"])
def add_appointment(patient_id):
    ap_datetime = request.form.get("ap_datetime")
    doctor_id = session["user_id"]
    reason = request.form.get("reason")

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO appointment
        (ap_datetime, reason, status, patient_id, doctor_id, dept_name)
        VALUES (%s, %s, 'Pending', %s, %s,
               (SELECT dept_name FROM doctor WHERE doctor_id = %s))
    """, (ap_datetime, reason, patient_id, doctor_id, doctor_id))

    conn.commit()
    cursor.close()

    return redirect(request.referrer)

@app.route("/patient/<int:ap_id>/cancel_appointment", methods=["POST"])
def cancel_appointment(ap_id):
    doctor_id = session["user_id"]

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE appointment
        SET status = 'Cancelled'
        WHERE ap_id = %s
    """, (ap_id,))

    conn.commit()
    cursor.close()

    return redirect(request.referrer)

@app.route("/patient/<patient_id>/prescriptions")
def patient_prescriptions(patient_id):
    profile = patient_profile_data(db, conn, patient_id)

    cursor = conn.cursor(db.cursors.DictCursor)

    cursor.execute("""
        SELECT
            DATE(prescribed_datetime) AS prescribed_datetime,
            CONCAT('Dr ', d.first_name, ' ', d.last_name) AS doctor_name,
            p.dosage_instruction,
            p.start_date,
            p.end_date
        FROM prescription p
        LEFT JOIN doctor d ON d.doctor_id = p.doctor_id
        WHERE p.patient_id = %s
        ORDER BY p.prescribed_datetime DESC
    """, (patient_id,))

    prescriptions = cursor.fetchall()
    cursor.close()

    return render_template(
        "patient_prescriptions.html",
        patient=profile,
        prescriptions=prescriptions,
        role=session["role"],
        username=session["username"],
        active_tab="prescriptions"
    )

@app.route("/patient/<int:patient_id>/create-prescription", methods=["POST"])
def create_prescription(patient_id):
    doctor_id = request.form.get("doctor_id")
    dosage_instruction = request.form.get("dosage_instruction")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO prescription
        (dosage_instruction, start_date, end_date, patient_id, doctor_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (dosage_instruction, start_date, end_date, patient_id, doctor_id))

    conn.commit()
    cursor.close()

    return redirect(url_for("patient_prescriptions", patient_id=patient_id))
    

@app.route("/patient/<int:patient_id>/lab-tests")
def patient_lab_tests(patient_id):
    profile = patient_profile_data(db, conn, patient_id)
    tests = lab_test_data(db, conn, patient_id)

    return render_template(
        "patient_lab_tests.html",
        patient=profile,
        reviewed_lab_tests=tests["reviewed_lab_tests"],
        unreviewed_lab_tests = tests["unreviewed_lab_tests"],
        pending_lab_tests=tests["pending_lab_tests"],
        active_tab="lab_tests",
        role=session["role"]
    )

@app.route("/patient/<int:patient_id>/lab-tests/<int:test_id>/add-result", methods=["POST"])
def add_lab_result(patient_id, test_id):
    results = request.form.get("results")

    cursor = conn.cursor(db.cursors.DictCursor)

    cursor.execute("""
        UPDATE laboratory_test
        SET results = %s
        WHERE test_id = %s
        AND patient_id = %s
    """, (results, test_id, patient_id))

    conn.commit()
    cursor.close()

    return redirect(url_for("patient_lab_tests", patient_id=patient_id))


@app.route("/patient/<int:patient_id>/lab-tests/<int:test_id>/review", methods=["POST"])
def review_lab_test(patient_id, test_id):
    mark_lab_test_reviewed(db, conn, patient_id, test_id)
    return redirect(url_for("patient_lab_tests", patient_id=patient_id))



# @app.route("/patient/<patient_id>/notes")
# def patient_notes(patient_id):
#     return render_template("patient_notes.html", active_tab="notes")

# @app.route("/patient/<patient_id>/billing")
# def patient_billing(patient_id):
#     return render_template("patient_billing.html", active_tab="billing")


def fetch_departments():
    cursor = conn.cursor()
    cursor.execute("SELECT dept_name FROM department ORDER BY dept_name")
    departments = cursor.fetchall()
    cursor.close()
    return departments


def logged_in_user_name(user):
    return f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()


def require_login():
    return "user_id" in session


def normalize_phone(phone_value):
    if phone_value is None:
        return None
    phone_value = str(phone_value).strip()
    if phone_value == "":
        return None
    return phone_value


def password_matches(stored_hash, password):
    if not stored_hash:
        return False

    stored_hash = str(stored_hash).strip()
    password = str(password).strip()

    if stored_hash == password:
        return True

    try:
        return check_password_hash(stored_hash, password)
    except Exception:
        return False


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role", "").strip().lower()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        role_map = {
            "doctor": {
                "table": "doctor",
                "id_col": "doctor_id",
                "dashboard": "doctor_dashboard",
                "label": "Doctor"
            },
            "nurse": {
                "table": "nurse",
                "id_col": "nurse_id",
                "dashboard": "nurse_dashboard",
                "label": "Nurse"
            },
            "patient": {
                "table": "patient",
                "id_col": "patient_id",
                "dashboard": "patient_dashboard",
                "label": "Patient"
            },
            "admin": {
                "table": "Hospital_Administrator",
                "id_col": "admin_id",
                "dashboard": "admin_dashboard",
                "label": "Admin"
            }
        }

        if role not in role_map:
            flash("Please select a valid role.")
            return redirect(url_for("login"))

        cursor = conn.cursor(db.cursors.DictCursor)
        table = role_map[role]["table"]
        id_col = role_map[role]["id_col"]

        query = f"SELECT * FROM {table} WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        cursor.close()

        if not user:
            flash("No account found for this email.")
            return redirect(url_for("login"))

        saved_password = user.get("password_hash")

        if not password_matches(saved_password, password):
            flash("Invalid email or password.")
            return redirect(url_for("login"))

        session["user_id"] = user[id_col]
        session["role"] = role_map[role]["label"]
        session["username"] = logged_in_user_name(user)
        if role == "doctor":
            return redirect(url_for("doctor_dashboard", doctor_id=session["user_id"]))
        else:
            return redirect(url_for(role_map[role]["dashboard"]))

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        role = request.form.get("role", "").strip().lower()
        user_id = request.form.get("user_id", "").strip()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = normalize_phone(request.form.get("phone"))
        password = request.form.get("password", "").strip()

        dept_name = request.form.get("dept_name", "").strip()
        specialty = request.form.get("specialty", "").strip()
        role_name = request.form.get("role_name", "").strip()
        dob = request.form.get("dob", "").strip()
        gender = request.form.get("gender", "").strip()
        address = request.form.get("address", "").strip()

        if not role or not user_id or not first_name or not last_name or not email or not password:
            flash("Please fill in all required fields.")
            return redirect(url_for("signup"))

        if role in ["doctor", "nurse", "admin"] and not dept_name:
            flash("Please select a department.")
            return redirect(url_for("signup"))

        password_hash = generate_password_hash(password, method="pbkdf2:sha256")
        cursor = conn.cursor()

        try:
            if role == "doctor":
                cursor.execute("""
                    INSERT INTO doctor
                    (doctor_id, first_name, last_name, specialty, email, dept_name, password_hash)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id,
                    first_name,
                    last_name,
                    specialty or None,
                    email,
                    dept_name,
                    password_hash
                ))

            elif role == "nurse":
                cursor.execute("""
                    INSERT INTO nurse
                    (nurse_id, first_name, last_name, phone, email, dept_name, password_hash)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id,
                    first_name,
                    last_name,
                    phone,
                    email,
                    dept_name,
                    password_hash
                ))

            elif role == "patient":
                cursor.execute("""
                    INSERT INTO patient
                    (patient_id, first_name, last_name, dob, gender, address, phone, email, password_hash)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id,
                    first_name,
                    last_name,
                    dob or None,
                    gender or None,
                    address or None,
                    phone,
                    email,
                    password_hash
                ))

            elif role == "admin":
                cursor.execute("""
                    INSERT INTO Hospital_Administrator
                    (admin_id, first_name, last_name, phone, email, role_name, dept_name, password_hash)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id,
                    first_name,
                    last_name,
                    phone,
                    email,
                    role_name or "Administrator",
                    dept_name,
                    password_hash
                ))

            else:
                flash("Invalid role selected.")
                cursor.close()
                return redirect(url_for("signup"))

            conn.commit()
            flash("Account created successfully. Please log in.")
            return redirect(url_for("login"))

        except Exception as e:
            conn.rollback()
            flash(f"Signup failed: {str(e)}")
            return redirect(url_for("signup"))

        finally:
            cursor.close()

    departments = fetch_departments()
    return render_template("signup.html", departments=departments)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if not require_login():
        return redirect(url_for("login"))

    role = session.get("role")
    if role == "Doctor":
        return redirect(url_for("doctor_dashboard"))
    if role == "Admin":
        return redirect(url_for("admin_dashboard"))
    if role == "Nurse":
        return redirect(url_for("nurse_dashboard"))
    if role == "Patient":
        return redirect(url_for("patient_dashboard"))
    return redirect(url_for("login"))


# @app.route("/patients")
# def patients():
#     if not require_login():
#         return redirect(url_for("login"))

#     cursor = conn.cursor()
#     cursor.execute("""
#         SELECT patient_id, first_name, last_name, dob, gender, phone
#         FROM patient
#         ORDER BY patient_id
#     """)
#     out = cursor.fetchall()
#     cursor.close()
#     return render_template("patients.html", patients=out, role=session.get("role"), username=session.get("username"))


@app.route("/view_patient/<int:patient_id>")
def view_patient(patient_id):
    if not require_login():
        return redirect(url_for("login"))
    return redirect(url_for("patient_appointments", patient_id=patient_id))


@app.route("/delete_patient/<int:patient_id>")
def delete_patient_by_id(patient_id):
    if not require_login():
        return redirect(url_for("login"))

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM patient WHERE patient_id = %s", (patient_id,))
        conn.commit()
        message = "Patient deleted successfully."
        success = True
    except Exception as e:
        conn.rollback()
        message = str(e)
        success = False
    finally:
        cursor.close()

    return jsonify({"success": success, "message": message})


@app.route("/edit_patient/<int:patient_id>")
def edit_patient(patient_id):
    if not require_login():
        return redirect(url_for("login"))
    flash("Please use the update patient form to edit patient information.")
    return redirect(url_for("update_patient_form"))


@app.route("/doctors")
def doctors():
    if not require_login():
        return redirect(url_for("login"))

    cursor = conn.cursor()
    cursor.execute("""
        SELECT doctor_id, first_name, last_name, specialty, email, dept_name
        FROM doctor
        ORDER BY doctor_id
    """)
    out = cursor.fetchall()
    cursor.close()
    return render_template("doctors.html", doctors=out, role=session.get("role"), username=session.get("username"))


@app.route("/delete_doctor/<int:doctor_id>", methods=["GET", "POST"])
def delete_doctor_by_id(doctor_id):
    if not require_login():
        return redirect(url_for("login"))

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM doctor WHERE doctor_id = %s", (doctor_id,))
        conn.commit()
        message = "Doctor deleted successfully."
        success = True
    except Exception as e:
        conn.rollback()
        message = str(e)
        success = False
    finally:
        cursor.close()

    return jsonify({"success": success, "message": message})


@app.route("/edit_doctor/<int:doctor_id>")
def edit_doctor(doctor_id):
    if not require_login():
        return redirect(url_for("login"))
    flash("Please use the update doctor form to edit doctor information.")
    return redirect(url_for("update_doctor_form"))


# @app.route("/appointments")
# def appointments():
#     if not require_login():
#         return redirect(url_for("login"))

#     selected_date = request.args.get("date", date.today().isoformat())
#     search = request.args.get("search", "").strip()
#     gender = request.args.get("gender", "").strip()
#     status = request.args.get("status", "").strip()
#     page = max(int(request.args.get("page", 1)), 1)
#     per_page = 10
#     offset = (page - 1) * per_page
#     cursor = conn.cursor(db.cursors.DictCursor)

#     doctor_id = session["user_id"]

#     where_clauses = ["a.patient_id = p.patient_id", "a.doctor_id = %s"]
#     params = [doctor_id]

#     if selected_date:
#         where_clauses.append("DATE(a.ap_datetime) = %s")
#         params.append(selected_date)

#     if search:
#         where_clauses.append("(p.first_name LIKE %s OR p.last_name LIKE %s OR p.phone LIKE %s)")
#         like_value = f"%{search}%"
#         params.extend([like_value, like_value, like_value])

#     if gender:
#         where_clauses.append("p.gender = %s")
#         params.append(gender)

#     if status:
#         where_clauses.append("a.status = %s")
#         params.append(status)

#     where_sql = " AND ".join(where_clauses)

#     count_sql = f"""
#         SELECT COUNT(*) AS total_rows
#         FROM patient AS p
#         JOIN appointment AS a
#         WHERE {where_sql}
#     """
#     cursor.execute(count_sql, params)
#     count_result = cursor.fetchone()
#     total_rows = count_result["total_rows"] or 0
#     total_pages = max((total_rows + per_page - 1) // per_page, 1)

#     if page > total_pages:
#         page = total_pages
#         offset = (page - 1) * per_page

#     appointments_sql = f"""
#         SELECT
#             p.first_name,
#             p.last_name,
#             p.gender,
#             p.dob,
#             TIME(a.ap_datetime) AS time,
#             p.phone,
#             a.status
#         FROM patient AS p
#         JOIN appointment AS a
#         WHERE {where_sql}
#         ORDER BY a.ap_datetime ASC
#         LIMIT %s OFFSET %s
#     """
#     cursor.execute(appointments_sql, params + [per_page, offset])
#     appointments_list = cursor.fetchall()

#     cursor.execute(
#         "SELECT COUNT(*) AS total_appointments FROM appointment WHERE doctor_id = %s",
#         (doctor_id,)
#     )
#     stats1 = cursor.fetchone()

#     cursor.execute(
#         "SELECT COUNT(*) AS completed_appointments FROM appointment WHERE doctor_id = %s AND status = 'Completed'",
#         (doctor_id,)
#     )
#     stats2 = cursor.fetchone()

#     cursor.execute(
#         "SELECT COUNT(*) AS pending_appointments FROM appointment WHERE doctor_id = %s AND status = 'Pending'",
#         (doctor_id,)
#     )
#     stats3 = cursor.fetchone()

#     cursor.execute(
#         "SELECT COUNT(*) AS cancelled_appointments FROM appointment WHERE doctor_id = %s AND status = 'Cancelled'",
#         (doctor_id,)
#     )
#     stats4 = cursor.fetchone()

#     cursor.close()

#     start_row = 0 if total_rows == 0 else offset + 1
#     end_row = min(offset + per_page, total_rows)

#     return render_template(
#         "appointments.html",
#         appointments=appointments_list,
#         selected_date=selected_date,
#         total_appointments=stats1["total_appointments"] or 0,
#         completed_appointments=stats2["completed_appointments"] or 0,
#         pending_appointments=stats3["pending_appointments"] or 0,
#         cancelled_appointments=stats4["cancelled_appointments"] or 0,
#         current_search=search,
#         current_gender=gender,
#         current_status=status,
#         current_page=page,
#         per_page=per_page,
#         total_rows=total_rows,
#         total_pages=total_pages,
#         start_row=start_row,
#         end_row=end_row,
#         doctor_id=doctor_id,
#         role=session.get("role"),
#         username=session.get("username")
#     )


# @app.route("/doctor-dashboard")
# def doctor_dashboard():
#     if not require_login():
#         return redirect(url_for("login"))

#     doctor_id = session["user_id"]
#     cursor = conn.cursor(db.cursors.DictCursor)

#     cursor.execute("""
#         SELECT COUNT(*) AS today_appointments
#         FROM appointment
#         WHERE doctor_id = %s
#           AND DATE(ap_datetime) = CURDATE()
#     """, (doctor_id,))
#     today_appointments = cursor.fetchone()["today_appointments"]

#     cursor.execute("""
#         SELECT COUNT(DISTINCT patient_id) AS total_patients
#         FROM appointment
#         WHERE doctor_id = %s
#     """, (doctor_id,))
#     total_patients = cursor.fetchone()["total_patients"]

#     cursor.execute("""
#         SELECT COUNT(*) AS month_prescriptions
#         FROM prescription
#         WHERE doctor_id = %s
#           AND YEAR(prescribed_datetime) = YEAR(CURDATE())
#           AND MONTH(prescribed_datetime) = MONTH(CURDATE())
#     """, (doctor_id,))
#     month_prescriptions = cursor.fetchone()["month_prescriptions"]

#     cursor.execute("""
#         SELECT COUNT(*) AS month_lab_tests
#         FROM laboratory_test
#         WHERE doctor_id = %s
#           AND YEAR(ordered_datetime) = YEAR(CURDATE())
#           AND MONTH(ordered_datetime) = MONTH(CURDATE())
#     """, (doctor_id,))
#     month_lab_tests = cursor.fetchone()["month_lab_tests"]

#     cursor.execute("""
#         SELECT
#             p.patient_id,
#             p.first_name,
#             p.last_name,
#             p.gender,
#             TIMESTAMPDIFF(YEAR, p.dob, CURDATE()) AS age,
#             p.phone,
#             MAX(a.ap_datetime) AS last_seen
#         FROM patient p
#         JOIN appointment a ON a.patient_id = p.patient_id
#         WHERE a.doctor_id = %s
#         GROUP BY p.patient_id, p.first_name, p.last_name, p.gender, p.dob, p.phone
#         ORDER BY last_seen DESC
#         LIMIT 4
#     """, (doctor_id,))
#     recent_patients = cursor.fetchall()

#     cursor.execute("""
#         SELECT
#             CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
#             DATE_FORMAT(pr.prescribed_datetime, '%%b %%d, %%Y') AS prescribed_date,
#             CASE
#                 WHEN CHAR_LENGTH(pr.dosage_instruction) > 40
#                 THEN CONCAT(LEFT(pr.dosage_instruction, 40), '...')
#                 ELSE pr.dosage_instruction
#             END AS dosage_preview
#         FROM prescription pr
#         JOIN patient p ON pr.patient_id = p.patient_id
#         WHERE pr.doctor_id = %s
#         ORDER BY pr.prescribed_datetime DESC
#         LIMIT 4
#     """, (doctor_id,))
#     recent_prescriptions = cursor.fetchall()

#     cursor.execute("""
#         SELECT
#             DATE_FORMAT(a.ap_datetime, '%%h:%%i %%p') AS time,
#             CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
#             a.reason,
#             a.status
#         FROM appointment a
#         JOIN patient p ON a.patient_id = p.patient_id
#         WHERE a.doctor_id = %s
#           AND DATE(a.ap_datetime) = CURDATE()
#         ORDER BY a.ap_datetime ASC
#         LIMIT 5
#     """, (doctor_id,))
#     today_schedule = cursor.fetchall()

#     cursor.close()

#     stats = {
#         "today_appointments": today_appointments or 0,
#         "total_patients": total_patients or 0,
#         "month_prescriptions": month_prescriptions or 0,
#         "month_lab_tests": month_lab_tests or 0,
#     }

#     return render_template(
#         "dashboard.html",
#         stats=stats,
#         recent_patients=recent_patients,
#         recent_prescriptions=recent_prescriptions,
#         today_schedule=today_schedule,
#         active_tab="dashboard",
#         role=session.get("role"),
#         username=session.get("username")
#     )


@app.route("/admin-dashboard")
def admin_dashboard():
    if not require_login():
        return redirect(url_for("login"))

    cursor = conn.cursor(db.cursors.DictCursor)

    cursor.execute("SELECT COUNT(*) AS total_patients FROM patient")
    total_patients = cursor.fetchone()["total_patients"]

    cursor.execute("SELECT COUNT(*) AS total_doctors FROM doctor")
    total_doctors = cursor.fetchone()["total_doctors"]

    cursor.execute("SELECT COUNT(*) AS total_nurses FROM nurse")
    total_nurses = cursor.fetchone()["total_nurses"]

    cursor.execute("SELECT COUNT(*) AS total_departments FROM department")
    total_departments = cursor.fetchone()["total_departments"]

    cursor.execute("SELECT COUNT(*) AS total_schedules FROM staff_schedule")
    total_schedules = cursor.fetchone()["total_schedules"]

    cursor.execute("SELECT COUNT(*) AS total_beds FROM beds")
    total_beds = cursor.fetchone()["total_beds"]

    cursor.execute("""
        SELECT patient_id, first_name, last_name, phone, email
        FROM patient
        ORDER BY patient_id DESC
        LIMIT 5
    """)
    recent_patients = cursor.fetchall()

    cursor.execute("""
        SELECT doctor_id, first_name, last_name, specialty, dept_name
        FROM doctor
        ORDER BY doctor_id DESC
        LIMIT 5
    """)
    recent_doctors = cursor.fetchall()

    cursor.execute("""
        SELECT nurse_id, first_name, last_name, dept_name
        FROM nurse
        ORDER BY nurse_id DESC
        LIMIT 5
    """)
    recent_nurses = cursor.fetchall()

    cursor.execute("""
        SELECT shift_id, shift_date, shift_type, start_time, end_time, doctor_id, nurse_id
        FROM staff_schedule
        ORDER BY shift_date DESC, start_time DESC
        LIMIT 5
    """)
    recent_schedules = cursor.fetchall()

    cursor.execute("""
        SELECT ward, room, building, bed_no, admit_id
        FROM beds
        ORDER BY building, ward, room, bed_no
        LIMIT 8
    """)
    bed_inventory = cursor.fetchall()

    cursor.close()

    stats = {
        "total_patients": total_patients or 0,
        "total_doctors": total_doctors or 0,
        "total_nurses": total_nurses or 0,
        "total_departments": total_departments or 0,
        "total_schedules": total_schedules or 0,
        "total_beds": total_beds or 0,
    }

    return render_template(
        "admin_dashboard.html",
        stats=stats,
        recent_patients=recent_patients,
        recent_doctors=recent_doctors,
        recent_nurses=recent_nurses,
        recent_schedules=recent_schedules,
        bed_inventory=bed_inventory,
        role=session.get("role"),
        username=session.get("username")
    )


@app.route("/nurse-dashboard")
def nurse_dashboard():
    if not require_login():
        return redirect(url_for("login"))

    cursor = conn.cursor(db.cursors.DictCursor)
    nurse_id = session["user_id"]

    cursor.execute("""
        SELECT nurse_id, first_name, last_name, phone, email, dept_name
        FROM nurse
        WHERE nurse_id = %s
    """, (nurse_id,))
    nurse = cursor.fetchone()
    cursor.close()

    return render_template(
        "nurse_dashboard.html",
        nurse=nurse,
        role=session.get("role"),
        username=session.get("username")
    )


@app.route("/patient-dashboard")
def patient_dashboard():
    if not require_login():
        return redirect(url_for("login"))

    cursor = conn.cursor(db.cursors.DictCursor)
    patient_id = session["user_id"]

    cursor.execute("""
        SELECT patient_id, first_name, last_name, dob, gender, address, phone, email
        FROM patient
        WHERE patient_id = %s
    """, (patient_id,))
    patient = cursor.fetchone()
    cursor.close()

    return render_template(
        "patient_dashboard.html",
        patient=patient,
        role=session.get("role"),
        username=session.get("username")
    )


@app.route("/patient_profile")
def patient_profile():
    if not require_login():
        return redirect(url_for("login"))
    return render_template("patient_profile.html", role=session.get("role"), username=session.get("username"))


@app.route("/patient/<patient_id>")
def patient_overview(patient_id):
    if not require_login():
        return redirect(url_for("login"))
    return render_template(
        "patient_overview.html",
        active_tab="overview",
        role=session.get("role"),
        username=session.get("username")
    )


# @app.route("/patient/<patient_id>/appointments")
# def patient_appointments(patient_id):
#     if not require_login():
#         return redirect(url_for("login"))

#     doctor_id = session.get("user_id")
#     appointment = appointment_data(db=db, conn=conn, patient_id=patient_id, doctor_id=doctor_id)
#     patients_profile = patient_profile_data(db, conn, patient_id)
#     stats = patient_statistics(db, conn, patient_id)

#     return render_template(
#         "patient_appointments.html",
#         upcoming_appointments=appointment["upcoming_appointments"],
#         past_appointments=appointment["past_appointments"],
#         patient=patients_profile,
#         stats=stats,
#         active_tab="appointments",
#         role=session.get("role"),
#         username=session.get("username")
#     )


# @app.route("/patient/<patient_id>/admissions")
# def patient_admissions(patient_id):
#     if not require_login():
#         return redirect(url_for("login"))

#     patients_profile = patient_profile_data(db, conn, patient_id)
#     adm = admission(db, conn, patient_id)

#     return render_template(
#         "patient_admissions.html",
#         admissions=adm,
#         patient=patients_profile,
#         role=session.get("role"),
#         username=session.get("username"),
#         active_tab="admissions"
#     )


# @app.route("/patient/<patient_id>/medical-records")
# def patient_medical_records(patient_id):
#     if not require_login():
#         return redirect(url_for("login"))

#     patients_profile = patient_profile_data(db, conn, patient_id)
#     records = medical_record(db, conn, patient_id)

#     return render_template(
#         "patient_medical_records.html",
#         medical_records=records,
#         patient=patients_profile,
#         role=session.get("role"),
#         username=session.get("username"),
#         active_tab="medical_records"
#     )


# @app.route("/patient/<int:patient_id>/add-note", methods=["POST"])
# def add_note(patient_id):
#     if not require_login():
#         return redirect(url_for("login"))

#     note_text = request.form.get("note_text", "").strip()
#     note_type = request.form.get("note_type", "").strip()

#     if not note_text:
#         return redirect(url_for("patient_medical_records", patient_id=patient_id))

#     nurse_id = session.get("user_id")

#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO medical_record_notes
#         (note_text, note_type, date_time, patient_id, nurse_id)
#         VALUES (%s, %s, NOW(), %s, %s)
#     """, (note_text, note_type or None, patient_id, nurse_id))
#     conn.commit()
#     cursor.close()

#     return redirect(url_for("patient_medical_records", patient_id=patient_id))


# @app.route("/patient/<int:patient_id>/add-appointment", methods=["POST"])
# def add_appointment(patient_id):
#     if not require_login():
#         return redirect(url_for("login"))

#     ap_datetime = request.form.get("ap_datetime")
#     doctor_id = request.form.get("doctor_id")
#     reason = request.form.get("reason")

#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO appointment
#         (ap_datetime, reason, status, patient_id, doctor_id, dept_name)
#         VALUES (%s, %s, 'Pending', %s, %s,
#                (SELECT dept_name FROM doctor WHERE doctor_id = %s))
#     """, (ap_datetime, reason, patient_id, doctor_id, doctor_id))
#     conn.commit()
#     cursor.close()

#     return redirect(request.referrer or url_for("patient_appointments", patient_id=patient_id))


# @app.route("/patient/<patient_id>/prescriptions")
# def patient_prescriptions(patient_id):
#     if not require_login():
#         return redirect(url_for("login"))

#     profile = patient_profile_data(db, conn, patient_id)
#     cursor = conn.cursor(db.cursors.DictCursor)

#     cursor.execute("""
#         SELECT
#             DATE(prescribed_datetime) AS prescribed_datetime,
#             CONCAT('Dr ', d.first_name, ' ', d.last_name) AS doctor_name,
#             p.dosage_instruction,
#             p.start_date,
#             p.end_date
#         FROM prescription p
#         LEFT JOIN doctor d ON d.doctor_id = p.doctor_id
#         WHERE p.patient_id = %s
#         ORDER BY p.prescribed_datetime DESC
#     """, (patient_id,))
#     prescriptions = cursor.fetchall()
#     cursor.close()

#     return render_template(
#         "patient_prescriptions.html",
#         patient=profile,
#         prescriptions=prescriptions,
#         role=session.get("role"),
#         username=session.get("username"),
#         active_tab="prescriptions"
#     )


# @app.route("/patient/<int:patient_id>/create-prescription", methods=["POST"])
# def create_prescription(patient_id):
#     if not require_login():
#         return redirect(url_for("login"))

#     doctor_id = request.form.get("doctor_id")
#     dosage_instruction = request.form.get("dosage_instruction")
#     start_date = request.form.get("start_date")
#     end_date = request.form.get("end_date")

#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO prescription
#         (dosage_instruction, start_date, end_date, patient_id, doctor_id, prescribed_datetime)
#         VALUES (%s, %s, %s, %s, %s, NOW())
#     """, (dosage_instruction, start_date, end_date, patient_id, doctor_id))
#     conn.commit()
#     cursor.close()

#     return redirect(url_for("patient_prescriptions", patient_id=patient_id))


# @app.route("/patient/<int:patient_id>/lab-tests")
# def patient_lab_tests(patient_id):
#     if not require_login():
#         return redirect(url_for("login"))

#     profile = patient_profile_data(db, conn, patient_id)
#     tests = lab_test_data(db, conn, patient_id)

#     return render_template(
#         "patient_lab_tests.html",
#         patient=profile,
#         reviewed_lab_tests=tests["reviewed_lab_tests"],
#         unreviewed_lab_tests=tests["unreviewed_lab_tests"],
#         active_tab="lab_tests",
#         role=session.get("role"),
#         username=session.get("username")
#     )


# @app.route("/patient/<int:patient_id>/lab-tests/<int:test_id>/review", methods=["POST"])
# def review_lab_test(patient_id, test_id):
#     if not require_login():
#         return redirect(url_for("login"))

#     mark_lab_test_reviewed(db, conn, patient_id, test_id)
#     return redirect(url_for("patient_lab_tests", patient_id=patient_id))


@app.route("/patient/<patient_id>/notes")
def patient_notes(patient_id):
    if not require_login():
        return redirect(url_for("login"))
    return render_template(
        "patient_notes.html",
        active_tab="notes",
        role=session.get("role"),
        username=session.get("username")
    )


@app.route("/patient/<patient_id>/billing")
def patient_billing(patient_id):
    if not require_login():
        return redirect(url_for("login"))
    return render_template(
        "patient_billing.html",
        active_tab="billing",
        role=session.get("role"),
        username=session.get("username")
    )


@app.route("/favicon.ico")
def favicon():
    return "", 204


@app.route("/table/<name>")
def person(name):
    if not require_login():
        return redirect(url_for("login"))

    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {name};")
    out = cursor.fetchall()

    result = "<h1>Table Data</h1>"
    for row in out:
        result += "<p>" + ", ".join([str(i) for i in row]) + "</p>"

    cursor.close()
    return result


@app.route("/add_doctor_form")
def add_doctor_form():
    if not require_login():
        return redirect(url_for("login"))

    departments = fetch_departments()
    return render_template("add_doctor.html", departments=departments, success=False)


@app.route("/add_doctor", methods=["POST"])
def add_doctor():
    if not require_login():
        return redirect(url_for("login"))

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
    """, (doctor_id, first_name, last_name, specialty or None, email, department_name))
    conn.commit()
    cursor.close()

    departments = fetch_departments()
    return render_template("add_doctor.html", departments=departments, success=True)


@app.route("/delete_doctor_form")
def delete_doctor_form():
    if not require_login():
        return redirect(url_for("login"))

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
@app.route("/delete_doctor", methods=["POST"])
def delete_doctor_form_submit():
    if not require_login():
        return redirect(url_for("login"))

    doctor_id = request.form["doctor_id"]
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM doctor WHERE doctor_id = %s", (doctor_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        flash(f"Delete failed: {str(e)}")
    finally:
        cursor.close()

    return redirect(url_for("delete_doctor_form"))


@app.route("/update_doctor_form")
def update_doctor_form():
    if not require_login():
        return redirect(url_for("login"))

    cursor = conn.cursor()
    cursor.execute("SELECT doctor_id, first_name, last_name FROM doctor")
    doctors = cursor.fetchall()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("update_doctor.html", doctors=doctors, departments=departments, success=False)


@app.route("/update_doctor", methods=["POST"])
def update_doctor():
    if not require_login():
        return redirect(url_for("login"))

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
    """, (first_name, last_name, specialty or None, email, department_name, doctor_id))
    conn.commit()

    cursor.execute("SELECT doctor_id, first_name, last_name FROM doctor")
    doctors = cursor.fetchall()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("update_doctor.html", doctors=doctors, departments=departments, success=True)


@app.route("/add_patient_form")
def add_patient_form():
    if not require_login():
        return redirect(url_for("login"))

    return render_template("add_patient.html", success=False)


@app.route("/add_patient", methods=["POST"])
def add_patient():
    if not require_login():
        return redirect(url_for("login"))

    patient_id = request.form["patient_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    dob = request.form["dob"]
    gender = request.form["gender"]
    address = request.form["address"]
    phone = normalize_phone(request.form.get("phone"))
    email = request.form["email"]

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patient (patient_id, first_name, last_name, dob, gender, address, phone, email)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (patient_id, first_name, last_name, dob or None, gender or None, address or None, phone, email))
    conn.commit()
    cursor.close()

    return render_template("add_patient.html", success=True)


@app.route("/delete_patient_form")
def delete_patient_form():
    if not require_login():
        return redirect(url_for("login"))

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
@app.route("/delete_patient", methods=["POST"])
def delete_patient_form_submit():
    if not require_login():
        return redirect(url_for("login"))

    patient_id = request.form["patient_id"]
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM patient WHERE patient_id = %s", (patient_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        flash(f"Delete failed: {str(e)}")
    finally:
        cursor.close()

    return redirect(url_for("delete_patient_form"))


@app.route("/update_patient_form")
def update_patient_form():
    if not require_login():
        return redirect(url_for("login"))

    cursor = conn.cursor()
    cursor.execute("SELECT patient_id, first_name, last_name FROM patient")
    patients = cursor.fetchall()
    cursor.close()
    return render_template("update_patient.html", patients=patients, success=False)


@app.route("/update_patient", methods=["POST"])
def update_patient():
    if not require_login():
        return redirect(url_for("login"))

    patient_id = request.form["patient_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    dob = request.form["dob"]
    gender = request.form["gender"]
    address = request.form["address"]
    phone = normalize_phone(request.form.get("phone"))
    email = request.form["email"]

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE patient
        SET first_name = %s, last_name = %s, dob = %s, gender = %s,
            address = %s, phone = %s, email = %s
        WHERE patient_id = %s
    """, (first_name, last_name, dob or None, gender or None, address or None, phone, email, patient_id))
    conn.commit()

    cursor.execute("SELECT patient_id, first_name, last_name FROM patient")
    patients = cursor.fetchall()
    cursor.close()
    return render_template("update_patient.html", patients=patients, success=True)


@app.route("/add_nurse_form")
def add_nurse_form():
    if not require_login():
        return redirect(url_for("login"))

    departments = fetch_departments()
    return render_template("add_nurse.html", departments=departments, success=False)


@app.route("/add_nurse", methods=["POST"])
def add_nurse():
    if not require_login():
        return redirect(url_for("login"))

    nurse_id = request.form["nurse_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    phone = normalize_phone(request.form.get("phone"))
    email = request.form["email"]
    department_name = request.form["department_name"]

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO nurse (nurse_id, first_name, last_name, phone, email, dept_name)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nurse_id, first_name, last_name, phone, email, department_name))
    conn.commit()
    cursor.close()

    departments = fetch_departments()
    return render_template("add_nurse.html", departments=departments, success=True)


@app.route("/delete_nurse_form")
def delete_nurse_form():
    if not require_login():
        return redirect(url_for("login"))

    cursor = conn.cursor()
    cursor.execute("SELECT nurse_id, first_name, last_name FROM nurse")
    nurses = cursor.fetchall()
    cursor.close()
    return render_template("delete_nurse.html", nurses=nurses)


@app.route("/delete_nurse", methods=["POST"])
def delete_nurse():
    if not require_login():
        return redirect(url_for("login"))

    nurse_id = request.form["nurse_id"]
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM nurse WHERE nurse_id = %s", (nurse_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        flash(f"Delete failed: {str(e)}")
    finally:
        cursor.close()

    return redirect(url_for("delete_nurse_form"))


@app.route("/update_nurse_form")
def update_nurse_form():
    if not require_login():
        return redirect(url_for("login"))

    cursor = conn.cursor()
    cursor.execute("SELECT nurse_id, first_name, last_name FROM nurse")
    nurses = cursor.fetchall()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("update_nurse.html", nurses=nurses, departments=departments, success=False)


@app.route("/update_nurse", methods=["POST"])
def update_nurse():
    if not require_login():
        return redirect(url_for("login"))

    nurse_id = request.form["nurse_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    phone = normalize_phone(request.form.get("phone"))
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


@app.route("/add_admin_form")
def add_admin_form():
    if not require_login():
        return redirect(url_for("login"))

    departments = fetch_departments()
    return render_template("add_admin.html", departments=departments, success=False)


@app.route("/add_admin", methods=["POST"])
def add_admin():
    if not require_login():
        return redirect(url_for("login"))

    admin_id = request.form["admin_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    phone = normalize_phone(request.form.get("phone"))
    email = request.form["email"]
    role_name = request.form["role_name"]
    department_name = request.form["department_name"]

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Hospital_Administrator
        (admin_id, first_name, last_name, phone, email, role_name, dept_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (admin_id, first_name, last_name, phone, email, role_name or "Administrator", department_name))
    conn.commit()
    cursor.close()

    departments = fetch_departments()
    return render_template("add_admin.html", departments=departments, success=True)


@app.route("/delete_admin_form")
def delete_admin_form():
    if not require_login():
        return redirect(url_for("login"))

    cursor = conn.cursor()
    cursor.execute("SELECT admin_id, first_name, last_name FROM Hospital_Administrator")
    admins = cursor.fetchall()
    cursor.close()
    return render_template("delete_admin.html", admins=admins)


@app.route("/delete_admin", methods=["POST"])
def delete_admin():
    if not require_login():
        return redirect(url_for("login"))

    admin_id = request.form["admin_id"]
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Hospital_Administrator WHERE admin_id = %s", (admin_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        flash(f"Delete failed: {str(e)}")
    finally:
        cursor.close()

    return redirect(url_for("delete_admin_form"))


@app.route("/update_admin_form")
def update_admin_form():
    if not require_login():
        return redirect(url_for("login"))

    cursor = conn.cursor()
    cursor.execute("SELECT admin_id, first_name, last_name FROM Hospital_Administrator")
    admins = cursor.fetchall()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("update_admin.html", admins=admins, departments=departments, success=False)


@app.route("/update_admin", methods=["POST"])
def update_admin():
    if not require_login():
        return redirect(url_for("login"))

    admin_id = request.form["admin_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    phone = normalize_phone(request.form.get("phone"))
    email = request.form["email"]
    role_name = request.form["role_name"]
    department_name = request.form["department_name"]

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Hospital_Administrator
        SET first_name = %s, last_name = %s, phone = %s, email = %s,
            role_name = %s, dept_name = %s
        WHERE admin_id = %s
    """, (first_name, last_name, phone, email, role_name or "Administrator", department_name, admin_id))
    conn.commit()

    cursor.execute("SELECT admin_id, first_name, last_name FROM Hospital_Administrator")
    admins = cursor.fetchall()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("update_admin.html", admins=admins, departments=departments, success=True)


@app.route("/doctor_menu")
def doctor_menu():
    if not require_login():
        return redirect(url_for("login"))

    return render_template(
        "role_menu.html",
        role_name="Doctor",
        add_url="/add_doctor_form",
        update_url="/update_doctor_form",
        delete_url="/delete_doctor_form"
    )


@app.route("/patient_menu")
def patient_menu():
    if not require_login():
        return redirect(url_for("login"))

    return render_template(
        "role_menu.html",
        role_name="Patient",
        add_url="/add_patient_form",
        update_url="/update_patient_form",
        delete_url="/delete_patient_form"
    )


@app.route("/nurse_menu")
def nurse_menu():
    if not require_login():
        return redirect(url_for("login"))

    return render_template(
        "role_menu.html",
        role_name="Nurse",
        add_url="/add_nurse_form",
        update_url="/update_nurse_form",
        delete_url="/delete_nurse_form"
    )


@app.route("/admin_menu")
def admin_menu():
    if not require_login():
        return redirect(url_for("login"))

    return render_template(
        "role_menu.html",
        role_name="Administrator",
        add_url="/add_admin_form",
        update_url="/update_admin_form",
        delete_url="/delete_admin_form"
    )


@app.route("/departments")
def departments():
    if not require_login():
        return redirect(url_for("login"))

    cursor = conn.cursor()
    cursor.execute("SELECT dept_name, dept_location, phone FROM department")
    departments_data = cursor.fetchall()
    cursor.close()
    return render_template("departments.html", departments=departments_data, role=session.get("role"), username=session.get("username"))


@app.route("/staff-schedules")
def staff_schedules():
    if not require_login():
        return redirect(url_for("login"))

    cursor = conn.cursor(db.cursors.DictCursor)
    cursor.execute("SELECT * FROM staff_schedule ORDER BY shift_date DESC, start_time DESC")
    schedules = cursor.fetchall()
    cursor.close()
    return render_template("staff_schedules.html", schedules=schedules, role=session.get("role"), username=session.get("username"))


@app.route("/beds")
def beds():
    if not require_login():
        return redirect(url_for("login"))

    cursor = conn.cursor(db.cursors.DictCursor)
    cursor.execute("SELECT * FROM beds ORDER BY building, ward, room, bed_no")
    beds_data = cursor.fetchall()
    cursor.close()
    return render_template("beds.html", beds=beds_data, role=session.get("role"), username=session.get("username"))


if __name__ == "__main__":
    app.run(debug=True)

    app.run(debug=True, port=5001)