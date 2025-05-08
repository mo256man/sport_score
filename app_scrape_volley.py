from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import pandas as pd
import sqlite3
import datetime
from app_draw_graph import draw_graph_plotly

DB_NAME = "game_score.db"
TABLE = "volley_score"

def parse_match_details(match, latest_date):
    year = int(match.find_element(By.CLASS_NAME, "year").text)      # 年 2024
    date = match.find_element(By.CLASS_NAME, "date").text           # 月日 03.01
    month = int(date.split(".")[0])                                 # 月 3
    teamA = match.find_element(By.CLASS_NAME, "teamA").text.strip().split("\n")[0]
    teamB = match.find_element(By.CLASS_NAME, "teamB").text.strip().split("\n")[0]
    points = match.find_element(By.CLASS_NAME, "point").text        # 2-1
    if points == "VS":                                              # 試合が未だとVSになるので
        return "NOT_STARTED"
    else:                                                           # VSでなかったら
        season = year if month>8 else year-1                        # シーズン
        date = f"{year}-{date.replace('.', '-')}"                   # 年月日 2024-03-01
        pointA, pointB = points.split("-")                          # 各チームのポイント
        if date > latest_date:                                      # 日付がDB最新日付より大ならば
            return [season, date, teamA, pointA, teamB, pointB]     # リストに追加する
        else:
            return "ALREADY_EXISTS"

def fetch_volley_data():
    # まず、既存DBの最新日付を取得する
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = f"SELECT MAX(date) FROM {TABLE};"
    cursor.execute(query)
    latest_date = cursor.fetchone()[0]

    # 日程・結果のページ　最新（最終）ページが表示される
    url = "https://www.svleague.jp/ja/sv_women/match/list"
    driver = webdriver.Edge(service=Service(r"./msedgedriver.exe"))
    driver.get(url)

    # まずページ数をカウントする
    page_area =  driver.find_element(By.CLASS_NAME, "pagination")
    page_links = page_area.find_elements(By.CSS_SELECTOR, "li.number a")
    numbers = [int(link.text) for link in page_links]
    max_number = max(numbers)

    results = []
    for i in range(1, max_number + 1):
        print(f"{url}?pg={i}")
        driver.get(f"{url}?pg={i}")
        result_area = driver.find_element(By.CLASS_NAME, "matchArea3")
        matches = result_area.find_elements(By.CLASS_NAME, "matchScheduleBlock")

        is_break = False
        for match in matches:
            result = parse_match_details(match, latest_date)
            if result == "ALREADY_EXISTS":
                pass
            elif result == "NOT_STARTED":
                is_berak = True
            else:
                results.append(result)
        if is_break:
            break
    driver.quit()

    # データをDBに書き込む
    columns = ["season", "date", "teamA", "pointA", "teamB", "pointB"]
    df = pd.DataFrame(results, columns=columns)
    conn = sqlite3.connect(DB_NAME)
    df.to_sql(TABLE, conn, if_exists="append", index=False)
    conn.close()

def calculate_team_points(season=None):
    """
    試合結果をポイント累計にする
    """
    # シーズン
    if season is None:
        today = datetime.datetime.today()
        year = today.year
        month = today.month
        season = year if month>8 else year-1                        # シーズン

    # DB取り込み
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = f"SELECT * FROM {TABLE} WHERE season={season};"
    cursor.execute(query)
    match_data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(match_data, columns=columns)
    conn.close()

    # 元データを加工し、各チームがどのチームと対戦した結果 という表を作る
    rename_dict = {"teamA": "team", "pointA": "point", "teamB":"opponent", "pointB":"oppo_point"}
    dfA = df.rename(columns=rename_dict)[["date", "team", "point", "opponent", "oppo_point"]]

    rename_dict = {"teamB": "team", "pointB": "point", "teamA":"opponent", "pointA":"oppo_point"}
    dfB = df.rename(columns=rename_dict)[["date", "team", "point", "opponent", "oppo_point"]]

    team_df = pd.concat([dfA, dfB], ignore_index=True, axis=0)      # 縦に結合
    team_df["date"] = pd.to_datetime(team_df["date"], format="%Y-%m-%d")
    team_df["result"] = "△"
    team_df.loc[team_df["point"] > team_df["oppo_point"], "result"] = "○"
    team_df.loc[team_df["point"] < team_df["oppo_point"], "result"] = "●"


    # これをもとに、試合がない日の累計ポイントも出すようにする
    all_dates = team_df["date"].unique()     # 全日程
    all_teams = team_df["team"].unique()    # 全チーム
    full_index = pd.MultiIndex.from_product([all_dates, all_teams], names=["date", "team"])
    full_df = pd.DataFrame(index=full_index).reset_index()

    # 累積ポイントを元データから取得
#     merged = pd.merge(full_df, df[['date', 'team', 'point']], on=['date', 'team'], how='left')
    merged = pd.merge(full_df, team_df, on=["date", "team"], how="left")

    # 累積ポイントの計算（試合のない日はNaN → 前方補完）
    merged['point'] = merged['point'].fillna(0)
    merged['cumsum'] = merged.groupby('team')['point'].cumsum()


    print(merged[merged["team"]=="刈谷"])




    return merged




def calculate_team_points0(season=None):
    """
    試合結果をポイント累計にする
    """
    # シーズン
    if season is None:
        today = datetime.datetime.today()
        year = today.year
        month = today.month
        season = year if month>8 else year-1                        # シーズン

    # DB取り込み
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = f"SELECT * FROM {TABLE} WHERE season={season};"
    cursor.execute(query)
    match_data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(match_data, columns=columns)
    conn.close()

    # 元データを加工し、各チームがどのチームと対戦した結果 という表を作る
    rename_dict = {"teamA": "team", "pointA": "point", "teamB":"opponent", "pointB":"oppo_point"}
    dfA = df.rename(columns=rename_dict)[["date", "team", "point", "opponent", "oppo_point"]]

    rename_dict = {"teamB": "team", "pointB": "point", "teamA":"opponent", "pointA":"oppo_point"}
    dfB = df.rename(columns=rename_dict)[["date", "team", "point", "opponent", "oppo_point"]]

    team_df = pd.concat([dfA, dfB], ignore_index=True, axis=0)      # 縦に結合
    team_df["date"] = pd.to_datetime(team_df["date"], format="%Y-%m-%d")
    team_df["result"] = "△"
    team_df.loc[team_df["point"] > team_df["oppo_point"], "result"] = "○"
    team_df.loc[team_df["point"] < team_df["oppo_point"], "result"] = "●"
    return team_df

def main():
    # スクレイピングして元データを取得する
    # fetch_volley_data()
    team_df = calculate_team_points()
    draw_graph_plotly(team_df, "volley")


if __name__ == "__main__":
    main()