import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, KAFKA_TOPIC, KAFKA_BOOTSTRAP_SERVERS
from kafka import KafkaProducer
import json
import pandas as pd


def load_to_postgres(df, table_name="spotify_tracks"):
    """
    Load dataframe into PostgreSQL table.
    Supports album images and playlist metadata.
    """
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()

    for _, row in df.iterrows():
        release_date = row.get('release_date')
        if pd.isna(release_date):
            release_date = None  # PostgreSQL accepts NULL
        elif isinstance(release_date, pd.Timestamp):
            release_date = release_date.strftime('%Y-%m-%d')

        cur.execute(f"""
        INSERT INTO {table_name} 
            (track_id, track_name, artist_name, album_name, popularity, release_date, album_image_url, playlist_id, playlist_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (track_id) DO NOTHING
        """, (
            row['track_id'],
            row['track_name'],
            row['artist_name'],
            row['album_name'],
            row['popularity'],
            release_date,
            row.get('album_image_url'),
            row.get('playlist_id'),
            row.get('playlist_name')
        ))

    conn.commit()
    cur.close()
    conn.close()


def produce_to_kafka(df):
    """
    Send dataframe records to Kafka topic.
    Converts any pandas Timestamp objects or NaT to strings to avoid JSON serialization errors.
    """
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    for record in df.to_dict(orient='records'):
        for key, value in record.items():
            if isinstance(value, pd.Timestamp):
                record[key] = value.strftime('%Y-%m-%d')
            elif pd.isna(value):  # handle NaT or NaN
                record[key] = None
        producer.send(KAFKA_TOPIC, record)

    producer.flush()

