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

# ---------- GLOBAL SESSION CACHE (CRITICAL FIX) ----------
SESSION_CACHE = {}

def get_session(year, track, session_type):
    key = f"{year}_{track}_{session_type}"
    if key not in SESSION_CACHE:
        s = fastf1.get_session(year, track, session_type)
        s.load()
        SESSION_CACHE[key] = s
    return SESSION_CACHE[key]


# ---------- TELEMETRY ----------
def get_tel(session, driver):
    lap = session.laps.pick_drivers([driver]).pick_fastest()
    tel = lap.get_telemetry()
    return lap, tel[['Distance','Speed','Throttle','Brake','X','Y']]


# ---------- (ALL YOUR GRAPH / TABLE FUNCTIONS STAY SAME) ----------
# build_animated_track
# compare_speed
# build_delta
# single_graph
# build_results_table
# ⬆️ keep them EXACTLY as you wrote


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

    dash_table.DataTable(
        id='results_table',
        page_size=20,
        style_header={'backgroundColor': '#111', 'color': 'white', 'fontWeight': 'bold'},
        style_cell={'backgroundColor': '#0b0f1a', 'color': 'white', 'textAlign': 'center'}
    )
])

# ---------- CALLBACKS ----------

@app.callback(
    Output('track','options'),
    Output('track','value'),
    Input('year','value')
)
def update_tracks(year):
    schedule = fastf1.get_event_schedule(year)
    schedule = schedule[schedule['EventFormat'] != 'testing']
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
    session = get_session(year, track, session_type)  # ✅ uses cache
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

    session = get_session(year, track, session_type)  # ✅ uses cache once

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
