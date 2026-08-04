"""
maintenance.py - Калькулятор отложен до лучших времен
"""

import streamlit as st
import random
from datetime import datetime

st.set_page_config(
    page_title="Калькулятор отложен",
    page_icon="⏳",
    layout="centered"
)

# ============================================================
# CSS СТИЛИ
# ============================================================

st.markdown("""
<style>
    .main-title {
        font-size: 52px;
        font-weight: 900;
        text-align: center;
        color: #1a5276;
        animation: pulse 2s ease-in-out infinite;
        text-shadow: 0 0 30px rgba(26, 82, 118, 0.15);
    }
    .subtitle {
        font-size: 24px;
        text-align: center;
        color: #2e86c1;
        margin-top: -5px;
        font-weight: 300;
    }
    .icon-big {
        font-size: 80px;
        text-align: center;
        display: block;
        margin: 15px 0;
    }
    .info-box {
        background: rgba(46, 134, 193, 0.05);
        border: 2px dashed #2e86c1;
        border-radius: 15px;
        padding: 30px;
        margin: 25px 0;
        text-align: center;
    }
    .info-box .big-text {
        font-size: 28px;
        font-weight: 600;
        color: #1a5276;
    }
    .info-box .small-text {
        font-size: 16px;
        color: #5d6d7e;
        margin-top: 10px;
    }
    .footer-text {
        text-align: center;
        color: #95a5a6;
        font-size: 13px;
        margin-top: 40px;
        border-top: 1px solid rgba(46,134,193,0.15);
        padding-top: 20px;
        line-height: 1.8;
    }
    .footer-text .company {
        font-size: 15px;
        font-weight: 700;
        color: #1a5276;
        letter-spacing: 0.5px;
    }
    .time-stamp {
        font-size: 14px;
        color: #bdc3c7;
        text-align: center;
        margin-top: 20px;
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.02); opacity: 0.9; }
        100% { transform: scale(1); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# КОНТЕНТ
# ============================================================

st.markdown('<div class="icon-big">⏳</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">КАЛЬКУЛЯТОР ОТЛОЖЕН</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">До лучших времен</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <div class="big-text">🔄 Ведутся технические работы</div>
    <div class="small-text">
        Калькулятор временно недоступен.<br>
        Приносим извинения за неудобства.
    </div>
</div>
""", unsafe_allow_html=True)

# Сообщение о возврате
messages = [
    "Скоро вернемся с обновлениями",
    "Работаем над улучшением сервиса",
    "Готовим новый функционал",
    "Оптимизируем расчеты"
]
msg = random.choice(messages)

st.markdown(f"""
<div style="text-align: center; font-size: 18px; color: #2e86c1; padding: 15px;">
    📌 {msg}
</div>
""", unsafe_allow_html=True)

# Кнопка проверки статуса
if st.button("🔄 Проверить статус", use_container_width=True):
    st.rerun()

# ============================================================
# ПОДВАЛ
# ============================================================

st.markdown(f"""
<div class="footer-text">
    <div class="company">🧪 Калькулятор свойств углеводородов</div>
    <div>ООО «ИЗП» · Группа моделирования технологических процессов</div>
    <div>под руководством Клепцова Д.В.</div>
    <div class="time-stamp">
        Страница обновлена: {datetime.now().strftime('%d.%m.%Y %H:%M')}
    </div>
</div>
""", unsafe_allow_html=True)