import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Helper Functions ---
def parse_transition(row, col_name, sunrise, sunset, next_day_str):
    value = row[col_name]
    results = []
    if pd.isna(value):
        return ["N/A"]

    if 'full night' in value:
        results.append(f"{value}")
    elif '+' in value:
        name, time = value.split(' ')
        hours, minutes, seconds = map(int, time.split(':'))
        hours -= 24
        dt = datetime.strptime(f"{hours}:{minutes}:{seconds}", "%H:%M:%S") + timedelta(days=1)
        results.append(f"{name} till {dt.strftime('%I:%M:%S %p')} on {next_day_str}")
    elif ' ' in value:
        name, time = value.split(' ')
        dt = datetime.strptime(time, "%H:%M:%S")
        if dt <= sunrise:
            next_value = next_row[col_name]
            results.append(f"{next_value} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}")
        elif dt > sunset:
            results.append(f"{name} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}")
        else:
            next_value = next_row[col_name].split(' ')[0] if ' ' in next_row[col_name] else next_row[col_name]
            results.append(f"{name} from {sunrise.strftime('%I:%M %p')} to {dt.strftime('%I:%M %p')}, {next_value} from {dt.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}")
    return results

# --- Streamlit App ---
st.set_page_config(page_title="Kshoura Karma Panchangam Tool", layout="centered")
st.title("🗓️ Panchangam Lookup for Selected Date")

# Load Data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/pthiyaga1/KshourakarmaNirdeshavali/main/Panchangam_April-June_2025_filled_full.csv"
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# Select a date
date_selected = st.date_input("Pick a date", min_value=df['Date'].min(), max_value=df['Date'].max())
today_row = df[df['Date'] == pd.to_datetime(date_selected)]
next_row = df[df['Date'] == pd.to_datetime(date_selected) + timedelta(days=1)]

if not today_row.empty and not next_row.empty:
    today_row = today_row.iloc[0]
    next_row = next_row.iloc[0]
    day = today_row['Day']
    st.success(f"📅 {day}, {date_selected.strftime('%B %d, %Y')}")

    # Parse times
    sunrise = datetime.strptime(today_row['Sunrise'], "%H:%M:%S")
    sunset = datetime.strptime(today_row['Sunset'], "%H:%M:%S")
    next_day_str = (pd.to_datetime(date_selected) + timedelta(days=1)).strftime('%m/%d/%Y')

    # Tithi
    tithi_results = parse_transition(today_row, 'Tithi', sunrise, sunset, next_day_str)
    st.markdown(f"<b style='color:#0066cc'>🔷 Tithis b/w Sunrise & Sunset:</b> {'; '.join(tithi_results)}", unsafe_allow_html=True)

    # Nakshatra
    nakshatra_results = parse_transition(today_row, 'Nakshatra', sunrise, sunset, next_day_str)
    st.markdown(f"<b style='color:#ffaa00'>🌟 Nakshatras b/w Sunrise & Sunset:</b> {'; '.join(nakshatra_results)}", unsafe_allow_html=True)

    # Yogam
    yogam_results = parse_transition(today_row, 'Yogam', sunrise, sunset, next_day_str)
    st.markdown(f"<b style='color:#228B22'>🧘 Yogam b/w Sunrise & Sunset:</b> {'; '.join(yogam_results)}", unsafe_allow_html=True)

    # 📜 Display Shastra chart
    st.image("https://raw.githubusercontent.com/pthiyaga1/KshourakarmaNirdeshavali/main/image.png", use_container_width=True)
else:
    st.warning("The date you selected is not available in the Panchangam data.")
