from flask import Flask, render_template, request
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import requests

app = Flask(__name__)

# -----------------------------
# Open-Meteo client setup
# -----------------------------
cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=3, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


# -----------------------------
# City → Coordinates
# -----------------------------
def get_coordinates(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1}

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    if "results" not in data:
        return None

    result = data["results"][0]
    return result["latitude"], result["longitude"], result["name"], result["country"]


# -----------------------------
# Weather Fetch
# -----------------------------
def get_weather(lat, lon):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": [
            "uv_index",
            "sunshine_duration",
            "direct_radiation",
        ],
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "is_day",
            "precipitation",
            "wind_speed_10m",
            "rain",
            "wind_direction_10m",
        ],
        "wind_speed_unit": "mph",
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # -----------------------------
    # CURRENT WEATHER
    # -----------------------------
    current = response.Current()

    weather_current = {
        "temperature": current.Variables(0).Value(),
        "humidity": current.Variables(1).Value(),
        "apparent_temperature": current.Variables(2).Value(),
        "is_day": bool(current.Variables(3).Value()),
        "precipitation": current.Variables(4).Value(),
        "wind_speed": current.Variables(5).Value(),
        "rain": current.Variables(6).Value(),
        "wind_direction": current.Variables(7).Value(),
        "time": current.Time(),
    }

    # -----------------------------
    # HOURLY DATA
    # -----------------------------
    hourly = response.Hourly()

    hourly_uv_index = hourly.Variables(0).ValuesAsNumpy()
    hourly_sunshine_duration = hourly.Variables(1).ValuesAsNumpy()
    hourly_direct_radiation = hourly.Variables(2).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )
    }

    hourly_data["uv_index"] = hourly_uv_index
    hourly_data["sunshine_duration"] = hourly_sunshine_duration
    hourly_data["direct_radiation"] = hourly_direct_radiation

    hourly_df = pd.DataFrame(hourly_data)

    # Only return next 12 hours (keeps page fast)
    hourly_preview = hourly_df.head(12).to_dict(orient="records")

    return weather_current, hourly_preview


# -----------------------------
# Flask Route
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    weather = None
    hourly = None
    location = None
    error = None

    if request.method == "POST":
        city = request.form.get("city")

        coords = get_coordinates(city)
        if not coords:
            error = "City not found."
        else:
            lat, lon, name, country = coords
            weather, hourly = get_weather(lat, lon)
            location = f"{name}, {country}"

    return render_template(
        "index.html",
        weather=weather,
        hourly=hourly,
        location=location,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
