import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("📅 Prasanna's Panchangam Lookup Tool for Portland, OR - Rev3")
st.subheader("Select a date to find Tithis & Nakshatras b/w Sunrise & Sunset with timings")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/pthiyaga1/KhourakarmaNirdeshavali/main/Panchangam_April-June_2025_filled_full.csv"
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# Let user pick a date
selected_date = st.date_input("Pick a date", min_value=df['Date'].min(), max_value=df['Date'].max())

# Get row for selected date and next date
today_row = df[df['Date'] == pd.to_datetime(selected_date)]
next_day_row = df[df['Date'] == pd.to_datetime(selected_date) + timedelta(days=1)]

if not today_row.empty and not next_day_row.empty:
    # Get sunrise and sunset times
    sunrise_str = today_row.iloc[0]['Sunrise']
    sunset_str = today_row.iloc[0]['Sunset']
    sunrise = datetime.strptime(sunrise_str, "%H:%M:%S")
    sunset = datetime.strptime(sunset_str, "%H:%M:%S")

    # --- TITHI LOGIC ---
    tithi_today = today_row.iloc[0]['Tithi']
    tithi_name, tithi_end_str = tithi_today.rsplit(' ', 1)
    tithi_end = datetime.strptime(tithi_end_str, "%H:%M:%S")

    if sunrise < tithi_end < sunset:
        next_tithi_name = next_day_row.iloc[0]['Tithi'].split(' ')[0]
        tithi_display = f"{tithi_name} from {sunrise.strftime('%H:%M')} to {tithi_end.strftime('%H:%M')}, " \
                        f"{next_tithi_name} from {tithi_end.strftime('%H:%M')} to {sunset.strftime('%H:%M')}"
    else:
        tithi_display = f"{tithi_name} from {sunrise.strftime('%H:%M')} to {sunset.strftime('%H:%M')}"

    # --- NAKSHATRA LOGIC ---
    nakshatra_today = today_row.iloc[0]['Nakshatra']
    nakshatra_name, nak_end_str = nakshatra_today.rsplit(' ', 1)
    nak_end = datetime.strptime(nak_end_str, "%H:%M:%S")

    if sunrise < nak_end < sunset:
        next_nak_name = next_day_row.iloc[0]['Nakshatra'].split(' ')[0]
        nak_display = f"{nakshatra_name} from {sunrise.strftime('%H:%M')} to {nak_end.strftime('%H:%M')}, " \
                      f"{next_nak_name} from {nak_end.strftime('%H:%M')} to {sunset.strftime('%H:%M')}"
    else:
        nak_display = f"{nakshatra_name} from {sunrise.strftime('%H:%M')} to {sunset.strftime('%H:%M')}"

    # Display
    st.success(f"📆 Date: {selected_date.strftime('%B %d, %Y')}")
    st.write(f"🌀 **Tithis b/w sunrise & sunset**: {tithi_display}")
    st.write(f"🌟 **Nakshatras b/w sunrise & sunset**: {nak_display}")
else:
    st.warning("This date or the next date is not in the data. Please try another one.")
