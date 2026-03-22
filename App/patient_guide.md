# Hospital Management System — Adding Patient CRUD

## Complete Step-by-Step Guide (VS Code + Git + Flask)

---

## Part 1: Project Setup in VS Code with Git

### Step 1: Clone your Git repository

Open a terminal in VS Code (`Ctrl + `` ` or `Terminal → New Terminal`) and run:

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

If you already have the project folder locally, just open it in VS Code via **File → Open Folder**.

### Step 2: Create a Python virtual environment

```bash
python -m venv venv
```

Activate it:

- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

### Step 3: Install dependencies

```bash
pip install flask pymysql
```

### Step 4: Verify your folder structure

Your project should look like this:

```
your-project/
├── app.py
├── dbms_tables.sql
├── templates/
│   ├── connection.html
│   ├── add_doctor.html
│   ├── delete_doctor.html
│   ├── update_doctor.html
│   ├── add_patient.html       ← NEW
│   ├── delete_patient.html    ← NEW
│   └── update_patient.html    ← NEW
```

If you don't already have a `templates/` folder, create it and move all your `.html` files into it. Flask expects templates in a folder named `templates/`.

---

## Part 2: New Files to Add

You need to create **3 new HTML files** inside the `templates/` folder and **update `app.py`** with new routes. All files are provided below.

---

## Part 3: Code for `app.py` — Patient Routes to Add

Open `app.py` and add the following routes **after your existing doctor routes** (before the `if __name__` block):

```python
# ─────────────────────────────────────────────
#  PATIENT ROUTES
# ─────────────────────────────────────────────

# ---------- ADD PATIENT ----------

@app.route('/add_patient_form')
def add_patient_form():
    cursor = conn.cursor()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("add_patient.html", departments=departments, success=False)


@app.route('/add_patient', methods=['POST'])
def add_patient():
    patient_id = request.form['patient_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    dob = request.form['dob']
    gender = request.form['gender']
    address = request.form['address']
    phone = request.form['phone']
    email = request.form['email']
    department_name = request.form['department_name']

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patient (patient_id, first_name, last_name, dob, gender,
                             address, phone, email, dept_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (patient_id, first_name, last_name, dob, gender,
          address, phone, email, department_name))
    conn.commit()

    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("add_patient.html", departments=departments, success=True)


# ---------- DELETE PATIENT ----------

@app.route('/delete_patient_form')
def delete_patient_form():
    cursor = conn.cursor()
    cursor.execute("SELECT patient_id, first_name, last_name FROM patient")
    patients = cursor.fetchall()
    cursor.close()
    return render_template("delete_patient.html", patients=patients)


@app.route('/delete_patient', methods=['POST'])
def delete_patient():
    patient_id = request.form['patient_id']
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patient WHERE patient_id = %s", (patient_id,))
    conn.commit()
    cursor.close()
    return redirect(url_for('delete_patient_form'))


# ---------- UPDATE PATIENT ----------

@app.route('/update_patient_form')
def update_patient_form():
    cursor = conn.cursor()
    cursor.execute("SELECT patient_id, first_name, last_name FROM patient")
    patients = cursor.fetchall()
    cursor.execute("SELECT dept_name FROM department")
    departments = cursor.fetchall()
    cursor.close()
    return render_template("update_patient.html", patients=patients, departments=departments)


@app.route('/update_patient', methods=['POST'])
def update_patient():
    patient_id = request.form['patient_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    dob = request.form['dob']
    gender = request.form['gender']
    address = request.form['address']
    phone = request.form['phone']
    email = request.form['email']
    department_name = request.form['department_name']

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE patient
        SET first_name = %s, last_name = %s, dob = %s, gender = %s,
            address = %s, phone = %s, email = %s, dept_name = %s
        WHERE patient_id = %s
    """, (first_name, last_name, dob, gender,
          address, phone, email, department_name, patient_id))
    conn.commit()
    cursor.close()
    return redirect(url_for('update_patient_form'))
```

### How each route works

| URL                    | Method | What it does                                        |
|------------------------|--------|-----------------------------------------------------|
| `/add_patient_form`    | GET    | Shows the add-patient form with department dropdown |
| `/add_patient`         | POST   | Inserts a new patient row into the database         |
| `/delete_patient_form` | GET    | Shows a dropdown of existing patients to delete     |
| `/delete_patient`      | POST   | Deletes the selected patient by ID                  |
| `/update_patient_form` | GET    | Shows patients and departments for editing          |
| `/update_patient`      | POST   | Updates the selected patient's information          |

