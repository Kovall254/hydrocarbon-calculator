# ============================================================
# СТРАНИЦА "НА ОБСЛУЖИВАНИИ" (ВСТРОЕННАЯ)
# ============================================================

import streamlit as st
import random
from datetime import datetime

st.set_page_config(
    page_title="Калькулятор на обслуживании",
    page_icon="🌡️",
    layout="centered"
)

# === ОСНОВНЫЕ ШУТКИ (22 шт.) ===
JOKES = [
    # Король и Шут (4)
    "🎸 «А я иду, шагаю по Москве» — калькулятор ушел охлаждаться.",
    "🧟 «Проклятый старый дом» — калькулятор перегрелся в старом корпусе.",
    "🎻 «Кукла колдуна» — калькулятор заколдовали, он перегрелся.",
    "⚰️ «Лесник» — калькулятор ушел в лес, искать прохладу.",
    
    # Рик и Морти (4)
    "🧪 «Наука, битч!» — сказал калькулятор и перегрелся.",
    "🥒 Калькулятор: «Смотрите, инженер, я огурчик! Калькулятор-огурчик»",
    "📺 «Приключений на 20 минут, зашли и вышли» — калькулятор на перерыве.",
    "🚀 Калькулятор улетел в другую вселенную. Там прохладно.",
    
    # Матрица (3)
    "💊 Калькулятор выбрал красную таблетку. Теперь он знает правду о перегреве.",
    "🕶️ Калькулятор в матрице. Выбирает между перегревом и охлаждением.",
    "🐇 Калькулятор: «Следуй за белым кроликом» — и ушел охлаждаться.",
    
    # Терминатор (3)
    "💀 Калькулятор: «Я вернусь... когда остыну».",
    "🔫 Калькулятор: «I'll be back». Ушел охлаждаться.",
    "🤖 Калькулятор — терминатор. Ему нужна жидкость для охлаждения.",
    
    # Во все тяжкие (4)
    "🧪 «В чем сила, брат? Пока думал — перегрелся =(»",
    "🧊 Калькулятор взял программиста в заложники и требует перерыв.",
    "🔥 Калькулятор: «Я тот, кто стучит... по клавиатуре». Требует перерыва.",
    "💰 «Скажи, что я не перегреюсь!» — сказал калькулятор. И перегрелся.",
    
    # Властелин колец (4)
    "💍 Калькулятор: «Моя прелесть!» — и перегрелся от счастья.",
    "🧙 «Ты не пройдешь!» — сказал калькулятор и перегрелся.",
    "🔥 Калькулятор: «Огонь и лёд» — сам себя охлаждает.",
    "⛰️ Калькулятор ушел в Мордор. Там прохладно.",
]

# === СЕКРЕТНАЯ ПРАВОСЛАВНАЯ ШУТКА (1/150) ===
SECRET_JOKE = "«Прости меня, инженер, ибо согрешил я — перегрелся на работе» — сказал калькулятор."

ICONS = ["🎸", "🧟", "🎻", "⚰️", "🧪", "🥒", "📺", "🚀", "💊", "🕶️", "🐇", "💀", "🔫", "🤖", "🧪", "🧊", "🔥", "💰", "💍", "🧙", "🔥", "⛰️"]

def get_random_joke():
    # С вероятностью 1/150 показываем секретную шутку
    if random.randint(1, 2) == 1:
        return SECRET_JOKE, True, "⛪"  # Иконка церкви
    joke = random.choice(JOKES)
    icon = random.choice(ICONS)
    return joke, False, icon

joke, is_secret, icon = get_random_joke()

