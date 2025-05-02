from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import plotly.graph_objects as go

def get_links(driver):
    # リンクのあるli要素を取得する ページ遷移するたびにおこなう必要がある
    button_area = driver.find_element(By.CLASS_NAME, "pagenumber")          # ページ遷移ボタンが並んでいるdiv
    li_elements = button_area.find_elements(By.CSS_SELECTOR, "li.number")   # その中のli class="number"要素
    return li_elements

def get_data(url):
    driver = webdriver.Edge(service=Service(r"./msedgedriver.exe"))
    driver.get(url)
    links = get_links(driver)
    link_count = len(links)
    table_data = []
    for i in range(link_count):
        links[i].click()
        table = driver.find_element(By.CLASS_NAME, "table_type_odd")
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            tds = row.find_elements(By.TAG_NAME, "td")
            if tds:                                         # thの行は無視してtdの行のみ
                row_data = [td.text for td in tds]
                table_data.append(row_data)
        links = get_links(driver)                           # 遷移後のページであらためてリンクを取得する
    driver.quit()
    return table_data

def make_dataframe(table_data):
    # 元データを加工する
    data = []
    for row in table_data:
        # ["2024-10-11', 'サントリー\n0-3\n大阪Ｂ', '17-25', '19-25', '21-25', '', '', 'A', 'B', 'MOVIE"]
        date = row[0]
        results = row[1].replace("\n", "-").split("-")
        team1, point1, point2, team2 = results[0], int(results[1]), int(results[2]), results[3]
        scores = []
        for c in [2, 3, 4, 5, 6]:
            if row[c] == "":
                scores.extend([None, None])
            else:
                score_list = row[c].split("-")
                scores.extend([int(sc) for sc in score_list])
        data.append([date, team1, point1, point2, team2] + scores)

    # dfを定義
    columns = [
        "date", "teamA", "pointA", "pointB", "teamB",
        "scoreA1", "scoreB1", "scoreA2", "scoreB2", "scoreA3", "scoreB3",
        "scoreA4", "scoreB4", "scoreA5", "scoreB5"
    ]

    df = pd.DataFrame(data, columns=columns)
    df.to_csv("data_table.csv", index=False)

    # AチームとBチームに分けてそれを縦に結合する opponent
    rename_dict = {"teamA": "team", "pointA": "point", "teamB":"opponent", "pointB":"oppo_point"}
    dfA = df.rename(columns=rename_dict)[["date", "team", "point", "opponent", "oppo_point"]]
    rename_dict = {"teamB": "team", "pointB": "point", "teamA":"opponent", "pointA":"oppo_point"}
    dfB = df.rename(columns=rename_dict)[["date", "team", "point", "opponent", "oppo_point"]]
    team_df = pd.concat([dfA, dfB], ignore_index=True, axis=0)
    team_df["result"] = "△"
    team_df.loc[team_df["point"] > team_df["oppo_point"], "result"] = "○"
    team_df.loc[team_df["point"] < team_df["oppo_point"], "result"] = "●"
    team_df.to_csv("team_data.csv", index=False)

