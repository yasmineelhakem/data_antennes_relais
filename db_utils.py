from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
import pandas as pd
from geoalchemy2 import Geometry
import geopandas as gpd

load_dotenv()

def init_database():
    engine = get_engine()
    create_sql = """
    CREATE TABLE IF NOT EXISTS antennes (
        code_site VARCHAR(50),
        adresse TEXT,
        operateur VARCHAR(50),
        mise_en_serv DATE,
        mise_en_serv_4g DATE,
        mise_en_serv_5g_3500 DATE,
        type_clean VARCHAR(50),
        geom GEOMETRY(Point, 4326),
        arrondissement INT
    );
    """
    with engine.begin() as conn:
        conn.execute(text(create_sql))
        print("Table 'antennes' created.")

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
    engine = get_engine()
    df.to_sql(
        'antennes',
        engine,
        if_exists="append",
        index=False,
        dtype={"geom": Geometry("POINT", srid=4326)}
    )

def load_from_db():
    engine = get_engine()
    df = gpd.read_postgis(
        f"SELECT * FROM antennes",
        engine,
        geom_col="geom"
    )
    return df
if __name__ == "__main__":
    init_database()
    df = pd.read_csv("data/antennes_clean.csv")
    load_to_db(df)
