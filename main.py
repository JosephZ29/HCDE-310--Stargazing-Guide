from flask import Flask, render_template, request
from datetime import datetime
import urllib.parse, urllib.request, urllib.error, json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)
##################################################################################################

baseurl = "https://weatherapi-com.p.rapidapi.com/forecast.json"
apiID = "63379beebfmsha8fb3ff08613941p1de3e5jsn933de39a87ac"


def get_content(q='Seattle', days=3, dt='2021-12-12'):
    url = baseurl + "?" + urllib.parse.urlencode({'q': q, 'days': days, 'dt': dt})
    x = urllib.request.Request(url)
    x.add_header('x-rapidapi-key', apiID)
    return json.loads(urllib.request.urlopen(x).read())


##################################################################################################

@app.route("/")
def main_handler():
    app.logger.info("In MainHandler")
    return render_template('forecast.html', page_title="Weather Forecast")


def forecast_loc(name, date, type):
    if type == "basic":
        rowData = get_content(q=name, dt=date)
        briefData = ""
        briefData += "City: " + name + "<br><br>Local Time: " + "%s" % rowData['location']['localtime']
        briefData += "<br><br>Wheather Condition: " + rowData['current']['condition']['text']
        briefData += "<br><br>Temperature: " + "%s" % rowData['current']['temp_c'] + " °C (" + "%s" % \
                     rowData['current']['temp_f'] + " °F）"
        wind_mph = rowData['current']['wind_mph']
        if wind_mph <= 1:
            wind = 'Calm'
        elif wind_mph > 1 and wind_mph <= 3:
            wind = "Light air"
        elif wind_mph > 3 and wind_mph <= 7:
            wind = "Light breeze"
        elif wind_mph > 7 and wind_mph <= 12:
            wind = "Gentle breeze"
        elif wind_mph > 12 and wind_mph <= 18:
            wind = "Moderate breeze"
        elif wind_mph > 18 and wind_mph <= 24:
            wind = "Fresh breeze"
        elif wind_mph > 24 and wind_mph <= 31:
            wind = "Strong breeze"
        elif wind_mph > 31 and wind_mph <= 38:
            wind = "Near gale"
        elif wind_mph > 38 and wind_mph <= 46:
            wind = "Gale"
        elif wind_mph > 46 and wind_mph <= 54:
            wind = "Sever gale"
        elif wind_mph > 54 and wind_mph <= 63:
            wind = "Storm"
        elif wind_mph > 63 and wind_mph <= 72:
            wind = "Violent storm"
        elif wind_mph > 72 and wind_mph <= 83:
            wind = "Hurricane"

        briefData += "<br><br>Wind Force: " + wind
        briefData += "<br><br>Humidity: " + "%s" % rowData['current']['humidity'] + "%"

    return briefData

