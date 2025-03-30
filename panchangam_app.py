import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Title & Subtitle
st.title("🔧 Kshoura Karma Nirdeshavali - Haircut Date Checker - Rev07")
st.subheader("📍 Portland, OR")

# Load data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/pthiyaga1/KshourakarmaNirdeshavali/main/Panchangam_April-June_2025_filled_full.csv"
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# Janma Nakshatra list
nakshatras_list = [
    "Ashvini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Aardra", "Punarvasu", "Pushya", "Aslesha", "Magha",
    "P. Phalguni or Purva", "U. Phalguni or Uttara", "Hasta", "Chitra", "Svaati", "Vishaakha", "Anuraadha", "Jyeshtha",
    "Mula", "P.shadha", "U.shada", "Shravana", "Dhanishta", "Shatabhisha", "P. Bhadrapada", "U. Bhadrapada", "Revati"
]

# User inputs
selected_date = st.date_input("Select the date you're considering for haircut", min_value=df['Date'].min(), max_value=df['Date'].max())
janma_nakshatra = st.selectbox("Select your Janma Nakshatra", nakshatras_list)

# Helper function to parse tithi/nakshatra/yogam with time

def parse_transition(data_str, fallback_str):
    if pd.isna(data_str):
        return fallback_str
    if "full night" in data_str:
        return data_str
    if ' ' not in data_str:
        return data_str
    try:
        name, time = data_str.split(' ')
        hour, minute, second = map(int, time.split(":"))
        if hour >= 24:
            dt = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(days=1, hours=hour-24, minutes=minute, seconds=second)
        else:
            dt = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(hours=hour, minutes=minute, seconds=second)
        return (name, dt.time())
    except:
        return fallback_str

# Function to check haircut rules
def is_good_haircut_day(row, janma_nakshatra):
    reasons = []
    good = True

    # Weekday check
    weekday = row['Day']
    if weekday in ["Sunday", "Tuesday", "Saturday"]:
        good = False
        reasons.append(f"Avoid haircut on {weekday}s")

    # Tithi check
    banned_tithis = ["Prathama", "Chaturthi", "Shashti", "Navami", "Chaturdashi", "Poornima", "Amavasya"]
    tithi = str(row['Tithi']).split(" ")[0]
    if tithi in banned_tithis:
        good = False
        reasons.append(f"Tithi '{tithi}' is not allowed for haircut")

    # Nakshatra check
    allowed_nakshatras = ["Ashwini", "Mrigasheersham", "Punarvasu", "Pushyam", "Hastam", "Chitra", "Swati", "Jyestha", "Shravana", "Dhanishta", "Shatabhishak", "Revati"]
    nak = str(row['Nakshatra']).split(" ")[0]
    if nak not in allowed_nakshatras:
        good = False
        reasons.append(f"Nakshatra '{nak}' is not among allowed nakshatras")

    # Janma nakshatra match check
    if janma_nakshatra in str(row['Nakshatra']):
        good = False
        reasons.append(f"Avoid haircut on your Janma Nakshatra: {janma_nakshatra}")

    # Yogam check
    banned_yogas = ["Vyatipata", "Vaidhriti"]
    yoga = str(row['Yogam']).split(" ")[0]
    if yoga in banned_yogas:
        good = False
        reasons.append(f"Yogam '{yoga}' is not allowed")

    return good, reasons

# Display Panchangam for selected date
st.markdown("### 🗌 Panchangam Lookup for Selected Date")
today_row = df[df['Date'] == pd.to_datetime(selected_date)]
next_day_row = df[df['Date'] == pd.to_datetime(selected_date) + timedelta(days=1)]

if not today_row.empty and not next_day_row.empty:
    today = today_row.iloc[0]
    next_day = next_day_row.iloc[0]
    sunrise = datetime.strptime(today['Sunrise'], "%H:%M:%S").time()
    sunset = datetime.strptime(today['Sunset'], "%H:%M:%S").time()

    tithi_data = parse_transition(today['Tithi'], next_day['Tithi'])
    nakshatra_data = parse_transition(today['Nakshatra'], next_day['Nakshatra'])
    yogam_data = parse_transition(today['Yogam'], next_day['Yogam'])

    if isinstance(tithi_data, tuple):
        tithi_str = f"{tithi_data[0]} till {tithi_data[1].strftime('%I:%M %p')}"
    else:
        tithi_str = tithi_data

    if isinstance(nakshatra_data, tuple):
        nakshatra_str = f"{nakshatra_data[0]} till {nakshatra_data[1].strftime('%I:%M %p')}"
    else:
        nakshatra_str = nakshatra_data

    if isinstance(yogam_data, tuple):
        yogam_str = f"{yogam_data[0]} till {yogam_data[1].strftime('%I:%M %p')}"
    else:
        yogam_str = yogam_data

    st.write(f"\n\n\U0001f4c6 **{today['Day']}, {selected_date.strftime('%B %d, %Y')}**")
    st.markdown(f"<b style='color:#0066cc'>\U0001f537 Tithi:</b> {tithi_str}", unsafe_allow_html=True)
    st.markdown(f"<b style='color:#ffaa00'>\U0001f31f Nakshatra:</b> {nakshatra_str}", unsafe_allow_html=True)
    st.markdown(f"<b style='color:#228B22'>\U0001f9d8 Yogam:</b> {yogam_str}", unsafe_allow_html=True)

    good, reasons = is_good_haircut_day(today, janma_nakshatra)
    if good:
        st.success("\n\n✅ You can proceed with haircut on this date.")
    else:
        st.error("\n\n❌ Not a good day for haircut due to following reasons:")
        for r in reasons:
            st.markdown(f"- {r}")

        # Suggest next 2 good days
        st.info("\n\n✉ Suggesting next 2 good days:")
        future = df[df['Date'] > pd.to_datetime(selected_date)]
        found = 0
        for _, row in future.iterrows():
            ok, _ = is_good_haircut_day(row, janma_nakshatra)
            if ok:
                st.markdown(f"- **{row['Day']}, {row['Date'].strftime('%B %d, %Y')}**")
                found += 1
            if found == 2:
                break

# Show guidance image
st.image("https://raw.githubusercontent.com/pthiyaga1/KshourakarmaNirdeshavali/main/image.png", use_container_width=True)
