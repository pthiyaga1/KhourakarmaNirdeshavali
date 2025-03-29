import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("✂️ Kshoura Karma Nirdeshavali - Rev04 - 03/29/25")
st.subheader("📍 Portland OR")

# Load the CSV from GitHub
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/pthiyaga1/KshourakarmaNirdeshavali/main/Panchangam_April-June_2025_filled_full.csv"
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# Let user pick a date
selected_date = st.date_input("Pick a date", min_value=df['Date'].min(), max_value=df['Date'].max())

# Get row for selected and next day
today_row = df[df['Date'] == pd.to_datetime(selected_date)]
next_day = selected_date + timedelta(days=1)
next_day_row = df[df['Date'] == pd.to_datetime(next_day)]

if not today_row.empty:
    row = today_row.iloc[0]
    next_row = next_day_row.iloc[0] if not next_day_row.empty else None

    # Parse sunrise and sunset
    sunrise = datetime.strptime(f"{selected_date} {row['Sunrise']}", "%Y-%m-%d %H:%M:%S")
    sunset = datetime.strptime(f"{selected_date} {row['Sunset']}", "%Y-%m-%d %H:%M:%S")

    def format_period(event_str, label, row_date):
        if pd.isna(event_str) or event_str.strip() == "":
            return None
        try:
            name, time_str = event_str.split()
            h, m, s = map(int, time_str.split(":"))
            if h >= 24:
                h -= 24
                next_day_time = datetime.combine(row_date + timedelta(days=1), datetime.min.time()) + timedelta(hours=h, minutes=m, seconds=s)
                return f"{name} till {next_day_time.strftime('%I:%M:%S %p on %m/%d/%Y')}"
            else:
                end_time = datetime.combine(row_date, datetime.min.time()) + timedelta(hours=h, minutes=m, seconds=s)
                if end_time < sunrise:
                    return None
                if end_time > sunset:
                    return f"{name} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
                return f"{name} from {sunrise.strftime('%I:%M %p')} to {end_time.strftime('%I:%M %p')}"
        except:
            return None

    tithi_str = format_period(row['Tithi'], "Tithi", selected_date) or ""
    if next_row is not None and next_row['Tithi']:
        next_tithi_name = next_row['Tithi'].split()[0]
        tithi_str += f", {next_tithi_name} after {sunset.strftime('%I:%M %p')}"

    nakshatra_str = format_period(row['Nakshatra'], "Nakshatra", selected_date) or ""
    if next_row is not None and next_row['Nakshatra']:
        next_nakshatra_name = next_row['Nakshatra'].split()[0]
        nakshatra_str += f", {next_nakshatra_name} after {sunset.strftime('%I:%M %p')}"

    # Display day
    st.success(f"📅 {selected_date.strftime('%A, %B %d, %Y')}")

    # Display info
    st.markdown(f"🔷 **Tithis b/w Sunrise & Sunset:** {tithi_str if tithi_str else 'N/A'}")
    st.markdown(f"🌟 **Nakshatras b/w Sunrise & Sunset:** {nakshatra_str if nakshatra_str else 'N/A'}")

    # Show the image
    st.image("image.png", use_container_width=True)

else:
    st.warning("Selected date not found in data.")
