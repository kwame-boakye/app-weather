import datetime as dt
import requests

# Define the base URL for the OpenWeatherMap API
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

# Open the file containing the API key, read its content, and remove any leading/trailing whitespace
Api_Key = open('//home//kelvin-boakye//repos//weather-app//Weather-Dashboard//api_key.txt', 'r').read().strip()
City = "Grambling"

def kelvin_to_celsius_fahreinheit(kelvin):   
    celsius = kelvin - 273.15
    fahreinheit = celsius * (9/5) + 32
    return celsius, fahreinheit

# Construct the final URL by appending the API key and city to the base URL
Final_URL = BASE_URL + "appid=" + Api_Key + "&q=" + City

# Send a GET request to the API and convert the response to JSON format
response = requests.get(Final_URL).json()

# Extract relevant data from the JSON response
temp_kelvin = response['main']['temp']
temp_celsius, temp_fahreinheit = kelvin_to_celsius_fahreinheit(temp_kelvin)
feels_like_kelvin = response['main']['temp']
feels_like_celsius, feels_like_fahreinheit = kelvin_to_celsius_fahreinheit(
    feels_like_kelvin
)
wind_speed = response['wind']['speed']
humidity = response['main']['humidity']
description = response['weather'][0]['description']
sunrise_time = dt.datetime.fromtimestamp(response['sys']['sunrise'],  
                                         tz=dt.timezone.utc)
sunset_time = dt.datetime.fromtimestamp(response['sys']['sunset'],  
                                         tz=dt.timezone.utc)

# Prepare the output string to display the weather information
output = (
    f"Weather in {City}:\n"
    f"Temperature: {temp_celsius:.2f}C / {temp_fahreinheit:.2f}F\n"
    f"Feels Like: {feels_like_celsius:.2f}C / {feels_like_fahreinheit:.2f}F\n"
    f"Humidity: {humidity}%\n"
    f"Wind Speed: {wind_speed} m/s\n"
    f"Description: {description.capitalize()}\n"
    f"Sunrise: {sunrise_time.strftime('%Y-%m-%d %H:%M:%S')} UTC+0\n"
    f"Sunset: {sunset_time.strftime('%Y-%m-%d %H:%M:%S')} UTC+0"
)

print(output)
                                            
