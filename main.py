import os
import logging


from flask import render_template
import connexion

app = connexion.App(__name__, specification_dir="./")
app.add_api("swagger.yml")


@app.route("/")
def index():
    logging.info("Rendering Page")
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
