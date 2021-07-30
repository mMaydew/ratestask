from flask import Flask, request, jsonify
from psycopg2 import connect
from re import compile
from os import environ

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.route('/rates', methods=['GET'])
def rates():
  raw_args = request.args.to_dict()
  # Remove unwanted parameters
  args = {
    key: raw_args[key]
    for key in raw_args
    if key in [
      "date_from",
      "date_to",
      "origin",
      "destination"
    ]
  }
  raw_args = None

  # regex to sanitise parameters
  regex_pattern = compile("[a-zA-Z0-9_-]+")
  for key in args:
    # Check that parameter actually has data
    if not args[key].strip():
      return {
        "error": "{0} parameter was not given.".format(key)
      }, 400

    # Check the parameter and put the santised version
    # in the args dictionary
    check_arg = regex_pattern.match(args[key]).group()
    args[key] = check_arg

  return jsonify(raw_args)


def query_db(query_string):
  db_connection = connect(
    host=environ.get("DATABASE_IP"),
    port=5432,
    database="postgres",
    user="postgres",
    password=environ.get("POSTGRES_PASSWORD")
  )

  cursor = db_connection.cursor()
  cursor.execute(query_string)
  queried_data = cursor.fetchall()
  db_connection.close()

  return queried_data


if __name__ == '__main__':
  app.run()