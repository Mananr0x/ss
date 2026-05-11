import streamlit as st
import pandas as pd
import plotly.express as px
from google.cloud import bigquery
from streamlit_autorefresh import st_autorefresh
import os

# --- Configuration ---
st.set_page_config(
    page_title="Smart Sand IoT Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh every 2 seconds (2000 ms)
count = st_autorefresh(interval=2000, limit=None, key="datarefresh")

# --- BigQuery Setup ---
PROJECT_ID = "smart-sand-project"
DATASET_ID = "sand_data"
TABLE_ID = "reading"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "service-account-key.json")

if not os.path.exists(SERVICE_ACCOUNT_FILE):
    st.error(
        f"ملف الاعتماد غير موجود: {SERVICE_ACCOUNT_FILE}\n"
        f"نزل ملف Service Account Key (JSON) من Google Cloud Console وحطه في نفس المجلد."
    )
    st.stop()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE

def init_bigquery_client():
    """Initialize BigQuery client."""
    try:
        client = bigquery.Client(project=PROJECT_ID)
        return client
    except Exception as e:
        st.error(f"Failed to initialize BigQuery client: {e}")
        return None

def fetch_sensor_data(client):
    """Fetch latest sensor readings from BigQuery."""
    query = f"SELECT temperature, voltage, timestamp FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}` ORDER BY timestamp DESC LIMIT 100"
    try:
        df = client.query(query).to_dataframe()
        if not df.empty and 'timestamp' in df.columns:
            df['event_time'] = pd.to_datetime(df['timestamp'], unit='s')
        return df
    except Exception as e:
        st.error(f"Error fetching data from BigQuery: {e}")
        return pd.DataFrame()

# --- Main Dashboard ---
def main():
    st.title("🏭 Smart Sand Real-Time IoT Dashboard")
    st.markdown("Monitoring temperature and voltage readings from Arduino sensors")
    
    # Initialize BigQuery client
    client = init_bigquery_client()
    if client is None:
        st.stop()
    
    # Fetch data
    df = fetch_sensor_data()
    
    if df.empty:
        st.warning("No data available. Please ensure:")
        st.markdown("1. Arduino sensor is connected and sending data")
        st.markdown("2. Bridge script (`bridge.py`) is running")
        st.markdown("3. Google Cloud credentials are configured")
        return
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    latest = df.iloc[0]
    
    with col1:
        st.metric(
            label="🌡️ Temperature (°C)",
            value=f"{latest['temperature']:.2f}",
            delta=f"{((latest['temperature'] - df.iloc[1]['temperature']) if len(df) > 1 else 0):.2f}°C"
        )
    
    with col2:
        st.metric(
            label="⚡ Voltage (V)",
            value=f"{latest['voltage']:.2f} V",
            delta=f"{((latest['voltage'] - df.iloc[1]['voltage']) if len(df) > 1 else 0):.2f} V"
        )
    
    with col3:
        st.metric(
            label="📊 Readings Count",
            value=len(df),
            delta="Last updated: just now"
        )
    
    # Charts
    st.subheader("📈 Real-Time Trends")
    
    # Temperature chart
    fig_temp = px.line(
        df, 
        x='event_time', 
        y='temperature',
        title='Temperature Over Time',
        labels={'event_time': 'Time', 'temperature': 'Temperature (°C)'},
        template='plotly_dark'
    )
    fig_temp.update_traces(line_color='#FF9800')
    st.plotly_chart(fig_temp, use_container_width=True)
    
    # Energy chart
    fig_voltage = px.line(
        df, 
        x='event_time', 
        y='voltage',
        title='Voltage Over Time',
        labels={'event_time': 'Time', 'voltage': 'Voltage (V)'},
        template='plotly_dark'
    )
    fig_voltage.update_traces(line_color='#4CAF50')
    st.plotly_chart(fig_voltage, use_container_width=True)
    
    # Data table
    st.subheader("📋 Recent Sensor Readings")
    st.dataframe(
        df[['event_time', 'temperature', 'voltage']]
        .rename(columns={'event_time': 'Timestamp', 'temperature': 'Temperature (°C)', 'voltage': 'Voltage (V)'}),
        use_container_width=True,
        hide_index=True
    )

if __name__ == "__main__":
    main()