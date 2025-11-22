from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
import pandas as pd
from geoalchemy2 import Geometry
import geopandas as gpd

load_dotenv()

def get_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    dbname = os.getenv("DB_NAME")
    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    engine = create_engine(db_url)
    return engine


def load_to_db(df):
    dbname = os.getenv("DB_NAME")
    engine = get_engine()
    df.to_sql(
        dbname,
        engine,
        if_exists="append",
        index=False,
        dtype={"geom": Geometry("POINT", srid=4326)}
    )

def load_from_db():
    engine = get_engine()
    dbname = os.getenv("DB_NAME")
    df = gpd.read_postgis(
        f"SELECT * FROM {dbname}",
        engine,
        geom_col="geom"
    )
    return df
df = load_from_db()