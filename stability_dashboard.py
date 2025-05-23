# stability_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Drug Stability Dashboard", layout="wide")

# --- DATABASE CONNECTION ---
@st.cache_data
def load_data():
    # Replace with your actual DB connection string
    db_path = os.path.abspath("stability_data.db")
    engine = create_engine(f"sqlite:///{db_path}")
    query = """
    SELECT time_point, temperature, position, molecular_weight, volume, impurity
    FROM stability_tests
    """
    return pd.read_sql(query, engine)

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.title("🔬 Filter Parameters")
min_time, max_time = st.sidebar.slider(
    "Select Time Range (days)", int(df['time_point'].min()), int(df['time_point'].max()),
    (int(df['time_point'].min()), int(df['time_point'].max()))
)

temperature_range = st.sidebar.slider(
    "Select Temperature Range (°C)", float(df['temperature'].min()), float(df['temperature'].max()),
    (float(df['temperature'].min()), float(df['temperature'].max()))
)

positions = st.sidebar.multiselect(
    "Select Position(s)",
    options=df['position'].unique(),
    default=list(df['position'].unique())
)

# --- FILTERED DATA ---
filtered_df = df[
    (df['time_point'] >= min_time) &
    (df['time_point'] <= max_time) &
    (df['temperature'] >= temperature_range[0]) &
    (df['temperature'] <= temperature_range[1]) &
    (df['position'].isin(positions))
]

# --- MAIN DASHBOARD ---
st.title("💊 Drug Stability Testing Dashboard")

st.subheader("Summary Statistics")
st.write(filtered_df[['molecular_weight', 'volume', 'impurity']].describe())

# --- PLOTS ---
col1, col2 = st.columns(2)

with col1:
    fig1 = px.line(filtered_df, x='time_point', y='molecular_weight',
                   color='position', title='Molecular Weight Over Time')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.line(filtered_df, x='time_point', y='volume',
                   color='position', title='Volume Over Time')
    st.plotly_chart(fig2, use_container_width=True)

# --- IMPURITY PLOT ---
st.subheader("📉 Impurity Over Time")
fig3 = px.line(filtered_df, x='time_point', y='impurity',
               color='position', title='Impurity Over Time')
st.plotly_chart(fig3, use_container_width=True)



