import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ======================================================
# 1. CONFIG & DATA LOADING
# ======================================================
st.set_page_config(page_title="Advanced Air Quality Dashboard", layout="wide")

@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    # Tambahkan kolom tambahan agar operasi grupby lebih cepat
    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month
    df['day'] = df['datetime'].dt.day
    df['hour'] = df['datetime'].dt.hour
    return df

# file_path = r"E:\All About Programs\Laskar AI\Data Analyst with Python\submission\dashboard\data_cleaned.csv"
file_path = "submission/dashboard/data_cleaned.csv"
df = load_data(file_path)

# Koordinat manual untuk tiap stasiun
station_coordinates = {
    'Aotizhongxin': (39.982, 116.417),
    'Changping': (40.218, 116.231),
    'Dingling': (40.290, 116.220),
    'Dongsi': (39.929, 116.417),
    'Guanyuan': (39.929, 116.339),
    'Gucheng': (39.928, 116.184),
    'Huairou': (40.375, 116.637),
    'Nongzhanguan': (39.933, 116.473),
    'Shunyi': (40.128, 116.653),
    'Tiantan': (39.886, 116.417),
    'Wanliu': (39.948, 116.287),
    'Wanshouxigong': (39.878, 116.339)
}
df['lat'] = df['station'].map(lambda x: station_coordinates.get(x, (None, None))[0])
df['lon'] = df['station'].map(lambda x: station_coordinates.get(x, (None, None))[1])

# Nama fitur yang lebih mudah dimengerti
feature_names = {
    "PM2.5": "Fine Particulate Matter (PM2.5)",
    "PM10": "Coarse Particulate Matter (PM10)",
    "SO2": "Sulfur Dioxide (SO2)",
    "NO2": "Nitrogen Dioxide (NO2)",
    "CO": "Carbon Monoxide (CO)",
    "O3": "Ozone (O3)",
    "TEMP": "Temperature (°C)",
    "PRES": "Pressure (hPa)",
    "DEWP": "Dew Point (°C)",
    "WSPM": "Wind Speed (m/s)",
    "AQI_True": "Air Quality Index (AQI)"
}

# ====================================================== 
# 2. SIDEBAR FILTERS
# ======================================================
st.sidebar.title("Filters")
st.sidebar.markdown("### Select Data Options")
selected_feature_key = st.sidebar.selectbox(
    "Select Feature", list(feature_names.keys()),
    format_func=lambda x: feature_names[x]
)
selected_station = st.sidebar.selectbox(
    "Select Station", ['All Stations'] + list(df['station'].unique())
)
selected_season = st.sidebar.multiselect(
    "Select Season", df['season'].unique(),
    default=list(df['season'].unique())
)

@st.cache_data
def filter_data(df, selected_season, selected_station):
    df_filtered = df[df['season'].isin(selected_season)]
    if selected_station != 'All Stations':
        df_filtered = df_filtered[df_filtered['station'] == selected_station]
    return df_filtered

df_filtered = filter_data(df, selected_season, selected_station)

# ======================================================
# 3. MAIN LAYOUT & AQI EXPANDER
# ======================================================
st.title("🌍 Advanced Air Quality Dashboard")
st.markdown("### Exploring Air Quality and Weather Data 2013-2017 in Beijing, China")

# Jika fitur AQI yang dipilih, tampilkan keterangan level AQI (US & China)
if selected_feature_key == "AQI_True":
    with st.expander("AQI Level Explanations (US & China)", expanded=True):
        st.markdown("**US AQI Levels:**")
        st.markdown("""
- **0-50:** Good  
- **51-100:** Moderate  
- **101-150:** Unhealthy for Sensitive Groups  
- **151-200:** Unhealthy  
- **201-300:** Very Unhealthy  
- **301-500:** Hazardous  
        """)

tabs = st.tabs([
    "📊 Overview",
    "📈 Trends",
    "🏆 Station Rankings",
    "🌦 Seasonal Patterns",
    "☁ Weather Impact",
    "🌍 Geographic Distribution",
    "📍 Station Details"
])