# === CSS ===
if is_secret:
    st.markdown(f"""
    <style>
        .main-title {{
            font-size: 60px;
            font-weight: 900;
            text-align: center;
            color: #FFD700;
            animation: pulse-gold 1.5s ease-in-out infinite;
            text-shadow: 0 0 30px rgba(255, 215, 0, 0.6),
                         0 0 60px rgba(255, 215, 0, 0.3);
        }}
        .subtitle {{
            font-size: 22px;
            text-align: center;
            color: #FFD700;
            margin-top: -10px;
            text-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
        }}
        .joke-box {{
            background: rgba(255, 215, 0, 0.05);
            border: 2px solid #FFD700;
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            text-align: center;
            font-size: 26px;
            font-weight: 600;
            color: #FFD700;
            box-shadow: 0 0 60px rgba(255, 215, 0, 0.2),
                        inset 0 0 60px rgba(255, 215, 0, 0.05);
            animation: glow-gold 1.5s ease-in-out infinite;
        }}
        .joke-box .emoji {{
            font-size: 52px;
            display: block;
            margin-bottom: 15px;
            filter: drop-shadow(0 0 30px rgba(255, 215, 0, 0.4));
        }}
        .footer-text {{
            text-align: center;
            color: #FFD700;
            font-size: 14px;
            margin-top: 40px;
            border-top: 1px solid rgba(255, 215, 0, 0.2);
            padding-top: 20px;
            opacity: 0.7;
        }}
        .footer-text .church {{
            margin-top: 8px;
            color: #FFD700;
            font-size: 16px;
            text-shadow: 0 0 15px rgba(255,215,0,0.2);
        }}
        .thermometer {{
            font-size: 90px;
            text-align: center;
            animation: shake 1s ease-in-out infinite;
            display: inline-block;
            filter: drop-shadow(0 0 30px rgba(255, 215, 0, 0.4));
            width: 100%;
        }}
        .progress-text {{
            font-size: 16px;
            color: #FFD700;
            text-align: center;
            text-shadow: 0 0 15px rgba(255, 215, 0, 0.3);
            animation: pulse-gold 1.5s ease-in-out infinite;
        }}
        .metric {{
            text-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
            color: #FFD700;
        }}
        @keyframes pulse-gold {{
            0% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.03); opacity: 0.9; }}
            100% {{ transform: scale(1); opacity: 1; }}
        }}
        @keyframes glow-gold {{
            0% {{ box-shadow: 0 0 20px rgba(255, 215, 0, 0.1), inset 0 0 20px rgba(255, 215, 0, 0.02); }}
            50% {{ box-shadow: 0 0 60px rgba(255, 215, 0, 0.3), inset 0 0 60px rgba(255, 215, 0, 0.08); }}
            100% {{ box-shadow: 0 0 20px rgba(255, 215, 0, 0.1), inset 0 0 20px rgba(255, 215, 0, 0.02); }}
        }}
        @keyframes shake {{
            0% {{ transform: rotate(-3deg); }}
            50% {{ transform: rotate(3deg); }}
            100% {{ transform: rotate(-3deg); }}
        }}
    </style>
    """, unsafe_allow_html=True)
else:
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
        .metric {
            text-shadow: 0 0 15px rgba(255, 107, 53, 0.1);
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
    </style>
    """, unsafe_allow_html=True)

# === ОТОБРАЖЕНИЕ ===
st.markdown('<div class="thermometer">🌡️</div>', unsafe_allow_html=True)

if is_secret:
    st.markdown('<div class="main-title">КАЛЬКУЛЯТОР СОГРЕШИЛ</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Требуется покаяние</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="main-title">КАЛЬКУЛЯТОР ПЕРЕГРЕЛСЯ</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Требуется охлаждение</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="joke-box">
    <span class="emoji">{icon}</span>
    {joke}
</div>
""", unsafe_allow_html=True)

st.markdown("---")

if is_secret:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="metric">', unsafe_allow_html=True)
        st.metric("Жар души", "🔥 99°C", "Согрешил")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric">', unsafe_allow_html=True)
        st.metric("Осталось до покаяния", "⏳ Неизвестно", "Батюшка уже в пути")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Температура процессора", "🔥 95°C", "Зашкаливает!")
    with col2:
        st.metric("Осталось до охлаждения", "⏳ Неизвестно", "Программист ищет лёд")

st.markdown("---")

if is_secret:
    st.markdown('<div style="text-align: center; color: #FFD700; font-size: 20px; text-shadow: 0 0 25px rgba(255,215,0,0.3);">И да пребудет с вами холод</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="text-align: center; color: #ff6b35; font-size: 20px; text-shadow: 0 0 25px rgba(255,107,53,0.3);">Приносим свои извинения за неудобства!</div>', unsafe_allow_html=True)

st.markdown("---")

if is_secret:
    st.markdown('<div class="progress-text">🙏 Аминь. Ожидайте остывания...</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="progress-text">⚡ Программист уже бежит с вёдрами... ⚡</div>', unsafe_allow_html=True)

if is_secret:
    st.markdown(f"""
    <div class="footer-text">
        <div style="text-shadow: 0 0 10px rgba(255,215,0,0.1);">
            © ООО «ИЗП» · Группа моделирования технологических процессов
        </div>
        <small style="text-shadow: 0 0 10px rgba(255,215,0,0.1);">
            Калькулятор вернется в строй, когда получит отпущение грехов
        </small>
        <div class="church">
            ⛪ Уже обратились к священнику
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
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