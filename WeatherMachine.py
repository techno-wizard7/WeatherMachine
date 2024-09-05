import argparse
import re
# import asyncio
from urllib.parse import quote_plus

import requests

DATA_HEADER_BASIC = {"F": ["Date", "Weather", "Temperature(F°)", "Feels Like", "Humidity", "UV Index", "Wind Direction",
                           "Wind Speed"],
                     "C": ["Date", "Weather", "Temperature(C°)", "Feels Like", "Humidity", "UV Index", "Wind Direction",
                           "Wind Speed"]}
DAILY_DATA_HEADER = {"F": ["Date", "Average Temperature(F°)", "Max Temperature", "Min Temperature", "UV Index"],
                     "C": ["Date", "Average Temperature(C°)", "Max Temperature", "Min Temperature", "UV Index"]} #, "", "", "", ""
HOURLY_DATA_HEADER = {"F": ["Time", "Weather", "Temperature(F°)", "Feels Like", "Humidity", "UV Index",
                      "Wind Chill","Wind Direction", "Wind Speed"],
                     "C": ["Time", "Weather", "Temperature(C°)", "Feels Like", "Humidity", "UV Index",
                      "Wind Chill", "Wind Direction", "Wind Speed"]}

def getColumnWidth(header, data):
    column_widths = [max(len(str(item)) for item in column) for column in zip(header, data)]
    return column_widths

def printBorder(column_widths):
    print("*" + "*".join("-" * (width + 2) for width in column_widths) + "*")


def printTable(headers, data):
    # UNDERLINE = "\033[4m"
    # RESET = "\033[0m"
    columnWidths = [max(len(str(item)) for item in column) for column in zip(headers, *data)]
    header_row = "|" + "|".join(f" {headers[i].ljust(columnWidths[i])} " for i in range(len(headers))) + "|"
    separator_row = "|" + "|".join("_" * (width + 2) for width in columnWidths) + "|"
    # if len(data) <= 1:
    #     UNDERLINE, RESET = '', ''  # We don't need these if there's only one line of data
    data_rows = [
        "|" + "|".join(f" {str(row[i]).ljust(columnWidths[i])} " for i in range(len(row))) + "|"
        # UNDERLINE + "|" + "|".join(f" {str(row[i]).ljust(columnWidths[i])} " for i in range(len(row))) + "|" + RESET
        for row in data
    ]
    # Print the table
    printBorder(columnWidths)
    print(header_row)
    print(separator_row)
    for row in data_rows:
        print(row)
    printBorder(columnWidths)



def getJsonFromUrl(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx and 5xx)
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        # Handle any errors that occurred during the request
        print(f"An error occurred: {e}")
        return None


def roundCoordinates(input_str):
    def round_match(match):
        number = float(match.group())
        return f"{number:.2f}"
    result_str = re.sub(r"\d+\.\d+", round_match, input_str)
    result_str = re.sub(r"(\.\d*?[1-9])0+$", r"\1", result_str)
    result_str = re.sub(r"\.(?=\D|$)", "", result_str)
    return result_str

def timeFormat(time):
    mid = len(time) // 2
    # Split the string into two halves
    firstHalf = time[:mid]
    secondHalf = time[mid:]

    # Join the halves with a colon
    result = firstHalf + ':' + secondHalf
    return result

def getPublicIP():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        ip = response.json().get("ip")
        return ip
    except requests.RequestException as e:
        return None


def getLocation(ip):
    try:
        response = requests.get(
            f"https://ipinfo.io/{ip}/json")  # will get location, could be more precise. Unsure if effective on cellular networks
        data = response.json()
        location = data.get("loc", "Location not found")
        return roundCoordinates(location)
    except requests.RequestException as e:
        return {"error": str(e)}


def formatDaily(weather, unit="F"):
    if unit == "F":
        speedUnits = "Miles"
    else:
        speedUnits = "Kmph"
    data = [weather['date'], weather[f'avgtemp{unit}'],
            weather[f'maxtemp{unit}'], weather[f'mintemp{unit}'], weather['uvIndex']]
    return data