# ======================================================
# 4. TAB 0: OVERVIEW
# ======================================================
with tabs[0]:
    st.subheader("📊 Overview: One Chart from Each Tab")
    st.markdown(
        "Di bawah ini adalah ringkasan singkat. "
        "Masing-masing chart mewakili satu tab lain di dashboard."
    )

    # ---------- Row 1 ----------
    row1_col1, row1_col2 = st.columns(2)

    # (1) Trends (contoh: Monthly Trend)
    with row1_col1:
        st.markdown("**Trends (Monthly)**")
        agg_monthly = df_filtered.groupby('month')[selected_feature_key].mean().reset_index()
        fig_monthly = px.line(
            agg_monthly, x='month', y=selected_feature_key,
            title=f'Monthly Trend of {feature_names.get(selected_feature_key)}',
            markers=True,
            labels={'month': 'Month', selected_feature_key: feature_names.get(selected_feature_key)}
        )
        fig_monthly.update_xaxes(range=[1, 12])
        st.plotly_chart(fig_monthly, use_container_width=True, key="overview_monthly")

    # (2) Station Rankings (contoh: bar chart)
    with row1_col2:
        st.markdown("**Station Rankings**")
        agg_station = df_filtered.groupby('station')[selected_feature_key].mean().reset_index()
        agg_station = agg_station.sort_values(by=selected_feature_key, ascending=False)

        fig_rank = px.bar(
            agg_station, x='station', y=selected_feature_key,
            title=f'Ranking of {feature_names.get(selected_feature_key)} Across Stations',
            text=selected_feature_key, color=selected_feature_key,
            color_continuous_scale='Viridis'
        )
        fig_rank.update_layout(
            xaxis_title="Station",
            yaxis_title=feature_names.get(selected_feature_key),
            xaxis={'categoryorder': 'total descending'},
            coloraxis_colorbar=dict(title=feature_names.get(selected_feature_key))
        )
        st.plotly_chart(fig_rank, use_container_width=True, key="overview_station_rank")

    # ---------- Row 2 ----------
    row2_col1, row2_col2 = st.columns(2)

    # (3) Seasonal Patterns (contoh: box chart)
    with row2_col1:
        st.markdown("**Seasonal Patterns**")
        fig_seasonal = px.box(
            df_filtered, x='season', y=selected_feature_key, color='season',
            title=f'Seasonal Distribution of {feature_names.get(selected_feature_key)}'
        )
        fig_seasonal.update_layout(xaxis_title="Season")
        st.plotly_chart(fig_seasonal, use_container_width=True, key="overview_seasonal")

    # (4) Weather Impact (contoh: average TEMP, DEWP, WSPM by season)
    with row2_col2:
        st.markdown("**Weather Impact**")
        agg_weather = df_filtered.groupby('season')[['TEMP', 'DEWP', 'WSPM']].mean().reset_index()
        fig_weather = go.Figure()
        for col in ['TEMP', 'DEWP', 'WSPM']:
            fig_weather.add_trace(
                go.Scatter(
                    x=agg_weather['season'], y=agg_weather[col],
                    mode='lines+markers', name=feature_names.get(col)
                )
            )
        fig_weather.update_layout(
            title="Average Weather Conditions by Season (TEMP, DEWP, WSPM)",
            xaxis_title="Season", yaxis_title="Value"
        )
        st.plotly_chart(fig_weather, use_container_width=True, key="overview_weather")

    # ---------- Row 3 ----------
    row3_col1, row3_col2 = st.columns(2)

    # (5) Geographic Distribution (contoh ringkas)
    with row3_col1:
        st.markdown("**Geographic Distribution**")

        # Contoh custom color scale ala AQI (0-500)
        aqi_colorscale = [
            [0.0, "green"],
            [0.2, "yellow"],
            [0.4, "orange"],
            [0.6, "red"],
            [0.8, "purple"],
            [1.0, "maroon"]
        ]

        df_geo = df_filtered.dropna(subset=['lat', 'lon'])
        df_geo = df_geo.groupby('station').agg({
            selected_feature_key: 'mean',
            'lat': 'first',
            'lon': 'first'
        }).reset_index()

        fig_map = px.scatter_geo(
            df_geo,
            lat='lat', lon='lon',
            color=selected_feature_key, size=selected_feature_key,
            color_continuous_scale=aqi_colorscale,
            range_color=[0, 500],  # Ubah jika data di luar 0-500
            size_max=15,
            projection="natural earth",
            hover_name='station',
            title=f'Geographic Distribution of {feature_names.get(selected_feature_key)}'
        )
        fig_map.update_layout(
            margin={"r":0, "t":30, "l":0, "b":0},
            coloraxis_colorbar=dict(title=feature_names.get(selected_feature_key))
        )
        st.plotly_chart(fig_map, use_container_width=True, key="overview_geo")

    # (6) Station Details (ringkas)
    with row3_col2:
        st.markdown("**Station Details**")
        if selected_station != "All Stations":
            station_data = df[df['station'] == selected_station]
            fig_station = px.line(
                station_data, x='datetime', y=selected_feature_key,
                title=f"{feature_names.get(selected_feature_key)} Over Time at {selected_station}",
                markers=True,
                labels={'datetime': 'Time', selected_feature_key: feature_names.get(selected_feature_key)}
            )
            st.plotly_chart(fig_station, use_container_width=True, key="overview_station_details")
        else:
            st.info("Pilih stasiun tertentu dari sidebar untuk melihat detail di sini.")

