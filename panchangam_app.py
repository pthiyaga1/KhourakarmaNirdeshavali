import streamlit as st
import pandas as pd

st.title("📅 Panchangam Lookup Tool1")
st.subheader("Select a date to find Tithi and Nakshatra")

# 📤 Load the CSV from GitHub or local
@st.cache_data
def load_data():
    # You can replace this URL with your own GitHub raw URL

    url = "https://raw.githubusercontent.com/pthiyaga1/KhourakarmaNirdeshavali/refs/heads/main/Panchangam_April-June_2025_filled_full.csv"
    df = pd.read_csv(url)
    return df

df = load_data()

# Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# 📅 Let user pick a date
selected_date = st.date_input("Pick a date", min_value=df['Date'].min(), max_value=df['Date'].max())

# 🔍 Search for the selected date
result = df[df['Date'] == pd.to_datetime(selected_date)]

# 🧾 Show result
if not result.empty:
    tithi = result.iloc[0].get('Tithi', 'N/A')
    nakshatra = result.iloc[0].get('Nakshatra', 'N/A')

    st.success(f"📆 Date: {selected_date.strftime('%B %d, %Y')}")
    st.write(f"🌀 **Tithi**: {tithi}")
    st.write(f"🌟 **Nakshatra**: {nakshatra}")
else:
    st.warning("This date is not available in the data. Try another one.")
