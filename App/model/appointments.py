def appointment_data(db, conn, patient_id, doctor_id):
    cursor = conn.cursor(db.cursors.DictCursor)    
    cursor.execute(f"""SELECT
    a.ap_id AS id,
    DATE_FORMAT(a.ap_datetime, '%Y-%m-%d %h:%i %p') AS ap_datetime,
    CONCAT(d.first_name, ' ', d.last_name) AS doctor_name,
    a.reason,
    a.status
    FROM appointment a
    LEFT JOIN doctor d ON d.doctor_id = a.doctor_id
    WHERE a.patient_id = {patient_id} 
        AND a.doctor_id = {doctor_id}
        AND a.ap_datetime >= NOW()
    ORDER BY a.ap_datetime ASC;""")

    upcoming_appointments = cursor.fetchall();

    cursor.execute(f"""SELECT
    a.ap_id AS id,
    DATE_FORMAT(a.ap_datetime, '%Y-%m-%d %h:%i %p') AS ap_datetime,
    CONCAT(d.first_name, ' ', d.last_name) AS doctor_name,
    a.reason,
    a.status
    FROM appointment a
    LEFT JOIN doctor d ON d.doctor_id = a.doctor_id
    WHERE a.patient_id = {patient_id} 
        AND a.doctor_id = {doctor_id}
        AND a.ap_datetime < NOW()
    ORDER BY a.ap_datetime ASC;""")

    past_appointments = cursor.fetchall();

    return {"upcoming_appointments":upcoming_appointments, "past_appointments":past_appointments}
