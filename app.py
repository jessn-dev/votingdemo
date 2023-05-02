import datetime
import logging
import os
from typing import Dict

from flask import Flask, render_template, request, Response
# from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm

import sqlalchemy

from connect_connector import connect_with_connector
from connect_connector_auto_iam_authn import connect_with_connector_auto_iam_authn

app = Flask(__name__)

logger = logging.getLogger()


def init_connection_pool() -> sqlalchemy.engine.base.Engine:
    if os.environ.get("INSTANCE_CONNECTION_NAME"):
        return connect_with_connector_auto_iam_authn() if os.environ.get("DB_IAM_USER") else connect_with_connector()

    raise ValueError(
        "Missing database connection type. Please define INSTANCE_CONNECTION_NAME"
    )


# create 'votes' table in database if it does not already exist
def migrate_db(db: sqlalchemy.engine.base.Engine) -> None:
    with db.connect() as conn:
        conn.execute(sqlalchemy.text(
            "CREATE TABLE IF NOT EXISTS votes "
            "( vote_id SERIAL NOT NULL, time_cast timestamp NOT NULL, "
            "candidate VARCHAR(250) NOT NULL, PRIMARY KEY (vote_id) );"
        ))
        conn.commit()


# This global variable is declared with a value of `None`, instead of calling
# `init_db()` immediately, to simplify testing. In general, it
# is safe to initialize your database connection pool when your script starts
# -- there is no need to wait for the first request.
db = None


# init_db lazily instantiates a database connection pool. Users of Cloud Run or
# App Engine may wish to skip this lazy instantiation and connect as soon
# as the function is loaded. This is primarily to help testing.
@app.before_first_request
def init_db() -> sqlalchemy.engine.base.Engine:
    global db
    db = init_connection_pool()
    migrate_db(db)


@app.route("/", methods=["GET"])
def render_index() -> str:
    context = get_index_context(db)
    return render_template("index.html", **context)


@app.route("/votes", methods=["POST"])
def cast_vote() -> Response:
    team = request.form['team']
    return save_vote(db, team)


# get_index_context gets data required for rendering HTML application
def get_index_context(db: sqlalchemy.engine.base.Engine) -> Dict:
    votes = []

    with db.connect() as conn:
        # Execute the query and fetch all results
        recent_votes = conn.execute(sqlalchemy.text(
            "SELECT candidate, time_cast FROM votes ORDER BY time_cast DESC LIMIT 5"
        )).fetchall()
        # Convert the results into a list of dicts representing votes
        for row in recent_votes:
            votes.append({"candidate": row[0], "time_cast": row[1]})

        stmt = sqlalchemy.text(
            "SELECT COUNT(vote_id) FROM votes WHERE candidate=:candidate"
        )
        # Count number of votes for tabs
        apple_count = conn.execute(stmt, parameters={"candidate": "APPLE"}).scalar()
        # Count number of votes for spaces
        android_count = conn.execute(stmt, parameters={"candidate": "ANDROID"}).scalar()

    return {
        "apple_count": apple_count,
        "recent_votes": votes,
        "android_count": android_count,
    }


# save_vote saves a vote to the database that was retrieved from form data
def save_vote(db: sqlalchemy.engine.base.Engine, team: str) -> Response:
    time_cast = datetime.datetime.now(tz=datetime.timezone.utc)
    # Verify that the team is one of the allowed options
    if team != "APPLE" and team != "ANDROID":
        logger.warning(f"Received invalid 'team' property: '{team}'")
        return Response(
            response="Invalid team specified. Should be one of 'APPLE' or 'ANDROID'",
            status=400,
        )

    # [START cloud_sql_postgres_sqlalchemy_connection]
    # Preparing a statement before hand can help protect against injections.
    stmt = sqlalchemy.text(
        "INSERT INTO votes (time_cast, candidate) VALUES (:time_cast, :candidate)"
    )
    try:
        # Using a with statement ensures that the connection is always released
        # back into the pool at the end of statement (even if an error occurs)
        with db.connect() as conn:
            conn.execute(stmt, parameters={"time_cast": time_cast, "candidate": team})
            conn.commit()
    except Exception as e:
        # If something goes wrong, handle the error in this section. This might
        # involve retrying or adjusting parameters depending on the situation.
        # [START_EXCLUDE]
        logger.exception(e)
        return Response(
            status=500,
            response="Unable to successfully cast vote! Please check the "
            "application logs for more details.",
        )
        # [END_EXCLUDE]
    # [END cloud_sql_postgres_sqlalchemy_connection]

    return Response(
        status=200,
        response=f"Vote successfully cast for '{team}' at time {time_cast}!",
    )



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
