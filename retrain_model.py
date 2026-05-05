import os
import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ===== CONFIG =====
DATA_PATH = "weather_data.csv"      # file được tạo từ fetch_weather.py
MODEL_PATH = "train_model.py"    # nơi lưu model
MIN_ROWS = 50                       # tối thiểu để train

# ===== ENCODE LABEL =====
def encode_label(label):
    mapping = {
        "Clear": 0,
        "Clouds": 1,
        "Rain": 2,
        "Other": 3
    }
    return mapping.get(label, 3)

# ===== RETRAIN =====
def retrain_model():
    print("🚀 Start retrain...")

    # 1. Check file
    if not os.path.exists(DATA_PATH):
        print("❌ Không tìm thấy file dữ liệu")
        return

    # 2. Load data
    df = pd.read_csv(DATA_PATH)

    if df.empty:
        print("❌ File dữ liệu rỗng")
        return

    print("📊 Số dòng:", len(df))

    # 3. Clean
    df = df.dropna().drop_duplicates()

    if len(df) < MIN_ROWS:
        print(f"⚠️ Chưa đủ dữ liệu ({len(df)} < {MIN_ROWS}) → bỏ qua")
        return

    # 4. Encode
    if "weather_group" not in df.columns:
        print("❌ Thiếu cột weather_group")
        print(df.columns)
        return

    df["label"] = df["weather_group"].apply(encode_label)

    # 5. Feature
    features = [
        "temperature", "temp_min", "temp_max", "humidity",
        "feels_like", "visibility", "cloudcover",
        "wind_speed", "wind_gust", "wind_direction", "pressure"
    ]

    # Check thiếu cột
    missing = [col for col in features if col not in df.columns]
    if missing:
        print("❌ Thiếu cột:", missing)
        return

    X = df[features]
    y = df["label"]

    # 6. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 7. Train
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric="mlogloss"
    )

    model.fit(X_train, y_train)

    # 8. Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"✅ Accuracy: {round(acc*100, 2)}%")

    # 9. Save model
    joblib.dump(model, MODEL_PATH)
    print(f"💾 Saved model → {MODEL_PATH}")

    print("🎉 Done retrain!")

# ===== RUN =====
if __name__ == "__main__":
    print(df.columns)
    retrain_model()
