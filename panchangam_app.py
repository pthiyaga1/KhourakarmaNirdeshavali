import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta

st.title("📅 Prasanna's Panchangam Lookup Tool for Portland, OR - Rev1 - 3/28/25")
st.subheader("Select a date to find Tithis b/w sunrise & sunset and Nakshatra")

# 📤 Load the CSV from GitHub
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/pthiyaga1/KhourakarmaNirdeshavali/main/Panchangam_April-June_2025_filled_full.csv"
    df = pd.read_csv(url)
    return df

df = load_data()
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Convert Tithi times to timedelta
def extract_tithi_info(row):
    tithi_entries = []
    for col in ['Tithi', 'Tithi2']:  # Assuming you may eventually split multiple tithis per day
        val = row.get(col) or row.get('Tithi')
        if pd.notna(val) and any(char.isdigit() for char in val):
            tithi_name = ''.join(filter(lambda c: not c.isdigit() and c != ':', val)).strip()
            time_part = ''.join(filter(lambda c: c.isdigit() or c == ':', val)).strip()
            try:
                if '+' in time_part:
                    time_str = time_part.split('+')[0]
                    time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
                    tithi_entries.append((tithi_name, time_obj))
            except:
                pass
    return tithi_entries

# 📅 Let user pick a date
selected_date = st.date_input("Pick a date", min_value=df['Date'].min(), max_value=df['Date'].max())

# Get data for the selected date and next date
day_data = df[df['Date'] == pd.to_datetime(selected_date)]
next_day_data = df[df['Date'] == pd.to_datetime(selected_date + timedelta(days=1))]

if not day_data.empty:
    sunrise_str = day_data.iloc[0].get('Sunrise', '')
    sunset_str = day_data.iloc[0].get('Sunset', '')

    try:
        sunrise = datetime.strptime(sunrise_str.strip(), "%H:%M:%S").time()
        sunset = datetime.strptime(sunset_str.strip(), "%H:%M:%S").time()
    except:
        sunrise = time(5, 0)
        sunset = time(18, 0)

    tithis_between = []

    # Check today's tithi timing
    today_tithi = extract_tithi_info(day_data.iloc[0])
    for name, t_time in today_tithi:
        if sunrise <= t_time <= sunset:
            tithis_between.append(name)

    # Check if previous day's tithi ended after sunrise
    if not next_day_data.empty:
        next_day_tithi = extract_tithi_info(next_day_data.iloc[0])
        for name, t_time in next_day_tithi:
            if
