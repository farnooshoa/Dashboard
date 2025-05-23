import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

# Set database path (use absolute path for consistency)
db_path = os.path.abspath("stability_data.db")
engine = create_engine(f"sqlite:///{db_path}")

@st.cache_data
def load_data():
    query = """
    SELECT time_point, temperature, position, molecular_weight, volume, impurity
    FROM stability_tests
    """
    df = pd.read_sql(query, engine)

    # Extract numerical day value for filtering and plotting
    df['time_point_days'] = df['time_point'].str.extract(r'(\d+)').astype(int)

    return df

# Load data
df = load_data()

st.title("📊 Stability Test Dashboard")

# Sidebar filter
min_day = int(df['time_point_days'].min())
max_day = int(df['time_point_days'].max())
selected_range = st.slider("Select Time Range (days)", min_day, max_day, (min_day, max_day))

# Filter data
filtered_df = df[(df['time_point_days'] >= selected_range[0]) & (df['time_point_days'] <= selected_range[1])]

st.subheader("Filtered Stability Test Data")
st.dataframe(filtered_df)

# Visualization
st.subheader("📈 Impurity Over Time")
impurity_chart = filtered_df.groupby('time_point_days')['impurity'].mean().reset_index()
st.line_chart(impurity_chart.rename(columns={"time_point_days": "Time (days)", "impurity": "Average Impurity"}))

st.subheader("📉 Molecular Weight Over Time")
mw_chart = filtered_df.groupby('time_point_days')['molecular_weight'].mean().reset_index()
st.line_chart(mw_chart.rename(columns={"time_point_days": "Time (days)", "molecular_weight": "Average Molecular Weight"}))