def prof_response(name, dt):
    profData = ""
    period = []
    d = datetime.fromisoformat(dt)
    dtime = d.date()
    dttime = 10000*dtime.year + 100*dtime.month + dtime.day
    rowData = get_content(q=name, dt=dttime)
    for hours in range(len(rowData['forecast']['forecastday'][0]['hour'])):
        if hours in [21,22,23] and rowData['forecast']['forecastday'][0]['hour'][hours]['wind_mph'] < 15.0:
            if rowData['forecast']['forecastday'][0]['hour'][hours]['humidity'] < 75:
                if rowData['forecast']['forecastday'][0]['hour'][hours]['cloud'] < 25:
                    if rowData['forecast']['forecastday'][0]['hour'][hours]['precip_mm'] < 1:
                        if rowData['forecast']['forecastday'][0]['hour'][hours]['windchill_c'] > 0:
                            if rowData['forecast']['forecastday'][0]['hour'][hours]['chance_of_rain'] < 10 and rowData['forecast']['forecastday'][0]['hour'][hours]['chance_of_snow'] < 10:
                                period.append(hours)

    for hs in range(len(rowData['forecast']['forecastday'][1]['hour'])):
        if hs in [0,1,2,3] and rowData['forecast']['forecastday'][1]['hour'][hs]['wind_mph'] < 15.0:
            if rowData['forecast']['forecastday'][1]['hour'][hs]['humidity'] < 75:
                if rowData['forecast']['forecastday'][1]['hour'][hs]['cloud'] < 25:
                    if rowData['forecast']['forecastday'][1]['hour'][hs]['precip_mm'] < 1:
                        if rowData['forecast']['forecastday'][1]['hour'][hs]['windchill_c'] > 0:
                            if rowData['forecast']['forecastday'][1]['hour'][hs]['chance_of_rain'] < 10 and rowData['forecast']['forecastday'][1]['hour'][hours]['chance_of_snow'] < 10:
                                period.append(hs)
    if len(period) == 1:
        profData += "%s"%period[0]+" is an hour good to stargaze.<br><br> I am waiting for your beautiful star photograph!"
    elif len(period) > 1:
        for h in range(len(period)):
            profData += "%s" % period[h] + ":00, "
        profData += "are the hours good to stargaze.<br><br>Hope you will have an enjoyable stargazing experience this night!"
    else:
        profData += "%s"%dt+" is not a good day to stargaze in "+name+".<br><br> Please choose another day."

    return profData

def prof_details(name, date):
    profData = ""
    d = datetime.fromisoformat(date)
    dtime = d.date()
    dttime = 10000 * dtime.year + 100 * dtime.month + dtime.day
    rowData = get_content(q=name, dt=dttime)
    profData += "Moon Illumination: "+"%s"%rowData['forecast']['forecastday'][0]['astro']['moon_illumination']
    profData += "<br><br>Temperature: "+"%s"%rowData['forecast']['forecastday'][0]['hour'][23]['temp_c']+"°C ("+"%s"%rowData['forecast']['forecastday'][0]['hour'][23]['temp_f']+"°F)"
    profData += "<br><br>Wind Speed: "+"%s"%"%s"%rowData['forecast']['forecastday'][0]['hour'][23]['wind_mph']+" mph"
    profData += "<br><br>Precipitation: "+"%s"%rowData['forecast']['forecastday'][0]['hour'][23]['precip_mm']+" mm"
    profData += "<br><br>Wind Chill: "+"%s"%rowData['forecast']['forecastday'][0]['hour'][23]['windchill_c']+"°C ("+"%s"%rowData['forecast']['forecastday'][0]['hour'][23]['windchill_f']+"°F)"
    profData += "<br><br>Humidity: "+"%s"%rowData['forecast']['forecastday'][0]['hour'][23]['humidity']+" %"
    profData += "<br><br>Cloud Cover: "+"%s"%rowData['forecast']['forecastday'][0]['hour'][23]['cloud']+" %"

    return profData

@app.route("/forecastresponse")
def forecast_response_handler():
    app.logger.info(request.args.get('name'))
    name = request.args.get('name')
    date = request.args.get('date')
    oneType = request.args.get('type')
    if name and date:
        if oneType == 'basic':
            return render_template('forecastresponse.html',
                                   name=name,
                                   date=date,
                                   page_title="Brief Forecast Page for %s" % name,
                                   forecasting=forecast_loc(name, date, oneType)
                                   )
        elif oneType == 'professional':
            return render_template('profresponse.html',
                                   name=name,
                                   date=date,
                                   page_title="Professional Guide Page for %s" % name,
                                   mainguide=prof_response(name, date),
                                   details=prof_details(name, date)
                                   )
    elif not name:
        return render_template('forecast'
                               '.html',
                               page_title="Searching Form - Error",
                               prompt="Please enter a correct city...")
    elif not date:
        return render_template('forecast.html',
                               page_title="Searching Form - Error",
                               prompt="Please enter a correct date...")


if __name__ == "__main__":
    # Used when running locally only. 
    # When deploying to Google AppEngine, a webserver process will
    # serve your app.
    app.run(host="localhost", port=8080, debug=True)