# ======================================================
# 5. TAB 1: TRENDS
# ======================================================
with tabs[1]:
    st.subheader("📈 Trends in Air Quality")

    trend_cols = st.columns(2)
    
    # Hourly
    agg_hourly = df_filtered.groupby('hour')[selected_feature_key].mean().reset_index()
    fig_hourly = px.line(
        agg_hourly, x='hour', y=selected_feature_key,
        title=f'Hourly Trend of {feature_names.get(selected_feature_key)}', markers=True,
        labels={'hour': 'Hour', selected_feature_key: feature_names.get(selected_feature_key)}
    )
    fig_hourly.update_xaxes(range=[0, 23])
    trend_cols[0].plotly_chart(fig_hourly, use_container_width=True, key="trends_hourly")
    
    # Daily
    agg_daily = df_filtered.groupby('day')[selected_feature_key].mean().reset_index()
    fig_daily = px.line(
        agg_daily, x='day', y=selected_feature_key,
        title=f'Daily Trend of {feature_names.get(selected_feature_key)}', markers=True,
        labels={'day': 'Day', selected_feature_key: feature_names.get(selected_feature_key)}
    )
    fig_daily.update_xaxes(range=[1, 31])
    trend_cols[1].plotly_chart(fig_daily, use_container_width=True, key="trends_daily")
    
    trend_cols = st.columns(2)
    # Monthly
    agg_monthly = df_filtered.groupby('month')[selected_feature_key].mean().reset_index()
    fig_monthly = px.line(
        agg_monthly, x='month', y=selected_feature_key,
        title=f'Monthly Trend of {feature_names.get(selected_feature_key)}', markers=True,
        labels={'month': 'Month', selected_feature_key: feature_names.get(selected_feature_key)}
    )
    fig_monthly.update_xaxes(range=[1, 12])
    trend_cols[0].plotly_chart(fig_monthly, use_container_width=True, key="trends_monthly")
    
    # Yearly
    agg_yearly = df_filtered.groupby('year')[selected_feature_key].mean().reset_index()
    fig_yearly = px.line(
        agg_yearly, x='year', y=selected_feature_key,
        title=f'Yearly Trend of {feature_names.get(selected_feature_key)}', markers=True,
        labels={'year': 'Year', selected_feature_key: feature_names.get(selected_feature_key)}
    )
    trend_cols[1].plotly_chart(fig_yearly, use_container_width=True, key="trends_yearly")

# ======================================================
# 6. TAB 2: STATION RANKINGS
# ======================================================
with tabs[2]:
    st.subheader("🏆 Air Quality Index (AQI) Rankings by Station")
    agg_station = df_filtered.groupby('station')[selected_feature_key].mean().reset_index()
    agg_station = agg_station.sort_values(by=selected_feature_key, ascending=False)
    
    fig_rank = px.bar(
        agg_station, x='station', y=selected_feature_key,
        title=f'Ranking of {feature_names.get(selected_feature_key)} Across Stations',
        text=selected_feature_key, color=selected_feature_key,
        color_continuous_scale='Viridis'
    )
    fig_rank.update_layout(
        xaxis_title="Station", 
        yaxis_title=feature_names.get(selected_feature_key),
        xaxis={'categoryorder': 'total descending'},
        coloraxis_colorbar=dict(title=feature_names.get(selected_feature_key))
    )
    st.plotly_chart(fig_rank, use_container_width=True, key="station_rankings_bar")
    
    agg_trend = df_filtered.groupby(['station', 'year'])[selected_feature_key].mean().reset_index()
    fig_trend = px.line(
        agg_trend, x='year', y=selected_feature_key, color='station',
        title=f'Trend of {feature_names.get(selected_feature_key)} Over Time'
    )
    fig_trend.update_layout(
        yaxis_title=feature_names.get(selected_feature_key),
        xaxis=dict(tickmode='linear', tick0=agg_trend['year'].min(), dtick=1)
    )
    st.plotly_chart(fig_trend, use_container_width=True, key="station_rankings_line")

    st.subheader("📋 Detailed Rankings Table")
    agg_station['Rank'] = agg_station[selected_feature_key].rank(ascending=False).astype(int)
    agg_station = agg_station.set_index('Rank')
    agg_station = agg_station.rename(columns={selected_feature_key: feature_names.get(selected_feature_key)})
    st.dataframe(agg_station.style.background_gradient(cmap="viridis"))