def draw_graph_plt():
    df = pd.read_csv("team_data.csv", header=0)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date")
    df["point_sum"] = df.groupby("team")["point"].cumsum()
    print(df.head())

    team_settings = {
        "刈谷": {"color":"red", "linewidth":2, "marker":"o"},
        "NEC川崎": {"color":"blue", "linewidth":1, "marker":""},
        "デンソー": {"color":"green", "linewidth":1, "marker":""},
        "PFU": {"color":"blue", "linewidth":1, "marker":""},
        "岡山": {"color":"green", "linewidth":1, "marker":""},
        "大阪MV": {"color":"blue", "linewidth":1, "marker":""},
        "SAGA久光": {"color":"green", "linewidth":1, "marker":""},
        "群馬": {"color":"blue", "linewidth":1, "marker":""},
        "A山形": {"color":"green", "linewidth":1, "marker":""},
        "姫路": {"color":"blue", "linewidth":1, "marker":""},
        "Astemo": {"color":"green", "linewidth":1, "marker":""},
        "KUROBE": {"color":"blue", "linewidth":1, "marker":""},
        "東レ滋賀": {"color":"green", "linewidth":1, "marker":""},
        "埼玉上尾": {"color":"blue", "linewidth":1, "marker":""},
    }


    # グラフの作成
    font_path = "C:\\Windows\\Fonts\\BIZ-UDGothicR.ttc"
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams["font.family"] = font_prop.get_name()

    plt.figure(figsize=(10, 6))
    offset = 10     # 初期値
    va = "bottom"
    for team, settings in team_settings.items():
        team_data = df[df["team"] == team].reset_index(drop=True)
        plt.plot(team_data["date"], team_data["point_sum"],
                color=settings["color"],
                linewidth=settings["linewidth"],
                marker = settings["marker"],
                label=team)
        if team == "刈谷":
            for index, row in team_data.iterrows():
                comment = f'{row["opponent"]}\n{row["result"]} {row["point"]}-{row["oppo_point"]}'
                if index > 0:
                    previous_row = team_data.iloc[index - 1]
                    date_difference = row["date"] - previous_row["date"]
                    if date_difference < pd.Timedelta(days=2):
                        offset = 1
                        va = "bottom"
                    else:
                        offset = -1
                        va = "top"
                    print(row["date"],previous_row["date"], offset, comment)
                plt.text(
                    row["date"], row["point_sum"]+offset,
                    comment,
                    fontsize=10, ha="center", va=va, zorder=5)

    # グラフの装飾
    plt.title('Cumulative Points by Team Over Time')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Points')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()

    # グラフの表示
    plt.tight_layout()
    plt.show()
    print("done.")

def draw_graph_plotly():
    df = pd.read_csv("team_data.csv", header=0)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date")
    df["point_sum"] = df.groupby("team")["point"].cumsum()

    team_settings = {
        "刈谷": {"color":"red"},
        "NEC川崎": {"color":"blue"},
        "デンソー": {"color":"green"},
        "PFU": {"color":"blue"},
        "岡山": {"color":"green"},
        "大阪MV": {"color":"blue"},
        "SAGA久光": {"color":"green"},
        "群馬": {"color":"blue"},
        "A山形": {"color":"green"},
        "姫路": {"color":"blue"},
        "Astemo": {"color":"green"},
        "KUROBE": {"color":"blue"},
        "東レ滋賀": {"color":"green"},
        "埼玉上尾": {"color":"blue"},
    }

    # Plotlyグラフの初期化
    fig = go.Figure()

    # 各チームのデータをプロット
    for team, settings in team_settings.items():
        team_data = df[df["team"] == team].reset_index(drop=True)

        # 刈谷のみポップアップテキストを表示
        if team == "刈谷":
            fig.add_trace(go.Scatter(
                x=team_data["date"],
                y=team_data["point_sum"],
                mode="lines+markers",
                name=team,
                line=dict(color=settings["color"]),
                text=[
                    f'{row["opponent"]}<br>{row["result"]} {row["point"]}-{row["oppo_point"]}'
                    for _, row in team_data.iterrows()
                ],  # 刈谷のデータポイントにのみテキストを追加
                hoverinfo="text+x+y"
            ))
        else:
            fig.add_trace(go.Scatter(
                x=team_data["date"],
                y=team_data["point_sum"],
                mode="lines",
                name=team,
                line=dict(color=settings["color"]),
                hoverinfo="x+y"  # 他チームはポップアップなし
            ))

    # グラフの装飾
    fig.update_layout(
        title="Cumulative Points by Team Over Time",
        xaxis_title="Date",
        yaxis_title="Cumulative Points",
        xaxis=dict(tickformat="%Y-%m-%d"),
        legend_title="Teams",
        hovermode="x unified",
        template="plotly_white"
    )

    # グラフを表示
    fig.show()

def main():
    # スクレイピングして元データを取得する
    # url = "https://www.svleague.jp/ja/round/listn/380"
    # table_data = get_data(url)
    # make_dataframe(table_data)
    # draw_graph_plt()
    draw_graph_plotly()


if __name__ == "__main__":
    main()