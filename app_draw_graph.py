import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def draw_graph_plt(df):
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



from dash import Dash, dcc, html
import plotly.graph_objects as go
import pandas as pd

def draw_graph_plotly(df, game=""):
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date")
    df["point_sum"] = df.groupby("team")["point"].cumsum()

    team_settings = {
        "刈谷": {"color":"red", "linewidth":3, "mode": "lines+markers", "marker":"red"},
        "NEC川崎": {"color":"blue", "linewidth":1, "mode": "lines"},
        "デンソー": {"color":"green", "linewidth":1, "mode": "lines"},
        "PFU": {"color":"blue", "linewidth":1, "mode": "lines"},
        "岡山": {"color":"green", "linewidth":1, "mode": "lines"},
        "大阪MV": {"color":"blue", "linewidth":1, "mode": "lines"},
        "SAGA久光": {"color":"green", "linewidth":1, "mode": "lines"},
        "群馬": {"color":"blue", "linewidth":1, "mode": "lines"},
        "A山形": {"color":"green", "linewidth":1, "mode": "lines"},
        "姫路": {"color":"blue", "linewidth":1, "mode": "lines"},
        "Astemo": {"color":"green", "linewidth":1, "mode": "lines"},
        "KUROBE": {"color":"blue", "linewidth":1, "mode": "lines"},
        "東レ滋賀": {"color":"green", "linewidth":1, "mode": "lines"},
        "埼玉上尾": {"color":"blue", "linewidth":1, "mode": "lines"},
    }

    # Plotlyグラフの初期化
    fig = go.Figure(layout=dict(height=800))

    unique_dates = sorted(df["date"].unique())

    # 各日付時点の累積ポイント順で全チームの情報を整形
    hover_text_by_date = {}
    for date in unique_dates:
        up_to_date = df[df["date"] <= date]
        latest_points = up_to_date.sort_values("date").groupby("team").last().reset_index()
        sorted_rows = latest_points.sort_values("cumsum", ascending=False)
        hover_text_by_date[date] = "<br>".join(
            f'{row["team"]} {row["result"]} ({row["cumsum"]})'
            for _, row in sorted_rows.iterrows()
        )

    # 各チームのデータをプロット
    for team, settings in team_settings.items():
        team_data = df[df["team"] == team].reset_index(drop=True)
        fig.add_trace(go.Scatter(
            x=team_data["date"],
            y=team_data["cumsum"],
            mode = settings["mode"],
            name = team,
            line=dict(color=settings["color"], width=settings["linewidth"]),
            marker=dict(symbol="circle", color=settings.get("marker", "rgba(0,0,0,0)")),
            text = [hover_text_by_date[date] for date in team_data["date"]],
#            text=[
#                f'<b>{row["team"]} {row["result"]}</b>:{row["point"]}-{row["oppo_point"]} {row["opponent"]}'
#                for _, row in team_data.iterrows()
#            ],
            hovertemplate='<span style="font-size:20px;">%{text}<extra></extra></span>',  # yの値は表示しない
            hoverinfo="text+x"
        ))

    # グラフの装飾
    fig.update_layout(
        title=game,
        xaxis_title="日付",
        yaxis_title="ポイント",
        xaxis=dict(tickformat="%Y-%m-%d"),
        legend_title="Teams",
        hovermode="closest",
        template="plotly_white",
        xaxis_title_font_size=18,
        yaxis_title_font_size=18,
        xaxis_tickfont_size=14,
        yaxis_tickfont_size=14,
    )

    # グラフを表示
    # return fig
    fig.show()