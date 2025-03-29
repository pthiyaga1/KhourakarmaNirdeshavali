import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image

st.set_page_config(page_title="Kshoura Karma Nirdeshavali", layout="centered")

st.title("✂️ Kshoura Karma Nirdeshavali - Rev04 - 03/29/25")
st.subheader("📍 Portland OR")
st.write("Select a date to find Tithis & Nakshatras b/w Sunrise & Sunset with timings")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/pthiyaga1/KshourakarmaNirdeshavali/main/Panchangam_April-June_2025_filled_full.csv"
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

selected_date = st.date_input("Pick a date", min_value=df['Date'].min(), max_value=df['Date'].max())

# Get today's and next day's rows
today_row = df[df['Date'] == pd.to_datetime(selected_date)]
next_row = df[df['Date'] == pd.to_datetime(selected_date + timedelta(days=1))]

if today_row.empty or next_row.empty:
    st.error("Data not available for selected date or next day.")
else:
    day_of_week = today_row.iloc[0]['Day']
    st.success(f"📅 {day_of_week}, {selected_date.strftime('%B %d, %Y')}")

    # Get sunrise and sunset times
    sunrise_str = today_row.iloc[0]['Sunrise']
    sunset_str = today_row.iloc[0]['Sunset']
    sunrise = datetime.strptime(sunrise_str, "%H:%M:%S").time()
    sunset = datetime.strptime(sunset_str, "%H:%M:%S").time()

    # ============ TITHI ============ #
    tithi1_info = today_row.iloc[0]['Tithi']
    tithi2_info = next_row.iloc[0]['Tithi']  # In case tithi spans beyond sunset

    tithi_parts = tithi1_info.split()
    tithi1_name = tithi_parts[0]
    tithi1_time = tithi_parts[1] if len(tithi_parts) > 1 else ""

    def parse_time_with_24_support(time_str, base_date):
        if ':' not in time_str:
            return None
        try:
            hour, minute, second = map(int, time_str.split(":"))
            if hour >= 24:
                hour -= 24
                return datetime.combine(base_date + timedelta(days=1), datetime.strptime(f"{hour}:{minute}:{second}", "%H:%M:%S").time())
            else:
                return datetime.combine(base_date, datetime.strptime(time_str, "%H:%M:%S").time())
        except:
            return None

    tithi1_end_dt = parse_time_with_24_support(tithi1_time, selected_date)

    tithi_str = ""
    if tithi1_end_dt:
        tithi_str += f"{tithi1_name} from {sunrise.strftime('%I:%M %p')} to {tithi1_end_dt.strftime('%I:%M %p')}, "
        tithi2_name = tithi2_info.split()[0]
        tithi_str += f"{tithi2_name} from {tithi1_end_dt.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
    else:
        tithi_str = f"{tithi1_name} (full day)"

    st.markdown(f"🔷 **Tithis b/w Sunrise & Sunset**: {tithi_str}")

    # ============ NAKSHATRA ============ #
    nakshatra_info = today_row.iloc[0]['Nakshatra']
    next_n_
