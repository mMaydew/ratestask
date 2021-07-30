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

  destination_codes = get_codes(args["destination"])
  origin_codes = get_codes(args["origin"])

  # If there is no dest/orig codes return a 400 error
  if not destination_codes:
    return {
      "error": "Destination location does not exist",
      "destination": args["destination"]
    }, 400
  if not origin_codes:
    return {
      "error": "Origin location does not exist",
      "origin": args["origin"]
    }, 400

  # Data to pass to the average price function:
  # args["date_from"], args["date_to"], origin_codes[0][0], destination_codes[0][0]

  return jsonify(raw_args)


def get_codes(location):
  '''
  Take location as an argument and return all the codes linked to it.\n
  Return an empty array if no codes exist for the given location.
  '''
  codes = query_db(
    """
    SELECT JSON_AGG(TO_JSON(json_data)->'code')
    FROM (
      SELECT ports.code
      FROM public.ports
      RIGHT JOIN public.regions
        ON regions.slug = ports.parent_slug
      WHERE regions.parent_slug = '{0}'
        OR ports.parent_slug = '{0}'
        OR ports.code = '{0}'
    ) AS json_data;
    """.format(location)
  )

  return codes


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