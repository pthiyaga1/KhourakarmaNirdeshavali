import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("✂️ Kshoura Karma Nirdeshavali - Rev04 - 03/29/25")
st.subheader("📍 Portland OR")

# 📤 Load the CSV from GitHub
@st.cache_data

def load_data():
    url = "https://raw.githubusercontent.com/pthiyaga1/KshourakarmaNirdeshavali/main/Panchangam_April-June_2025_filled_full.csv"
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# 📅 Let user pick a date
selected_date = st.date_input("Pick a date", min_value=df['Date'].min(), max_value=df['Date'].max())

# Get row for selected date and next date
today_row = df[df['Date'] == pd.to_datetime(selected_date)]
next_day_row = df[df['Date'] == pd.to_datetime(selected_date) + timedelta(days=1)]

if not today_row.empty and not next_day_row.empty:
    day = today_row.iloc[0]['Day']
    sunrise = datetime.strptime(today_row.iloc[0]['Sunrise'], "%H:%M:%S")
    sunset = datetime.strptime(today_row.iloc[0]['Sunset'], "%H:%M:%S")

    st.success(f"📅 {day}, {selected_date.strftime('%B %d, %Y')}")

    # === TITHI ===
    tithi_data = today_row.iloc[0]['Tithi']
    next_tithi = next_day_row.iloc[0]['Tithi']
    if pd.notna(tithi_data) and ' ' in tithi_data:
        tithi_name, tithi_time = tithi_data.split(' ')
        tithi_dt = datetime.strptime(tithi_time, "%H:%M:%S")
        if tithi_dt.hour >= 24:
            tithi_dt = tithi_dt - timedelta(hours=24)
            tithi_dt += timedelta(days=1)
        if tithi_dt > sunset:
            tithi_str = f"{tithi_name} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
        elif tithi_dt <= sunrise:
            tithi_str = f"{next_tithi} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
        else:
            tithi_str = f"{tithi_name} from {sunrise.strftime('%I:%M %p')} to {tithi_dt.strftime('%I:%M %p')}, {next_tithi} from {tithi_dt.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
    else:
        tithi_str = "N/A"
    st.markdown(f"<b style='color:#0066cc'>🔷 Tithis b/w Sunrise & Sunset:</b> {tithi_str}", unsafe_allow_html=True)

    # === NAKSHATRA ===
    nakshatra_data = today_row.iloc[0]['Nakshatra']
    next_nakshatra = next_day_row.iloc[0]['Nakshatra']
    nakshatra_str = ""
    if pd.notna(nakshatra_data):
        if "full night" in nakshatra_data:
            nakshatra_str = f"{nakshatra_data}"
        elif ' ' in nakshatra_data:
            nakshatra_name, nakshatra_time = nakshatra_data.split(' ')
            nakshatra_dt = datetime.strptime(nakshatra_time, "%H:%M:%S")
            if nakshatra_dt.hour >= 24:
                next_day = pd.to_datetime(selected_date) + timedelta(days=1)
                nakshatra_dt = nakshatra_dt - timedelta(hours=24)
                nakshatra_str = f"{nakshatra_name} till {nakshatra_dt.strftime('%I:%M:%S %p')} on {next_day.strftime('%m/%d/%Y')}"
            elif nakshatra_dt <= sunrise:
                nakshatra_str = f"{next_nakshatra} after {sunrise.strftime('%I:%M %p')}"
            elif nakshatra_dt > sunset:
                nakshatra_str = f"{nakshatra_name} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
            else:
                nakshatra_str = f"{nakshatra_name} from {sunrise.strftime('%I:%M %p')} to {nakshatra_dt.strftime('%I:%M %p')}, {next_nakshatra} after {nakshatra_dt.strftime('%I:%M %p')}"
    else:
        nakshatra_str = "N/A"
    st.markdown(f"<b style='color:#ffaa00'>🌟 Nakshatras b/w Sunrise & Sunset:</b> {nakshatra_str}", unsafe_allow_html=True)

    # === YOGAM ===
    yogam_data = today_row.iloc[0]['Yogam']
    next_yogam = next_day_row.iloc[0]['Yogam']
    yogam_str = ""
    if pd.notna(yogam_data):
        if "full night" in yogam_data:
            yogam_str = f"{yogam_data}"
        elif ' ' in yogam_data:
            yogam_name, yogam_time = yogam_data.split(' ')
            yogam_dt = datetime.strptime(yogam_time, "%H:%M:%S")
            if yogam_dt.hour >= 24:
                next_day = pd.to_datetime(selected_date) + timedelta(days=1)
                yogam_dt = yogam_dt - timedelta(hours=24)
                yogam_str = f"{yogam_name} till {yogam_dt.strftime('%I:%M:%S %p')} on {next_day.strftime('%m/%d/%Y')}"
            elif yogam_dt <= sunrise:
                yogam_str = f"{next_yogam} after {sunrise.strftime('%I:%M %p')}"
            elif yogam_dt > sunset:
                yogam_str = f"{yogam_name} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
            else:
                yogam_str = f"{yogam_name} from {sunrise.strftime('%I:%M %p')} to {yogam_dt.strftime('%I:%M %p')}, {next_yogam} after {yogam_dt.strftime('%I:%M %p')}"
    else:
        yogam_str = "N/A"
    st.markdown(f"<b style='color:#228B22'>🧘 Yogam b/w Sunrise & Sunset:</b> {yogam_str}", unsafe_allow_html=True)

    # Show guidance image
    st.image("https://raw.githubusercontent.com/pthiyaga1/KshourakarmaNirdeshavali/main/image.png", use_container_width=True)
else:
    st.warning("Date not available in the data. Please try another one.")
