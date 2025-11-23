import plotly.express as px
import plotly.graph_objects as go

def create_delay_chart(delai_par_arr):
    """Créer le graphique des délais de déploiement 5G"""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=delai_par_arr['arrondissement'],
        y=delai_par_arr['delai_5g'],
        marker_color='#3498db',
        text=delai_par_arr['delai_5g'].round(0),
        textposition='auto',
    ))

    fig.update_layout(
        title="Délai Moyen de Déploiement 5G par Arrondissement (en jours)",
        xaxis_title="Arrondissement",
        yaxis_title="Délai moyen (jours)",
        template="plotly_white",
        height=500
    )
    return fig

def create_antennas_repartition_chart(counts):
    """Créer le graphique de répartition des antennes"""
    fig = px.bar(
        counts,
        x='arrondissement',
        y='nb_antennes',
        color='operateur',
        title="Répartition des Antennes par Opérateur et Arrondissement",
        labels={'nb_antennes': 'Nombre d\'antennes', 'arrondissement': 'Arrondissement'},
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig.update_layout(
        template="plotly_white",
        height=500,
        xaxis_title="Arrondissement",
        yaxis_title="Nombre d'antennes"
    )
    return fig

def create_leaders_table(leaders):
    """Créer le tableau des leaders par arrondissement"""
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Arrondissement</b>', '<b>Opérateur Leader</b>', '<b>Nombre d\'Antennes</b>'],
            fill_color='#3498db',
            font=dict(color='white', size=14),
            align='center'
        ),
        cells=dict(
            values=[
                leaders['arrondissement'],
                leaders['operateur'],
                leaders['nb_antennes']
            ],
            fill_color='lavender',
            align='center',
            font=dict(size=12),
            height=30
        )
    )])

    fig.update_layout(
        title="Opérateur Leader par Arrondissement",
        height=500
    )
    return fig

def create_4g_5g_comparison_chart(repartition):
    """Créer le graphique de comparaison 4G vs 5G"""
    agg_by_arr = repartition.groupby('arrondissement').agg({
        'nb_4G': 'sum',
        'nb_5G': 'sum'
    }).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='4G',
        x=agg_by_arr['arrondissement'],
        y=agg_by_arr['nb_4G'],
        marker_color='#3498db'
    ))
    fig.add_trace(go.Bar(
        name='5G',
        x=agg_by_arr['arrondissement'],
        y=agg_by_arr['nb_5G'],
        marker_color='#e74c3c'
    ))

    fig.update_layout(
        title="Répartition 4G vs 5G par Arrondissement",
        xaxis_title="Arrondissement",
        yaxis_title="Nombre d'antennes",
        barmode='group',
        template="plotly_white",
        height=400
    )
    return fig

def create_5g_by_operator_chart(repartition):
    """Créer le graphique des antennes 5G par opérateur"""
    fig = go.Figure()

    for operateur in repartition['operateur'].unique():
        data_op = repartition[repartition['operateur'] == operateur]
        fig.add_trace(go.Bar(
            name=operateur,
            x=data_op['arrondissement'],
            y=data_op['nb_5G'],
            text=data_op['nb_5G'].astype(int),
            textposition='auto'
        ))

    fig.update_layout(
        title="Nombre d'Antennes 5G par Opérateur et Arrondissement",
        xaxis_title="Arrondissement",
        yaxis_title="Nombre d'antennes 5G",
        barmode='stack',
        template="plotly_white",
        height=400
    )
    return fig

def create_cluster_map(df_geo):
    """Créer la carte des clusters d'antennes"""
    fig = px.scatter_mapbox(
        df_geo[df_geo['cluster'] != -1],
        lat='lat',
        lon='lon',
        color='cluster',
        hover_data=['operateur', 'arrondissement'],
        title="Clusters d'Antennes (DBSCAN - eps=0.002, min_samples=5)",
        color_continuous_scale='Viridis',
        zoom=11,
        height=600
    )

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    return fig

def create_operator_map(df_geo):
    """Créer la carte de répartition par opérateur"""
    fig = px.scatter_mapbox(
        df_geo,
        lat='lat',
        lon='lon',
        color='operateur',
        hover_data=['arrondissement', 'cluster'],
        title="Répartition Géographique par Opérateur",
        zoom=11,
        height=600,
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    return fig