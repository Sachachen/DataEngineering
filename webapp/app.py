#!/usr/bin/env python3
"""
Dashboard Ligue 1 - Application Dash
Visualisation interactive des données du championnat de France
"""

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from mongo_client import MongoDBClient
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialisation de l'app Dash
app = dash.Dash(__name__, title="Ligue 1 Dashboard")
server = app.server

# Connexion MongoDB
mongo_client = MongoDBClient()

# Couleurs personnalisées
COLORS = {
    'background': '#0e1117',
    'card': '#1e2130',
    'text': '#ffffff',
    'primary': '#00d4ff',
    'secondary': '#ff4b4b',
    'success': '#00ff88',
    'warning': '#ffaa00',
}

# Layout de l'application
app.layout = html.Div(style={'backgroundColor': COLORS['background'], 'minHeight': '100vh', 'padding': '20px'}, children=[
    
    # Header
    html.Div([
        html.H1('⚽ Dashboard Ligue 1 2025-2026',
                style={'textAlign': 'center', 'color': COLORS['text'], 'marginBottom': '10px'}),
        html.P('Données en temps réel du championnat de France',
               style={'textAlign': 'center', 'color': COLORS['primary'], 'fontSize': '18px'}),
    ]),
    
    # Interval pour auto-refresh
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # 60 secondes
        n_intervals=0
    ),
    
    # Ligne de métriques
    html.Div(id='metrics-row', style={'marginTop': '30px', 'marginBottom': '30px'}),
    
    # Graphiques principaux
    html.Div([
        html.Div([
            html.Div([
                html.H3('🏆 Classement Ligue 1', style={'color': COLORS['text'], 'textAlign': 'center'}),
                dcc.Graph(id='classement-graph')
            ], style={'backgroundColor': COLORS['card'], 'padding': '20px', 'borderRadius': '10px'}),
        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),
        
        html.Div([
            html.H3('⚽ Top Buteurs (Équipes)', style={'color': COLORS['text'], 'textAlign': 'center'}),
            dcc.Graph(id='buteurs-graph')
        ], style={'width': '48%', 'display': 'inline-block', 'backgroundColor': COLORS['card'], 
                  'padding': '20px', 'borderRadius': '10px', 'verticalAlign': 'top'}),
    ], style={'marginBottom': '30px'}),
    
    # Tableau détaillé
    html.Div([
        html.H3('📊 Tableau Détaillé', style={'color': COLORS['text'], 'textAlign': 'center', 'marginBottom': '20px'}),
        html.Div(id='table-container')
    ], style={'backgroundColor': COLORS['card'], 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '30px'}),
    
    # Statistiques supplémentaires
    html.Div([
        html.Div([
            html.H3('📈 Différence de Buts', style={'color': COLORS['text'], 'textAlign': 'center'}),
            dcc.Graph(id='diff-graph')
        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%', 
                  'backgroundColor': COLORS['card'], 'padding': '20px', 'borderRadius': '10px'}),
        
        html.Div([
            html.H3('🎯 Forme (V-N-D)', style={'color': COLORS['text'], 'textAlign': 'center'}),
            dcc.Graph(id='forme-graph')
        ], style={'width': '48%', 'display': 'inline-block', 
                  'backgroundColor': COLORS['card'], 'padding': '20px', 'borderRadius': '10px'}),
    ]),
    
    # Footer
    html.Div([
        html.Hr(style={'borderColor': COLORS['primary'], 'marginTop': '40px'}),
        html.P([
            '🕷️ Données scrapées depuis Wikipedia | ',
            html.Span(id='last-update', style={'color': COLORS['primary']}),
            ' | Auto-refresh: 60s'
        ], style={'textAlign': 'center', 'color': COLORS['text'], 'marginTop': '20px'})
    ])
])


