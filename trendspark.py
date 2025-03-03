import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pandas as pd
import io
import requests
import json
from prophet import Prophet
import uuid
import arabic_reshaper
from bidi.algorithm import get_display

# إعداد الصفحة بتصميم عصري
st.set_page_config(
    page_title="TrendSpark™ - Ignite Your Trends",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS جذاب وعصري
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700;900&display=swap');
    
    * {font-family: 'Roboto', sans-serif;}
    
    .main {
        background: linear-gradient(135deg, #2D1B4E, #5B3A8C);
        color: #F9E6FF;
        padding: 40px;
        border-radius: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.6);
    }
    
    h1, h2, h3 {
        background: linear-gradient(90deg, #FF4D80, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        letter-spacing: -1px;
        text-shadow: 0 2px 10px rgba(255,77,128,0.5);
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #FF4D80, #FFAA00);
        color: #FFFFFF;
        border-radius: 50px;
        font-weight: 700;
        padding: 15px 35px;
        font-size: 18px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: none;
        box-shadow: 0 8px 20px rgba(255,77,128,0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 12px 30px rgba(255,170,0,0.7);
    }
    
    .stTextInput>div>div>input {
        background: rgba(255,255,255,0.1);
        border: 2px solid #FF4D80;
        border-radius: 15px;
        color: #FFD700;
        font-weight: bold;
        padding: 15px;
        font-size: 18px;
        box-shadow: 0 5px 15px rgba(255,77,128,0.3);
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #FFD700;
        box-shadow: 0 5px 20px rgba(255,215,0,0.5);
    }
    
    .stSelectbox>label, .stRadio>label {
        color: #FFD700;
        font-size: 24px;
        font-weight: 600;
        text-shadow: 1px 1px 5px rgba(0,0,0,0.5);
    }
    
    .stSelectbox>div>div>button {
        background: rgba(255,255,255,0.1);
        border: 2px solid #FF4D80;
        border-radius: 15px;
        color: #F9E6FF;
        padding: 15px;
        font-size: 18px;
    }
    
    .stRadio>div {
        background: rgba(255,255,255,0.05);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.4);
    }
    
    .stMarkdown {
        color: #E2D1F9;
        font-size: 18px;
        line-height: 1.6;
    }
    
    .share-btn {
        background: linear-gradient(90deg, #00DDEB, #00FF85);
        color: #FFFFFF;
        border-radius: 50px;
        padding: 12px 25px;
        text-decoration: none;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,221,235,0.4);
        font-size: 16px;
    }
    
    .share-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0,255,133,0.6);
    }
    
    .animate-in {
        animation: fadeInUp 1s forwards;
        opacity: 0;
    }
    
    @keyframes fadeInUp {
        from {opacity: 0; transform: translateY(20px);}
        to {opacity: 1; transform: translateY(0);}
    }
    </style>
""", unsafe_allow_html=True)

# تعريف الحالة الافتراضية
if "language" not in st.session_state:
    st.session_state["language"] = "English"
if "payment_verified" not in st.session_state:
    st.session_state["payment_verified"] = False
if "payment_initiated" not in st.session_state:
    st.session_state["payment_initiated"] = False
if "trend_data" not in st.session_state:
    st.session_state["trend_data"] = None

# العنوان والترحيب
st.markdown("""
    <h1 style='font-size: 60px; text-align: center; animation: fadeInUp 1s forwards;'>TrendSpark™</h1>
    <p style='font-size: 24px; text-align: center; animation: fadeInUp 1s forwards; animation-delay: 0.2s;'>
        Ignite Your Future with Hot Trends!<br>
        <em>Created by Anas Hani Zewail • Contact: +201024743503</em>
    </p>
