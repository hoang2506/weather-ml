from django.shortcuts import render

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier, XGBRegressor
from sklearn.metrics import accuracy_score, mean_squared_error
import pytz
import joblib, io
import os
import warnings
from .apps import WeatherConfig

# ===== CONFIG =====
# MODEL_PATH = "https://github.com/hoang2506/weather-ml/blob/5abb42c8eb816f388255b7cd30216dfbab315192/retrain_model.py"
FILE_PATH = "https://github.com/hoang2506/weather-ml/blob/5abb42c8eb816f388255b7cd30216dfbab315192/weather_data.csv"
API_KEY = "614c6943815553c19e55bb9ad160cf28"
BASE_URL = 'https://api.openweathermap.org/data/2.5/'
timezone = pytz.timezone('Asia/Ho_Chi_Minh')

RAW_URL = "https://raw.githubusercontent.com/hoang2506/weather-ml/main/retrain_model.pkl"

def load_model():
    response = requests.get(RAW_URL)
    model = joblib.load(io.BytesIO(response.content))
    return model

# Load model 1 lần
model = load_model()

# Map label
LABEL_MAP = {
    0: "Clear",
    1: "Clouds",
    2: "Rain",
    3: "Other"
}

def get_current_weather(city, lat, lon):
    url = f"{BASE_URL}weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        print(f"Lỗi: {data.get('message', 'Unknown error')}")
        return None

    weather_main = data["weather"][0]["main"]

    if weather_main in ["Drizzle", "Rain", "Thunderstorm"]:
        weather_group = "Rain"
    elif weather_main == "Clear":
        weather_group = "Clear"
    elif weather_main == "Clouds":
        weather_group = "Clouds"
    else:
        weather_group = "Other"

    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": round(data["main"]["temp"], 2),
        "feels_like": round(data["main"]["feels_like"], 2),
        "temp_min": round(data["main"]["temp_min"], 2),
        "temp_max": round(data["main"]["temp_max"], 2),
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "visibility": data.get("visibility", 10000),
        "cloudcover": data["clouds"]["all"],
        "wind_speed": data["wind"]["speed"],
        "wind_gust": data["wind"].get("gust", data["wind"]["speed"]),
        "wind_direction": data["wind"]["deg"],
        "weather_main": weather_main,
        "weather_group": weather_group
    }

def predict_weather_class(weather, model):
    features = [[
        weather["temperature"],
        weather["temp_min"],
        weather["temp_max"],
        weather["humidity"],
        weather["feels_like"],
        weather["visibility"],
        weather["cloudcover"],
        weather["wind_speed"],
        weather["wind_gust"],
        weather["wind_direction"],
        weather["pressure"]
    ]]

    pred = model.predict(features)[0]
    return LABEL_MAP.get(pred, "Unknown")

def encode_weather_group(label):
    reverse_map = {
        "Clear": 0,
        "Clouds": 1,
        "Rain": 2,
        "Other": 3
    }
    return reverse_map[label]

def load_latest_model():
    models = [f for f in os.listdir() if f.endswith(".pkl")]
    latest = max(models, key=os.path.getctime)
    return joblib.load(latest)

model = load_latest_model()

def prepare_regression_data(data, feature):
    series = data[feature].dropna().values
    X = series[:-1].reshape(-1, 1)
    y = series[1:]
    return X, y

def train_regression_model(X, y):
    model = XGBRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def predict_future(model, current_value, steps=5):
    predictions = []
    last_value = current_value

    for _ in range(steps):
        next_value = model.predict([[last_value]])[0]
        predictions.append(next_value)
        last_value = next_value

    return predictions

def reload_model_view(request):
    WeatherConfig.model = load_model()
    return JsonResponse({"status": "model reloaded"})

def weather_view(city, lat, lon):

    model = WeatherConfig.model
    weather = get_current_weather(city, lat, lon)
    if weather is None: return

    now = datetime.now(timezone)
    base_hour = now.replace(minute=0, second=0, microsecond=0)
    
    df_history = pd.read_csv(FILE_PATH)
    
    for label, (col, current_val) in {'Nhiệt độ (°C)': ('temperature', weather['temperature']), 'Độ ẩm (%)': ('humidity', weather['humidity'])}.items():
        X_r, y_r = prepare_regression_data(df_history, col)
        reg_model = train_regression_model(X_r, y_r)
        preds = predict_future(reg_model, current_val, steps=5)
        for i, val in enumerate(preds, 1):
            t = (base_hour + timedelta(hours=i)).strftime('%H:%M')
            print(f"    +{i} giờ ({t}): {round(val, 2)}")
