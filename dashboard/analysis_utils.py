import pandas as pd
from sklearn.cluster import DBSCAN
import numpy as np

def Evolution_5G(df):
    df['mise_en_serv'] = pd.to_datetime(df['mise_en_serv'], errors='coerce')
    df['mise_en_serv_5g_3500'] = pd.to_datetime(df['mise_en_serv_5g_3500'], errors='coerce')

    df_valid = df.dropna(subset=['mise_en_serv', 'mise_en_serv_5g_3500']).copy()
    df_valid.loc[:, 'delai_5g'] = (df_valid['mise_en_serv_5g_3500'] - df_valid['mise_en_serv']).dt.days

    delai_par_arr = (
        df_valid.groupby("arrondissement")['delai_5g']
        .mean()
        .reset_index()
        .sort_values(by="delai_5g")
    )

    return delai_par_arr

def antennas_repartition(df):
    counts = (
        df.groupby(['arrondissement', 'operateur'])
        .size()
        .reset_index(name='nb_antennes')
    )

    leader = counts.loc[counts.groupby("arrondissement")['nb_antennes'].idxmax()]
    return counts, leader

def get_4G_5G_repartition(df):

    cols = ['operateur', 'arrondissement', 'type_clean']
    df_new = df[cols].copy()
    def detect_4G(x):
        if x == 'Unknown':
            return np.nan
        return 1 if '4G' in x else 0

    def detect_5G(x):
        if x == 'Unknown':
            return np.nan
        return 1 if '5G' in x else 0

    df_new['has_4G'] = df_new['type_clean'].apply(detect_4G)
    df_new['has_5G'] = df_new['type_clean'].apply(detect_5G)

    repartition = df_new.groupby(['arrondissement','operateur']).agg(
        nb_4G=('has_4G','sum'),
        nb_5G=('has_5G','sum'),
        nb_total=('type_clean','count'),
        nb_unknown=('type_clean', lambda x: (x=='Unknown').sum())
    ).reset_index()
    return repartition

def geospatial_clustering(df):
    df['lon'] = df.geom.x
    df['lat'] = df.geom.y
    coords = df[['lon','lat']].to_numpy()
    model = DBSCAN(eps=0.002, min_samples=5).fit(coords)
    df['cluster'] = model.labels_
    return df[['operateur', 'arrondissement', 'cluster', 'lon', 'lat']]