def formatOneDay(weather, unit):
    if unit == "F":
        speedUnits = "Miles"
    else:
        speedUnits = "Kmph"
    data = [weather['localObsDateTime'], weather['weatherDesc'][0]['value'], weather[f'temp_{unit}'],
            weather[f'FeelsLike{unit}'], weather['humidity'], weather['uvIndex'], weather['winddir16Point'],
            weather[f'windspeed{speedUnits}']]
    return data

def formatHourly(weather, unit):
    if unit == "F":
        speedUnits = "Miles"
    else:
        speedUnits = "Kmph"
    data = [timeFormat(weather['time']), weather['weatherDesc'][0]['value'], weather[f'temp{unit}'],
            weather[f'FeelsLike{unit}'], weather['humidity'], weather['uvIndex'], weather[f'WindChill{unit}'], weather['winddir16Point'],
            weather[f'windspeed{speedUnits}']]
    return data

def getData(args):
    output = []
    # declare the client. the measuring unit used defaults to the metric system (celcius, km/h, etc.)
    # fetch a weather forecast from a city
    data = getJsonFromUrl(f'https://wttr.in/{quote_plus(args.Location)}?format=j1')
    if data['request'][0]['query'] == "Ban Not":  # Python-weather redirects to Ban Not if not found.
        raise ValueError(f'Location provided could not be found. Try another format as shown in https://wttr.in/:help')
    if args.m:
        units = "C"
    else:
        units = "F"
    location = data['nearest_area'][0]['areaName'][0]['value']
    print(f"Weather in {location}")
    if args.f:
        buffer = []
        for daily in data['weather']:
            buffer.append(formatDaily(daily, units)) #.extend(["", "", "", ""])
            printTable(DAILY_DATA_HEADER[units], buffer)
            buffer = []
            for hourly in daily['hourly']:
                buffer.append(formatHourly(hourly, units))
            printTable(HOURLY_DATA_HEADER[units], buffer)
            buffer = []
    elif not args.f and args.H:
        buffer = []
        # buffer.append(DATA_HEADER_BASIC[units])
        buffer.append(formatOneDay(data['current_condition'][0], units))
        printTable(DATA_HEADER_BASIC[units], buffer)
        buffer = []
        for hourly in data['weather'][0]['hourly']:
            buffer.append(formatHourly(hourly, units))
        printTable(HOURLY_DATA_HEADER[units], buffer)

    else:
        data = formatOneDay(data['current_condition'][0], units)
        # size = getColumnWidth([DATA_HEADER_BASIC[units], ])
        printTable(DATA_HEADER_BASIC[units], [data])
    return output


def getArgs(parser, input):
    args = parser.parse_args(input)
    # Check if -L is not used and Location is empty
    if not args.l and len(args.Location) == 0:
        parser.error("Location is required unless the -L flag is used.")
    # possibly flag an error if Location is given and -L is used. will default to text first currently.
    # elif args.l and not len(args.Location) == 0:
    #     parser.error("Location is not used if the -L flag is used.")
    elif len(args.Location) > 0:
        args.Location = ' '.join(args.Location)  # Combine words into a single string
    elif args.l:
        ip = getPublicIP()
        if ip:
            args.Location = getLocation(ip)
        else:
            parser.error("Device Location is not found. Couldn't get IP. Please check your settings")

    return args


def getParser():
    parser = argparse.ArgumentParser(description="Process a location string with optional flags.")
    parser.add_argument("-f", action="store_true",
                        help="-f Multi-Day Forecast")  # wanted to do 5-day forecast, accidentally picked an API that didn't have more than 3 days
    parser.add_argument("-H", action="store_true", help="-H Daily Hourly Forecast")
    parser.add_argument("-l", action="store_true", help="-l get Current Location")
    parser.add_argument("-m", action="store_true", help="-m use Metric")
    parser.add_argument("Location", type=str, nargs='*', help="Location string (required unless -l is used)")
    return parser

def run(input):
    args = getArgs(parser, input)
    if args.Location == "Exit":
        raise KeyboardInterrupt
    return getData(args)

if __name__ == '__main__':
    parser = getParser()
    while True:
        try:
            # Get input from the user
            input_str = input("Enter a Location and flags. Type 'Exit' to Exit")
            run(input_str.split())


        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except SystemExit:
            pass  # To prevent argparse from closing the loop

