# maintenance.py - Страница "На обслуживании"
import streamlit as st
import random
from datetime import datetime

# Список шуток
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

# === УПРОЩЕННЫЙ CSS (без анимаций) ===
st.markdown("""
<style>
    .main-title {
        font-size: 50px;
        font-weight: 900;
        text-align: center;
        color: #ff2d2d;
    }
    .subtitle {
        font-size: 20px;
        text-align: center;
        color: #ff6b35;
        margin-top: -10px;
    }
    .joke-box {
        background: rgba(255, 107, 53, 0.1);
        border: 2px solid #ff6b35;
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        text-align: center;
        font-size: 24px;
        font-weight: 600;
        color: #ff6b35;
    }
    .joke-box .emoji {
        font-size: 48px;
        display: block;
        margin-bottom: 15px;
    }
    .footer-text {
        text-align: center;
        color: #888;
        font-size: 14px;
        margin-top: 40px;
        border-top: 1px solid #eee;
        padding-top: 20px;
    }
    .thermometer {
        font-size: 80px;
        text-align: center;
    }
    .progress-text {
        font-size: 14px;
        color: #888;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# === СОДЕРЖАНИЕ ===
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

# === ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ ===
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.metric("Температура процессора", "🔥 95°C", "Зашкаливает!")

with col2:
    st.metric("Осталось до охлаждения", "≈ неизвестно", "Остывает")

st.markdown("---")
st.markdown('<div style="text-align: center; color: #ff6b35; font-size: 18px;">Приносим свои извинения за неудобства!</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div class="progress-text">⚡ Программист уже бежит с вёдрами... ⚡</div>', unsafe_allow_html=True)

# === ПОДВАЛ ===
st.markdown(f"""
<div class="footer-text">
    © ООО «ИЗП» · Группа моделирования технологических процессов<br>
    <small>Калькулятор вернется в строй примерно {datetime.now().strftime('%H:%M') + ' +15 мин'}</small>
</div>
""", unsafe_allow_html=True)