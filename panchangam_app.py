import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Constants ---
NAKSHATRAS = [
    "Ashvini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Aardra", "Punarvasu",
    "Pushya", "Aslesha", "Magha", "P. Phalguni or Purva", "U. Phalguni or Uttara",
    "Hasta", "Chitra", "Svaati", "Vishaakha", "Anuraadha", "Jyeshtha", "Mula",
    "P.shadha", "U.shada", "Shravana", "Dhanishta", "Shatabhisha",
    "P. Bhadrapada", "U. Bhadrapada", "Revati"
]

ALLOWED_DAYS = ["Monday", "Wednesday", "Friday"]
ALLOWED_NAKSHATRAS = [
    "Ashwini", "Mrigasheersham", "Punarvasu", "Pushyam", "Hastam", "Chitra",
    "Swati", "Jyeshta", "Shravana", "Dhanishta", "Shatabhishak", "Revati"
]
DISALLOWED_TITHIS = [
    "Prathama", "Chaturthi", "Shashti", "Navami", "Chaturdashi", "Poornima",
    "Amavasya"
]
DISALLOWED_YOGAS = ["Vyatheetapam", "Vaidhriti"]

# --- Helper Functions ---
def parse_transition(row, col_name, sunrise, sunset, next_day_str, next_row):
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

def is_haircut_allowed(day, tithi_text, nakshatra_text, yogam_text, janma_nakshatra):
    reasons = []

    if day not in ALLOWED_DAYS:
        reasons.append(f"Haircut not allowed on {day}.")

    if any(tithi in tithi_text for tithi in DISALLOWED_TITHIS):
        reasons.append("Tithi not suitable for haircut.")

    if any(nakshatra not in ALLOWED_NAKSHATRAS and nakshatra != "N/A" for nakshatra in [nakshatra_text]):
        reasons.append("Nakshatra not suitable for haircut.")

    if any(yoga in yogam_text for yoga in DISALLOWED_YOGAS):
        reasons.append("Yogam not suitable for haircut.")

    if janma_nakshatra.lower() in nakshatra_text.lower():
        reasons.append("Your Janma Nakshatra matches today's Nakshatra.")

    return reasons

# --- Streamlit App ---
st.set_page_config(page_title="Kshoura Karma Haircut Guide", layout="centered")
st.title("💇‍♂️ Kshoura Karma Haircut Date Guide")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/pthiyaga1/KshourakarmaNirdeshavali/main/Panchangam_April-June_2025_filled_full.csv"
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# Inputs
janma_nakshatra = st.selectbox("Select your Janma Nakshatra", NAKSHATRAS)
date_selected = st.date_input("When are you planning a haircut?", min_value=df['Date'].min(), max_value=df['Date'].max())
today_row = df[df['Date'] == pd.to_datetime(date_selected)]
next_row = df[df['Date'] == pd.to_datetime(date_selected) + timedelta(days=1)]

if not today_row.empty and not next_row.empty:
    today_row = today_row.iloc[0]
    next_row = next_row.iloc[0]
    day = today_row['Day']
    st.success(f"📅 {day}, {date_selected.strftime('%B %d, %Y')}")

    sunrise = datetime.strptime(today_row['Sunrise'], "%H:%M:%S")
    sunset = datetime.strptime(today_row['Sunset'], "%H:%M:%S")
    next_day_str = (pd.to_datetime(date_selected) + timedelta(days=1)).strftime('%m/%d/%Y')

    tithi = parse_transition(today_row, 'Tithi', sunrise, sunset, next_day_str, next_row)
    nakshatra = parse_transition(today_row, 'Nakshatra', sunrise, sunset, next_day_str, next_row)
    yogam = parse_transition(today_row, 'Yogam', sunrise, sunset, next_day_str, next_row)

    st.markdown(f"<b style='color:#0066cc'>🔷 Tithi:</b> {'; '.join(tithi)}", unsafe_allow_html=True)
    st.markdown(f"<b style='color:#ffaa00'>🌟 Nakshatra:</b> {'; '.join(nakshatra)}", unsafe_allow_html=True)
    st.markdown(f"<b style='color:#228B22'>🙏 Yogam:</b> {'; '.join(yogam)}", unsafe_allow_html=True)

    # Decision logic
    reasons = is_haircut_allowed(day, ' '.join(tithi), ' '.join(nakshatra), ' '.join(yogam), janma_nakshatra)

    if not reasons:
        st.success("✅ You can proceed with haircut on this date.")
    else:
        st.error("❌ Not a suitable date for haircut due to:")
        for reason in reasons:
            st.write(f"- {reason}")

        # Suggest 2 nearest good dates
        st.subheader("🔍 Next Best Haircut Dates:")
        valid_dates = []
        for offset in range(1, 30):
            check_date = pd.to_datetime(date_selected) + timedelta(days=offset)
            check_row = df[df['Date'] == check_date]
            next_r = df[df['Date'] == check_date + timedelta(days=1)]
            if not check_row.empty and not next_r.empty:
                check_row = check_row.iloc[0]
                next_r = next_r.iloc[0]
                t = parse_transition(check_row, 'Tithi', sunrise, sunset, next_day_str, next_r)
                n = parse_transition(check_row, 'Nakshatra', sunrise, sunset, next_day_str, next_r)
                y = parse_transition(check_row, 'Yogam', sunrise, sunset, next_day_str, next_r)
                r = is_haircut_allowed(check_row['Day'], ' '.join(t), ' '.join(n), ' '.join(y), janma_nakshatra)
                if not r:
                    valid_dates.append(check_date.strftime('%A, %B %d, %Y'))
            if len(valid_dates) >= 2:
                break
        if valid_dates:
            for d in valid_dates:
                st.write(f"✅ {d}")
        else:
            st.write("No suitable dates found in next 30 days.")

    st.image("https://raw.githubusercontent.com/pthiyaga1/KshourakarmaNirdeshavali/main/image.png", use_container_width=True)
else:
    st.warning("The date you selected is not available in the Panchangam data.")