# ======================================================
# 7. TAB 3: SEASONAL PATTERNS
# ======================================================
with tabs[3]:
    st.subheader("🌦 Seasonal Patterns of Air Quality")
    fig_seasonal = px.box(
        df_filtered, x='season', y=selected_feature_key, color='season',
        title=f'Seasonal Distribution of {feature_names.get(selected_feature_key)}'
    )
    fig_seasonal.update_layout(xaxis_title="Season")
    st.plotly_chart(fig_seasonal, use_container_width=True, key="seasonal_box")

    st.subheader("📈 Seasonal Trends")
    seasonal_cols = st.columns(2)
    agg_seasonal_year = df_filtered.groupby(['season', 'year'])[selected_feature_key].mean().reset_index()
    fig_seasonal_trend = px.line(
        agg_seasonal_year, x='year', y=selected_feature_key, color='season',
        title=f'Trend of {feature_names.get(selected_feature_key)} by Season'
    )
    fig_seasonal_trend.update_layout(
        yaxis_title=feature_names.get(selected_feature_key), 
        xaxis_title="Year"
    )
    seasonal_cols[0].plotly_chart(fig_seasonal_trend, use_container_width=True, key="seasonal_trend_line")
    
    agg_seasonal_station = df_filtered.groupby(['season', 'station'])[selected_feature_key].mean().reset_index()
    fig_seasonal_bar = px.bar(
        agg_seasonal_station, x='station', y=selected_feature_key, color='season',
        title=f'{feature_names.get(selected_feature_key)} by Season in Every Station'
    )
    fig_seasonal_bar.update_layout(
        yaxis_title=feature_names.get(selected_feature_key), 
        xaxis_title="Station"
    )
    seasonal_cols[1].plotly_chart(fig_seasonal_bar, use_container_width=True, key="seasonal_bar")

# ======================================================
# 8. TAB 4: WEATHER IMPACT
# ======================================================
with tabs[4]:
    st.subheader("☁ Weather Impact on Air Quality")
    weather_cols = st.columns(2)
    
    # TEMP, DEWP, WSPM by season
    agg_weather = df_filtered.groupby('season')[['TEMP', 'DEWP', 'WSPM']].mean().reset_index()
    fig_weather = go.Figure()
    for col in ['TEMP', 'DEWP', 'WSPM']:
        fig_weather.add_trace(
            go.Scatter(
                x=agg_weather['season'], y=agg_weather[col],
                mode='lines+markers', name=feature_names.get(col)
            )
        )
    fig_weather.update_layout(
        title="Average Weather Conditions by Season (TEMP, DEWP, WSPM)",
        xaxis_title="Season", yaxis_title="Value"
    )
    weather_cols[0].plotly_chart(fig_weather, use_container_width=True, key="weather_impact_lines")
    
    # PRES by season
    agg_pressure = df_filtered.groupby('season')['PRES'].mean().reset_index()
    fig_pressure = px.line(
        agg_pressure, x='season', y='PRES',
        title="Average Pressure by Season", markers=True,
        labels={'PRES': feature_names.get('PRES')}
    )
    fig_pressure.update_layout(
        xaxis_title="Season", 
        yaxis_title=feature_names.get('PRES')
    )
    weather_cols[1].plotly_chart(fig_pressure, use_container_width=True, key="weather_impact_pressure")
    
    # TEMP, DEWP, WSPM by station
    agg_weather_station = df_filtered.groupby('station')[['TEMP', 'DEWP', 'WSPM']].mean().reset_index()
    fig_weather_station = go.Figure()
    for col in ['TEMP', 'DEWP', 'WSPM']:
        fig_weather_station.add_trace(
            go.Scatter(
                x=agg_weather_station['station'], y=agg_weather_station[col],
                mode='lines+markers', name=feature_names.get(col)
            )
        )
    fig_weather_station.update_layout(
        title="Average Weather Conditions by Station (TEMP, DEWP, WSPM)",
        xaxis_title="Station", yaxis_title="Value"
    )
    weather_cols[0].plotly_chart(fig_weather_station, use_container_width=True, key="weather_station_lines")
    
    # PRES by station
    agg_pressure_station = df_filtered.groupby('station')['PRES'].mean().reset_index()
    fig_pressure_station = px.line(
        agg_pressure_station, x='station', y='PRES',
        title="Average Pressure by Station", markers=True,
        labels={'PRES': feature_names.get('PRES')}
    )
    fig_pressure_station.update_layout(
        xaxis_title="Station", 
        yaxis_title=feature_names.get('PRES')
    )
    weather_cols[1].plotly_chart(fig_pressure_station, use_container_width=True, key="weather_station_pressure")

