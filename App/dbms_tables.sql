
CREATE TABLE Department (
    dept_name VARCHAR(100) PRIMARY KEY,
    dept_location VARCHAR(100),
    phone VARCHAR(20)
);


CREATE TABLE Nurse (
    nurse_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    dept_name VARCHAR(100),
    FOREIGN KEY (dept_name) REFERENCES Department(dept_name)
);


CREATE TABLE Doctor (
    doctor_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    specialty VARCHAR(100),
    email VARCHAR(100),
    dept_name VARCHAR(100),
    FOREIGN KEY (dept_name) REFERENCES Department(dept_name)
);


CREATE TABLE Patient (
    patient_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    dob DATE,
    gender VARCHAR(10),
    address VARCHAR(200),
    phone VARCHAR(20),
    email VARCHAR(100),
    dept_name VARCHAR(100),
    FOREIGN KEY (dept_name) REFERENCES Department(dept_name)
);


CREATE TABLE Appointment (
    ap_id INT PRIMARY KEY,
    ap_datetime DATETIME,
    reason VARCHAR(255),
    status VARCHAR(50),
    patient_id INT,
    doctor_id INT,
    dept_name VARCHAR(100),
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id),
    FOREIGN KEY (dept_name) REFERENCES Department(dept_name)
);


CREATE TABLE Prescription (
    prescription_id INT PRIMARY KEY,
    prescribed_datetime DATETIME,
    dosage_instruction TEXT,
    start_date DATE,
    end_date DATE,
    patient_id INT,
    doctor_id INT,
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id)
);


CREATE TABLE Laboratory_test (
    test_id INT PRIMARY KEY,
    test_name VARCHAR(100),
    ordered_datetime DATETIME,
    results TEXT,
    patient_id INT,
    doctor_id INT,
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id)
);


CREATE TABLE Medical_record_notes (
    note_id INT PRIMARY KEY,
    note_text TEXT,
    note_type VARCHAR(50),
    date_time DATETIME,
    patient_id INT,
    nurse_id INT,
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    FOREIGN KEY (nurse_id) REFERENCES Nurse(nurse_id)
);


CREATE TABLE Admission (
    admit_id INT PRIMARY KEY,
    admit_datetime DATETIME,
    admission_reason VARCHAR(255),
    status VARCHAR(50),
    patient_id INT,
    doctor_id INT,
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id)
);


CREATE TABLE Discharge (
    discharge_id INT PRIMARY KEY,
    discharge_date DATE,
    summary TEXT,
    instructions TEXT,
    admit_id INT,
    FOREIGN KEY (admit_id) REFERENCES Admission(admit_id)
);


CREATE TABLE Beds (
    ward VARCHAR(50),
    room VARCHAR(50),
    building VARCHAR(50),
    bed_no INT,
    admit_id INT,
    PRIMARY KEY (ward, room, building, bed_no),
    FOREIGN KEY (admit_id) REFERENCES Admission(admit_id)
);


CREATE TABLE Staff_Schedule (
    shift_id INT PRIMARY KEY,
    shift_date DATE,
    shift_time VARCHAR(50),
    start_time TIME,
    end_time TIME,
    doctor_id INT,
    nurse_id INT,
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id),
    FOREIGN KEY (nurse_id) REFERENCES Nurse(nurse_id)
);


CREATE TABLE Assisted_by (
    nurse_id INT,
    doctor_id INT,
    PRIMARY KEY (nurse_id, doctor_id),
    FOREIGN KEY (nurse_id) REFERENCES Nurse(nurse_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id)
);


CREATE TABLE Belongs_to (
    nurse_id INT,
    dept_name VARCHAR(100),
    PRIMARY KEY (nurse_id, dept_name),
    FOREIGN KEY (nurse_id) REFERENCES Nurse(nurse_id),
    FOREIGN KEY (dept_name) REFERENCES Department(dept_name)
);


CREATE TABLE Associated_with (
    dept_name VARCHAR(100),
    doctor_id INT,
    PRIMARY KEY (dept_name, doctor_id),
    FOREIGN KEY (dept_name) REFERENCES Department(dept_name),
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id)
);
