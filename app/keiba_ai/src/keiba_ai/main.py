import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup

st.title("Keiba AI Application")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# 今日の日付
today = datetime.date.today()

# カレンダーで日付選択（今日以降のみ）
selected_date = st.date_input("レース日を選択", min_value=today, value=today)

st.write(f"選択した日付: {selected_date}")

# スクレイピングで出馬表データを取得する

url = f"https://race.netkeiba.com/top/race_list.html?kaisai_date={selected_date.strftime('%Y%m%d')}" 

st.write(f"データを取得中: {url}")

try:
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error("データの取得に失敗しました。")
except Exception as e:
    st.error(f"データの取得中にエラーが発生しました: {e}")
soup = BeautifulSoup(r.content, "html.parser")

st.write(soup.prettify())

title = soup.find("span", id="top_race_list_heading")
if title:
    st.write("タイトル:", title.text)