from flask import Flask, request, jsonify
from psycopg2 import connect
from re import compile
from os import environ

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.route('/rates', methods=['GET'])
def rates():
  raw_args = request.args.to_dict()
  required_params = [
      "date_from",
      "date_to",
      "origin",
      "destination"
    ]
  # Remove unwanted parameters
  args = {
    key: raw_args[key]
    for key in raw_args
    if key in required_params
  }
  raw_args = None

  if len(args) != 4:
    for param in required_params:
      if param not in args:
        return {
          "error": "{0} parameter was not given.".format(param)
        }, 400

  # regex to sanitise parameters
  regex_pattern = compile("[a-zA-Z0-9_-]+")
  for key in args:
    # Check that parameter actually has data
    if not args[key].strip():
      return {
        "error": "No data given for parameter {0}.".format(key)
      }, 400

    # Check the parameter and put the santised version
    # in the args dictionary
    check_arg = regex_pattern.match(args[key]).group()
    if len(check_arg) == 5:
      check_arg = check_arg.upper()
    else:
      check_arg = check_arg.lower()

    args[key] = check_arg

  destination_codes = get_codes(args["destination"])[0][0]
  origin_codes = get_codes(args["origin"])[0][0]

  # If there is no dest/orig codes return a 400 error
  if not destination_codes:
    return {
      "error": "destination does not exist",
      "destination": args["destination"]
    }, 400
  if not origin_codes:
    return {
      "error": "origin does not exist",
      "origin": args["origin"]
    }, 400

  output_data = average_price(
    args["date_from"],
    args["date_to"],
    origin_codes,
    destination_codes
  )[0][0]

  if not output_data:
    return jsonify([])

  return jsonify(output_data)


def get_codes(location):
  '''
  Take location as an argument and return all the codes linked to it.\n
  Return an empty array if no codes exist for the given location.\n
  Args:\n
    \tlocation - The location parameter from the API
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


def average_price(date_from, date_to, origin, destination):
  '''
  Take the sanitised params and codes to query for average prices.\n
  Args:\n
    \tdate_from\n
    \tdate_to\n
    \torigin\n
    \tdestination
  '''
  price_data = query_db(
    """
    SELECT JSON_AGG(TO_JSON(json_data))
    FROM (
      SELECT prices.day,
      CASE
        WHEN COUNT(prices.price) >= 3 THEN ROUND(AVG(prices.price), 0)
        WHEN COUNT(prices.price) < 3 THEN null
      END AS average_price
      FROM public.prices
      WHERE prices.orig_code in ({0})
        AND prices.dest_code in ({1})
        AND prices.day >= '{2}'
        AND prices.day <= '{3}'
      GROUP BY prices.day
      ORDER BY prices.day
    ) AS json_data;
    """.format(
      ", ".join(
        "'" + code + "'"
        for code in origin
      ),
      ", ".join(
        "'" + code + "'"
        for code in destination
      ),
      date_from,
      date_to
    )
  )

  return price_data


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