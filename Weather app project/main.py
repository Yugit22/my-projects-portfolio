import requests

API_KEY = "https://api.openweathermap.org/data/2.5/weather?q=London&appid"  # 🔑 Replace this with your OpenWeatherMap API key
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city):
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'  # You can use 'imperial' for Fahrenheit
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if response.status_code == 200:
        weather = data['weather'][0]['description'].title()
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']

        print(f"\n📍 Weather in {city.title()}:")
        print(f"🌡️ Temperature: {temp}°C (Feels like {feels_like}°C)")
        print(f"🌥️ Condition: {weather}")
        print(f"💧 Humidity: {humidity}%")
        print(f"💨 Wind Speed: {wind_speed} m/s\n")
    else:
        print("❌ Could not find weather data. Please check the city name or API key.")

def main():
    print("🌍 Real-Time Weather App")
    while True:
        city = input("\nEnter city name (or type 'exit' to quit): ")
        if city.lower() == 'exit':
            print("Goodbye! ☀️")
            break
        get_weather(city)

if __name__ == "__main__":
    main()
