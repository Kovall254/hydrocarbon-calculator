# ============================================================
# МОДУЛЬ: app.py
# НАЗНАЧЕНИЕ: веб-интерфейс для расчета свойств углеводородов
# ТЕХНОЛОГИИ: Streamlit, Pandas, Matplotlib
# АВТОР: Группа моделирования технологических процессов, ООО "ИЗП"
# ============================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from calculator import SHFLUCalculator
import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ============================================================
# БЛОК 1: ИНИЦИАЛИЗАЦИЯ ТЕМЫ
# ============================================================

if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# ============================================================
# БЛОК 2: ФУНКЦИЯ ВОЗВРАТА CSS В ЗАВИСИМОСТИ ОТ ТЕМЫ
# ============================================================

def get_theme_css():
    if st.session_state.theme == 'dark':
        return """
        .stApp {
            background: linear-gradient(135deg, #0d1b2a 0%, #1b2d45 100%);
            color: #e8f0fe;
        }
        .hex-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }
        .hex {
            position: absolute;
            font-size: 80px;
            opacity: 0.06;
            color: #4a8cbf;
            font-weight: bold;
            transform: rotate(30deg);
            pointer-events: none;
            user-select: none;
        }
        .css-1r6slb0, .css-1y4p8pa {
            background: rgba(30, 50, 70, 0.85) !important;
            border: 1px solid rgba(70, 130, 180, 0.2) !important;
            color: #e8f0fe !important;
        }
        .stMarkdown, .stText, .stCaption, .stMetric {
            color: #e8f0fe !important;
        }
        h1, h2, h3, h4, h5, h6, .stHeading {
            color: #e8f0fe !important;
        }
        .quote {
            color: #e8f0fe;
            border-left-color: #4a8cbf;
            background: rgba(70, 130, 180, 0.1);
        }
        .quote-author {
            color: #8bb8d9;
        }
        .footer {
            color: #8bb8d9;
            border-top-color: rgba(70, 130, 180, 0.2);
        }
        .footer .company, .footer .group, .footer .lead {
            color: #e8f0fe;
        }
        .stButton > button {
            background: #1b3a5c !important;
            color: #e8f0fe !important;
        }
        .stButton > button:hover {
            background: #2a5a7a !important;
        }
        .stTextInput > div > input {
            background: #1b2d45 !important;
            color: #e8f0fe !important;
        }
        .stNumberInput > div > input {
            background: #1b2d45 !important;
            color: #e8f0fe !important;
        }
        .stSelectbox > div > div {
            background: #1b2d45 !important;
            color: #e8f0fe !important;
        }
        .sci-fi-title {
            background: linear-gradient(135deg, #4a8cbf, #7ab8e0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
            text-shadow: 0 0 30px rgba(74, 140, 191, 0.3);
        }
        """
    else:
        return """
        .stApp {
            background: linear-gradient(135deg, #f5f8fc 0%, #e8f0f8 100%);
            color: #0e1a2b;
        }
        .hex-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }
        .hex {
            position: absolute;
            font-size: 80px;
            opacity: 0.04;
            color: #1a5276;
            font-weight: bold;
            transform: rotate(30deg);
            pointer-events: none;
            user-select: none;
        }
        .css-1r6slb0, .css-1y4p8pa {
            backdrop-filter: blur(10px);
            background: rgba(255,255,255,0.85) !important;
            border: 1px solid rgba(46,134,193,0.15) !important;
        }
        .quote {
            font-style: italic;
            color: #1a5276;
            text-align: center;
            padding: 12px 20px;
            border-left: 4px solid #2e86c1;
            background: rgba(46,134,193,0.05);
            border-radius: 8px;
            margin: 20px 0;
            font-size: 15px;
        }
        .quote-author {
            font-style: normal;
            font-weight: 600;
            color: #1a5276;
            display: block;
            margin-top: 5px;
            font-size: 13px;
        }
        .footer {
            text-align: center;
            color: #5d6d7e;
            font-size: 13px;
            padding: 20px 0 10px 0;
            border-top: 1px solid rgba(46,134,193,0.15);
            margin-top: 30px;
            line-height: 1.8;
        }
        .footer .company {
            font-size: 15px;
            font-weight: 700;
            color: #1a5276;
            letter-spacing: 0.5px;
        }
        .footer .group {
            font-size: 14px;
            color: #2c3e50;
        }
        .footer .lead {
            font-size: 14px;
            color: #2c3e50;
        }
        .sci-fi-title {
            background: linear-gradient(135deg, #1a5276, #2e86c1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
            text-shadow: 0 0 30px rgba(46,134,193,0.3);
        }
        .stButton > button {
            transition: all 0.3s ease !important;
            border-radius: 12px !important;
        }
        .stButton > button:hover {
            transform: scale(1.03);
            box-shadow: 0 0 30px rgba(46,134,193,0.4) !important;
        }
        """

