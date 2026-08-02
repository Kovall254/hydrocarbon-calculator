# maintenance.py - СТРАНИЦА "НА ОБСЛУЖИВАНИИ"
import streamlit as st
import random
from datetime import datetime

st.set_page_config(
    page_title="Калькулятор на обслуживании",
    page_icon="🌡️",
    layout="centered"
)

JOKES = [
    "🧊 Калькулятор перегрелся, программист бегает за льдом...",
    "🔥 Слишком много расчетов — калькулятор ушел в отпуск на Бали.",
    "🌡️ Температура калькулятора достигла 100°C. Нужно охлаждение!",
    "🧪 Калькулятор залили кофе. Сейчас сушим феном...",
    "⚡ Ошибка в системе: слишком много энтузиазма. Ждем перезагрузки.",
    "🌀 Калькулятор завис на расчете Z-фактора. Перезапускаем вселенную...",
    "🔧 Программист уже в пути с ведром воды. Скоро починим!",
    "🥵 Калькулятор жарится как шашлык. Дайте ему отдохнуть!",
    "💻 Калькулятор ушел за молоком. Вернется к обеду."
]

ICONS = ["🌡️", "🔥", "🧊", "💻", "⚡", "🌀", "🔧", "🥵", "🎲", "🧪"]

def get_random_joke():
    return random.choice(JOKES)

def get_random_icon():
    return random.choice(ICONS)

st.markdown("""
<style>
    .main-title {
        font-size: 60px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #ff6b35, #ff2d2d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulse 2s ease-in-out infinite;
        text-shadow: 0 0 30px rgba(255, 45, 45, 0.4),
                     0 0 60px rgba(255, 45, 45, 0.2);
    }
    .subtitle {
        font-size: 22px;
        text-align: center;
        color: #ff6b35;
        margin-top: -10px;
        text-shadow: 0 0 20px rgba(255, 107, 53, 0.3);
    }
    .joke-box {
        background: rgba(255, 107, 53, 0.1);
        border: 2px solid #ff6b35;
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        text-align: center;
        font-size: 26px;
        font-weight: 600;
        color: #ff6b35;
        box-shadow: 0 0 40px rgba(255, 107, 53, 0.15),
                    inset 0 0 40px rgba(255, 107, 53, 0.05);
        animation: glow-border 2s ease-in-out infinite;
    }
    .joke-box .emoji {
        font-size: 52px;
        display: block;
        margin-bottom: 15px;
        filter: drop-shadow(0 0 20px rgba(255, 107, 53, 0.3));
    }
    .footer-text {
        text-align: center;
        color: #888;
        font-size: 14px;
        margin-top: 40px;
        border-top: 1px solid rgba(255, 107, 53, 0.2);
        padding-top: 20px;
    }
    .thermometer {
        font-size: 90px;
        text-align: center;
        animation: shake 1s ease-in-out infinite;
        display: inline-block;
        filter: drop-shadow(0 0 30px rgba(255, 45, 45, 0.4));
        width: 100%;
    }
    .progress-text {
        font-size: 16px;
        color: #ff6b35;
        text-align: center;
        text-shadow: 0 0 15px rgba(255, 107, 53, 0.2);
        animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.03); opacity: 0.9; }
        100% { transform: scale(1); opacity: 1; }
    }
    @keyframes shake {
        0% { transform: rotate(-3deg); }
        50% { transform: rotate(3deg); }
        100% { transform: rotate(-3deg); }
    }
    @keyframes glow-border {
        0% { box-shadow: 0 0 20px rgba(255, 107, 53, 0.1), inset 0 0 20px rgba(255, 107, 53, 0.02); }
        50% { box-shadow: 0 0 50px rgba(255, 107, 53, 0.25), inset 0 0 50px rgba(255, 107, 53, 0.08); }
        100% { box-shadow: 0 0 20px rgba(255, 107, 53, 0.1), inset 0 0 20px rgba(255, 107, 53, 0.02); }
    }
    .metric {
        text-shadow: 0 0 15px rgba(255, 107, 53, 0.1);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="thermometer">🌡️</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">КАЛЬКУЛЯТОР ПЕРЕГРЕЛСЯ</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Требуется охлаждение</div>', unsafe_allow_html=True)

joke = get_random_joke()
icon = get_random_icon()

st.markdown(f"""
<div class="joke-box">
    <span class="emoji">{icon}</span>
    {joke}
</div>
""", unsafe_allow_html=True)

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="metric">', unsafe_allow_html=True)
    st.metric("Температура процессора", "🔥 95°C", "Зашкаливает!")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric">', unsafe_allow_html=True)
    st.metric("Осталось до охлаждения", "⏳ Неизвестно", "Программист ищет лёд")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div style="text-align: center; color: #ff6b35; font-size: 20px; text-shadow: 0 0 25px rgba(255,107,53,0.3);">Приносим свои извинения за неудобства!</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div class="progress-text">⚡ Программист уже бежит с вёдрами... ⚡</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="footer-text">
    <div style="text-shadow: 0 0 10px rgba(255,107,53,0.1);">
        © ООО «ИЗП» · Группа моделирования технологических процессов
    </div>
    <small style="text-shadow: 0 0 10px rgba(255,107,53,0.1);">
        Калькулятор вернется в строй, как только программист найдет лёд
    </small>
</div>
""", unsafe_allow_html=True)