# ======================================================
# 9. TAB 5: GEOGRAPHIC DISTRIBUTION (ADVANCED MAP)
# ======================================================
with tabs[5]:
    st.subheader("🌍 Geographic Distribution of Air Quality (Advanced Map)")
    
    # Contoh custom color scale ala AQI (0-500)
    aqi_colorscale = [
        [0.0, "green"],
        [0.2, "yellow"],
        [0.4, "orange"],
        [0.6, "red"],
        [0.8, "purple"],
        [1.0, "maroon"]
    ]

    df_geo = df_filtered.dropna(subset=['lat', 'lon'])
    df_geo = df_geo.groupby('station').agg({
        selected_feature_key: 'mean',
        'lat': 'first',
        'lon': 'first'
    }).reset_index()

    # Gunakan scatter_map untuk peta interaktif
    fig_map = px.scatter_map(
        df_geo,
        lat="lat",
        lon="lon",
        color=selected_feature_key,
        size=selected_feature_key,
        color_continuous_scale=aqi_colorscale,
        range_color=[0, 500],
        size_max=15,
        zoom=8,
        map_style="open-street-map",
        hover_name="station",
        title=f'Geographic Distribution of {feature_names.get(selected_feature_key)} by Station (map)'
    )
    fig_map.update_layout(
        margin={"r":0, "t":30, "l":0, "b":0},
        coloraxis_colorbar=dict(title=feature_names.get(selected_feature_key))
    )
    st.plotly_chart(fig_map, use_container_width=True, key="advanced_map")

# ======================================================
# 10. TAB 6: STATION DETAILS
# ======================================================
with tabs[6]:
    st.subheader("📍 Station Details")
    if selected_station != "All Stations":
        # Ambil data untuk stasiun terpilih
        station_data = df[df['station'] == selected_station]
        st.markdown(f"### Detail untuk stasiun: **{selected_station}**")
        st.markdown(f"**Koordinat:** {station_coordinates.get(selected_station, ('N/A', 'N/A'))}")
        st.markdown(f"**Total Data Record:** {len(station_data)}")
        st.markdown(
            f"**Rata-rata {feature_names.get(selected_feature_key)}:** "
            f"{station_data[selected_feature_key].mean():.2f}"
        )
        
        # Grafik time series untuk stasiun terpilih
        fig_station = px.line(
            station_data, x='datetime', y=selected_feature_key,
            title=f"{feature_names.get(selected_feature_key)} Over Time at {selected_station}",
            markers=True,
            labels={'datetime': 'Time', selected_feature_key: feature_names.get(selected_feature_key)}
        )
        st.plotly_chart(fig_station, use_container_width=True, key="station_details_chart")
        
        # Tampilkan tabel ringkasan data stasiun
        st.dataframe(station_data.sort_values('datetime').reset_index(drop=True))
    else:
        st.info("Silakan pilih stasiun tertentu dari sidebar untuk melihat detail.")

# ======================================================
# 11. SHOW RAW DATA OPTION
# ======================================================
if st.sidebar.checkbox("Show Raw Data"):
    st.subheader("📝 Raw Data")
    st.dataframe(df_filtered)
