import requests
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os

REALTIME_DATA_PATH = "/content/drive/MyDrive/Do_an/Data/realtime_weather_history.csv"

API_KEY = '614c6943815553c19e55bb9ad160cf28' 
BASE_URL = 'https://api.openweathermap.org/data/2.5/' 

province_coords = {
    "Ha Noi": (21.0285, 105.8542),
    "Ho Chi Minh": (10.8231, 106.6297),
    "Da Nang": (16.0544, 108.2022),
    "Hai Phong": (20.8449, 106.6881),
    "Can Tho": (10.0452, 105.7469),

    "An Giang": (10.5216, 105.1259),
    "Ba Ria - Vung Tau": (10.5417, 107.2428),
    "Bac Giang": (21.2819, 106.1977),
    "Bac Kan": (22.1470, 105.8348),
    "Bac Lieu": (9.2940, 105.7216),
    "Bac Ninh": (21.1214, 106.1110),
    "Ben Tre": (10.2434, 106.3756),
    "Binh Dinh": (13.7820, 109.2197),
    "Binh Duong": (11.3254, 106.4770),
    "Binh Phuoc": (11.7512, 106.7235),
    "Binh Thuan": (11.0904, 108.0721),

    "Ca Mau": (9.1768, 105.1524),
    "Cao Bang": (22.6356, 106.2522),
    "Dak Lak": (12.7100, 108.2378),
    "Dak Nong": (12.2646, 107.6098),
    "Dien Bien": (21.3860, 103.0230),
    "Dong Nai": (10.9453, 106.8240),
    "Dong Thap": (10.4938, 105.6882),
    "Gia Lai": (13.8079, 108.1094),
    "Ha Giang": (22.8233, 104.9836),
    "Ha Nam": (20.5411, 105.9229),
    "Ha Tinh": (18.3550, 105.8877),
    "Hai Duong": (20.9373, 106.3146),
    "Hau Giang": (9.7579, 105.6413),
    "Hoa Binh": (20.6861, 105.3131),
    "Hung Yen": (20.8526, 106.0169),

    "Khanh Hoa": (12.2585, 109.0526),
    "Kien Giang": (10.0125, 105.0809),
    "Kon Tum": (14.3545, 108.0076),
    "Lai Chau": (22.3964, 103.4703),
    "Lam Dong": (11.5753, 108.1429),
    "Lang Son": (21.8537, 106.7615),
    "Lao Cai": (22.4809, 103.9755),
    "Long An": (10.6956, 106.2431),
    "Nam Dinh": (20.4388, 106.1621),
    "Nghe An": (19.2342, 104.9200),
    "Ninh Binh": (20.2506, 105.9745),
    "Ninh Thuan": (11.6739, 108.8629),

    "Phu Tho": (21.2684, 105.2046),
    "Phu Yen": (13.0882, 109.0929),
    "Quang Binh": (17.6103, 106.3487),
    "Quang Nam": (15.5394, 108.0191),
    "Quang Ngai": (15.1214, 108.8044),
    "Quang Ninh": (21.0064, 107.2925),
    "Quang Tri": (16.7403, 107.1855),

    "Soc Trang": (9.6025, 105.9739),
    "Son La": (21.3256, 103.9188),
    "Tay Ninh": (11.3352, 106.1099),
    "Thai Binh": (20.4463, 106.3366),
    "Thai Nguyen": (21.5942, 105.8482),
    "Thanh Hoa": (19.8067, 105.7852),
    "Thua Thien Hue": (16.4637, 107.5909),
    "Tien Giang": (10.4493, 106.3420),
    "Tra Vinh": (9.8127, 106.2993),
    "Tuyen Quang": (21.8236, 105.2140),

    "Vinh Long": (10.2537, 105.9722),
    "Vinh Phuc": (21.3609, 105.5474),
    "Yen Bai": (21.7168, 104.8986),
}

def get_curent_weather(city, lat, lon):
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

def fetch_parallel(max_workers = 5):
  result = []

  with ThreadPoolExecutor(max_workers=max_workers) as excecutor:
    futures = []

    for city, (lat, lon) in province_coords.items():
       futures.append(excecutor.submit(get_curent_weather, city, lat, lon))

    for future in as_completed(futures):
      data = future.result()
      if data:
        result.append(data)

  return pd.DataFrame(result)

def save_to_csv(df, filename="/content/drive/MyDrive/Do_an/Data/realtime_weather_history.csv"):
    if df.empty:
        print("Không có dữ liệu")
        return

    file_exists = os.path.exists(filename)

    df.to_csv(
        filename,
        mode="a",
        header=not file_exists,
        index=False
    )

    print(f"Đã lưu {len(df)} dòng vào {filename}")

if __name__ == "__main__":
    print("Đang fetch dữ liệu...")

    while True:
        df = fetch_parallel(max_workers=5)
        save_to_csv(df)
        print("\n=== PREVIEW ===")
        print(df.head())
        time.sleep(3600)
