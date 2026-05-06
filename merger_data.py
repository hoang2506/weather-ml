import pandas as pd
import os
import requests

HIST_URL = "https://drive.google.com/uc?id=1fX3VeNhGsypxsHa1ia-3BlpCMsMk-pzi"
HIST_PATH = "data/historical_data.csv"

REAL_PATH = "data/weather_data.csv"
MERGED_PATH = "data/merged_data.csv"

def download_historical():
    if not os.path.exists(HIST_PATH):
        print("Download historical data...")
        r = requests.get(HIST_URL)
        with open(HIST_PATH, "wb") as f:
            f.write(r.content)

def merge_data():
    download_historical()

    df_hist = pd.read_csv(HIST_PATH)

    if os.path.exists(REAL_PATH):
        df_real = pd.read_csv(REAL_PATH)
        df = pd.concat([df_hist, df_real], ignore_index=True)
    else:
        df = df_hist

    df = df.dropna().drop_duplicates()

    df.to_csv(MERGED_PATH, index=False)
    print(f"merged: {len(df)} rows")

if __name__ == "__main__":
    merge_data()
