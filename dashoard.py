import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Smart Sand Pro Dashboard", layout="wide")

# --- 2. التنسيق الجمالي (الأسود والبرتقالي مثل صورة أمازون) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    div[data-testid="stMetric"] {
        background-color: #1A1C23;
        border: 1px solid #F39C12;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    [data-testid="stMetricValue"] { color: #F39C12 !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #BBBBBB !important; }
    h1, h2, h3 { color: #F39C12 !important; }
    .stDataFrame { background-color: #1A1C23; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. توليد بيانات وهمية (بدل الكلاود) ---
def fetch_dummy_data():
    # توليد 50 قراءة وهمية لآخر 50 دقيقة
    now = datetime.now()
    times = [now - timedelta(minutes=i) for i in range(50)]
    
    # بيانات عشوائية للحرارة والجهد تشبه قراءات الحساسات
    temps = np.random.uniform(25, 45, 50)
    voltages = np.random.uniform(1.5, 4.8, 50)
    
    df = pd.DataFrame({
        'timestamp': times,
        'temperature': temps,
        'voltage': voltages
    })
    return df

# جلب البيانات الوهمية
df = fetch_dummy_data()

# --- 4. عرض الواجهة ---
if not df.empty:
    # الهيدر العلوي
    st.title("🟠 SMART SAND REAL-TIME DASHBOARD (Simulation)")
    st.markdown("---")

    # الصف العلوي: البطاقات (المقاييس)
    m1, m2, m3, m4 = st.columns(4)
    latest = df.iloc[0] # القراءة الحالية
    
    m1.metric("TEMP (الحرارة)", f"{latest['temperature']:.1f}°C", "↑ 1.2%")
    m2.metric("VOLTAGE (الجهد)", f"{latest['voltage']:.2f}V", "↑ 0.5%")
    
    # كفاءة وهمية
    eff = round((latest['voltage'] / 5) * 100, 1)
    m3.metric("EFFICIENCY (الكفاءة)", f"{eff}%", "stable")
    m4.metric("STATUS (الحالة)", "SIMULATED", "Active")

    st.markdown("###")

    # الصف الثاني: الرسوم البيانية
    col1, col2 = st.columns([2, 1])

    with col1:
        # رسم بياني للحرارة والجهد
        fig_line = px.line(df, x='timestamp', y=['temperature', 'voltage'], 
                           title="Thermal & Energy Real-time Trend",
                           template="plotly_dark",
                           color_discrete_map={"temperature": "#F39C12", "voltage": "#3498db"})
        
        # تحسين شكل الخطوط
        fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        # رسم دائري لتوزيع كفاءة النظام
        fig_donut = go.Figure(data=[go.Pie(labels=['Produced', 'Storage', 'Loss'], 
                                         values=[eff, 100-eff-5, 5], hole=.6)])
        fig_donut.update_traces(marker=dict(colors=['#F39C12', '#D35400', '#2C3E50']))
        fig_donut.update_layout(template="plotly_dark", title="Power Distribution", showlegend=False)
        st.plotly_chart(fig_donut, use_container_width=True)

    # جدول البيانات في الأسفل
    st.subheader("📋 سجل البيانات الحالي (Simulated Data)")
    st.dataframe(df.head(10), use_container_width=True)

    # تذييل بسيط
    st.markdown("---")
    st.caption("Note: This dashboard is currently running in Simulation Mode with dummy data.")