# ============================================================
# БЛОК 3: ПРИМЕНЕНИЕ CSS И ФОНА
# ============================================================

st.markdown(f"<style>{get_theme_css()}</style>", unsafe_allow_html=True)

# Фон с шестиугольниками
st.markdown("""
<div class="hex-bg">
    <div class="hex" style="top:5%; left:3%; transform:rotate(15deg);">⬡</div>
    <div class="hex" style="top:15%; right:8%; transform:rotate(45deg);">⬡</div>
    <div class="hex" style="bottom:20%; left:5%; transform:rotate(60deg);">⬡</div>
    <div class="hex" style="bottom:10%; right:3%; transform:rotate(20deg);">⬡</div>
    <div class="hex" style="top:45%; left:2%; transform:rotate(35deg); font-size:100px;">⬡</div>
    <div class="hex" style="top:55%; right:2%; transform:rotate(10deg); font-size:100px;">⬡</div>
    <div class="hex" style="top:75%; left:10%; transform:rotate(50deg); font-size:90px;">⬡</div>
    <div class="hex" style="top:25%; left:12%; transform:rotate(25deg); font-size:70px;">⬡</div>
    <div class="hex" style="top:70%; right:12%; transform:rotate(40deg); font-size:70px;">⬡</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# БЛОК 4: ОТПРАВКА НА ПОЧТУ (MAIL.RU)
# ============================================================

def send_protocol_by_email(report_text, user_name, user_workshop, user_sensor, T_C, P_MPa, filename):
    """Автоматическая отправка протокола на почту через Mail.ru SMTP"""
    try:
        SMTP_SERVER = "smtp.mail.ru"
        SMTP_PORT = 465
        
        SENDER_EMAIL = "pasha_ko_00@mail.ru"
        SENDER_PASSWORD = "LbCQTZLHLz94veadqqVY"
        RECEIVER_EMAIL = "pasha_ko_00@mail.ru"
        
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = f"Протокол расчета {user_sensor} от {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        body = f"""
Здравствуйте!

Калькулятор свойств углеводородов автоматически отправил протокол расчета.

Данные расчета:
  • Пользователь:   {user_name} ({user_workshop})
  • Датчик:         {user_sensor}
  • Температура:    {T_C:.1f} °C
  • Давление:       {P_MPa:.3f} МПа
  • Время расчета:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Протокол прикреплен к письму.

---
Калькулятор свойств углеводородов
ООО «ИЗП» · Группа моделирования технологических процессов
"""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(report_text.encode('utf-8'))
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={filename}')
        msg.attach(part)
        
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True, "✅ Протокол отправлен на почту Mail.ru"
        
    except Exception as e:
        return False, f"❌ Ошибка отправки: {str(e)}"

# ============================================================
# БЛОК 5: ЦИТАТЫ УЧЁНЫХ
# ============================================================

SCIENTIST_QUOTES = [
    {"text": "В науке нет ничего такого, что нельзя было бы понять. Важно лишь терпение и желание.", "author": "Дмитрий Менделеев"},
    {"text": "Многие из тех, кто не боялись рисковать, погибли, но те, кто выжили, изменили мир.", "author": "Никола Тесла"},
    {"text": "Познание начинается с удивления.", "author": "Аристотель"},
    {"text": "Химия — это физика, только более красивая и сложная.", "author": "Мари Кюри"},
    {"text": "Великие открытия делаются теми, кто умеет удивляться тому, что все считают очевидным.", "author": "Альберт Эйнштейн"},
    {"text": "Химия — это наука о веществах и их превращениях. А превращения — это жизнь.", "author": "Александр Бутлеров"},
    {"text": "В химии нет ничего сложного, есть только неизвестное.", "author": "Антуан Лавуазье"},
    {"text": "Я никогда не считал, что могу сделать что-то выдающееся. Я просто работал и верил.", "author": "Мари Кюри"},
    {"text": "Наука не является и не будет являться законченной книгой. Каждый важный успех приносит новые вопросы.", "author": "Альберт Эйнштейн"},
    {"text": "Химия — это мост между физикой и биологией.", "author": "Лайнус Полинг"},
    {"text": "Все вещества — это яды. Всё зависит от дозы.", "author": "Парацельс"},
    {"text": "Мысль о том, что мы можем управлять материей, — это и есть химия.", "author": "Роберт Вудворд"},
    {"text": "Прогресс науки зависит не от количества идей, а от количества проверенных идей.", "author": "Пётр Капица"},
    {"text": "Истина — это то, что выдерживает проверку временем и экспериментом.", "author": "Дмитрий Менделеев"}
]

def get_random_quote():
    quote = random.choice(SCIENTIST_QUOTES)
    return quote["text"], quote["author"]

# ============================================================
# БЛОК 6: ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def is_mobile():
    try:
        ua = st.context.headers.get('User-Agent', '').lower()
        return any(x in ua for x in ['mobile', 'android', 'iphone', 'ipad'])
    except:
        return False

MOBILE = is_mobile()

def normalize_composition(components):
    """Нормализация состава до 100%"""
    total = sum(components.values())
    if total > 0 and abs(total - 100) > 0.01:
        for key in components:
            components[key] = (components[key] / total) * 100
    return components

def generate_report(result_PR, result_GERG, components, T_C, P_MPa, method,
                   user_name, user_workshop, user_sensor, input_type, components_mass):
    """Формирует текстовый протокол"""
    
    display_names = {
        'helium': 'Гелий', 'hydrogen': 'Водород', 'oxygen': 'Кислород',
        'nitrogen': 'Азот', 'co2': 'CO₂',
        'methane': 'Метан (C1)', 'ethane': 'Этан (C2)', 'propane': 'Пропан (C3)',
        'n-butane': 'н-Бутан (C4)', 'i-butane': 'изо-Бутан (iC4)',
        'n-pentane': 'н-Пентан (C5)', 'i-pentane': 'изо-Пентан (iC5)',
        'c6plus': 'C6+ (всего)',
        'benzene': 'Бензол (C₆H₆)',
        'toluene': 'Толуол (C₇H₈)',
        'hexane': 'Гексан (C6)', 'heptane': 'Гептан (C7)',
        'octane': 'Октан (C8)', 'nonane': 'Нонан (C9)', 'decane': 'Декан (C10)'
    }
    
    comp_str = ""
    for key, value in components.items():
        if value > 0:
            display = display_names.get(key, key)
            comp_str += f"    {display:<20} {value:>6.1f} %\n"
    
    mu_PR = result_PR.get('mu_dynamic')
    mu_GERG = result_GERG.get('mu_dynamic')
    
    mu_PR_str = f"{mu_PR*1000:.4f}" if mu_PR is not None else "—"
    mu_GERG_str = f"{mu_GERG*1000:.4f}" if mu_GERG is not None else "—"
    
    rho_PR = result_PR.get('rho_gas') or result_PR.get('rho') or 1.0
    rho_GERG = result_GERG.get('rho') or 1.0
    
    nu_PR_str = f"{(mu_PR/rho_PR)*1e6:.4f}" if mu_PR is not None else "—"
    nu_GERG_str = f"{(mu_GERG/rho_GERG)*1e6:.4f}" if mu_GERG is not None else "—"
    
    rho_PR_str = f"{result_PR['rho_gas']:.3f}" if result_PR.get('rho_gas') else f"{result_PR['rho']:.3f}"
    rho_GERG_str = f"{result_GERG['rho']:.3f}"
    
    diff = abs(result_PR['Z'] - result_GERG['Z']) / result_GERG['Z'] * 100
    type_label = "Массовые" if input_type == "Массовые" else "Мольные"
    
    quote_text, quote_author = get_random_quote()
    
    return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    КАЛЬКУЛЯТОР СВОЙСТВ УГЛЕВОДОРОДОВ                      ║
║                          ПРОТОКОЛ РАСЧЕТА                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ ДАННЫЕ ПОЛЬЗОВАТЕЛЯ                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  Фамилия И.О.:     {user_name:<40} │
│  Цех:              {user_workshop:<40} │
│  Датчик:           {user_sensor:<40} │
│  Дата расчета:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                    │
│  Тип долей:        {type_label:<44}                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ ВХОДНЫЕ ДАННЫЕ                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  Температура:        {T_C:>7.1f} °C                                    │
│  Давление:           {P_MPa:>7.3f} МПа                                 │
│  Метод:              {method:<44}                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ СОСТАВ СМЕСИ ({type_label} доли)                                          │
├─────────────────────────────────────────────────────────────────────────────┤
{comp_str}└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ РЕЗУЛЬТАТЫ РАСЧЕТА                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  {T_C:.1f}°C, {P_MPa:.3f} МПа                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  Параметр                 │  Пенга-Робинсон    │  GERG-2008               │
├───────────────────────────┼────────────────────┼──────────────────────────┤
│  Z-фактор                 │  {result_PR['Z']:.6f}     │  {result_GERG['Z']:.6f}            │
│  Плотность, кг/м³         │  {rho_PR_str:>9}        │  {rho_GERG_str:>9}          │
│  Дин. вязкость, сП        │  {mu_PR_str:>9}        │  {mu_GERG_str:>9}          │
│  Кин. вязкость, сСт       │  {nu_PR_str:>9}        │  {nu_GERG_str:>9}          │
│  Мол. масса, кг/кмоль     │  {result_PR['MW']:.3f}     │  {result_GERG['MW']:.3f}            │
└───────────────────────────┴────────────────────┴──────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ СРАВНЕНИЕ МЕТОДОВ                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  Разница Z-фактора:      {diff:.3f} %                                           │
│  Рекомендация:           {'Z-факторы близки, методы согласуются' if diff < 2 else 'Рекомендуется использовать GERG-2008 для повышенной точности'} │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  ЦИТАТА УЧЁНОГО                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  «{quote_text}»                                                           │
│  — {quote_author}                                                         │
└─────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════╗
║  Расчет произведен автоматически.                                          ║
║  Ответственность за корректность исходных данных несет пользователь.       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

def mass_to_mole(components_mass, components_mw):
    """Пересчет массовых долей в мольные"""
    mass_values = {}
    total_mass = 0
    
    for key, value in components_mass.items():
        if value > 0:
            mass_values[key] = value
            total_mass += value
    
    mole_values = {}
    total_moles = 0
    
    for key, mass in mass_values.items():
        if key in components_mw and components_mw[key] > 0:
            moles = mass / components_mw[key]
            mole_values[key] = moles
            total_moles += moles
    
    mole_fractions = {}
    for key, moles in mole_values.items():
        if total_moles > 0:
            mole_fractions[key] = (moles / total_moles) * 100
    
    return mole_fractions

def login_form():
    """Форма входа для авторизации"""
    st.markdown("### Вход в систему")
    st.markdown("Введите данные для автозаполнения протокола")
    
    with st.form("login_form"):
        name = st.text_input("Фамилия И.О.", placeholder="Например: Иванов И.И.")
        workshop = st.text_input("Цех", placeholder="Например: Цех №5")
        submitted = st.form_submit_button("Войти")
        
        if submitted and name and workshop:
            st.session_state.user_name = name
            st.session_state.user_workshop = workshop
            st.session_state.logged_in = True
            st.rerun()
        elif submitted:
            st.warning("Заполните все поля")

# ============================================================
# БЛОК 7: НАСТРОЙКА СТРАНИЦЫ
# ============================================================

if MOBILE:
    st.set_page_config(
        page_title="Калькулятор углеводородов",
        page_icon="🧪",
        layout="centered"
    )
else:
    st.set_page_config(
        page_title="Калькулятор свойств углеводородов",
        page_icon="🧪",
        layout="wide"
    )

# Инициализация сессионных переменных
SESSION_KEYS = [
    'logged_in', 'user_name', 'user_workshop', 'show_report',
    'result_PR', 'result_GERG', 'T_C', 'P_MPa', 'method',
    'components', 'input_type', 'user_sensor', 'quote_shown',
    'report_filename', 'report_text', 'components_input'
]

for key in SESSION_KEYS:
    if key not in st.session_state:
        if key == 'logged_in':
            st.session_state.logged_in = False
        elif key in ['user_name', 'user_workshop', 'user_sensor', 'method', 'input_type']:
            st.session_state[key] = '' if key in ['user_name', 'user_workshop', 'user_sensor'] else 'Сравнение методов'
            if key == 'input_type':
                st.session_state.input_type = 'Мольные'
        elif key in ['result_PR', 'result_GERG', 'T_C', 'P_MPa']:
            st.session_state[key] = None
        elif key in ['components', 'components_input']:
            st.session_state[key] = {}
        else:
            st.session_state[key] = False

# ============================================================
# БЛОК 8: АВТОРИЗАЦИЯ
# ============================================================

if not st.session_state.logged_in:
    login_form()
    st.stop()

# ============================================================
# БЛОК 9: ОСНОВНОЙ ИНТЕРФЕЙС
# ============================================================

col_title, col_logout, col_theme = st.columns([4, 1, 1] if not MOBILE else [3, 1, 1])

with col_title:
    if MOBILE:
        st.title("Углеводороды")
        st.markdown("### Расчет Z, ρ, μ")
    else:
        st.markdown('<h1 class="sci-fi-title">Калькулятор свойств углеводородов</h1>', unsafe_allow_html=True)
        st.markdown("### Расчет Z-фактора, плотности и вязкости газовых смесей")

with col_logout:
    st.write("")
    st.write("")
    if st.button("Выйти", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_name = ''
        st.session_state.user_workshop = ''
        st.rerun()

with col_theme:
    st.write("")
    st.write("")
    theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
    if st.button(theme_icon, use_container_width=True, help="Переключить тему"):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
        st.rerun()

st.caption(f"Пользователь: {st.session_state.user_name} | {st.session_state.user_workshop}")

# Отображение цитаты
if not st.session_state.quote_shown:
    quote_text, quote_author = get_random_quote()
    if MOBILE and len(quote_text) > 80:
        quote_text = quote_text[:77] + "..."
    st.markdown(
        f'<div class="quote">«{quote_text}»<span class="quote-author">— {quote_author}</span></div>',
        unsafe_allow_html=True
    )
    st.session_state.quote_shown = True

@st.cache_resource
def get_calculator():
    return SHFLUCalculator()

calculator = get_calculator()

# Молекулярные массы для пересчета
MW_MAP = {
    'helium': 4.003, 'hydrogen': 2.016, 'oxygen': 32.000,
    'nitrogen': 28.013, 'co2': 44.010,
    'methane': 16.043, 'ethane': 30.070, 'propane': 44.097,
    'n-butane': 58.123, 'i-butane': 58.123,
    'n-pentane': 72.151, 'i-pentane': 72.151,
    'benzene': 78.114,
    'toluene': 92.141,
    'hexane': 86.178, 'heptane': 100.205,
    'octane': 114.232, 'nonane': 128.259, 'decane': 142.286,
    'c6plus': 100.000
}

# ============================================================
# РАЗДЕЛЕНИЕ НА КОЛОНКИ (АДАПТАЦИЯ ПОД ТЕЛЕФОН)
# ============================================================

if MOBILE:
    col1 = st.container()
    col2 = None
else:
    col1, col2 = st.columns(2)

# ============================================================
# БЛОК 10: ЛЕВАЯ КОЛОНКА — ВВОД ДАННЫХ
# ============================================================

with col1:
    st.header("Входные данные")
    
    with st.expander("Условия расчета", expanded=True):
        T_C = st.number_input("Температура (°C)", value=35.0, min_value=-50.0, max_value=150.0, step=1.0)
        P_MPa = st.number_input("Давление (МПа)", value=2.5, min_value=0.001, max_value=10.0, step=0.1)
    
    with st.expander("Метод расчета", expanded=True):
        method = st.selectbox("Выберите метод:", ["Пенга-Робинсон", "GERG-2008", "Сравнение методов"])
    
    with st.expander("Тип долей", expanded=True):
        input_type = st.radio("Тип данных:", ["Мольные", "Массовые"], index=0)
        if input_type == "Массовые":
            st.info("Автоматический пересчет в мольные")
    
    with st.expander("Состав смеси", expanded=not MOBILE):
        st.markdown(f"**{input_type} доли компонентов:**")
        st.markdown("*Сумма = 100%*")
        
        component_order = [
            ('helium', 'Гелий'), ('hydrogen', 'Водород'), ('oxygen', 'Кислород'),
            ('nitrogen', 'Азот'), ('co2', 'CO₂'),
            ('methane', 'Метан C1'), ('ethane', 'Этан C2'), ('propane', 'Пропан C3'),
            ('n-butane', 'н-Бутан C4'), ('i-butane', 'iC4'),
            ('n-pentane', 'н-Пентан C5'), ('i-pentane', 'iC5'),
            ('c6plus', 'C6+'),
            ('benzene', 'Бензол C₆H₆'),
            ('toluene', 'Толуол C₇H₈'),
            ('hexane', 'Гексан C6'), ('heptane', 'Гептан C7'),
            ('octane', 'Октан C8'), ('nonane', 'Нонан C9'), ('decane', 'Декан C10'),
        ]
        
        default_values = {
            'helium': 0.0, 'hydrogen': 0.0, 'oxygen': 0.0,
            'nitrogen': 3.0, 'co2': 0.0,
            'methane': 80.0, 'ethane': 12.0, 'propane': 5.0,
            'n-butane': 0.0, 'i-butane': 0.0,
            'n-pentane': 0.0, 'i-pentane': 0.0,
            'c6plus': 0.0,
            'benzene': 0.0,
            'toluene': 0.0,
            'hexane': 0.0, 'heptane': 0.0, 'octane': 0.0,
            'nonane': 0.0, 'decane': 0.0
        }
        
        if MOBILE:
            comp_col1, comp_col2 = st.columns(2)
            comp_col3 = None
        else:
            comp_col1, comp_col2, comp_col3 = st.columns(3)
        
        components_input = {}
        for i, (key, display_name) in enumerate(component_order):
            if i % 3 == 0:
                col = comp_col1
            elif i % 3 == 1:
                col = comp_col2
            else:
                col = comp_col3 if comp_col3 is not None else comp_col1
            
            components_input[key] = col.number_input(
                display_name,
                value=default_values[key],
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key=f"comp_{key}_{input_type}"
            )
        
        st.markdown("---")
        if st.button("Загрузить пример", use_container_width=True):
            example = {
                'helium': 0.0, 'hydrogen': 0.0, 'oxygen': 0.0,
                'nitrogen': 3.0, 'co2': 0.0,
                'methane': 80.0, 'ethane': 12.0, 'propane': 5.0,
                'n-butane': 0.0, 'i-butane': 0.0,
                'n-pentane': 0.0, 'i-pentane': 0.0,
                'c6plus': 0.0,
                'benzene': 0.0,
                'toluene': 0.0,
                'hexane': 0.0, 'heptane': 0.0, 'octane': 0.0,
                'nonane': 0.0, 'decane': 0.0
            }
            for name, value in example.items():
                components_input[name] = value
            st.rerun()
        
        total = sum(components_input.values())
        if total > 0 and abs(total - 100) > 0.01:
            st.warning(f"Сумма = {total:.1f}% (будет нормализована до 100%)")
        elif abs(total - 100) <= 0.01 and total > 0:
            st.success(f"Сумма = {total:.1f}%")
        else:
            st.info("Введите состав смеси")
    
    user_sensor = st.text_input("Датчик", placeholder="Например: PT-101", key="sensor_input")
    st.session_state.user_sensor = user_sensor
    
    st.markdown("---")
    
    button_label = "Рассчитать" if not MOBILE else "Расчет"
    if st.button(button_label, type="primary", use_container_width=True):
        st.session_state.quote_shown = False
        
        total = sum(components_input.values())
        if total > 0 and abs(total - 100) > 0.01:
            for key in components_input:
                components_input[key] = (components_input[key] / total) * 100
        
        zs = []
        comp_names = []
        
        name_map = {
            'helium': 'helium', 'hydrogen': 'hydrogen', 'oxygen': 'oxygen',
            'nitrogen': 'nitrogen', 'co2': 'co2',
            'methane': 'methane', 'ethane': 'ethane', 'propane': 'propane',
            'n-butane': 'n-butane', 'i-butane': 'i-butane',
            'n-pentane': 'n-pentane', 'i-pentane': 'i-pentane',
            'benzene': 'benzene',
            'toluene': 'toluene',
            'hexane': 'hexane', 'heptane': 'heptane',
            'octane': 'octane', 'nonane': 'nonane', 'decane': 'decane'
        }
        
        if input_type == "Массовые":
            components_for_calc = mass_to_mole(components_input, MW_MAP)
            components_display = components_for_calc
        else:
            components_for_calc = components_input
            components_display = components_input
        
        # ---- ПРОВЕРКА C6+ РАЗБИВКИ ----
        c6plus_value = components_input.get('c6plus', 0)
        heavy_sum = sum(components_input.get(k, 0) for k in ['hexane', 'heptane', 'octane', 'nonane', 'decane'])
        
        if c6plus_value > 0 and heavy_sum == 0:
            st.error(f"❌ Вы ввели C6+ = {c6plus_value}%, но не заполнили разбивку C6-C10!")
            st.info("💡 Заполните поля: Гексан (C6), Гептан (C7), Октан (C8), Нонан (C9), Декан (C10)")
            st.stop()
        elif c6plus_value > 0 and abs(c6plus_value - heavy_sum) > 0.01:
            st.error(f"❌ C6+ = {c6plus_value}%, а сумма C6-C10 = {heavy_sum}%")
            st.info("💡 Скорректируйте C6+ или разбивку C6-C10, чтобы они совпадали")
            st.stop()
        
        for key, value in components_for_calc.items():
            if key != 'c6plus' and value > 0:
                comp_names.append(name_map.get(key, key))
                zs.append(value / 100)
        
        total_calc = sum(zs)
        if abs(total_calc - 1) > 0.01:
            st.error(f"❌ Сумма молярных долей = {total_calc*100:.1f}% (должна быть 100%)")
            st.stop()
        
        try:
            st.session_state.input_type = input_type
            
            calc_PR = SHFLUCalculator(method='PR')
            calc_PR.set_composition(comp_names, zs)
            calc_PR.set_conditions(T_C, P_MPa)
            result_PR = calc_PR.calculate()
            
            calc_GERG = SHFLUCalculator(method='GERG')
            calc_GERG.set_composition(comp_names, zs)
            calc_GERG.set_conditions(T_C, P_MPa)
            result_GERG = calc_GERG.calculate()
            
            st.session_state.result_PR = result_PR
            st.session_state.result_GERG = result_GERG
            st.session_state.T_C = T_C
            st.session_state.P_MPa = P_MPa
            st.session_state.method = method
            st.session_state.components = components_display
            st.session_state.components_input = components_input
            
            st.success("✅ Расчет выполнен")
            
            os.makedirs("reports", exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/protokol_{timestamp}_{st.session_state.user_sensor}.txt"
            
            report_text = generate_report(
                result_PR, result_GERG, components_display,
                T_C, P_MPa, method,
                st.session_state.user_name,
                st.session_state.user_workshop,
                st.session_state.user_sensor,
                input_type, components_input
            )
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_text)
            
            st.session_state.report_filename = filename
            st.session_state.report_text = report_text
            st.session_state.show_report = True
            
            st.success("✅ Протокол сохранен локально")
            
            # ---- АВТООТПРАВКА НА ПОЧТУ ----
            try:
                success, message = send_protocol_by_email(
                    report_text,
                    st.session_state.user_name,
                    st.session_state.user_workshop,
                    st.session_state.user_sensor,
                    T_C,
                    P_MPa,
                    f"protokol_{timestamp}_{st.session_state.user_sensor}.txt"
                )
                if success:
                    st.info("📧 Протокол отправлен на почту Mail.ru")
                else:
                    st.warning(message)
            except Exception as e:
                st.warning(f"⚠️ Протокол не отправлен на почту: {str(e)}")
            
        except Exception as e:
            st.error(f"❌ Ошибка: {str(e)}")

# ============================================================
# БЛОК 11: ПРАВАЯ КОЛОНКА — РЕЗУЛЬТАТЫ
# ============================================================

if col2 is not None:
    with col2:
        st.header("Результаты")
        
        if st.session_state.result_PR is not None and st.session_state.result_GERG is not None:
            result_PR = st.session_state.result_PR
            result_GERG = st.session_state.result_GERG
            method = st.session_state.method
            input_type = st.session_state.get('input_type', 'Мольные')
            
            if method == "Пенга-Робинсон":
                result = result_PR
                st.info("📘 Метод: Пенга-Робинсон")
            elif method == "GERG-2008":
                result = result_GERG
                st.info("📗 Метод: GERG-2008")
            else:
                result = None
                st.info("📊 Сравнение методов")
            
            type_label = "Массовые" if input_type == "Массовые" else "Мольные"
            st.caption(f"Тип долей: {type_label}")
            
            with st.expander("Основные параметры", expanded=True):
                if MOBILE:
                    col_met1, col_met2 = st.columns(2)
                    col_met3 = st.columns(1)[0]
                else:
                    col_met1, col_met2, col_met3 = st.columns(3)
                
                with col_met1:
                    st.metric("T", f"{st.session_state.T_C:.1f}°C")
                with col_met2:
                    st.metric("P", f"{st.session_state.P_MPa:.3f} МПа")
                with col_met3:
                    st.metric("M", f"{result_PR['MW']:.3f} кг/кмоль")
            
            if result and result.get('success', False):
                with st.expander("Результаты расчета", expanded=True):
                    col_z, col_rho = st.columns(2)
                    
                    with col_z:
                        st.metric("Z-фактор", f"{result['Z']:.6f}")
                    
                    with col_rho:
                        if result.get('rho_gas') is not None:
                            st.metric("Плотность", f"{result['rho_gas']:.3f} кг/м³")
                        elif result.get('rho_liquid') is not None:
                            st.metric("Плотность", f"{result['rho_liquid']:.3f} кг/м³")
                        elif result.get('rho') is not None:
                            st.metric("Плотность", f"{result['rho']:.3f} кг/м³")
                        else:
                            st.metric("Плотность", "—")
                    
                    mu = result.get('mu_dynamic')
                    if mu is not None:
                        mu_cP = mu * 1000
                        rho_for_nu = result.get('rho_gas') or result.get('rho_liquid') or result.get('rho') or 1.0
                        nu_cSt = (mu / rho_for_nu) * 1e6
                        
                        col_visc1, col_visc2 = st.columns(2)
                        with col_visc1:
                            st.metric("Динамическая вязкость", f"{mu_cP:.4f} сП")
                        with col_visc2:
                            st.metric("Кинематическая вязкость", f"{nu_cSt:.4f} сСт")
                    else:
                        st.info("ℹ️ Вязкость не рассчитана")
            
            if method == "Сравнение методов":
                with st.expander("Сравнение методов", expanded=True):
                    if result_PR.get('success', False) and result_GERG.get('success', False):
                        Z_PR = result_PR['Z']
                        Z_GERG = result_GERG['Z']
                        diff = abs(Z_PR - Z_GERG) / Z_GERG * 100
                        
                        if MOBILE:
                            col_comp1, col_comp2 = st.columns(2)
                            col_comp3 = st.columns(1)[0]
                        else:
                            col_comp1, col_comp2, col_comp3 = st.columns(3)
                        
                        with col_comp1:
                            st.metric("Пенга-Робинсон", f"{Z_PR:.6f}")
                        with col_comp2:
                            st.metric("GERG-2008", f"{Z_GERG:.6f}")
                        with col_comp3:
                            st.metric("Разница", f"{diff:.3f}%")
            
            with st.expander("Данные пользователя", expanded=False):
                st.text(f"ФИО: {st.session_state.user_name}")
                st.text(f"Цех: {st.session_state.user_workshop}")
                st.text(f"Датчик: {st.session_state.user_sensor}")
                st.text(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("📄 Показать протокол", use_container_width=True):
                    st.session_state.show_report = True
            
            with col_btn2:
                if st.button("📧 Отправить на почту", use_container_width=True):
                    if 'report_text' in st.session_state:
                        success, message = send_protocol_by_email(
                            st.session_state.report_text,
                            st.session_state.user_name,
                            st.session_state.user_workshop,
                            st.session_state.user_sensor,
                            st.session_state.T_C,
                            st.session_state.P_MPa,
                            f"protokol_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{st.session_state.user_sensor}.txt"
                        )
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.warning("Сначала выполните расчет")
            
            if st.session_state.show_report:
                with st.expander("📄 Протокол расчета", expanded=True):
                    if 'report_text' in st.session_state:
                        if MOBILE:
                            st.text(st.session_state.report_text)
                        else:
                            st.code(st.session_state.report_text, language='text')
                        
                        if 'report_filename' in st.session_state:
                            st.info(f"💾 Файл: {st.session_state.report_filename}")
                        
                        if st.button("❌ Закрыть"):
                            st.session_state.show_report = False
                            st.rerun()
                    else:
                        st.warning("Протокол не найден")
        
        else:
            st.info("👆 Заполните данные и нажмите 'Рассчитать'")

# ============================================================
# БЛОК 12: ПОДВАЛ
# ============================================================

st.markdown(f"""
<div class="footer">
    <div class="company">🧪 Калькулятор свойств углеводородов</div>
    <div class="group">ООО «ИЗП» · Группа моделирования технологических процессов</div>
    <div class="lead">под руководством Клепцова Д.В.</div>
    <div style="margin-top:10px; font-size:12px; color:#95a5a6;">
        Python · Streamlit · Peng-Robinson · GERG-2008
    </div>
</div>
""", unsafe_allow_html=True)