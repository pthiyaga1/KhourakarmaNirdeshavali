import streamlit as st
import pandas as pd
from datetime import datetime, time

st.title("🗕️ Prasanna's Panchangam Lookup Tool for Portland, OR - Rev1 - 3/28/25")
st.subheader("Select a date to find Tithis b/w sunrise & sunset and Nakshatra")

# 📄 Load the CSV
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/pthiyaga1/KhourakarmaNirdeshavali/main/Panchangam_April-June_2025_filled_full.csv"
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    return df

df = load_data()

# 🗓️ Let user pick a date
selected_date = st.date_input("Pick a date", min_value=df['Date'].min(), max_value=df['Date'].max())

# 🔍 Search for current and next day rows
current_day = df[df['Date'] == pd.to_datetime(selected_date)]
next_day = df[df['Date'] == pd.to_datetime(selected_date) + pd.Timedelta(days=1)]

if not current_day.empty:
    row = current_day.iloc[0]
    sunrise = datetime.strptime(row['Sunrise'], '%H:%M:%S').time()
    sunset = datetime.strptime(row['Sunset'], '%H:%M:%S').time()

    # Extract tithi and time
    tithi_entry = row['Tithi']
    try:
        tithi_name, tithi_time_str = tithi_entry.split()
        tithi_time = datetime.strptime(tithi_time_str.replace('+', ''), '%H:%M:%S').time()
    except:
        tithi_name = tithi_entry
        tithi_time = None

    # Get next day's tithi if available
    tithi_next = None
    if not next_day.empty:
        tithi_next_entry = next_day.iloc[0]['Tithi']
        tithi_next = tithi_next_entry.split()[0] if isinstance(tithi_next_entry, str) else None

    # 📅 Display
    st.success(f"🗓️ Date: {selected_date.strftime('%B %d, %Y')}")

    if tithi_time and sunrise <= tithi_time <= sunset:
        tithis_today = f"{tithi_name}, {tithi_next}" if tithi_next else tithi_name
    else:
        tithis_today = f"{tithi_name}"

    st.write(f"🔀 **Tithis b/w sunrise & sunset**: {tithis_today}")

    nakshatra = row.get('Nakshatra', 'N/A')
    st.write(f"🌟 **Nakshatra**: {nakshatra}")
else:
    st.warning("This date is not available in the data. Try another one.")
