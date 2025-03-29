import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Kshoura Karma Nirdeshavali", layout="centered")
st.title("💇‍♂️ Kshoura Karma Nirdeshavali - Rev04 - 03/29/25")
st.subheader("📍 Portland OR")

# === Load Data ===
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/pthiyaga1/KshourakarmaNirdeshavali/main/Panchangam_April-June_2025_filled_full.csv"
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# === Utility function to parse and interpret transition fields ===
def parse_transition(value_today, value_next):
    try:
        if pd.isna(value_today):
            return "N/A"

        if "full night" in value_today:
            return value_today

        if ' ' in value_today:
            name, time = value_today.split(' ')
            time_cleaned = time.replace("+", "").strip()
            dt = datetime.strptime(time_cleaned, "%H:%M:%S")
            return name, dt
        else:
            return value_today, None
    except:
        return "N/A", None

# === Section 1: Show haircut dates based on birth star ===
st.header("🔍 Get Haircut/Shaving Allowed Dates")

nakshatra_list = [
    "Ashvini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Aardra", "Punarvasu", "Pushya",
    "Aslesha", "Magha", "P. Phalguni or Purva", "U. Phalguni or Uttara", "Hasta", "Chitra", "Svaati",
    "Vishaakha", "Anuraadha", "Jyeshtha", "Mula", "P.shadha", "U.shada", "Shravana", "Dhanishta",
    "Shatabhisha", "P. Bhadrapada", "U. Bhadrapada", "Revati"
]

user_nakshatra = st.selectbox("Select your Janma Nakshatra:", nakshatra_list)

now = datetime.now()
st.write(f"🕒 Current time: {now.strftime('%A, %B %d, %Y %I:%M:%S %p')}")

# Haircut rules (simplified logic for demo)
allowed_days = ["Monday", "Wednesday", "Friday", "Thursday"]
avoid_nakshatras = [
    "Ashvini", "Mrigasheersham", "Punarvasu", "Pushyam", "Hastam", "Chitra", "Swati", "Jyeshta",
    "Shravana", "Dhanishta", "Shatabhishak", "Revati"
]
avoid_tithis = ["Prathama", "Chaturthi", "Shashti", "Navami", "Chaturdashi", "Poornima", "Amavasya"]
avoid_yogas = ["Vyatheetapa", "Vaidhriti"]

future_dates = []
for i in range(1, 30):
    date = now.date() + timedelta(days=i)
    row = df[df['Date'] == pd.to_datetime(date)]
    if not row.empty:
        day = row.iloc[0]['Day']
        tithi = str(row.iloc[0]['Tithi']).split(' ')[0]
        nakshatra = str(row.iloc[0]['Nakshatra']).split(' ')[0]
        yoga = str(row.iloc[0]['Yogam']).split(' ')[0]

        if day in allowed_days and tithi not in avoid_tithis and yoga not in avoid_yogas and user_nakshatra not in nakshatra:
            future_dates.append((date.strftime('%A, %B %d, %Y'), day, tithi, nakshatra, yoga))

if future_dates:
    st.markdown("### ✅ Next 2 Allowed Haircut/Shaving Dates:")
    for item in future_dates[:2]:
        st.markdown(f"- **{item[0]}** ({item[1]}): Tithi - {item[2]}, Nakshatra - {item[3]}, Yogam - {item[4]}")
else:
    st.warning("No suitable haircut/shaving days found in the next 30 days.")

# === Section 2: Panchangam for selected date ===
st.header("📆 Panchangam Lookup for a Selected Date")
selected_date = st.date_input("Pick a date", min_value=df['Date'].min(), max_value=df['Date'].max())

# Get today's and next day's data
selected_day = df[df['Date'] == pd.to_datetime(selected_date)]
next_day = df[df['Date'] == pd.to_datetime(selected_date) + timedelta(days=1)]

if not selected_day.empty and not next_day.empty:
    day = selected_day.iloc[0]['Day']
    sunrise = datetime.strptime(selected_day.iloc[0]['Sunrise'], "%H:%M:%S")
    sunset = datetime.strptime(selected_day.iloc[0]['Sunset'], "%H:%M:%S")
    st.success(f"📅 {day}, {selected_date.strftime('%B %d, %Y')}")

    # Tithi
    tname1, tdt = parse_transition(selected_day.iloc[0]['Tithi'], next_day.iloc[0]['Tithi'])
    tname2 = str(next_day.iloc[0]['Tithi']).split(' ')[0]
    if tdt is None:
        tithi_str = tname1
    elif tdt <= sunrise:
        tithi_str = f"{tname2} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
    elif tdt > sunset:
        tithi_str = f"{tname1} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
    else:
        tithi_str = f"{tname1} from {sunrise.strftime('%I:%M %p')} to {tdt.strftime('%I:%M %p')}, {tname2} from {tdt.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
    st.markdown(f"<b style='color:#0066cc'>🔷 Tithis b/w Sunrise & Sunset:</b> {tithi_str}", unsafe_allow_html=True)

    # Nakshatra
    nname1, ndt = parse_transition(selected_day.iloc[0]['Nakshatra'], next_day.iloc[0]['Nakshatra'])
    nname2 = str(next_day.iloc[0]['Nakshatra']).split(' ')[0]
    if ndt is None:
        nak_str = nname1
    elif ndt <= sunrise:
        nak_str = f"{nname2} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
    elif ndt > sunset:
        nak_str = f"{nname1} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
    else:
        nak_str = f"{nname1} from {sunrise.strftime('%I:%M %p')} to {ndt.strftime('%I:%M %p')}, {nname2} after {ndt.strftime('%I:%M %p')}"
    st.markdown(f"<b style='color:#ffaa00'>🌟 Nakshatras b/w Sunrise & Sunset:</b> {nak_str}", unsafe_allow_html=True)

    # Yogam
    yname1, ydt = parse_transition(selected_day.iloc[0]['Yogam'], next_day.iloc[0]['Yogam'])
    yname2 = str(next_day.iloc[0]['Yogam']).split(' ')[0]
    if ydt is None:
        yogam_str = yname1
    elif ydt <= sunrise:
        yogam_str = f"{yname2} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
    elif ydt > sunset:
        yogam_str = f"{yname1} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}"
    else:
        yogam_str = f"{yname1} from {sunrise.strftime('%I:%M %p')} to {ydt.strftime('%I:%M %p')}, {yname2} after {ydt.strftime('%I:%M %p')}"
    st.markdown(f"<b style='color:#228B22'>🧘 Yogam b/w Sunrise & Sunset:</b> {yogam_str}", unsafe_allow_html=True)

    # Guidance Image
    st.image("https://raw.githubusercontent.com/pthiyaga1/KshourakarmaNirdeshavali/main/image.png", use_container_width=True)

else:
    st.warning("Date not available in data.")
