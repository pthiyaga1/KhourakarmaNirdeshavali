import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("📅 Kshoura Karma Nirdeshavali - Rev4")
st.subheader("Portand - OR - Rev4 ")

# Load CSV from GitHub or local
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/pthiyaga1/KhourakarmaNirdeshavali/main/Panchangam_April-June_2025_filled_full.csv"
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# Let user pick a date
selected_date = st.date_input("Pick a date", min_value=df['Date'].min(), max_value=df['Date'].max())

# Get today's and next day's rows
today_row = df[df['Date'] == pd.to_datetime(selected_date)]
next_day_row = df[df['Date'] == pd.to_datetime(selected_date) + timedelta(days=1)]

if not today_row.empty and not next_day_row.empty:
    # Extract times
    sunrise_str = today_row.iloc[0]['Sunrise']
    sunset_str = today_row.iloc[0]['Sunset']

    sunrise = datetime.strptime(sunrise_str.strip(), "%H:%M:%S")
    sunset = datetime.strptime(sunset_str.strip(), "%H:%M:%S")

    # Tithi Logic
    tithi_str = today_row.iloc[0]['Tithi']
    tithi_next = next_day_row.iloc[0]['Tithi']

    try:
        tithi_end_str = tithi_str.split()[-1]  # last part like 11:25:00
        tithi_end_time = datetime.strptime(tithi_end_str.strip(), "%H:%M:%S")
        if sunrise < tithi_end_time < sunset:
            tithi_range = f"{tithi_str.split()[0]} from {sunrise.strftime('%I:%M %p')} to {tithi_end_time.strftime('%I:%M %p')}, {tithi_next.split()[0]} from {tithi_end_time.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
        else:
            tithi_range = f"{tithi_str.split()[0]} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
    except:
        tithi_range = "N/A"

    # Nakshatra Logic
    nakshatra_str = today_row.iloc[0]['Nakshatra']
    nakshatra_next = next_day_row.iloc[0]['Nakshatra']

    try:
        nakshatra_end_str = nakshatra_str.split()[-1]
        nakshatra_end_time = datetime.strptime(nakshatra_end_str.strip(), "%H:%M:%S")
        if sunrise < nakshatra_end_time < sunset:
            nakshatra_range = f"{nakshatra_str.split()[0]} from {sunrise.strftime('%I:%M %p')} to {nakshatra_end_time.strftime('%I:%M %p')}, {nakshatra_next.split()[0]} from {nakshatra_end_time.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
        else:
            nakshatra_range = f"{nakshatra_str.split()[0]} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
    except:
        nakshatra_range = "N/A"

    # Day of the week
    day_of_week = selected_date.strftime("%A")

    # Display results
    st.success(f"📆 {day_of_week}, {selected_date.strftime('%B %d, %Y')}")
    st.write(f"🔷 **Tithis b/w Sunrise & Sunset**: {tithi_range}")
    st.write(f"🌟 **Nakshatras b/w Sunrise & Sunset**: {nakshatra_range}")

    # Show image below
    st.image("image.png", caption="Kshoura Karma Nirdeshavali", use_column_width=True)

else:
    st.warning("Data not available for selected date or the next day.")
