import fastf1
import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
from fastf1.utils import delta_time
import os

# ---------- FASTF1 CACHE (Render safe) ----------
cache_dir = "/tmp/fastf1_cache"
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

# ---------- GLOBAL SESSION CACHE ----------
SESSION_CACHE = {}

def get_session(year, track, session_type):
    key = f"{year}_{track}_{session_type}"
    if key not in SESSION_CACHE:
        s = fastf1.get_session(year, track, session_type)

        # 🔥 LOAD ONLY WHAT IS NEEDED (critical for Render memory)
        s.load(laps=True, telemetry=True, weather=False, messages=False)

        SESSION_CACHE[key] = s
    return SESSION_CACHE[key]


# ---------- TELEMETRY ----------
def get_tel(session, driver):
    lap = session.laps.pick_drivers([driver]).pick_fastest()
    tel = lap.get_telemetry()
    return lap, tel[['Distance','Speed','Throttle','Brake','X','Y']]


# ---------- GRAPHS ----------
def build_animated_track(tel, driver, lap):
    x = tel['X'] - tel['X'].mean()
    y = tel['Y'] - tel['Y'].mean()

    speed = tel['Speed']
    throttle = tel['Throttle']
    brake = tel['Brake']

    step = 8
    frame_duration = 240
    frames = []

    for idx, i in enumerate(range(10, len(x), step)):
        frames.append(
            go.Frame(
                name=str(idx),
                data=[
                    go.Scatter(x=x, y=y, mode='lines',
                               line=dict(width=3)),
                    go.Scatter(
                        x=[x.iloc[i]],
                        y=[y.iloc[i]],
                        mode='markers+text',
                        marker=dict(size=16),
                        text=[f"{int(speed.iloc[i])} km/h"],
                        textposition="top center",
                    )
                ]
            )
        )

    fig = go.Figure(
        data=[
            go.Scatter(x=x, y=y, mode='lines'),
            go.Scatter(x=[x.iloc[10]], y=[y.iloc[10]],
                       mode='markers')
        ],
        frames=frames
    )

    fig.update_layout(
        template="plotly_dark",
        title=f"{driver} Racing Line Replay",
        xaxis_visible=False,
        yaxis=dict(visible=False, scaleanchor="x", scaleratio=1),
        height=500,
        updatemenus=[{
            "type": "buttons",
            "buttons": [{
                "label": "▶ Play",
                "method": "animate",
                "args": [None, {"frame": {"duration": frame_duration}}]
            }]
        }]
    )

    return fig


def compare_speed(tel1, tel2, d1, d2):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tel1['Distance'], y=tel1['Speed'], name=d1))
    fig.add_trace(go.Scatter(x=tel2['Distance'], y=tel2['Speed'], name=d2))
    fig.update_layout(template="plotly_dark", title="Speed Comparison", height=350)
    return fig


def build_delta(lap1, lap2, d1, d2):
    delta, ref, comp = delta_time(lap1, lap2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ref['Distance'], y=delta, name=f"{d1} vs {d2}"))
    fig.update_layout(template="plotly_dark", title="Delta Time", height=350)
    return fig


def single_graph(tel, driver, col, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tel['Distance'], y=tel[col], name=driver))
    fig.update_layout(template="plotly_dark",
                      title=f"{driver} {title}",
                      height=300)
    return fig


def build_results_table(session, session_type):
    res = session.results[['Position','Abbreviation','TeamName']]
    return res.to_dict('records'), [{"name": i, "id": i} for i in res.columns]


# ---------- APP ----------
app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H2("F1 Telemetry Dashboard", style={'textAlign': 'center'}),

    html.Div([
        dcc.Dropdown(id='year',
                     options=[{'label': y, 'value': y} for y in range(2021, 2026)],
                     value=2025),
        dcc.Dropdown(id='track'),
        dcc.Dropdown(id='session',
                     options=[{'label': 'Qualifying', 'value': 'Q'},
                              {'label': 'Race', 'value': 'R'}],
                     value='Q'),
        dcc.Dropdown(id='driver1'),
        dcc.Dropdown(id='driver2'),
    ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(5,1fr)', 'gap': '10px'}),

    html.Div([
        dcc.Graph(id='track1'),
        dcc.Graph(id='track2')
    ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'}),

    dcc.Graph(id='delta_graph'),
    dcc.Graph(id='speed_graph'),

    html.Div([
        dcc.Graph(id='throttle1'),
        dcc.Graph(id='throttle2')
    ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'}),

    html.Div([
        dcc.Graph(id='brake1'),
        dcc.Graph(id='brake2')
    ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'}),

    html.H3("Session Results", style={'textAlign': 'center', 'marginTop': '40px'}),

    dash_table.DataTable(id='results_table', page_size=20)
])


@app.callback(
    Output('track','options'),
    Output('track','value'),
    Input('year','value')
)
def update_tracks(year):
    schedule = fastf1.get_event_schedule(year)
    opts = [{'label':row['EventName'], 'value':row['EventName']}
            for _, row in schedule.iterrows()]
    return opts, opts[0]['value']


@app.callback(
    Output('driver1','options'),
    Output('driver2','options'),
    Output('driver1','value'),
    Output('driver2','value'),
    Input('year','value'),
    Input('track','value'),
    Input('session','value'),
)
def update_drivers(year, track, session_type):
    session = get_session(year, track, session_type)
    drivers = sorted(session.laps['Driver'].unique())
    opts = [{'label':d, 'value':d} for d in drivers]
    return opts, opts, drivers[0], drivers[1]


@app.callback(
    Output('track1','figure'),
    Output('track2','figure'),
    Output('delta_graph','figure'),
    Output('speed_graph','figure'),
    Output('throttle1','figure'),
    Output('throttle2','figure'),
    Output('brake1','figure'),
    Output('brake2','figure'),
    Output('results_table','data'),
    Output('results_table','columns'),
    Input('year','value'),
    Input('track','value'),
    Input('session','value'),
    Input('driver1','value'),
    Input('driver2','value'),
)
def update(year, track, session_type, d1, d2):
    session = get_session(year, track, session_type)

    lap1, tel1 = get_tel(session, d1)
    lap2, tel2 = get_tel(session, d2)

    data, cols = build_results_table(session, session_type)

    return (
        build_animated_track(tel1, d1, lap1),
        build_animated_track(tel2, d2, lap2),
        build_delta(lap1, lap2, d1, d2),
        compare_speed(tel1, tel2, d1, d2),
        single_graph(tel1, d1, 'Throttle', 'Throttle'),
        single_graph(tel2, d2, 'Throttle', 'Throttle'),
        single_graph(tel1, d1, 'Brake', 'Brake'),
        single_graph(tel2, d2, 'Brake', 'Brake'),
        data, cols
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050)