""", unsafe_allow_html=True)

# واجهة المستخدم
st.markdown("<h2 style='text-align: center;'>Catch the Next Big Thing</h2>", unsafe_allow_html=True)
trend_topic = st.text_input("Enter Trend Topic (e.g., Fashion 2025):", "Fashion 2025", help="Discover trending insights!")
language = st.selectbox("Select Language:", ["English", "Arabic"])
st.session_state["language"] = language
plan = st.radio("Choose Your Spark:", ["Trend Alert (Free)", "Spark Starter ($3)", "Trend Pro ($8)", "Trend Master ($15)", "VIP Monthly ($25/month)"])
st.markdown("""
    <p style='text-align: center;'>
        <strong>Trend Alert (Free):</strong> Quick Trend Peek<br>
        <strong>Spark Starter ($3):</strong> Basic Trend Report<br>
        <strong>Trend Pro ($8):</strong> Full Report + 7-Day Forecast<br>
        <strong>Trend Master ($15):</strong> Advanced Insights + Tips<br>
        <strong>VIP Monthly ($25/month):</strong> Daily Trends + Alerts
    </p>
""", unsafe_allow_html=True)

# بيانات PayPal Sandbox
PAYPAL_CLIENT_ID = "AQd5IZObL6YTejqYpN0LxADLMtqbeal1ahbgNNrDfFLcKzMl6goF9BihgMw2tYnb4suhUfprhI-Z8eoC"
PAYPAL_SECRET = "EPk46EBw3Xm2W-R0Uua8sLsoDLJytgSXqIzYLbbXCk_zSOkdzFx8jEbKbKxhjf07cnJId8gt6INzm6_V"
PAYPAL_API = "https://api-m.sandbox.paypal.com"

# دوال PayPal
def get_paypal_access_token():
    try:
        url = f"{PAYPAL_API}/v1/oauth2/token"
        headers = {"Accept": "application/json", "Accept-Language": "en_US"}
        data = {"grant_type": "client_credentials"}
        response = requests.post(url, headers=headers, auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET), data=data)
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        st.error(f"Failed to connect to PayPal: {e}")
        return None

def create_payment(access_token, amount, description):
    try:
        url = f"{PAYPAL_API}/v1/payments/payment"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
        payment_data = {
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "transactions": [{"amount": {"total": amount, "currency": "USD"}, "description": description}],
            "redirect_urls": {
                "return_url": "https://smartpulse-nwrkb9xdsnebmnhczyt76s.streamlit.app/?success=true",
                "cancel_url": "https://smartpulse-nwrkb9xdsnebmnhczyt76s.streamlit.app/?cancel=true"
            }
        }
        response = requests.post(url, headers=headers, json=payment_data)
        response.raise_for_status()
        for link in response.json()["links"]:
            if link["rel"] == "approval_url":
                return link["href"]
        st.error("Failed to extract payment URL.")
        return None
    except Exception as e:
        st.error(f"Failed to create payment request: {e}")
        return None

# بيانات وهمية واقعية
sentiment = {"positive": {"strong": 50, "mild": 20}, "negative": {"strong": 10, "mild": 15}, "neutral": 25}
total_mentions = 200
trend_by_day = {
    "2025-02-26_positive": 40, "2025-02-26_negative": 10,
    "2025-02-27_positive": 45, "2025-02-27_negative": 8,
    "2025-02-28_positive": 38, "2025-02-28_negative": 12
}
regions = {"Global": {"positive": 70, "negative": 20, "neutral": 30}}
hot_keywords = [("sustainability", 65), ("minimalism", 45)]

# دوال التحليل
def generate_trend_chart(trend_topic, language, trend_by_day):
    try:
        days = sorted(set(k.split('_')[0] for k in trend_by_day.keys()))
        positive = [trend_by_day.get(f"{day}_positive", 0) for day in days]
        negative = [trend_by_day.get(f"{day}_negative", 0) for day in days]
        plt.figure(figsize=(8, 5))
        plt.plot(days, positive, label="Positive Buzz" if language == "English" else "الضجة الإيجابية", color="#00FF85", linewidth=2.5)
        plt.plot(days, negative, label="Negative Buzz" if language == "English" else "الضجة السلبية", color="#FF4D80", linewidth=2.5)
        plt.title(f"{trend_topic} Trend Buzz", fontsize=18, color="white", pad=20)
        plt.gca().set_facecolor('#2D1B4E')
        plt.gcf().set_facecolor('#2D1B4E')
        plt.legend(fontsize=12, facecolor="#2D1B4E", edgecolor="white", labelcolor="white")
        plt.xticks(color="white", fontsize=10)
        plt.yticks(color="white", fontsize=10)
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches="tight")
        img_buffer.seek(0)
        plt.close()
        return img_buffer
    except Exception as e:
        st.error(f"Failed to generate trend chart: {e}")
        return None

def generate_forecast(trend_topic, language, trend_by_day):
    try:
        days = sorted(set(k.split('_')[0] for k in trend_by_day.keys()))
        total_buzz = [trend_by_day.get(f"{day}_positive", 0) - trend_by_day.get(f"{day}_negative", 0) for day in days]
        df = pd.DataFrame({'ds': days, 'y': total_buzz})
        df['ds'] = pd.to_datetime(df['ds'])
        model = Prophet(daily_seasonality=True)
        model.fit(df)
        future = model.make_future_dataframe(periods=7)
        forecast = model.predict(future)
        plt.figure(figsize=(10, 6))
        plt.plot(df['ds'], df['y'], label="Actual Buzz" if language == "English" else "الضجة الفعلية", color="#00FF85", linewidth=2.5)
        plt.plot(forecast['ds'], forecast['yhat'], label="Forecast" if language == "English" else "التوقعات", color="#FFD700", linewidth=2.5)
        plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color="#FFD700", alpha=0.3)
        plt.title(f"{trend_topic} 7-Day Forecast", fontsize=18, color="white", pad=20)
        plt.gca().set_facecolor('#2D1B4E')
        plt.gcf().set_facecolor('#2D1B4E')
        plt.legend(fontsize=12, facecolor="#2D1B4E", edgecolor="white", labelcolor="white")
        plt.xticks(color="white", fontsize=10)
        plt.yticks(color="white", fontsize=10)
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches="tight")
        img_buffer.seek(0)
        plt.close()
        trend = "Rising" if forecast['yhat'].iloc[-1] > forecast['yhat'].iloc[-8] else "Declining"
        reco = f"Trend: {trend}. Act fast if rising, diversify if declining."
        return img_buffer, reco
    except Exception as e:
        st.error(f"Failed to generate forecast: {e}")
        return None, None

def generate_report(trend_topic, language, regions, hot_keywords, sentiment, trend_by_day, total_mentions, trend_chart_buffer, forecast_chart_buffer=None, plan="Spark Starter"):
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontSize = 12
        style.textColor = colors.black
        style.fontName = "Helvetica"

        report = f"TrendSpark Report: {trend_topic}\n"
        report += "=" * 50 + "\n"
        report += f"Plan: {plan}\n"
        report += f"Total Mentions: {total_mentions}\n"
        if language == "Arabic":
            report = arabic_reshaper.reshape(report)
            report = get_display(report)

        content = [Paragraph(report, style)]
        content.append(Image(trend_chart_buffer, width=400, height=300))
        
        if forecast_chart_buffer and plan in ["Trend Pro ($8)", "Trend Master ($15)", "VIP Monthly ($25/month)"]:
            content.append(Image(forecast_chart_buffer, width=400, height=300))
            content.append(Spacer(1, 20))
        
        if plan in ["Trend Master ($15)", "VIP Monthly ($25/month)"]:
            content.append(Paragraph("Top Keywords: " + ", ".join([f"{k} ({v}%)" for k, v in hot_keywords]), style))
            content.append(Paragraph("Investment Tip: Focus on rising regions like Global (70% Positive).", style))
        
        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Failed to generate report: {e}")
        return None

# تشغيل التطبيق
if st.button("Spark My Trend!", key="spark_trend"):
    with st.spinner("Sparking Your Insights..."):
        trend_chart_buffer = generate_trend_chart(trend_topic, language, trend_by_day)
        if trend_chart_buffer:
            st.session_state["trend_data"] = {"trend_chart": trend_chart_buffer.getvalue()}
            st.image(trend_chart_buffer, caption="Trend Buzz Overview")
            
            share_url = "https://smartpulse-nwrkb9xdsnebmnhczyt76s.streamlit.app/"
            telegram_group = "https://t.me/+K7W_PUVdbGk4MDRk"
            
            st.markdown("<h3 style='text-align: center;'>Spread the Spark!</h3>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<a href="https://api.whatsapp.com/send?text=Try%20TrendSpark:%20{share_url}" target="_blank" class="share-btn">WhatsApp</a>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<a href="https://t.me/share/url?url={share_url}&text=TrendSpark%20is%20fire!" target="_blank" class="share-btn">Telegram</a>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<a href="https://www.facebook.com/sharer/sharer.php?u={share_url}" target="_blank" class="share-btn">Messenger</a>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<a href="https://discord.com/channels/@me?message=Check%20TrendSpark:%20{share_url}" target="_blank" class="share-btn">Discord</a>', unsafe_allow_html=True)
            
            st.markdown(f"<p style='text-align: center;'>Join our Telegram: <a href='{telegram_group}' target='_blank'>Click Here</a> - Invite 3 friends for a FREE report!</p>", unsafe_allow_html=True)
            
            if plan == "Trend Alert (Free)":
                st.info("Upgrade to unlock full reports, forecasts, and tips!")
            else:
                if not st.session_state["payment_verified"] and not st.session_state["payment_initiated"]:
                    access_token = get_paypal_access_token()
                    if access_token:
                        amount = {"Spark Starter ($3)": "3.00", "Trend Pro ($8)": "8.00", "Trend Master ($15)": "15.00", "VIP Monthly ($25/month)": "25.00"}[plan]
                        approval_url = create_payment(access_token, amount, f"TrendSpark {plan}")
                        if approval_url:
                            st.session_state["payment_url"] = approval_url
                            st.session_state["payment_initiated"] = True
                            unique_id = uuid.uuid4()
                            st.markdown(f"""
                                <a href="{approval_url}" target="_blank" id="paypal_auto_link_{unique_id}" style="display:none;">PayPal</a>
                                <script>
                                    setTimeout(function() {{
                                        document.getElementById("paypal_auto_link_{unique_id}").click();
                                    }}, 100);
                                </script>
                            """, unsafe_allow_html=True)
                            st.info(f"Payment window opened for {plan}. Complete it to ignite your insights!")
                elif st.session_state["payment_verified"]:
                    forecast_chart_buffer, reco = generate_forecast(trend_topic, language, trend_by_day) if plan in ["Trend Pro ($8)", "Trend Master ($15)", "VIP Monthly ($25/month)"] else (None, None)
                    if forecast_chart_buffer:
                        st.session_state["trend_data"]["forecast_chart"] = forecast_chart_buffer.getvalue()
                        st.image(forecast_chart_buffer, caption="7-Day Trend Forecast")
                        st.write(reco)
                    
                    trend_chart_buffer = io.BytesIO(st.session_state["trend_data"]["trend_chart"])
                    forecast_chart_buffer = io.BytesIO(st.session_state["trend_data"]["forecast_chart"]) if "forecast_chart" in st.session_state["trend_data"] else None
                    pdf_data = generate_report(trend_topic, language, regions, hot_keywords, sentiment, trend_by_day, total_mentions, trend_chart_buffer, forecast_chart_buffer, plan)
                    if pdf_data:
                        st.download_button(
                            label=f"Download Your {plan.split(' (')[0]} Report",
                            data=pdf_data,
                            file_name=f"{trend_topic}_trendspark_report.pdf",
                            mime="application/pdf",
                            key="download_report"
                        )
                        st.success(f"{plan.split(' (')[0]} Report Ready! Share with friends for more perks!")
