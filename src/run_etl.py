# run_etl.py
import logging
from datetime import datetime
from extract import get_spotify_client, extract_multiple_playlists
from transform import transform_tracks
from load import load_to_postgres, produce_to_kafka
from utils import ensure_log_dir
import pandas as pd

# Setup logging
ensure_log_dir()
logging.basicConfig(
    filename="../logs/etl.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def run_etl():
    try:
        logging.info("ETL job started.")

        # Extract
        sp = get_spotify_client()

        # List of playlists to extract from
        playlist_ids = [
            "4Pxnn3ljvIbXYrcd51Bx9C",  # Playlist 1
            "1aTh9IAG5rLD3fKY9G2rdE",  # Playlist 2
            "4tUaDzlL2wK46ZIGBDVaPn",  # Playlist 3
            # Add more playlists here
        ]

        raw_df = extract_multiple_playlists(sp, playlist_ids)

        if raw_df.empty:
            logging.warning("No tracks extracted from any playlist. Check playlist IDs or Spotify API credentials.")
            print("Warning: No tracks extracted from any playlist.")
            return

        logging.info(f"Extracted {len(raw_df)} tracks from Spotify playlists.")

        # Transform
        try:
            clean_df = transform_tracks(raw_df)
            if clean_df.empty:
                logging.warning("Transformed dataframe is empty after cleaning.")
                print("Warning: Transformed dataframe is empty.")
                return
            logging.info(f"Transformed dataframe shape: {clean_df.shape}")
        except Exception as e:
            logging.error(f"Error during transformation: {e}", exc_info=True)
            print(f"Error during transformation: {e}")
            return

        # Load
        try:
            load_to_postgres(clean_df)
            produce_to_kafka(clean_df)
            logging.info("Data loaded successfully to PostgreSQL and Kafka.")
        except Exception as e:
            logging.error(f"Error during loading: {e}", exc_info=True)
            print(f"Error during loading: {e}")

        logging.info("ETL job completed successfully.")

    except Exception as e:
        logging.error(f"ETL job failed: {e}", exc_info=True)
        print(f"Error during ETL: {e}")

if __name__ == "__main__":
    run_etl()
