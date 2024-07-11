

from flask import Flask, request, jsonify, render_template
import requests, json
from weather import Weather

app = Flask(__name__)

response_dict = {
    'status': '',
    'message': '',
    'data': {}
}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/get_forecast', methods=['GET'])
def get_forecast():
    """
    This function implements an API-Endpoint to get the forecast
    """
    resp_dict = response_dict.copy()
    weather = Weather()
    
    city = request.args.get('city')
    country = request.args.get('country')
    
    missing_params = []
    for key in ['city', 'country']:
        if locals()[key] is None:
            missing_params.append(key)

    if missing_params != []:
        resp_dict['message'] = f"Missing parameters: {', '.join(missing_params)}"
        resp_dict['status'] = 'error'
        return jsonify(resp_dict), 400
    
    forecast = weather.get_forecast(city, country)
    if forecast[1] != 200:
        return jsonify(forecast[0]), forecast[1]

    return render_template('index.html', weather_data=forecast[0]['data'])

@app.route('/health', methods=['GET'])
def get_health():
    """
    This function will be used as an API-Endpoint to check the health of the API
    """

    return jsonify({'status': 'success', 'message': 'The API is healthy', 'data':{}}), 200
    

    
