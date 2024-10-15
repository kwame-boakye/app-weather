import datetime as dt
import requests


BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
Api_Key = open('//home//kelvin-boakye//KelvinBoakye//Weather-Dashboard//api_key.txt', 'rt').read().strip()
#'b054c5b99b9b6d5ae986c1649c6a30ee'
City = "Grambling"

def kelvin_to_celsius_fahreinheit(kelvin):
    celsius = kelvin - 273.15
    fahreinheit = celsius * (9/5) + 32
    return celsius, fahreinheit


Final_URL = BASE_URL + "appid=" + Api_Key + "&q=" + City

response = requests.get(Final_URL).json()

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
                                            
