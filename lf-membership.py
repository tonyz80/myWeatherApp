from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Convert city → coordinates using Open-Meteo geocoding API
def get_coordinates(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city,
        "count": 1
    }

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    if "results" not in data:
        return None

    result = data["results"][0]
    return result["latitude"], result["longitude"], result["name"], result["country"]


# Fetch weather
def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True
    }

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    return data.get("current_weather", None)


@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    location = None
    error = None

    if request.method == "POST":
        city = request.form.get("city")

        coords = get_coordinates(city)
        if not coords:
            error = "City not found."
        else:
            lat, lon, name, country = coords
            weather = get_weather(lat, lon)
            location = f"{name}, {country}"

    return render_template(
        "index.html",
        weather=weather,
        location=location,
        error=error
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
