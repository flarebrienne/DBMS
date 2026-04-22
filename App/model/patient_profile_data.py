def patient_profile_data(db, conn, patient_id):
    cursor = conn.cursor(db.cursors.DictCursor)

    # 🔹 Patient basic info
    cursor.execute("""
        SELECT 
            p.patient_id,
            p.first_name,
            p.last_name,
            p.dob,
            TIMESTAMPDIFF(YEAR, p.dob, CURDATE()) AS age,
            p.gender,
            p.address,
            p.phone,
            p.email
        FROM patient p
        WHERE p.patient_id = %s
    """, (patient_id,))

    
    patient = cursor.fetchone()

    cursor.close()
    return patient;

def patient_statistics(db, conn, patient_id):
    cursor = conn.cursor(db.cursors.DictCursor)
    cursor.execute("""
        SELECT COUNT(*) AS total_appointments
        FROM appointment
        WHERE patient_id = %s
    """, (patient_id,))
    total_appointments = cursor.fetchone()["total_appointments"]

    cursor.execute("""
        SELECT COUNT(*) AS total_admissions
        FROM admission
        WHERE patient_id = %s
    """, (patient_id,))
    total_admissions = cursor.fetchone()["total_admissions"]

    cursor.execute("""
        SELECT COUNT(*) AS total_prescriptions
        FROM prescription
        WHERE patient_id = %s
    """, (patient_id,))
    total_prescriptions = cursor.fetchone()["total_prescriptions"]

    cursor.execute("""
        SELECT COUNT(*) AS total_lab_tests
        FROM laboratory_test
        WHERE patient_id = %s
    """, (patient_id,))
    total_lab_tests = cursor.fetchone()["total_lab_tests"]

    stats = {
        "total_appointments": total_appointments,
        "total_admissions": total_admissions,
        "total_prescriptions": total_prescriptions,
        "total_lab_tests": total_lab_tests
    }

    cursor.close()
    return stats;

def admission(db, conn, patient_id):
    cursor = conn.cursor(db.cursors.DictCursor)
    cursor.execute("""
        SELECT status, admit_id, admit_datetime, admission_reason FROM admission WHERE patient_id= %s
    """, (patient_id,))
    admission = cursor.fetchall()
    cursor.close()
    return admission


def medical_record(db, conn, patient_id):
    cursor = conn.cursor(db.cursors.DictCursor)
    cursor.execute("""
        SELECT date_time, note_type, concat(first_name, ' ', last_name ) as nurse_name, note_text FROM medical_record_notes AS a join nurse AS n ON a.nurse_id=n.nurse_id WHERE patient_id= %s
    """, (patient_id,))
    admission = cursor.fetchall()
    cursor.close()
    return admission

def medical_record(db, conn, patient_id):
    cursor = conn.cursor(db.cursors.DictCursor)
    cursor.execute("""
        SELECT date_time, note_type, concat(first_name, ' ', last_name ) as nurse_name, note_text FROM medical_record_notes AS a join nurse AS n ON a.nurse_id=n.nurse_id WHERE patient_id= %s
    """, (patient_id,))
    admission = cursor.fetchall()
    cursor.close()
    return admission

def lab_test_data(db, conn, patient_id):
    cursor = conn.cursor(db.cursors.DictCursor)

    cursor.execute("""
        SELECT
            l.test_id,
            l.ordered_datetime,
            l.test_name,
            CONCAT(d.first_name, ' ', d.last_name) AS doctor_name,
            l.results,
            l.status
        FROM laboratory_test l
        JOIN doctor d ON d.doctor_id = l.doctor_id
        WHERE l.patient_id = %s
          AND l.status = 0
        ORDER BY l.ordered_datetime DESC
    """, (patient_id,))
    unreviewed = cursor.fetchall()

    cursor.execute("""
        SELECT
            l.test_id,
            l.ordered_datetime,
            l.test_name,
            CONCAT(d.first_name, ' ', d.last_name) AS doctor_name,
            l.results,
            l.status
        FROM laboratory_test l
        JOIN doctor d ON d.doctor_id = l.doctor_id
        WHERE l.patient_id = %s
          AND l.status = 1
        ORDER BY l.ordered_datetime DESC
    """, (patient_id,))
    reviewed = cursor.fetchall()

    cursor.close()

    return {
        "unreviewed_lab_tests": unreviewed,
        "reviewed_lab_tests": reviewed
    }


def mark_lab_test_reviewed(db, conn, patient_id, test_id):
    cursor = conn.cursor(db.cursors.DictCursor)
    cursor.execute("""
        UPDATE laboratory_test
        SET status = 1
        WHERE test_id = %s
          AND patient_id = %s
    """, (test_id, patient_id))
    conn.commit()
    cursor.close()