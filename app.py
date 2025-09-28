import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(
    page_title="GEO-SENTIFY VIT",
    layout="wide"
)

st.title("GEO-SENTIFY VIT 🗺️")
st.markdown("""
This AI-driven interactive web application is designed to visualize public sentiment associated with specific geographical locations within and around all VIT campuses. 
The primary objective is to provide a dynamic and visually engaging tool for understanding community perception.
""")

try:
    df = pd.read_csv("vit_feedback_with_sentiment.csv")
except FileNotFoundError:
    st.error("Error: 'vit_feedback_with_sentiment.csv' not found. Please run Phase 3 script to generate it.")
    st.stop()

col1, col2 = st.columns([3, 2])

with col1:
    st.header("📍 Sentiment Map")

    map_center = [df['latitude'].mean(), df['longitude'].mean()]
    
    # Create the base map
    m = folium.Map(location=map_center, zoom_start=16)

    # Add different tile layers for different map styles
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Maps'
    ).add_to(m)

    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&h=p&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Satellite'
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB positron',
        name='Positron (Light)'
    ).add_to(m)

    # Create feature groups for filtering sentiment markers
    positive_group = folium.FeatureGroup(name='Positive 👍').add_to(m)
    negative_group = folium.FeatureGroup(name='Negative 👎').add_to(m)
    neutral_group = folium.FeatureGroup(name='Neutral 😐').add_to(m)

    # Add improved markers to the correct group
    for idx, row in df.iterrows():
        popup_html = f"""
        <b>Location:</b> {row['location_name']}<br>
        <b>Sentiment:</b> {row['sentiment']}<br>
        <hr>
        <i>"{row['feedback_text']}"</i>
        """
        
        if row['sentiment'] == 'POSITIVE':
            icon_symbol, icon_color, target_group = 'thumbs-up', 'green', positive_group
        elif row['sentiment'] == 'NEGATIVE':
            icon_symbol, icon_color, target_group = 'thumbs-down', 'red', negative_group
        else:
            icon_symbol, icon_color, target_group = 'info-sign', 'gray', neutral_group

        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=icon_color, icon=icon_symbol)
        ).add_to(target_group)

    # Add the layer control to the map
    folium.LayerControl().add_to(m)
    
    st_folium(m, width=725, height=500)

with col2:
    st.header("📊 Data Insights")

    sentiment_counts = df['sentiment'].value_counts()
    st.subheader("Sentiment Distribution")
    
    fig = px.bar(sentiment_counts, 
                 x=sentiment_counts.index, 
                 y=sentiment_counts.values,
                 labels={'x':'Sentiment', 'y':'Number of Reviews'},
                 color=sentiment_counts.index,
                 color_discrete_map={'POSITIVE':'green', 'NEGATIVE':'red', 'NEUTRAL':'gray'})
    st.plotly_chart(fig, use_container_width=True)

st.header("📝 Raw Feedback Data")
st.dataframe(df)