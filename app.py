import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from folium.plugins import MarkerCluster

st.set_page_config(
    page_title="GEO-SENTIFY VIT",
    layout="wide"
)

st.title("GEO-SENTIFY VIT 🗺️")
st.markdown("""
This AI-driven interactive web application visualizes public sentiment associated with specific geographical locations within and around all VIT campuses.  
The goal is to provide a dynamic and visually engaging tool for understanding community perception.
""")

try:
    df = pd.read_csv("vit_feedback_with_sentiment.csv")
except FileNotFoundError:
    st.error("❌ Error: 'vit_feedback_with_sentiment.csv' not found. Please run Phase 3 script to generate it.")
    st.stop()

st.sidebar.header("🔍 Filters")

sentiments = df['sentiment'].unique().tolist()
sentiment_filter = st.sidebar.multiselect(
    "Select Sentiments", 
    options=sentiments, 
    default=sentiments
)

if 'campus' in df.columns:
    campuses = df['campus'].unique().tolist()
    campus_filter = st.sidebar.multiselect(
        "Select Campus", 
        options=campuses, 
        default=campuses
    )
    df_filtered = df[(df['sentiment'].isin(sentiment_filter)) & (df['campus'].isin(campus_filter))]
else:
    df_filtered = df[df['sentiment'].isin(sentiment_filter)]

col1, col2 = st.columns([3, 2])

with col1:
    st.header("📍 Sentiment Map")

    if df_filtered.empty:
        st.warning("No data available for the selected filters.")
    else:
        map_center = [df_filtered['latitude'].mean(), df_filtered['longitude'].mean()]
        m = folium.Map(location=map_center, zoom_start=16)

        color_map = {
            'POSITIVE': 'green',
            'NEGATIVE': 'red',
            'NEUTRAL': 'gray'
        }

        marker_cluster = MarkerCluster().add_to(m)

        for _, row in df_filtered.iterrows():
            popup_text = f"""
            <b>Sentiment:</b> {row['sentiment']}<br>
            <b>Feedback:</b> {row['feedback_text'][:150]}...
            """
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=row['sentiment'],
                icon=folium.Icon(color=color_map.get(row['sentiment'], 'blue'), icon='comment')
            ).add_to(marker_cluster)

        st_folium(m, width=725, height=500, returned_objects=[])

with col2:
    st.header("📊 Data Insights")

    sentiment_order = ['POSITIVE', 'NEUTRAL', 'NEGATIVE']
    sentiment_counts = df_filtered['sentiment'].value_counts().reindex(sentiment_order, fill_value=0)

    st.subheader("Sentiment Distribution")
    fig = px.bar(
        sentiment_counts,
        x=sentiment_counts.index,
        y=sentiment_counts.values,
        labels={'x': 'Sentiment', 'y': 'Number of Reviews'},
        color=sentiment_counts.index,
        color_discrete_map={'POSITIVE': 'green', 'NEGATIVE': 'red', 'NEUTRAL': 'gray'}
    )
    st.plotly_chart(fig, use_container_width=True)

st.header("📝 Raw Feedback Data")
st.dataframe(df_filtered)

st.download_button(
    "⬇️ Download Filtered Feedback Data",
    df_filtered.to_csv(index=False),
    "filtered_feedback.csv",
    "text/csv"
)
