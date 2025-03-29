import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("📅 Prasanna's Panchangam Lookup Tool for Portland, OR - Rev2 - 3/28/25")
st.subheader("Select a date to find Tithis & Nakshatras between sunrise & sunset")

# 📤 Load the CSV from GitHub or local
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/pthiyaga1/KhourakarmaNirdeshavali/main/Panchangam_April-June_2025_filled_full.csv"
    df = pd.read_csv(url)
    return df

df = load_data()
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# 📅 Date input
selected_date = st.date_input("Pick a date", min_value=df['Date'].min(), max_value=df['Date'].max())
result = df[df['Date'] == pd.to_datetime(selected_date)]

# 🧾 Show Panchangam
if not result.empty:
    sunrise_str = result.iloc[0].get("Sunrise", "06:00:00")
    sunset_str = result.iloc[0].get("Sunset", "18:00:00")

    # Convert times to datetime objects
    sunrise = datetime.combine(selected_date, datetime.strptime(sunrise_str.strip(), "%H:%M:%S").time())
    sunset = datetime.combine(selected_date, datetime.strptime(sunset_str.strip(), "%H:%M:%S").time())

    # --- Handle Tithi ---
    tithi_info = result.iloc[0].get("Tithi", "N/A")
    tithi_split = tithi_info.split(" ")
    tithi_name = " ".join(tithi_split[:-1])
    tithi_time_str = tithi_split[-1] if len(tithi_split) > 1 else None

    tithi_output = "N/A"
    if tithi_time_str:
        try:
            tithi_time = datetime.combine(selected_date, datetime.strptime(tithi_time_str, "%H:%M:%S").time())
            if sunrise <= tithi_time <= sunset:
                # Get next day's Tithi
                next_day = pd.to_datetime(selected_date) + timedelta(days=1)
                next_row = df[df['Date'] == next_day]
                if not next_row.empty:
                    tithi_output = f"{tithi_name} & {next_row.iloc[0]['Tithi']}"
                else:
                    tithi_output = f"{tithi_name}"
            else:
                tithi_output = tithi_name
        except:
            tithi_output = tithi_name

    # --- Handle Nakshatra ---
    nakshatra_info = result.iloc[0].get("Nakshatra", "N/A")
    nakshatra_split = nakshatra_info.split(" ")
    nakshatra_name = " ".join(nakshatra_split[:-1])
    nakshatra_time_str = nakshatra_split[-1] if len(nakshatra_split) > 1 else None

    nakshatra_output = "N/A"
    if nakshatra_time_str:
        try:
            nakshatra_time = datetime.combine(selected_date, datetime.strptime(nakshatra_time_str, "%H:%M:%S").time())
            if sunrise <= nakshatra_time <= sunset:
                next_day = pd.to_datetime(selected_date) + timedelta(days=1)
                next_row = df[df['Date'] == next_day]
                if not next_row.empty:
                    nakshatra_output = f"{nakshatra_name} & {next_row.iloc[0]['Nakshatra']}"
                else:
                    nakshatra_output = f"{nakshatra_name}"
            else:
                nakshatra_output = nakshatra_name
        except:
            nakshatra_output = nakshatra_name

    # ✅ Display
    st.success(f"📆 Date: {selected_date.strftime('%B %d, %Y')}")
    st.write(f"🌀 **Tithis b/w sunrise & sunset**: {tithi_output}")
    st.write(f"🌟 **Nakshatras b/w sunrise & sunset**: {nakshatra_output}")
else:
    st.warning("This date is not available in the data. Try another one.")
