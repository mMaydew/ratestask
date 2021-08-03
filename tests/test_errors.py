from requests import get
import pytest


def test_missing_parameter():
  param_strings = {
    "date_from": "?date_to=2016-01-10&origin=china_main&destination=north_europe_main",
    "date_to": "?date_from=2016-01-01&origin=china_main&destination=north_europe_main",
    "origin": "?date_from=2016-01-01&date_to=2016-01-10&destination=north_europe_main",
    "destination": "?date_from=2016-01-01&date_to=2016-01-10&origin=china_main"
  }
  for param in param_strings:
    url = "http://localhost/rates%s" % (param_strings[param])
    api_output = get(url)

    assert api_output.status_code == 400
    assert api_output.json()["error"] == "%s parameter was not given." % param


def test_missing_param_data():
  param_strings = {
    "date_from": "?date_from=&date_to=2016-01-10&origin=china_main&destination=north_europe_main",
    "date_to": "?date_from=2016-01-01&date_to=&origin=china_main&destination=north_europe_main",
    "origin": "?date_from=2016-01-01&date_to=2016-01-10&origin=&destination=north_europe_main",
    "destination": "?date_from=2016-01-01&date_to=2016-01-10&origin=china_main&destination="
  }
  for param in param_strings:
    url = "http://localhost/rates%s" % (param_strings[param])
    api_output = get(url)

    assert api_output.status_code == 400
    assert api_output.json()["error"] == "No data given for parameter %s." % param