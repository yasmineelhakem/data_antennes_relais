import dash
from dash import dcc, html, Input, Output
from dashboard.analysis_utils import (
    Evolution_5G,
    antennas_repartition,
    get_4G_5G_repartition,
    geospatial_clustering
)
from db_utils import load_from_db
from dashboard.visualizations import (
    create_delay_chart,
    create_antennas_repartition_chart,
    create_leaders_table,
    create_4g_5g_comparison_chart,
    create_5g_by_operator_chart,
    create_cluster_map
)


def prepare_data_from_df(df):
    delai_par_arr = Evolution_5G(df)
    counts, leaders = antennas_repartition(df)
    repartition = get_4G_5G_repartition(df)
    df_geo = geospatial_clustering(df)

    return {
        'delai_par_arr': delai_par_arr,
        'counts': counts,
        'leaders': leaders,
        'repartition': repartition,
        'df_geo': df_geo
    }

def create_header():
    # Créer header du dashboard
    return html.Div([
        html.H1("Dashboard Antennes Relais",
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
        html.P("Analyse du déploiement des antennes 4G et 5G",
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': 16})
    ], style={'padding': '20px', 'backgroundColor': '#ecf0f1'})

def create_tabs():
    return dcc.Tabs(id='tabs', value='tab-delais', children=[
        dcc.Tab(label='📊 Répartition Antennes', value='tab-repartition'),
        dcc.Tab(label='🏆 Leaders par Arrondissement', value='tab-leaders'),
        dcc.Tab(label='📡 Répartition 4G/5G', value='tab-4g5g'),
        dcc.Tab(label='⏱️ Délais de Déploiement', value='tab-delais'),
        dcc.Tab(label='🗺️ Analyse Géospatiale', value='tab-geo'),
    ], style={'marginBottom': 20})

def create_stats_cards(values, labels, colors):
    # Créer containers pour mettre des stat
    cards = []
    for val, label, color in zip(values, labels, colors):
        card = html.Div([
            html.H3(f"{val}", style={'color': color, 'margin': '0'}),
            html.P(label, style={'margin': '0', 'fontSize': '14px'})
        ], style={
            'textAlign': 'center',
            'padding': '20px',
            'backgroundColor': 'white',
            'borderRadius': '5px',
            'flex': '1',
            'margin': '0 10px'
        })
        cards.append(card)
    return html.Div(cards, style={'display': 'flex', 'marginBottom': '20px'})

def create_analysis_box(text):
    # Container pour les analyses
    return html.Div([
        html.H4("📌 Analyse", style={'color': '#2c3e50'}),
        html.P(text)
    ], style={
        'padding': '20px',
        'backgroundColor': 'white',
        'borderRadius': '5px',
        'marginTop': '20px'
    })

def create_layout():
    #Créer le layout complet du dashboard
    return html.Div([
        create_header(),
        create_tabs(),
        html.Div(id='tabs-content', style={'padding': '20px'})
    ], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f5f5f5'})

def create_app(data):
    app = dash.Dash(__name__)
    app.layout = create_layout()

    @app.callback(
        Output('tabs-content', 'children'),
        Input('tabs', 'value')
    )
    def render_content(tab):
        if tab == 'tab-delais':
            fig = create_delay_chart(data['delai_par_arr'])
            return html.Div([
                dcc.Graph(figure=fig),
                create_analysis_box(
                    "Ce graphique montre le délai moyen (en jours) entre la mise en service initiale "
                    "et le déploiement de la 5G pour chaque arrondissement. "
                )
            ])

        elif tab == 'tab-repartition':
            fig = create_antennas_repartition_chart(data['counts'])
            return html.Div([
                dcc.Graph(figure=fig),
                create_analysis_box(
                    "Ce graphique compare le nombre d'antennes déployées par chaque opérateur "
                    "dans chaque arrondissement, permettant d'identifier les zones de forte présence."
                )
            ])

        elif tab == 'tab-leaders':
            fig = create_leaders_table(data['leaders'])
            return html.Div([
                dcc.Graph(figure=fig),
                create_analysis_box(
                    "Ce tableau identifie l'opérateur ayant le plus grand nombre d'antennes "
                    "dans chaque arrondissement (position dominante)."
                )
            ])

        elif tab == 'tab-4g5g':
            fig1 = create_4g_5g_comparison_chart(data['repartition'])
            fig2 = create_5g_by_operator_chart(data['repartition'])

            total_4g = data['repartition']['nb_4G'].sum()
            total_5g = data['repartition']['nb_5G'].sum()
            ratio_5g = (total_5g / (total_4g + total_5g)) * 100 if (total_4g + total_5g) > 0 else 0

            stats = create_stats_cards(
                [int(total_4g), int(total_5g), f"{ratio_5g:.1f}%"],
                ["Antennes 4G", "Antennes 5G", "Taux de 5G"],
                ['#3498db', '#e74c3c', '#2ecc71']
            )

            return html.Div([
                stats,
                dcc.Graph(figure=fig1),
                dcc.Graph(figure=fig2),
                create_analysis_box(
                    "Ces graphiques montrent la répartition détaillée des antennes 4G et 5G "
                    "par arrondissement et par opérateur. Le premier graphique compare 4G vs 5G, "
                    "le second montre la contribution de chaque opérateur au déploiement 5G."
                )
            ])

        elif tab == 'tab-geo':
            fig1 = create_cluster_map(data['df_geo'])

            nb_clusters = len(data['df_geo'][data['df_geo']['cluster'] != -1]['cluster'].unique())
            nb_noise = len(data['df_geo'][data['df_geo']['cluster'] == -1])
            nb_clustered = len(data['df_geo']) - nb_noise

            stats = create_stats_cards(
                [nb_clusters, nb_noise, nb_clustered],
                ["Clusters identifiés", "Antennes isolées", "Antennes en cluster"],
                ['#3498db', '#e74c3c', '#2ecc71']
            )

            return html.Div([
                stats,
                dcc.Graph(figure=fig1),
                create_analysis_box(
                    "Le clustering DBSCAN (eps=0.002, min_samples=5) identifie les zones de forte "
                    "concentration d'antennes. Les points colorés indiquent des clusters (zones denses), "
                    "tandis que les antennes isolées (cluster = -1) sont des points de bruit. "
                )
            ])

    return app


if __name__ == '__main__':
    df = load_from_db()
    data = prepare_data_from_df(df)
    app = create_app(data)
    app.run(debug=True)
