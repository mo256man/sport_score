from dash import Dash, dcc, html
import plotly.graph_objects as go
import pandas as pd

def draw_graph_plotly(game=""):
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
    fig = go.Figure(layout=dict(height=800))

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
        title=game,
        xaxis_title="日付",
        yaxis_title="ポイント",
        xaxis=dict(tickformat="%Y-%m-%d"),
        legend_title="Teams",
        hovermode="x unified",
        template="plotly_white"
    )

    # グラフを表示
    return fig
