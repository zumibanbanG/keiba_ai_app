print("Hello")

import requests
from bs4 import BeautifulSoup
import csv
import time
import os

# 出力ディレクトリ作成
os.makedirs("data", exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

year_start = 2019
year_end = 2025

# 競馬場IDと名称
places = {
    "01": "札幌", "02": "函館", "03": "福島", "04": "新潟",
    "05": "東京", "06": "中山", "07": "中京", "08": "京都",
    "09": "阪神", "10": "小倉"
}

for year in range(year_start, year_end):
    race_data_all = []
    race_data_all.append([
        'race_id','馬','騎手','馬番','走破時間','オッズ','通過順','着順',
        '体重','体重変化','性','齢','斤量','上がり','人気',
        '場名','レース名','日付'
    ])

    for place_id, place_name in places.items():
        for kaiji in range(1, 7 + 1):
            for nichiji in range(1, 13 + 1):
                race_id_prefix = f"{year}{place_id}0{kaiji}{nichiji:02d}"
                for race_num in range(1, 13 + 1):
                    race_id = f"{race_id_prefix}{race_num:02d}"
                    url = f"https://db.netkeiba.com/race/{race_id}/"
                    print(f"Fetching: {url}")
                    try:
                        r = requests.get(url, headers=headers)
                        if r.status_code != 200:
                            continue
                    except Exception as e:
                        print(f"Retrying after error: {e}")
                        time.sleep(10)
                        continue

                    soup = BeautifulSoup(r.content, "html.parser")
                    table = soup.find("table", class_="race_table_01")
                    if table is None:
                        continue
                    rows = table.find_all("tr")[1:]  # skip header

                    # レース名・日付を取得
                    try:
                        title = soup.find("h1").text.strip()
                        date_info = soup.select_one("p.smalltxt").text.strip().split(" ")[0]
                    except:
                        title = ""
                        date_info = ""

                    for row in rows:
                        cols = row.find_all("td")
                        if len(cols) < 15:
                            continue
                        try:
                            horse_name = cols[3].text.strip()
                            jockey = cols[6].text.strip()
                            horse_num = cols[2].text.strip()
                            time_val = cols[7].text.strip()
                            odds = cols[12].text.strip()
                            passing = cols[10].text.strip()
                            rank = cols[0].text.strip()
                            body = cols[14].text.strip()
                            sex_age = cols[4].text.strip()
                            weight = cols[5].text.strip()
                            last_3f = cols[11].text.strip()
                            pop = cols[13].text.strip()

                            if "(" in body:
                                weight_val, weight_diff = body.split("(")
                                weight_val = weight_val.strip()
                                weight_diff = weight_diff.strip(")")
                            else:
                                weight_val = ""
                                weight_diff = ""

                            sex = sex_age[0]
                            age = sex_age[1:]

                            race_data_all.append([
                                race_id,
                                horse_name,
                                jockey,
                                horse_num,
                                time_val,
                                odds,
                                passing,
                                rank,
                                weight_val,
                                weight_diff,
                                sex,
                                age,
                                weight,
                                last_3f,
                                pop,
                                place_name,
                                title,
                                date_info
                            ])
                        except Exception as e:
                            print(f"Error parsing row: {e}")
                            continue

                    time.sleep(3)

    # 年ごとに保存
    with open(f"data/{year}.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(race_data_all)
    print(f"Year {year} saved.")
