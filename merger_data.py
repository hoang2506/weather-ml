import pandas as pd
import os
import requests

HIST_URL = "https://drive.google.com/uc?id=1fX3VeNhGsypxsHa1ia-3BlpCMsMk-pzi"
HIST_PATH = "historical_data.csv"

REAL_PATH = "weather_data.csv"
MERGED_PATH = "merged_data.csv"

def download_historical():
    if not os.path.exists(HIST_PATH):
        print("Download historical data...")
        r = requests.get(HIST_URL)

        if r.status_code != 200:
            raise Exception("Download failed")

        with open(HIST_PATH, "wb") as f:
            f.write(r.content)

def merge_data():
    download_historical()

    # đọc an toàn
    df_hist = pd.read_csv(HIST_PATH, on_bad_lines='skip')

    if os.path.exists(REAL_PATH):
        df_real = pd.read_csv(REAL_PATH, on_bad_lines='skip')

        # đồng bộ cột
        common_cols = list(set(df_hist.columns) & set(df_real.columns))
        df_hist = df_hist[common_cols]
        df_real = df_real[common_cols]

        df = pd.concat([df_hist, df_real], ignore_index=True)
    else:
        df = df_hist

    df = df.drop_duplicates()

    df.to_csv(MERGED_PATH, index=False)

    print(f"merged: {len(df)} rows")

if __name__ == "__main__":
    merge_data()
