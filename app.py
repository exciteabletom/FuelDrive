from flask import Flask, render_template

app = Flask(__name__)
app.env["app_name"] = "FuelDrive"


@app.route("/")
def main_page():
    return render_template("main.html")


if __name__ == "__main__":
    app.run()
