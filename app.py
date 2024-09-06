# # app.py (Flask Backend)
# # built by Kordell Carmin
import types
from flask import Flask, request, render_template
from WeatherMachine import run, getLocation

app = Flask(__name__)

def formatInput(location, f=False, H=False, m=False):
    # because I wrote this only thinking of backend functionality first (my mistake) it's arguments are handled through
    # an argparse created parser. This fixes that. Slightly clunky imo, but hey, the goal was for working not perfect
    args = types.SimpleNamespace()
    setattr(args, "Location", location)
    setattr(args, 'f', f)
    setattr(args, 'H', H)
    setattr(args, 'm', m)
    return args

@app.route('/')
def index():
    if "location" in request.args:
        location = request.args.get('location', 'No text provided')
        if location == "Location not found":
            return get404(f"Sorry but we could not find your location.")
        fiveDay = request.args.get('fiveDay', default=False, type=bool)  # , 'No text provided'
        hourly = request.args.get('hourly', default=False, type=bool)
        metric = request.args.get('metric', default=False, type=bool)
        output = run(formatInput(location, hourly, fiveDay, metric))
        if output is None:
            return get404([f"Weather data could not be found for {location}"])
        elif output[0] == "ERROR":
            return get404([f"Weather data could not be found for {location}"])
        render = render_template('WeatherMachine.html', text=output)
        return render
    else:
        return render_template('WeatherMachine.html', text = None)
@app.route('/404')
def get404(message=None):
    if message is not None:
        message=[message]
    return render_template('404.html', text=message)

@app.route('/lookup')
def lookup():
    text = request.args.get('text', 'No text provided')
    fiveDay = request.args.get('fiveDay', default=False, type=bool)  # , 'No text provided'
    hourly = request.args.get('hourly', default=False, type=bool)
    metric = request.args.get('metric', default=False, type=bool)
    output = run(formatInput(text, hourly, fiveDay, metric))
    render = render_template('WeatherMachine.html', text=output)
    return render



if __name__ == '__main__':
    app.run(debug=True)
