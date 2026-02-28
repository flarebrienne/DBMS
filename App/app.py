from flask import Flask
import pymysql as db

app = Flask(__name__)

conn = db.connect(
    host="localhost",
    user="root",
    password="",      # put your password here if any
    database="test"
)

@app.route("/person")
def person():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM person;")
    out = cursor.fetchall()

    result = "<h1>Persons:</h1>"
    for row in out:
        result += "<p>" + ", ".join([str(i) for i in row]) + "</p>"

    cursor.close()
    return result




@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Connection Status</title>
        <style>
            body {
                margin: 0;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background-color: #f4f4f4;
                font-family: Arial, sans-serif;
            }
            .box {
                background-color: orange;
                padding: 40px 60px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            }
            h1 {
                color: white;
                margin-bottom: 15px;
            }
            p {
                color: white;
                font-size: 20px;
                margin: 0;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Database Connected Successfully</h1>
            <p>Abdourahman, Bikash, Farhana</p>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)
