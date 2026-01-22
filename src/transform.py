import pandas as pd

def transform_tracks(df):
    """
    Transform tracks dataframe:
    - Fill missing values safely
    - Standardize column names
    - Keep playlist info
    """
    df = df.copy()

    # Standardize column names
    df.columns = [c.lower() for c in df.columns]

    # Popularity
    if 'popularity' in df.columns:
        if pd.api.types.is_numeric_dtype(df['popularity']):
            df['popularity'] = df['popularity'].fillna(0).astype(int)
        else:
            df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce').fillna(0).astype(int)

    # Release date
    if 'release_date' in df.columns:
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['release_date'] = df['release_date'].where(df['release_date'].notna(), None)

    # Album image URL
    if 'album_image_url' in df.columns:
        df['album_image_url'] = df['album_image_url'].where(df['album_image_url'].notna(), None)

    # Playlist info
    if 'playlist_name' in df.columns:
        df['playlist_name'] = df['playlist_name'].where(df['playlist_name'].notna(), 'Unknown')
    if 'playlist_id' in df.columns:
        df['playlist_id'] = df['playlist_id'].where(df['playlist_id'].notna(), 'Unknown')

    # Drop duplicates
    if 'track_id' in df.columns:
        df = df.drop_duplicates(subset='track_id')

    return df
