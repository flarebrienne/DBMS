from flask import Flask, render_template
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


if __name__ == "__main__":
    app.run(debug=True)
