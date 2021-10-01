# -*- coding: utf-8 -*-
import json

from flask import Flask, request
from jinja2 import Environment
from urllib.request import Request, urlopen

app = Flask(__name__)
environment = Environment()


def jsonfilter(value):
    return json.dumps(value)


environment.filters["json"] = jsonfilter

def error_response(message):
    response_template = environment.from_string("""
    {
      "status": "error",
      "message": {{message|json}},
      "data": {
        "version": "1.0"
      }
    }
    """)
    payload = response_template.render(message=message)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response

def query_response(value, grammar_entry):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.1",
        "result": [
          {
            "value": {{value|json}},
            "confidence": 1.0,
            "grammar_entry": {{grammar_entry|json}}
          }
        ]
      }
    }
    """)
    payload = response_template.render(value=value, grammar_entry=grammar_entry)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response

def multiple_query_response(results):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "result": [
        {% for result in results %}
          {
            "value": {{result.value|json}},
            "confidence": 1.0,
            "grammar_entry": {{result.grammar_entry|json}}
          }{{"," if not loop.last}}
        {% endfor %}
        ]
      }
    }
     """)
    payload = response_template.render(results=results)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response

def validator_response(is_valid):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "is_valid": {{is_valid|json}}
      }
    }
    """)
    payload = response_template.render(is_valid=is_valid)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/dummy_query_response", methods=['POST'])
def dummy_query_response():
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.1",
        "result": [
          {
            "value": "dummy",
            "confidence": 1.0,
            "grammar_entry": null
          }
        ]
      }
    }
     """)
    payload = response_template.render()
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/action_success_response", methods=['POST'])
def action_success_response():
    response_template = environment.from_string("""
   {
     "status": "success",
     "data": {
       "version": "1.1"
     }
   }
   """)
    payload = response_template.render()
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response

# GET WEATHER FROM API
def get_weather_data(city,country, unit="metric"):
    '''
    Args:
        city, country:str
        unit (optional): 'metric'|'standard'|'imperial' => returns temperature in C|K|F
    Returns: 
        a JSON dict
    '''
    # Replace spaces with '+'
    spaces_to_plus = lambda name : ''.join([c if c.isalnum() else '+' for c in name])
    city, country = spaces_to_plus(city), spaces_to_plus(country)

    api_key = '439da00c4e597bf7c30a0cc885fad5e4'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&units={unit}&APPID={api_key}"

    try:
      request = Request(url)
      response = urlopen(request)
      data = response.read()
      return json.loads(data)
    except Exception:
      return 'city not found'

@app.route("/get_temperature", methods=['POST'])
def get_temperature():
    payload = request.get_json()
    city = payload["context"]["facts"]["city_to_search"]["grammar_entry"]
    country = payload["context"]["facts"]["country_to_search"]["grammar_entry"]
    city, country = str(city), str(country)

    # Optional unit parameter
    if 'unit_to_search' in payload["context"]["facts"]:  
      unit = payload["context"]["facts"]["unit_to_search"]["grammar_entry"] 
      unit = str(unit) # 'metric'|'standard'|'imperial'
    else:
      unit = 'metric'

    weather_data = get_weather_data(city, country, unit=unit)
    if type(weather_data)==str:
      out = weather_data
    else:
      temp_now = weather_data['main']['temp']
      degrees_unit = {'metric':'°C', 'imperial':'°F', 'standard':'°K'}[unit]
      out = str(round(temp_now, 1)) + degrees_unit

    return query_response(value=out, grammar_entry=None)

@app.route("/get_weather", methods=['POST'])
def get_weather():
    payload = request.get_json()
    
    city = payload["context"]["facts"]["city_to_search"]["grammar_entry"]
    country = payload["context"]["facts"]["country_to_search"]["grammar_entry"]
    city, country = str(city), str(country)

    weather_data = get_weather_data(city, country)
    if type(weather_data)==str:
      out = weather_data
    else:
      out = weather_data['weather'][0]['description']

    return query_response(value=out, grammar_entry=None)