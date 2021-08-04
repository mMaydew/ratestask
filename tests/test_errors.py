from requests import get


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


def test_location_cases():
  param_strings = {
    "code_uppercase": "?date_from=2016-01-01&date_to=2016-01-02&origin=CNSGH&destination=IEDUB",
    "code_lowercase": "?date_from=2016-01-01&date_to=2016-01-02&origin=cnsgh&destination=iedub",
    "slug_uppercase": "?date_from=2016-01-01&date_to=2016-01-02&origin=china_main&destination=north_europe_main",
    "slug_lowercase": "?date_from=2016-01-01&date_to=2016-01-02&origin=china_main&destination=north_europe_main",
    "region_uppercase": "?date_from=2016-01-01&date_to=2016-01-02&origin=CHINA_MAIN&destination=NORTHERN_EUROPE",
    "region_lowercase": "?date_from=2016-01-01&date_to=2016-01-02&origin=china_main&destination=northern_europe"
  }
  for param in param_strings:
    url = "http://localhost/rates%s" % (param_strings[param])
    api_output = get(url)

    assert api_output.status_code == 200


def test_incorrect_location():
  param_strings = {
    "origin": "?date_from=2016-01-01&date_to=2016-01-02&origin=djfhf&destination=north_europe_main",
    "destination": "?date_from=2016-01-01&date_to=2016-01-02&origin=china_main&destination=djfhf"
  }

  for param in param_strings:
    url = "http://localhost/rates%s" % (param_strings[param])
    api_output = get(url)

    assert api_output.status_code == 400
    assert api_output.json()["error"] == "%s does not exist" % (param)
    # Static because it returns the parameter given and there is no need to test others
    assert api_output.json()[param] == "DJFHF"