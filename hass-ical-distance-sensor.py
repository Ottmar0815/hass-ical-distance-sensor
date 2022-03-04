from genericpath import isfile
import sys
import requests, json, urllib, yaml
import datetime, pytz
from icalendar import Calendar

DESTINATIONS=[]
error=''
distance=0
payload={}
headers = {}

try:
    configfile = sys.argv[1]
    if not isfile(configfile):
        error = 'OPEN CONFIG: Argument is not a File!'
except Exception as e:
    error = 'OPEN CONFIG: no File is specified'
else:
    try:
        # Konfiguration
        with open(configfile, "r") as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        DEPARTURE           = cfg['HOME']
        ICAL_LINK           = cfg['ICAL_LINK']
        GEOAPIFY_API_KEY    = cfg['GEOAPIFY_API_KEY']
        TIME_ZONE           = cfg['TIME_ZONE']
        OFFSET              = cfg['OFFSET']
        FACTOR              = cfg['FACTOR']
        MIN                 = cfg['MIN']
        DAY_CHANGE          = cfg['DAY_CHANGE']
    except Exception as e:
        error = 'OPEN CONFIG: ' + str(e.__doc__)
    else:
        # Load Current Timestamp
        currDateTime = datetime.datetime.now(pytz.timezone(TIME_ZONE))

# Load Departure-Coordinates
if error == '':
    try:
        location_DEPARTURE_text = urllib.parse.quote(DEPARTURE)
        url_DEPARTURE = "https://api.geoapify.com/v1/geocode/search?text=" + location_DEPARTURE_text + "&limit=1&format=json&apiKey=" + GEOAPIFY_API_KEY
        response_DEPARTURE = requests.request("GET", url_DEPARTURE, headers=headers, data=payload)
        response_DEPARTURE_json = json.loads(response_DEPARTURE.text)
        location_DEPARTURE = response_DEPARTURE_json['results'][0]['lat'], response_DEPARTURE_json['results'][0]['lon']
        #print(location_from)
    except Exception as e:
        error = 'GET FROM-LOCATION(' + DEPARTURE + '): ' + str(e.__doc__)

# Load Sunset
if error == '' and DAY_CHANGE == 'Sunset':
    try:
        url_SUNSET = "https://api.sunrise-sunset.org/json?lat=" + str(location_DEPARTURE[0]) + "&lng=" + str(location_DEPARTURE[1]) + "&date=" + currDateTime.date().strftime('%Y-%m-%d') + "&formatted=0"
        response_SUNSET = requests.request("GET", url_SUNSET, headers=headers, data=payload)
        response_SUNSET_json = json.loads(response_SUNSET.text)
        dayChange = datetime.datetime.strptime(response_SUNSET_json['results']['sunset'], '%Y-%m-%dT%H:%M:%S%z')
    except Exception as e:
        error = 'GET DAY_CHANGE(Sunset): ' + str(e.__doc__)
# Load FixTime
elif error == '' and DAY_CHANGE == 'FixTime':
    try:
        FixTime = datetime.datetime.strptime(cfg['FIX_TIME'], '%H:%M:%S').time()
        dayChange = datetime.datetime.combine(currDateTime.date(), FixTime, currDateTime.tzinfo)
    except Exception as e:
        error = 'GET DAY_CHANGE(FixTime): ' + str(e.__doc__)
else:
    error = 'DAY_CHANGE: Parameter is not valid!'

# Load Calendar
if error == '':
    try:
        today = currDateTime.date()
        tomorrow = currDateTime.date() + datetime.timedelta(days=1)

        ical = requests.get(ICAL_LINK)
        gcal = Calendar.from_ical(ical.text)
        for component in gcal.walk():
            if component.name == "VEVENT":
                summary = component.get('summary')
                dtstart = component.get('dtstart')
                location = component.get('LOCATION')
                if isinstance(dtstart.dt, datetime.datetime):
                    eventDate = dtstart.dt.date()
                    if currDateTime > dayChange:
                        if (eventDate == today or eventDate == tomorrow) and (dtstart.dt > currDateTime):
                            DESTINATIONS.append(location)
                    else:
                        if (eventDate == today) and (dtstart.dt > currDateTime):
                            DESTINATIONS.append(location)
                elif isinstance(dtstart.dt, datetime.date):
                    eventDate = dtstart.dt
                    if currDateTime > dayChange:
                        if (eventDate == tomorrow):
                            DESTINATIONS.append(location)
                    else:
                        if (eventDate == today):
                            DESTINATIONS.append(location)
                else:
                    raise Exception("Can't find valid DateTime of Event: " + summary)
    except Exception as e:
        error = 'GET ICAL: ' + str(e.__doc__)
        
for DESTINATION in DESTINATIONS:
    # Load Destination-Coordinates
    if error == '':
        try:
            location_DESTINATION_text = urllib.parse.quote(DESTINATION)
            url_DESTINATION = "https://api.geoapify.com/v1/geocode/search?text=" + location_DESTINATION_text + "&limit=1&format=json&apiKey=" + GEOAPIFY_API_KEY
            response_DESTINATION = requests.request("GET", url_DESTINATION, headers=headers, data=payload)
            response_DESTINATION_json = json.loads(response_DESTINATION.text)
            location_DESTINATION = response_DESTINATION_json['results'][0]['lat'], response_DESTINATION_json['results'][0]['lon']
            #print(location_to)
        except Exception as e:
            error = 'GET TO-LOCATION(' + DESTINATION + '): ' + str(e.__doc__)

    # Load Route-Distance
    if error == '':
        try:
            url_ROUTE = "https://api.geoapify.com/v1/routing?waypoints=" + str(location_DEPARTURE[0]) + "," + str(location_DEPARTURE[1]) + "|" + str(location_DESTINATION[0]) + "," + str(location_DESTINATION[1]) + "&mode=drive&lang=de&apiKey=" + GEOAPIFY_API_KEY
            response_ROUTE = requests.request("GET", url_ROUTE, headers=headers, data=payload)
            response_ROUTE_json = json.loads(response_ROUTE.text)

            # Load Meters from Route convert to Kilometers and double for outward and return
            distance = distance + (int(response_ROUTE_json['features'][0]['properties']['distance']) / 1000 * 2)
        except Exception as e:
            error = 'GET ROUTE(' + DEPARTURE + ')-(' + DESTINATION + '): ' + str(e.__doc__)

if error == '':
    distance = distance * FACTOR + OFFSET
    distance = float.__round__(distance, 1)
    if distance < MIN:
        distance = MIN

if error != '':
    json_payload = {
        'distance' : 'unknown',
        'Error' : error
    }
elif distance != '':
    json_payload = {
        'distance' : distance,
        'Error' : 'No Error'
    }
else:
    json_payload = {
        'distance' : 'unknown',
        'Error' : 'unknown'
    }

jsonString = json.dumps(json_payload, indent=4)
print(jsonString)