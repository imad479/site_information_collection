import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io
from requests.auth import HTTPBasicAuth

# --- KOBO CONFIG ---
username = "imad479"
password = "1m@dL2dh1@1234"
form_uids = [
    "a93k5tBLafPoXgCessToMp",
    "azNkMX2aQEcLkRfrtZen9w",
    "awsrgDXSJeyN6GDn8U2Qmm",
    "abTW6BtavKXD9ekXbeMhav",
    "apU47ShsSjs2owJKF4286M"
]

@st.cache_data(ttl=3600)
def load_data():
    all_data = []
    for uid in form_uids:
        api_url = f"https://kf.kobotoolbox.org/api/v2/assets/{uid}/data.json"
        response = requests.get(api_url, auth=HTTPBasicAuth(username, password))
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                all_data.append(pd.DataFrame(results))
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame()

# --- SIDEBAR FILTERS ---
st.sidebar.title("🔍 Filters")
df = load_data()

if df.empty:
    st.warning("No data found from any form.")
    st.stop()

# Filter dropdowns
user_column = "username"
district_column = "_1_1_Name_of_the_City_"

usernames = df[user_column].dropna().unique()
districts = df[district_column].dropna().unique()

selected_user = st.sidebar.selectbox("Select Username", options=['All'] + sorted(usernames))
selected_district = st.sidebar.selectbox("Select District", options=['All'] + sorted(districts))

# Apply filters
if selected_user != 'All':
    df = df[df[user_column] == selected_user]
if selected_district != 'All':
    df = df[df[district_column] == selected_district]

st.sidebar.markdown(f"### Total Rows: {len(df)}")

# --- MAIN DASHBOARD ---
st.title("📊 Site Information Collection (Live Dashboard)")
st.write("Filtered Dataset:")
st.dataframe(df, use_container_width=True)

# --- STATS ---
st.markdown("### 📈 Summary Statistics")
st.write(df.describe(include='all'))

# --- VISUALIZATION ---
st.markdown("### 📊 Visualizations")
col_x = st.selectbox("Select X-axis column", df.columns)
numeric_cols = df.select_dtypes(include='number').columns
col_y = st.selectbox("Select Y-axis column (numeric)", numeric_cols if not numeric_cols.empty else [None])

chart_type = st.selectbox("Select Chart Type", ["Bar", "Pie", "Histogram"])

if chart_type == "Bar" and col_y:
    fig = px.bar(df, x=col_x, y=col_y, title="Bar Chart")
    st.plotly_chart(fig, use_container_width=True)
elif chart_type == "Pie":
    fig = px.pie(df, names=col_x, title="Pie Chart")
    st.plotly_chart(fig, use_container_width=True)
elif chart_type == "Histogram" and col_y:
    fig = px.histogram(df, x=col_y, title="Histogram")
    st.plotly_chart(fig, use_container_width=True)

# --- DATA DOWNLOAD ---
st.markdown("### 📥 Download Filtered Data")
col1, col2 = st.columns(2)

csv = df.to_csv(index=False).encode('utf-8')
excel_io = io.BytesIO()
df.to_excel(excel_io, index=False, engine='openpyxl')

col1.download_button("Download CSV", csv, "filtered_data.csv", "text/csv")
col2.download_button("Download Excel", excel_io.getvalue(), "filtered_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.success("✅ Dashboard loaded successfully.")
