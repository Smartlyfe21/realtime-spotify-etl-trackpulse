# spotify_dashboard.py
import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# ✅ PAGE CONFIG — MUST BE FIRST
st.set_page_config(
    page_title="🎧 TrackPulse",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ AUTO-REFRESH EVERY 15 SECONDS
st_autorefresh(interval=15000, key="dashboard_refresh")

# ✅ HEADER DESIGN
st.markdown("""
    <style>
        .title {
            font-size: 42px;
            font-weight: 800;
            text-align: center;
            color: #1DB954;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            letter-spacing: 1px;
            padding-bottom: 0.5rem;
        }
        .subtitle {
            text-align: center;
            font-size: 18px;
            color: #ccc;
            margin-top: -10px;
        }
        .stApp {
            background: linear-gradient(135deg, #000000 40%, #121212 100%);
        }
        .card {
            background-color: #1DB95433;
            border-radius: 12px;
            padding: 10px;
            text-align: center;
            box-shadow: 2px 2px 5px #aaaaaa;
            margin-bottom: 15px;
        }
        .card h4 {
            color: #1DB954;
            margin-bottom: 5px;
        }
        .card p {
            margin: 2px 0;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🎧 TrackPulse — Spotify Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Analyze Top Tracks, Artists & Albums — Play them directly!</div>', unsafe_allow_html=True)
st.markdown("---")

# ✅ DATABASE CONNECTION
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "spotify_db"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

@st.cache_data(ttl=60)
def load_data():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        query = """
        SELECT track_name, artist_name, album_name, popularity, release_date, album_image_url, track_id
        FROM spotify_tracks
        ORDER BY popularity DESC
        LIMIT 500;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        # Clean columns
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce').dt.date
        df['album_image_url'] = df['album_image_url'].where(df['album_image_url'].notna(), None)
        return df
    except Exception as e:
        st.error(f"⚠️ Failed to load data: {e}")
        return pd.DataFrame()

df = load_data()

# ✅ CHECK IF DATA EXISTS
if df.empty:
    st.warning("⚠️ No data available. Run `python src/run_etl.py` first.")
    st.stop()

# ✅ SIDEBAR FILTERS
st.sidebar.header("Filter Tracks")
artist_filter = st.sidebar.multiselect(
    "Artist",
    options=df["artist_name"].dropna().unique(),
    default=[]
)
album_filter = st.sidebar.multiselect(
    "Album",
    options=df["album_name"].dropna().unique(),
    default=[]
)

# ✅ APPLY FILTERS
filtered_df = df.copy()
if artist_filter:
    filtered_df = filtered_df[filtered_df["artist_name"].isin(artist_filter)]
if album_filter:
    filtered_df = filtered_df[filtered_df["album_name"].isin(album_filter)]

# ✅ METRICS SUMMARY
col1, col2, col3 = st.columns(3)
col1.metric("🎶 Total Tracks", len(filtered_df))
col2.metric("👩‍🎤 Unique Artists", filtered_df["artist_name"].nunique())
col3.metric("📀 Unique Albums", filtered_df["album_name"].nunique())

st.markdown("---")

# ✅ TOP ARTISTS BAR CHART
st.subheader("📊 Top Artists by Track Count")
artist_counts = filtered_df["artist_name"].value_counts().reset_index()
artist_counts.columns = ["artist_name", "track_count"]
fig_artists = px.bar(
    artist_counts.head(15),
    x="artist_name",
    y="track_count",
    text="track_count",
    color="track_count",
    color_continuous_scale="Teal",
    labels={"track_count": "Tracks", "artist_name": "Artist"}
)
fig_artists.update_layout(plot_bgcolor="#121212", paper_bgcolor="#121212", font_color="white")
st.plotly_chart(fig_artists, use_container_width=True)

# ✅ TRACKS BY RELEASE YEAR
st.subheader("📅 Tracks by Release Year")
filtered_df["release_year"] = pd.to_datetime(filtered_df["release_date"], errors='coerce').dt.year
fig_years = px.histogram(
    filtered_df,
    x="release_year",
    nbins=20,
    color_discrete_sequence=["#1DB954"],
    labels={"release_year": "Year", "count": "Tracks"}
)
fig_years.update_layout(plot_bgcolor="#121212", paper_bgcolor="#121212", font_color="white")
st.plotly_chart(fig_years, use_container_width=True)

# ✅ DISPLAY TRACKS AS CARDS
# ✅ DISPLAY TRACKS AS CARDS
st.subheader(f"🎵 Showing {len(filtered_df)} Tracks")
cols_per_row = 4

for i in range(0, len(filtered_df), cols_per_row):
    cols = st.columns(cols_per_row)
    for j, (_, row) in enumerate(filtered_df.iloc[i:i + cols_per_row].iterrows()):
        col = cols[j]
        with col:
            st.markdown(f'<div class="card">', unsafe_allow_html=True)
            if row["album_image_url"]:
                st.image(row["album_image_url"], width=180)
            st.markdown(f"<h4>{row['track_name']}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p>{row['artist_name']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p>Album: {row['album_name']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p>Popularity: {row['popularity']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p>Release Date: {row['release_date']}</p>", unsafe_allow_html=True)

            # ✅ Play preview if available, else show Spotify link
            if 'preview_url' in row and row['preview_url']:
                st.audio(row['preview_url'], format="audio/mp3")
            elif row['track_id']:
                st.markdown(
                    f'<a href="https://open.spotify.com/track/{row["track_id"]}" target="_blank">▶️ Play on Spotify</a>',
                    unsafe_allow_html=True
                )

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
