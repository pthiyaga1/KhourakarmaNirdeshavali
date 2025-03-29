import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# -------------------------
# Load Data
# -------------------------
@st.cache_data

def load_data():
    url = "https://raw.githubusercontent.com/pthiyaga1/KshourakarmaNirdeshavali/main/Panchangam_April-June_2025_filled_full.csv"
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# -------------------------
# Janma Nakshatra Input
# -------------------------
nakshatras = [
    "Ashvini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Aardra", "Punarvasu", "Pushya", "Aslesha",
    "Magha", "P. Phalguni or Purva", "U. Phalguni or Uttara", "Hasta", "Chitra", "Svaati", "Vishaakha",
    "Anuraadha", "Jyeshtha", "Mula", "P.shadha", "U.shada", "Shravana", "Dhanishta", "Shatabhisha",
    "P. Bhadrapada", "U. Bhadrapada", "Revati"
]

st.title("💇 Kshoura Karma Nirdeshavali - Rev05")
st.subheader("📍 Portland OR")

user_nakshatra = st.selectbox("Select your Janma Nakshatra", nakshatras)
current_time = datetime.now()
st.markdown(f"**Current timestamp:** {current_time.strftime('%A, %B %d, %Y %I:%M %p')}")

# -------------------------
# Rule Filters
# -------------------------
def is_haircut_allowed(row, user_nakshatra):
    disallowed_tithis = ["Prathama", "Chaturthi", "Shashti", "Navami", "Chaturdashi", "Poornima", "Amavasya"]
    disallowed_yogas = ["Vyatheetapam", "Vaidhriti"]
    allowed_nakshatras = ["Ashwini", "Mrigasheerham", "Punarvasu", "Pushyam", "Hastam", "Chitra", "Swati", "Jyeshta", "Shravana", "Dhanishta", "Shatabhishak", "Revati"]

    day = row['Day']
    if day in ["Sunday", "Tuesday", "Saturday"]:
        return False

    tithi = str(row['Tithi']).split(' ')[0] if pd.notna(row['Tithi']) else ""
    if tithi in disallowed_tithis:
        return False

    yoga = str(row['Yogam']).split(' ')[0] if pd.notna(row['Yogam']) else ""
    if any(y in yoga for y in disallowed_yogas):
        return False

    nakshatra = str(row['Nakshatra']).split(' ')[0] if pd.notna(row['Nakshatra']) else ""
    if user_nakshatra.split()[0] in nakshatra:  # Janma Nakshatra check
        return False
    if nakshatra not in allowed_nakshatras:
        return False

    return True

# -------------------------
# Suggest Haircut Dates
# -------------------------
st.markdown("---")
st.markdown("### 💇 Next 2 Allowed Haircut Days")
suggestions = []
for idx, row in df.iterrows():
    if row['Date'] > current_time and is_haircut_allowed(row, user_nakshatra):
        suggestions.append(row)
    if len(suggestions) == 2:
        break

if suggestions:
    for s in suggestions:
        st.success(f"{s['Day']}, {s['Date'].strftime('%B %d, %Y')} — Tithi: {s['Tithi']}, Nakshatra: {s['Nakshatra']}, Yogam: {s['Yogam']}")
else:
    st.warning("No allowed haircut dates found in this dataset.")

# -------------------------
# Pick a Date - Legacy Functionality
# -------------------------
st.markdown("---")
st.markdown("### 🌄 Panchangam Lookup for a Selected Date")
selected_date = st.date_input("Pick a date", min_value=df['Date'].min(), max_value=df['Date'].max())
today_row = df[df['Date'] == pd.to_datetime(selected_date)]
next_day_row = df[df['Date'] == pd.to_datetime(selected_date) + timedelta(days=1)]

if not today_row.empty and not next_day_row.empty:
    day = today_row.iloc[0]['Day']
    sunrise = datetime.strptime(today_row.iloc[0]['Sunrise'], "%H:%M:%S")
    sunset = datetime.strptime(today_row.iloc[0]['Sunset'], "%H:%M:%S")
    st.success(f"🗓️ {day}, {selected_date.strftime('%B %d, %Y')}")

    def parse_transition(data_today, data_next, sunrise, sunset, label):
        transition_str = ""
        if pd.notna(data_today) and ' ' in data_today:
            name, time = data_today.split(' ')
            dt = datetime.strptime(time, "%H:%M:%S")
            if dt.hour >= 24:
                dt -= timedelta(hours=24)
                dt += timedelta(days=1)
                transition_str = f"{name} till {dt.strftime('%I:%M:%S %p')} on {(selected_date + timedelta(days=1)).strftime('%m/%d/%Y')}"
            elif dt <= sunrise:
                transition_str = f"{data_next} after {sunrise.strftime('%I:%M %p')}"
            elif dt > sunset:
                transition_str = f"{name} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
            else:
                transition_str = f"{name} from {sunrise.strftime('%I:%M %p')} to {dt.strftime('%I:%M %p')}, {data_next} after {dt.strftime('%I:%M %p')}"
        elif pd.notna(data_today):
            transition_str = data_today
        else:
            transition_str = "N/A"

        icon_map = {
            'Tithi': '🔹',
            'Nakshatra': '🌟',
            'Yogam': '🧘'
        }
        color_map = {
            'Tithi': '#0066cc',
            'Nakshatra': '#ffaa00',
            'Yogam': '#228B22'
        }
        st.markdown(f"<b style='color:{color_map[label]}'> {icon_map[label]} {label}s b/w Sunrise & Sunset:</b> {transition_str}", unsafe_allow_html=True)

    parse_transition(today_row.iloc[0]['Tithi'], next_day_row.iloc[0]['Tithi'], sunrise, sunset, 'Tithi')
    parse_transition(today_row.iloc[0]['Nakshatra'], next_day_row.iloc[0]['Nakshatra'], sunrise, sunset, 'Nakshatra')
    parse_transition(today_row.iloc[0]['Yogam'], next_day_row.iloc[0]['Yogam'], sunrise, sunset, 'Yogam')

# -------------------------
# Reference Image
# -------------------------
st.image("https://raw.githubusercontent.com/pthiyaga1/KshourakarmaNirdeshavali/main/image.png", use_container_width=True)
