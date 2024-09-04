import re
import requests
import argparse
# import asyncio
from urllib.parse import quote_plus
import os

DATE_HEADER = [""]
DATA_HEADER = ["Weather", "Feels Like", "Temperature", "Humidity", "UV Index", "Wind Speed", "Wind Direction"]

def get_json_from_url(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx and 5xx)

        # Parse the JSON content
        data = response.json()

        return data

    except requests.exceptions.RequestException as e:
        # Handle any errors that occurred during the request
        print(f"An error occurred: {e}")
        return None

def round_coordinates(input_str):
    # Define a function to round a number to two decimal places
    def round_match(match):
        number = float(match.group())
        return f"{number:.2f}"

    # Use regular expressions to find all numbers in the input string
    result_str = re.sub(r"\d+\.\d+", round_match, input_str)

    # Remove any trailing zeros and decimal points if not needed
    result_str = re.sub(r"(\.\d*?[1-9])0+$", r"\1", result_str)
    result_str = re.sub(r"\.(?=\D|$)", "", result_str)

    return result_str

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        ip = response.json().get("ip")
        return ip
    except requests.RequestException as e:
        return None

def get_location(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json") #will get location, could be more precise. Unsure if effective on cellular networks
        data = response.json()
        location = data.get("loc", "Location not found")
        return round_coordinates(location)
    except requests.RequestException as e:
        return {"error": str(e)}

def formatWeather(weather):
    return None


def getweather(args):
    # declare the client. the measuring unit used defaults to the metric system (celcius, km/h, etc.)
        # fetch a weather forecast from a city
    weather = get_json_from_url(f'https://wttr.in/{quote_plus(args.Location)}?format=j1')
    if weather['request'][0]['query'] == "Ban Not": #Python-weather redirects to Ban Not if not found.
        raise ValueError(f'Location provided could not be found. Try another format as shown in https://wttr.in/:help')
    if args.F and args.H:
        for daily in weather['weather']:
            print(daily)
            # hourly forecasts
            for hourly in daily['hourly']:
                print(f' --> {hourly!r}')
    elif not args.F and args.H:
            # hourly forecasts
            for hourly in weather['weather']['hourly']:
                print(f' --> {hourly!r}')
    elif args.F and not args.H:
        for daily in weather.daily_forecasts:
            print(daily)
    else:
        print(weather['current_condition'][0])

def getArgs(parser, input):
    args = parser.parse_args(input)
    # Check if -L is not used and Location is empty
    if not args.l and len(args.Location) == 0:
        parser.error("Location is required unless the -L flag is used.")
    #possibly flag an error if Location is given and -L is used. will default to text first currently.
    # elif args.l and not len(args.Location) == 0:
    #     parser.error("Location is not used if the -L flag is used.")
    elif len(args.Location) > 0:
        args.Location = ' '.join(args.Location)  # Combine words into a single string
        print(f"Location: {args.Location}")
    elif args.l:
        ip = get_public_ip()
        if ip:
            args.Location = get_location(ip)
        else:
            parser.error("Device Location is not found. Please Connect to the internet")

    return args

def getParser():
    parser = argparse.ArgumentParser(description="Process a location string with optional flags.")
    parser.add_argument("-f", action="store_true", help="-f Three Day Forecast")
    parser.add_argument("-H", action="store_true", help="-H Daily Hourly Forecast")
    parser.add_argument("-l", action="store_true", help="-l get Current Location")
    parser.add_argument("-m", action="store_true", help="-m use Metric")
    parser.add_argument("-a", action="store_true", help="-a All data")
    parser.add_argument("Location", type=str, nargs='*', help="Location string (required unless -l is used)")
    return parser

def print_table(headers, data):
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"
    # Calculate column widths based on the longest word in each column
    column_widths = [max(len(str(item)) for item in column) for column in zip(headers, *data)]

    # Create the top border
    top_border = "*" + "*".join("-" * (width + 2) for width in column_widths) + "*"

    # Create the header row
    header_row = "|" + "|".join(f" {headers[i].ljust(column_widths[i])} " for i in range(len(headers))) + "|"

    # Create the separator row
    separator_row = "|" + "|".join("_" * (width + 2) for width in column_widths) + "|"

    # Create the data rows
    data_rows = [
        UNDERLINE + "|" + "|".join(f" {str(row[i]).ljust(column_widths[i])} " for i in range(len(row))) + "|" + RESET for row in data
    ]

    # Print the table
    print(top_border)
    print(header_row)
    print(separator_row)
    for row in data_rows:
        print(row)
    print(top_border)

if __name__ == '__main__':
    # if os.name == 'nt':
    #     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    parser = getParser()

    while True:
        try:
            # Get input from the user
            input_str = input("Enter a Location and Flags  ")
            args = getArgs(parser, input_str.split())
            # Parse the input

            # asyncio.run(
            getweather(args) #)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except SystemExit:
            pass  # To prevent argparse from closing the loop