---

## Part 4: HTML Templates

### File 1 — `templates/add_patient.html`

Create this file inside the `templates/` folder:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Add Patient</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .form-container {
            background: white;
            padding: 25px;
            border-radius: 10px;
            width: 380px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h2 { text-align: center; }
        label {
            display: block;
            margin-top: 10px;
            font-weight: bold;
            font-size: 14px;
        }
        input, select, button {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            border-radius: 5px;
            border: 1px solid #ccc;
            box-sizing: border-box;
        }
        button {
            margin-top: 15px;
            background-color: #007bff;
            color: white;
            border: none;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background-color: #0056b3; }
        .back-link {
            display: block;
            text-align: center;
            margin-top: 15px;
            color: #007bff;
            text-decoration: none;
        }
        .back-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>Add Patient</h2>

        {% if success %}
        <div style="background-color:#d4edda;color:#155724;padding:10px;
                     margin-bottom:15px;border-radius:5px;border:1px solid #c3e6cb;">
            Patient has been successfully added!
        </div>
        {% endif %}

        <form action="/add_patient" method="POST">
            <label for="patient_id">Patient ID:</label>
            <input type="number" name="patient_id" id="patient_id"
                   placeholder="e.g. 101" required>

            <label for="first_name">First Name:</label>
            <input type="text" name="first_name" id="first_name"
                   placeholder="First Name" required>

            <label for="last_name">Last Name:</label>
            <input type="text" name="last_name" id="last_name"
                   placeholder="Last Name" required>

            <label for="dob">Date of Birth:</label>
            <input type="date" name="dob" id="dob" required>

            <label for="gender">Gender:</label>
            <select name="gender" id="gender" required>
                <option value="" disabled selected>Select Gender</option>
                <option value="M">Male</option>
                <option value="F">Female</option>
                <option value="O">Other</option>
            </select>

            <label for="address">Address:</label>
            <input type="text" name="address" id="address" placeholder="Address">

            <label for="phone">Phone:</label>
            <input type="text" name="phone" id="phone" placeholder="Phone Number">

            <label for="email">Email:</label>
            <input type="email" name="email" id="email" placeholder="Email">

            <label for="department_name">Department:</label>
            <select name="department_name" id="department_name" required>
                <option value="" disabled selected>Select Department</option>
                {% for dept in departments %}
                <option value="{{ dept[0] }}">{{ dept[0] }}</option>
                {% endfor %}
            </select>

            <button type="submit">Add Patient</button>
        </form>
        <a class="back-link" href="/">← Back to Home</a>
    </div>
</body>
</html>
```

---

### File 2 — `templates/delete_patient.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Delete Patient</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .form-container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            width: 380px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h2 { text-align: center; }
        label {
            display: block;
            margin-top: 10px;
            font-weight: bold;
            font-size: 14px;
        }
        select, button {
            display: block;
            margin-top: 5px;
            padding: 10px;
            width: 100%;
            border-radius: 5px;
            border: 1px solid #ccc;
            box-sizing: border-box;
        }
        button {
            margin-top: 20px;
            background-color: #e74c3c;
            color: white;
            border: none;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background-color: #c0392b; }
        .back-link {
            display: block;
            text-align: center;
            margin-top: 15px;
            color: #007bff;
            text-decoration: none;
        }
        .back-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>Delete Patient</h2>
        <form action="/delete_patient" method="POST">
            <label for="patient_id">Select Patient:</label>
            <select name="patient_id" id="patient_id" required>
                <option value="" disabled selected>-- Choose a Patient --</option>
                {% for patient in patients %}
                <option value="{{ patient[0] }}">
                    {{ patient[1] }} {{ patient[2] }} (ID: {{ patient[0] }})
                </option>
                {% endfor %}
            </select>
            <button type="submit">Delete Patient</button>
        </form>
        <a class="back-link" href="/">← Back to Home</a>
    </div>
</body>
</html>
```

---

### File 3 — `templates/update_patient.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Update Patient</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .form-container {
            background: white;
            padding: 25px;
            border-radius: 10px;
            width: 380px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h2 { text-align: center; }
        label {
            display: block;
            margin-top: 10px;
            font-weight: bold;
            font-size: 14px;
        }
        input, select, button {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            border-radius: 5px;
            border: 1px solid #ccc;
            box-sizing: border-box;
        }
        button {
            margin-top: 15px;
            background-color: #28a745;
            color: white;
            border: none;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background-color: #218838; }
        .back-link {
            display: block;
            text-align: center;
            margin-top: 15px;
            color: #007bff;
            text-decoration: none;
        }
        .back-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>Update Patient</h2>

        {% if success %}
        <div style="background-color:#d4edda;color:#155724;padding:10px;
                     margin-bottom:15px;border-radius:5px;border:1px solid #c3e6cb;">
            Patient has been successfully updated!
        </div>
        {% endif %}

        <form action="/update_patient" method="POST">
            <label for="patient_id">Select Patient:</label>
            <select name="patient_id" id="patient_id" required>
                <option value="" disabled selected>-- Choose a Patient --</option>
                {% for patient in patients %}
                <option value="{{ patient[0] }}">
                    {{ patient[1] }} {{ patient[2] }} (ID: {{ patient[0] }})
                </option>
                {% endfor %}
            </select>

            <label for="first_name">First Name:</label>
            <input type="text" name="first_name" id="first_name"
                   placeholder="First Name" required>

            <label for="last_name">Last Name:</label>
            <input type="text" name="last_name" id="last_name"
                   placeholder="Last Name" required>

            <label for="dob">Date of Birth:</label>
            <input type="date" name="dob" id="dob" required>

            <label for="gender">Gender:</label>
            <select name="gender" id="gender" required>
                <option value="" disabled selected>Select Gender</option>
                <option value="M">Male</option>
                <option value="F">Female</option>
                <option value="O">Other</option>
            </select>

            <label for="address">Address:</label>
            <input type="text" name="address" id="address" placeholder="Address">

            <label for="phone">Phone:</label>
            <input type="text" name="phone" id="phone" placeholder="Phone Number">

            <label for="email">Email:</label>
            <input type="email" name="email" id="email" placeholder="Email">

            <label for="department_name">Department:</label>
            <select name="department_name" id="department_name" required>
                <option value="" disabled selected>Select Department</option>
                {% for dept in departments %}
                <option value="{{ dept[0] }}">{{ dept[0] }}</option>
                {% endfor %}
            </select>

            <button type="submit">Update Patient</button>
        </form>
        <a class="back-link" href="/">← Back to Home</a>
    </div>
</body>
</html>
```

---

## Part 5: Running the Flask App

### Step 1: Make sure your virtual environment is active

You should see `(venv)` at the beginning of your terminal prompt.

### Step 2: Run Flask

```bash
python app.py
```

You should see output like:

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 3: Open in browser

Go to these URLs to test each feature:

| Feature         | URL                                        |
|-----------------|--------------------------------------------|
| Home page       | http://127.0.0.1:5000/                     |
| Add Patient     | http://127.0.0.1:5000/add_patient_form     |
| Delete Patient  | http://127.0.0.1:5000/delete_patient_form  |
| Update Patient  | http://127.0.0.1:5000/update_patient_form  |

---

## Part 6: Pushing Changes to Git

After everything works, commit and push your changes:

```bash
# Stage the new and modified files
git add app.py
git add templates/add_patient.html
git add templates/delete_patient.html
git add templates/update_patient.html

# Commit with a descriptive message
git commit -m "Add patient CRUD: add, update, delete functionality"

# Push to remote
git push origin main
```

If your default branch is `master` instead of `main`, use `git push origin master`.

---

## Part 7: Important Notes

### Foreign key constraint on delete

The Patient table is referenced by Appointment, Prescription, Laboratory_test, Admission, and Medical_record_notes. If you try to delete a patient who has related records in any of those tables, MySQL will throw a foreign key constraint error. You would need to delete the related records first, or add `ON DELETE CASCADE` to the foreign keys in your schema.

### Database schema match

The Patient table columns used in these routes match your `dbms_tables.sql` schema exactly:
`patient_id`, `first_name`, `last_name`, `dob`, `gender`, `address`, `phone`, `email`, `dept_name`.

### Gender domain constraint

The form dropdown limits gender to `M`, `F`, or `O` — matching the `Patient.gender IN ('M', 'F', 'O')` domain constraint from your schema report.
