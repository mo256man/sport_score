# app.py
from flask import Flask, render_template, request, jsonify
from dash import Dash, dcc, html, Input, Output, ctx
from dash import dcc, html
import plotly.express as px
from app_draw_graph import draw_graph_plotly

server = Flask(__name__)
dash_app = Dash(__name__, server=server, url_base_pathname="/dash/")
ip_flags = {}

dash_app.layout = html.Div([
    html.Button("バレー", id="btnVolley", n_clicks=0, className="custom-button"),
    html.Button("ハンド", id="btnHandball", n_clicks=0, className="custom-button"),
    dcc.Graph(id="dynamic-graph", figure=draw_graph_plotly("初期")),
])

@server.before_request
def detect_ip():
    ip = request.remote_addr
    # 自分自身ならTrue
    ip_flags[ip] = ip.startswith("127.") or ip.startswith("192.168.") 

@dash_app.callback(
    Output("btnVolley", "style"),
    Output("btnHandball", "style"),
    Output("dynamic-graph", "figure"),
    Input("btnVolley", "n_clicks"),
    Input("btnHandball", "n_clicks")
)
def update_graph(n_clicks_graph1, n_clicks_graph2):
    default_style = {"backgroundColor": "lightgray"}
    active_style = {"backgroundColor": "lightblue"}
    id = ctx.triggered_id
    if id == "btnVolley":
        volley_style = active_style
        handball_style = default_style
        fig = draw_graph_plotly("バレー")
    elif id == "btnHandball":
        volley_style = default_style
        handball_style = active_style
        fig = draw_graph_plotly("ハンド")
    return volley_style, handball_style, fig


@server.route("/")
def index():
    ip = request.remote_addr
    print(ip)
    if ip == "127.0.0.1" or ip == "::1":
        ip_msg = "サーバー自身からのアクセス"
    else:
        ip_msg = "他PCからのアクセス"
    return render_template("index.html", ip_msg=ip_msg)

@server.route("/select_game", methods=["POST"])
def your_endpoint():
    data = request.get_json()
    received_value = data.get("key", "不明")

    # レスポンスを辞書形式で作成
    response_data = {
        "status": "success",
        "game": received_value + "だ！"
    }
    return jsonify(response_data)

if __name__ == "__main__":
    server.run(debug=True)
