import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

class ShutubaScraper:
    """
    Playwrightを使ってnetkeibaの出馬表ページから枠、馬番、性齢、斤量、騎手、予想オッズ、人気を取得するクラス。
    """
    def __init__(self, headless=True):
        self.headless = headless

    def fetch_race_data(self, race_url):
        """
        指定した出馬表ページからデータを取得。
        :param race_url: 出馬表ページのURL
        :return: dictのリスト
        """
        result = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            page.goto(race_url)
            page.wait_for_selector('table.RaceTable01', timeout=60000)
            rows = page.query_selector_all('table.RaceTable01 tbody tr')
            for row in rows:
                try:
                    cols = row.query_selector_all('td')
                    if len(cols) < 10:
                        continue
                    waku = cols[0].inner_text().strip()
                    umaban = cols[1].inner_text().strip()
                    # 馬名は4列目（index=3）
                    uma_name = cols[3].inner_text().strip() if len(cols) > 3 else ''
                    sex_age = cols[4].inner_text().strip()
                    kinryo = cols[5].inner_text().strip()
                    jockey = cols[6].inner_text().strip()
                    # 馬体重(増減)欄から数値と増減を分離
                    weight_raw = cols[8].inner_text().strip() if len(cols) > 8 else ''
                    weight_match = re.match(r'^(\d+)(?:\(([-+]?\d+)\))?$', weight_raw)
                    weight = weight_match.group(1) if weight_match else ''
                    weight_diff = weight_match.group(2) if weight_match else ''
                    # 予想オッズ
                    odds_el = cols[9].query_selector('span')
                    odds = odds_el.inner_text().strip() if odds_el else ''
                    # 人気
                    ninki_el = cols[10].query_selector('span')
                    ninki = ninki_el.inner_text().strip() if ninki_el else ''
                    result.append({
                        '枠': waku,
                        '馬番': umaban,
                        '馬名': uma_name,
                        '性齢': sex_age,
                        '斤量': kinryo,
                        '騎手': jockey,
                        '体重': weight,
                        '体重変化': weight_diff,
                        '予想オッズ': odds,
                        '人気': ninki
                    })
                except Exception:
                    continue
            browser.close()
        return result

    def fetch_race_list(self, list_url):
        """
        レース一覧ページから場所・レース番号・クラス名・発走時刻・距離/コース・頭数・レースIDのセットを取得する
        :param list_url: レース一覧ページのURL
        :return: [{'place': ..., 'race_no': ..., 'class_name': ..., 'time': ..., 'course': ..., 'num_horses': ..., 'race_id': ...}, ...]
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            page.goto(list_url)
            page.wait_for_selector('.RaceList_DataItem a', timeout=60000)
            html = page.content()
            browser.close()
        soup = BeautifulSoup(html, 'html.parser')
        race_list = []
        seen_ids = set()
        for a in soup.select('.RaceList_DataItem a'):
            href = a.get('href', '')
            m = re.search(r'race_id=(\d+)', href)
            if not m:
                continue
            race_id = m.group(1)
            if race_id in seen_ids:
                continue
            seen_ids.add(race_id)
            race_name_full = a.get_text(strip=True)
            # 例: "1R3歳未勝利10:05ダ1400m16頭"
            m_race = re.match(r'([0-9]+)R(.+?)([0-9]{1,2}:[0-9]{2})([芝ダ障].*?m)([0-9]+)頭', race_name_full)
            if m_race:
                race_no = m_race.group(1)
                class_name = m_race.group(2).strip()
                time = m_race.group(3)
                course = m_race.group(4).strip()
                num_horses = m_race.group(5)
            else:
                race_no = ''
                class_name = ''
                time = ''
                course = ''
                num_horses = ''
            # aタグから親をたどって直近のRaceList_DataTitleを探す
            place = ''
            parent = a
            for _ in range(5):  # 5階層まで遡る
                parent = parent.parent
                if parent is None:
                    break
                title_tag = parent.find_previous('p', class_='RaceList_DataTitle')
                if title_tag:
                    m_place = re.search(r'\d+回\s*([\u4e00-\u9fff]+)\s*\d+日目', title_tag.get_text())
                    if m_place:
                        place = m_place.group(1)
                    break
            race_list.append({
                'place': place,
                'race_no': race_no,
                'class_name': class_name,
                'time': time,
                'course': course,
                'num_horses': num_horses,
                'race_id': race_id
            })
        return race_list
