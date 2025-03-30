import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

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
        time = time.replace('+', '')  # remove plus sign
        try:
            hours, minutes, seconds = map(int, time.split(':'))
            if hours >= 24:
                hours -= 24
                dt = datetime.strptime(f"{hours}:{minutes}:{seconds}", "%H:%M:%S") + timedelta(days=1)
            else:
                dt = datetime.strptime(time, "%H:%M:%S")
            results.append(f"{name} till {dt.strftime('%I:%M:%S %p')} on {next_day_str}")
        except ValueError:
            results.append(f"{name} timing unavailable")
    elif ' ' in value:
        name, time = value.split(' ')
        try:
            dt = datetime.strptime(time, "%H:%M:%S")
            if dt <= sunrise:
                next_value = next_row[col_name]
                results.append(f"{next_value} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}")
            elif dt > sunset:
                results.append(f"{name} from {sunrise.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}")
            else:
                next_value = next_row[col_name].split(' ')[0] if ' ' in next_row[col_name] else next_row[col_name]
                results.append(f"{name} from {sunrise.strftime('%I:%M %p')} to {dt.strftime('%I:%M %p')}, {next_value} from {dt.strftime('%I:%M %p')} to {sunset.strftime('%I:%M %p')}")
        except ValueError:
            results.append(f"{name} timing format error")
    return results

# --- Streamlit App ---
st.set_page_config(page_title="Kshoura Karma Panchangam Tool", layout="centered")
st.title("✂️ Kshoura Karma Nirdeshavali - Haircut Date Checker - Rev08")

# Load Data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/pthiyaga1/KshourakarmaNirdeshavali/main/Panchangam_April-June_2025_filled_full.csv"
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

janma_nakshatras = [
    "Ashvini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Aardra", "Punarvasu", "Pushya", "Aslesha",
    "Magha", "P. Phalguni or Purva", "U. Phalguni or Uttara", "Hasta", "Chitra", "Svaati", "Vishaakha",
    "Anuraadha", "Jyeshtha", "Mula", "P.shadha", "U.shada", "Shravana", "Dhanishta", "Shatabhisha",
    "P. Bhadrapada", "U. Bhadrapada", "Revati"
]

st.subheader("🔍 Select details for haircut evaluation")
selected_date = st.date_input("Select the date you're considering for haircut", min_value=df['Date'].min(), max_value=df['Date'].max())
user_nakshatra = st.selectbox("Select your Janma Nakshatra", janma_nakshatras)

check_row = df[df['Date'] == pd.to_datetime(selected_date)]
next_row = df[df['Date'] == pd.to_datetime(selected_date) + timedelta(days=1)]