# Callbacks
@app.callback(
    [Output('metrics-row', 'children'),
     Output('classement-graph', 'figure'),
     Output('buteurs-graph', 'figure'),
     Output('table-container', 'children'),
     Output('diff-graph', 'figure'),
     Output('forme-graph', 'figure'),
     Output('last-update', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    """Mise à jour de tous les éléments du dashboard"""
    
    # Récupération des données
    teams = mongo_client.get_teams(limit=20)
    top_scorers = mongo_client.get_top_scorers(limit=10)
    stats = mongo_client.get_stats()
    total_teams = mongo_client.get_total_teams()
    total_goals = mongo_client.get_total_goals()
    
    # Conversion en DataFrame
    df = pd.DataFrame(teams) if teams else pd.DataFrame()
    df_scorers = pd.DataFrame(top_scorers) if top_scorers else pd.DataFrame()
    
    # Métriques
    metrics = html.Div([
        create_metric_card('🏆 Équipes', total_teams, COLORS['primary']),
        create_metric_card('⚽ Total Buts', total_goals, COLORS['success']),
        create_metric_card('📅 Saison', stats.get('saison', '2025-2026'), COLORS['warning']),
        create_metric_card('📊 Journée', stats.get('journee', '-'), COLORS['secondary']),
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap'})
    
    # Graphique classement
    if not df.empty:
        fig_classement = go.Figure(data=[
            go.Bar(
                x=df['points'].head(10),
                y=df['equipe'].head(10),
                orientation='h',
                marker=dict(
                    color=df['points'].head(10),
                    colorscale='Blues',
                    showscale=False
                ),
                text=df['points'].head(10),
                textposition='auto',
            )
        ])
        fig_classement.update_layout(
            paper_bgcolor=COLORS['card'],
            plot_bgcolor=COLORS['card'],
            font=dict(color=COLORS['text']),
            xaxis_title='Points',
            yaxis=dict(autorange='reversed'),
            height=500,
            margin=dict(l=20, r=20, t=20, b=20)
        )
    else:
        fig_classement = create_empty_figure('Aucune donnée disponible')
    
    # Graphique buteurs
    if not df_scorers.empty:
        fig_buteurs = go.Figure(data=[
            go.Bar(
                x=df_scorers['equipe'],
                y=df_scorers['buts_pour'],
                marker=dict(
                    color=df_scorers['buts_pour'],
                    colorscale='Reds',
                    showscale=False
                ),
                text=df_scorers['buts_pour'],
                textposition='auto',
            )
        ])
        fig_buteurs.update_layout(
            paper_bgcolor=COLORS['card'],
            plot_bgcolor=COLORS['card'],
            font=dict(color=COLORS['text']),
            yaxis_title='Buts marqués',
            xaxis_tickangle=-45,
            height=400,
            margin=dict(l=20, r=20, t=20, b=80)
        )
    else:
        fig_buteurs = create_empty_figure('Aucune donnée disponible')
    
    # Tableau détaillé
    if not df.empty:
        table = create_detailed_table(df)
    else:
        table = html.P('Aucune donnée disponible', 
                      style={'textAlign': 'center', 'color': COLORS['text'], 'padding': '20px'})
    
    # Graphique différence de buts
    if not df.empty:
        fig_diff = go.Figure(data=[
            go.Bar(
                x=df['equipe'].head(10),
                y=df['difference'].head(10),
                marker=dict(
                    color=df['difference'].head(10),
                    colorscale='RdYlGn',
                    showscale=False,
                    cmin=-20,
                    cmax=20
                ),
                text=df['difference'].head(10),
                textposition='auto',
            )
        ])
        fig_diff.update_layout(
            paper_bgcolor=COLORS['card'],
            plot_bgcolor=COLORS['card'],
            font=dict(color=COLORS['text']),
            yaxis_title='Différence',
            xaxis_tickangle=-45,
            height=400,
            margin=dict(l=20, r=20, t=20, b=80)
        )
    else:
        fig_diff = create_empty_figure('Aucune donnée disponible')
    
    # Graphique forme
    if not df.empty:
        fig_forme = go.Figure(data=[
            go.Bar(
                name='Victoires',
                x=df['equipe'].head(10),
                y=df['victoires'].head(10),
                marker_color=COLORS['success']
            ),
            go.Bar(
                name='Nuls',
                x=df['equipe'].head(10),
                y=df['nuls'].head(10),
                marker_color=COLORS['warning']
            ),
            go.Bar(
                name='Défaites',
                x=df['equipe'].head(10),
                y=df['defaites'].head(10),
                marker_color=COLORS['secondary']
            )
        ])
        fig_forme.update_layout(
            barmode='stack',
            paper_bgcolor=COLORS['card'],
            plot_bgcolor=COLORS['card'],
            font=dict(color=COLORS['text']),
            yaxis_title='Matchs',
            xaxis_tickangle=-45,
            height=400,
            legend=dict(orientation='h', y=1.1),
            margin=dict(l=20, r=20, t=40, b=80)
        )
    else:
        fig_forme = create_empty_figure('Aucune donnée disponible')
    
    # Dernière mise à jour
    last_update = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    return metrics, fig_classement, fig_buteurs, table, fig_diff, fig_forme, last_update


def create_metric_card(title, value, color):
    """Crée une carte métrique"""
    return html.Div([
        html.H4(title, style={'color': color, 'marginBottom': '10px', 'fontSize': '16px'}),
        html.H2(str(value), style={'color': COLORS['text'], 'margin': '0', 'fontSize': '32px', 'fontWeight': 'bold'})
    ], style={
        'backgroundColor': COLORS['card'],
        'padding': '20px',
        'borderRadius': '10px',
        'textAlign': 'center',
        'minWidth': '200px',
        'margin': '10px',
        'border': f'2px solid {color}'
    })


def create_empty_figure(message):
    """Crée une figure vide avec un message"""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=20, color=COLORS['text'])
    )
    fig.update_layout(
        paper_bgcolor=COLORS['card'],
        plot_bgcolor=COLORS['card'],
        height=400,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    return fig


def create_detailed_table(df):
    """Crée un tableau HTML détaillé"""
    
    # Style du tableau
    table_style = {
        'width': '100%',
        'borderCollapse': 'collapse',
        'color': COLORS['text']
    }
    
    header_style = {
        'backgroundColor': COLORS['primary'],
        'color': COLORS['background'],
        'padding': '12px',
        'textAlign': 'left',
        'fontWeight': 'bold',
        'borderBottom': f"2px solid {COLORS['background']}"
    }
    
    cell_style = {
        'padding': '10px',
        'borderBottom': f"1px solid {COLORS['background']}"
    }
    
    # Création du header
    header = html.Thead(html.Tr([
        html.Th('Pos', style=header_style),
        html.Th('Équipe', style=header_style),
        html.Th('Pts', style=header_style),
        html.Th('J', style=header_style),
        html.Th('V', style=header_style),
        html.Th('N', style=header_style),
        html.Th('D', style=header_style),
        html.Th('BP', style=header_style),
        html.Th('BC', style=header_style),
        html.Th('Diff', style=header_style),
    ]))
    
    # Création des lignes
    rows = []
    for _, row in df.iterrows():
        rows.append(html.Tr([
            html.Td(row['position'], style=cell_style),
            html.Td(row['equipe'], style={**cell_style, 'fontWeight': 'bold'}),
            html.Td(row['points'], style={**cell_style, 'fontWeight': 'bold', 'color': COLORS['primary']}),
            html.Td(row.get('matchs_joues', '-'), style=cell_style),
            html.Td(row.get('victoires', '-'), style={**cell_style, 'color': COLORS['success']}),
            html.Td(row.get('nuls', '-'), style={**cell_style, 'color': COLORS['warning']}),
            html.Td(row.get('defaites', '-'), style={**cell_style, 'color': COLORS['secondary']}),
            html.Td(row.get('buts_pour', '-'), style=cell_style),
            html.Td(row.get('buts_contre', '-'), style=cell_style),
            html.Td(
                row.get('difference', '-'),
                style={
                    **cell_style,
                    'color': COLORS['success'] if row.get('difference', 0) > 0 else COLORS['secondary']
                }
            ),
        ]))
    
    tbody = html.Tbody(rows)
    
    return html.Table([header, tbody], style=table_style)


if __name__ == '__main__':
    logger.info('🚀 Starting Ligue 1 Dashboard...')
    logger.info('📊 Dashboard available at http://0.0.0.0:8050')
    app.run_server(host='0.0.0.0', port=8050, debug=False)
