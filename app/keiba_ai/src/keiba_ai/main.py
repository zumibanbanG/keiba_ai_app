import streamlit as st
import datetime
from mylib.get_data import ShutubaScraper
from mylib.inference import LightGBMInference

st.title("Keiba AI Application")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

scraper = ShutubaScraper()


# 今日の日付
today = datetime.date.today()

# カレンダーで日付選択（今日以降のみ）
selected_date = st.date_input("select date", min_value=today, value=today)



# 日付ごとにレースリストをキャッシュ（セッション状態）
if 'last_date' not in st.session_state or st.session_state['last_date'] != selected_date:
    url = f"https://race.netkeiba.com/top/race_list.html?kaisai_date={selected_date.strftime('%Y%m%d')}"
    with st.spinner("Loading race list..."):
        race_list = scraper.fetch_race_list(url)
    st.session_state['race_list'] = race_list
    st.session_state['last_date'] = selected_date
else:
    race_list = st.session_state.get('race_list', [])

# レース選択用セレクトボックス（デフォルト空）
default_option = "レースを選択してください"
race_options = [default_option] + [
    f"{r['place']} {r['race_no']}R {r['class_name']} {r['time']} {r['course']} {r['num_horses']}頭 ({r['race_id']})"
    for r in race_list
]
race_id_map = {opt: r['race_id'] for opt, r in zip(race_options[1:], race_list)}

selected_race = st.selectbox("select race", race_options, index=0) if race_options else None

if selected_race and selected_race != default_option:
    selected_race_id = race_id_map[selected_race]
    shutuba_url = f"https://race.netkeiba.com/race/shutuba.html?race_id={selected_race_id}"
    with st.spinner("Fetching race data..."):
        shutuba_list = scraper.fetch_race_data(shutuba_url)
    if shutuba_list:
        st.write("Race data:")
        st.dataframe(shutuba_list)
    else:
        st.write("Failed to fetch race data")

# 推論用のLightGBMモデルをGCSからダウンロードして推論する
bucket_name = "keiba_ai_models"
model_blob_path = "lgbm_model.txt"
inference = LightGBMInference(bucket_name, model_blob_path)
# ここでshutuba_listを前処理して特徴量Xを作成してから、inference.predict(X)を呼び出す
features = ['オッズ', '体重', '斤量', '人気', '馬番', '体重変化', '齢']


# shutuba_listから特徴量を抽出してXを作成する（eda.ipynbの前処理を参考）
import pandas as pd

def preprocess_shutuba_list(shutuba_list, features):
    """
    shutuba_list: list of dict (スクレイピング結果)
    features: list of str (使う特徴量名)
    return: pd.DataFrame (推論用特徴量)
    """
    df = pd.DataFrame(shutuba_list)
    # 必要なカラムのみ抽出
    df = df.copy()
    # 「馬名」をインデックスにする
    if "馬名" in df.columns:
        df.set_index("馬名", inplace=True)
    # 「予想オッズ」→「オッズ」
    if "予想オッズ" in df.columns:
        df.rename(columns={"予想オッズ": "オッズ"}, inplace=True)
    # 型変換（数値化）
    for col in features:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            df[col] = float('nan')
    return df[features]

# 推論実行例
if selected_race and selected_race != default_option and shutuba_list:
    X = preprocess_shutuba_list(shutuba_list, features)
    # 推論
    with st.spinner("AI predicting..."):
        preds = inference.predict(X)
    st.write("AI Prediction Ranking (Top 3):")
    pred_df = pd.DataFrame({"Horse": X.index, "Win Probability": preds})
    pred_df = pred_df.sort_values("Win Probability", ascending=False).reset_index(drop=True)
    top3 = pred_df.head(3)

    # 順位ごとに薄い背景色
    color_map = ["#FFF9E3", "#F5F5F5", "#F4DFCF"]  # very light gold/silver/bronze
    html = "<div style='font-size:1.1em;'>"
    rank_labels = ["1st", "2nd", "3rd"]
    for i, row in top3.iterrows():
        rank = rank_labels[i] if i < len(rank_labels) else f"{i+1}th"
        color = color_map[i] if i < len(color_map) else "#f9f9f9"
        html += f"<div style='background:{color};padding:8px;margin:4px;border-radius:8px;border-bottom:2px solid #aaa;'>"
        html += f"<span style='text-decoration:underline;font-weight:bold;'>{rank}</span> "
        html += f"{row['Horse']} <span style='float:right;'>Probability: {row['Win Probability']:.2%}</span>"
        html += "</div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("<div style='text-align:right;font-size:1.3em;font-weight:bold;'>All you need is betting !!</div>", unsafe_allow_html=True)