if not check_row.empty and not next_row.empty:
    check_row = check_row.iloc[0]
    next_r = next_row.iloc[0]
    day = check_row['Day']
    sunrise = datetime.strptime(check_row['Sunrise'], "%H:%M:%S")
    sunset = datetime.strptime(check_row['Sunset'], "%H:%M:%S")
    next_day_str = (pd.to_datetime(selected_date) + timedelta(days=1)).strftime('%m/%d/%Y')

    st.markdown(f"### 🗓️ Panchangam Lookup for Selected Date")
    st.success(f"📅 {day}, {selected_date.strftime('%B %d, %Y')}")

    t = parse_transition(check_row, 'Tithi', sunrise, sunset, next_day_str, next_r)
    n = parse_transition(check_row, 'Nakshatra', sunrise, sunset, next_day_str, next_r)
    y = parse_transition(check_row, 'Yogam', sunrise, sunset, next_day_str, next_r)

    st.markdown(f"<b style='color:#0066cc'>🔷 Tithi:</b> {'; '.join(t)}", unsafe_allow_html=True)
    st.markdown(f"<b style='color:#ffaa00'>🌟 Nakshatra:</b> {'; '.join(n)}", unsafe_allow_html=True)
    st.markdown(f"<b style='color:#228B22'>🧘 Yogam:</b> {'; '.join(y)}", unsafe_allow_html=True)

    # --- Haircut Check Logic ---
    issues = []

    if day in ["Sunday", "Tuesday", "Saturday"]:
        issues.append(f"Haircut not allowed on {day}s.")
    if any(x.split()[0] in ["Prathama", "Chaturthi", "Shashti", "Navami", "Chaturdashi", "Poornima", "Amavasya"] for x in t):
        issues.append("Tithi not suitable for haircut.")
    if not any(x.split()[0] in ["Ashwini", "Mrigashirsha", "Punarvasu", "Pushya", "Hastam", "Chitra", "Swati", "Jyeshtha", "Shravana", "Dhanishta", "Shatabhishak", "Revati"] for x in n):
        issues.append("Nakshatra is not allowed.")
    if any(x.split()[0] in ["Vyatheepatham", "Vaidhriti"] for x in y):
        issues.append("Yogam not allowed for haircut.")
    if any(user_nakshatra.split()[0] in x for x in n):
        issues.append("Today is your Janma Nakshatra. Avoid haircut.")

    if not issues:
        st.success("✅ You can proceed with haircut on this date.")
    else:
        st.error("❌ Haircut not recommended on this date for the following reasons:")
        for issue in issues:
            st.markdown(f"- {issue}")

    # Suggest 2 future good dates
    st.markdown("### 📆 Next Good Haircut Dates")
    future_dates = df[df['Date'] > pd.to_datetime(selected_date)].copy()
    future_dates = future_dates.reset_index(drop=True)

    valid_days = []
    for i in range(len(future_dates)-1):
        row = future_dates.iloc[i]
        next_r = future_dates.iloc[i+1]
        sun = datetime.strptime(row['Sunrise'], "%H:%M:%S")
        sst = datetime.strptime(row['Sunset'], "%H:%M:%S")
        dt = row['Date']
        next_str = (dt + timedelta(days=1)).strftime('%m/%d/%Y')

        t = parse_transition(row, 'Tithi', sun, sst, next_str, next_r)
        n = parse_transition(row, 'Nakshatra', sun, sst, next_str, next_r)
        y = parse_transition(row, 'Yogam', sun, sst, next_str, next_r)

        day = row['Day']
        reasons = []
        if day in ["Sunday", "Tuesday", "Saturday"]:
            reasons.append("bad weekday")
        if any(x.split()[0] in ["Prathama", "Chaturthi", "Shashti", "Navami", "Chaturdashi", "Poornima", "Amavasya"] for x in t):
            reasons.append("bad tithi")
        if not any(x.split()[0] in ["Ashwini", "Mrigashirsha", "Punarvasu", "Pushya", "Hastam", "Chitra", "Swati", "Jyeshtha", "Shravana", "Dhanishta", "Shatabhishak", "Revati"] for x in n):
            reasons.append("bad nakshatra")
        if any(x.split()[0] in ["Vyatheepatham", "Vaidhriti"] for x in y):
            reasons.append("bad yogam")
        if any(user_nakshatra.split()[0] in x for x in n):
            reasons.append("janma match")

        if not reasons:
            valid_days.append((dt.strftime('%A %B %d, %Y'), t, n, y))
        if len(valid_days) >= 2:
            break

    if valid_days:
        for i, (d, t, n, y) in enumerate(valid_days):
            st.markdown(f"**{i+1}. {d}**")
            st.markdown(f"🔷 Tithi: {'; '.join(t)}")
            st.markdown(f"🌟 Nakshatra: {'; '.join(n)}")
            st.markdown(f"🧘 Yogam: {'; '.join(y)}")
    else:
        st.info("No suitable dates found in the immediate future.")

    st.image("https://raw.githubusercontent.com/pthiyaga1/KshourakarmaNirdeshavali/main/image.png", use_container_width=True)
else:
    st.warning("The date you selected is not available in the Panchangam data.")
