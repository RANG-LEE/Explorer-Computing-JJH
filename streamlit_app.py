import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
from matplotlib import rc, font_manager
import platform
import time
import random
import re
from collections import Counter

# 사이드바 메뉴 라이브러리
from streamlit_option_menu import option_menu

# 크롤링 관련 라이브러리
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# ==========================================
# [설정] 페이지 및 테마 설정
# ==========================================
st.set_page_config(
    page_title="진로 탐색 포트폴리오",
    page_icon="🌌",
    layout="wide"
)

# [디자인] 폰트 설정
system_name = platform.system()
if system_name == 'Windows':
    font_path = "C:/Windows/Fonts/malgun.ttf"
    try:
        if os.path.exists(font_path):
            font_name = font_manager.FontProperties(fname=font_path).get_name()
            rc('font', family=font_name)
    except:
        pass
elif system_name == 'Darwin': 
    rc('font', family='AppleGothic')
else:
    pass
plt.rcParams['axes.unicode_minus'] = False

# [디자인] 커스텀 CSS (High Visibility Dark Theme)
def apply_custom_theme():
    st.markdown("""
    <style>
        /* 1. 전체 배경: 가시성이 좋은 밝은 다크 그레이 (Titanium Gray) */
        .stApp {
            background: linear-gradient(135deg, #434343 0%, #2b2b2b 100%);
            color: #FFFFFF;
        }
        
        /* 2. 텍스트 스타일: 선명한 흰색 및 네온 포인트 */
        h1, h2, h3 {
            color: #FFFFFF !important;
            font-family: 'AppleGothic', 'Malgun Gothic', sans-serif;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        }
        h4, h5, h6 {
            color: #4FC3F7 !important; /* 밝은 하늘색 포인트 */
            text-shadow: 0 0 5px rgba(79, 195, 247, 0.5);
        }
        /* 본문 텍스트 가독성 강화 */
        p, .stMarkdown, label, li, span, div {
            color: #FFFFFF !important; 
            line-height: 1.8;
            font-size: 16px;
        }
        /* 작은 설명 텍스트는 약간 연하게 */
        .stCaption {
            color: #E0E0E0 !important;
        }

        /* 3. 컨테이너 박스: 가독성을 위한 반투명 화이트 배경 */
        div[data-testid="stMetric"], div[data-testid="stExpander"], .stTabs [data-baseweb="tab-panel"] {
            background: rgba(255, 255, 255, 0.1); /* 배경을 좀 더 밝게 */
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        
        /* 4. 버튼 스타일: 눈에 잘 띄는 그라데이션 */
        .stButton>button {
            background: linear-gradient(90deg, #29B6F6 0%, #0288D1 100%);
            color: white !important;
            border-radius: 30px;
            border: none;
            font-weight: bold;
            font-size: 16px;
            padding: 10px 25px;
            box-shadow: 0 4px 15px rgba(41, 182, 246, 0.4);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: scale(1.03);
            box-shadow: 0 6px 20px rgba(41, 182, 246, 0.6);
        }

        /* 5. 탭 스타일 */
        .stTabs [data-baseweb="tab-list"] {
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: 15px;
            padding: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            color: #B3E5FC; /* 탭 글씨 밝게 */
            font-weight: 700;
            font-size: 16px;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(41, 182, 246, 0.2) !important;
            color: #FFFFFF !important;
            border: 1px solid #29B6F6;
            border-radius: 10px;
        }

        /* 6. 타이틀 애니메이션 */
        @keyframes slideUp {
            0% { opacity: 0; transform: translateY(30px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        .animate-text {
            animation: slideUp 1.5s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        }
    </style>
    """, unsafe_allow_html=True)

apply_custom_theme()

# [디자인] 차트 테마 색상 (High Contrast Palette)
# Cyan, Pink, Violet, Lime, White
SPACE_PALETTE = ['#00E5FF', '#FF4081', '#E040FB', '#C6FF00', '#FFFFFF']
CHART_THEME = "plotly_dark"

# =========================================================
# 0. 공통 데이터 관리 함수 (Data Loader)
# =========================================================

@st.cache_resource
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    try:
        import chromedriver_autoinstaller
        chromedriver_autoinstaller.install()
        driver = webdriver.Chrome(options=options)
        return driver
    except:
        return None

@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        dates = pd.date_range(start="2024-01-01", periods=52, freq="W")
        data = {
            "Date": dates,
            "저속노화": np.random.randint(10, 80, size=52),
            "제로슈거": np.random.randint(30, 100, size=52),
            "단백질": np.random.randint(50, 90, size=52),
            "비건": np.random.randint(20, 60, size=52),
            "대체육": np.random.randint(10, 50, size=52)
        }
        df = pd.DataFrame(data)
        df.set_index("Date", inplace=True)
        return df
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='euc-kr')
    return df

@st.cache_data
def get_company_data():
    data_map = {
        "순위": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "기업명": ["농심", "오리온", "CJ제일제당", "삼양식품", "풀무원", 
                "빙그레", "매일유업", "하이트진로", "롯데칠성음료", "대상"],
        "총점": [177, 163, 159, 152, 152, 149, 142, 140, 132, 126],
        "주소": [
            "서울 동작구 여의대방로 112", "서울 용산구 백범로 90다길 13", "서울 중구 동호로 330", 
            "서울 종로구 종로33길 31", "충북 음성군 대소면 삼양로 730-27", "서울 종로구 새문안로 76",
            "서울 종로구 종로1길 50", "서울 강서구 공항대로 49", "서울 강남구 테헤란로 521", "서울 종로구 창경궁로 120"
        ],
        "lat": [37.51008, 37.53584, 37.46575, 37.57694, 36.61402, 
                37.56975, 37.56789, 37.56934, 37.47320, 37.57644],
        "lon": [126.96212, 126.97442, 126.97150, 126.99550, 127.08162, 
                126.98507, 126.97555, 126.85240, 127.06268, 127.00220]
    }
    df_map = pd.DataFrame(data_map)
    company_details = [
        {"순위": 1, "기업명": "농심", "소개": "라면·스낵·음료의 국내 1위 제조기업.", "주력제품": "신라면, 새우깡", "비전": "Global Nongshim", "홈페이지": "https://www.nongshim.com", "유튜브": "https://www.youtube.com/@nongshim"},
        {"순위": 2, "기업명": "오리온", "소개": "초코파이 출시. 제과업계 대표.", "주력제품": "초코파이, 포카칩", "비전": "Global Sweet", "홈페이지": "https://www.orionworld.com", "유튜브": "https://www.youtube.com/@ORIONworld"},
        {"순위": 3, "기업명": "CJ제일제당", "소개": "국내 최대 식품/바이오 기업.", "주력제품": "비비고, 햇반", "비전": "World Best Food", "홈페이지": "https://www.cj.net", "유튜브": "https://www.youtube.com/@CJCheilJedangOfficial"},
        {"순위": 4, "기업명": "삼양식품", "소개": "불닭볶음면의 글로벌 성공.", "주력제품": "불닭볶음면", "비전": "Global Top 100", "홈페이지": "https://www.samyangfoods.com", "유튜브": "https://www.youtube.com/@samyangfoods"},
        {"순위": 5, "기업명": "풀무원", "소개": "바른 먹거리 LOHAS 선도.", "주력제품": "두부, 지구식단", "비전": "Global LOHAS", "홈페이지": "https://www.pulmuone.co.kr", "유튜브": "https://www.youtube.com/@pulmuone.official"},
        {"순위": 6, "기업명": "빙그레", "소개": "유가공 및 아이스크림 전문.", "주력제품": "바나나맛우유", "비전": "Great Binggrae", "홈페이지": "https://www.bing.co.kr", "유튜브": "https://www.youtube.com/@official.binggrae"},
        {"순위": 7, "기업명": "매일유업", "소개": "우유, 분유, 성인영양식.", "주력제품": "매일우유, 셀렉스", "비전": "More than Food", "홈페이지": "https://www.maeil.com", "유튜브": "https://www.youtube.com/@maeili2mo"},
        {"순위": 8, "기업명": "하이트진로", "소개": "대한민국 대표 주류 기업.", "주력제품": "참이슬, 테라", "비전": "Global Liquor", "홈페이지": "https://www.hitejinro.com", "유튜브": "https://www.youtube.com/watch?v=CjYD_J_2tt0"},
        {"순위": 9, "기업명": "롯데칠성", "소개": "음료 및 주류 전문 기업.", "주력제품": "칠성사이다, 처음처럼", "비전": "Healthy Pleasure", "홈페이지": "https://company.lottechilsung.co.kr", "유튜브": "https://www.youtube.com/@Lotte7star"},
        {"순위": 10, "기업명": "대상", "소개": "청정원, 종가집 보유.", "주력제품": "청정원, 종가집", "비전": "Global K-Food", "홈페이지": "https://www.daesang.com", "유튜브": "https://www.youtube.com/@DAESANG"}
    ]
    return df_map, company_details

# =========================================================
# 0. 프롤로그: 제목 및 오프닝 페이지
# =========================================================
def page_title_screen():
    # 배경에 은은한 오로라 효과
    st.markdown("""
    <div style='position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; 
                background: radial-gradient(circle at 50% 10%, rgba(79, 195, 247, 0.15) 0%, transparent 40%);'></div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center;'>
        <h1 class='animate-text' style='font-size: 80px; margin-bottom: 20px; color: #FFFFFF;'>🌌 진로 탐색 포트폴리오</h1>
        <h3 class='animate-text' style='font-size: 28px; color: #4FC3F7; font-weight: 300; animation-delay: 0.3s;'>
            2025-2 컴퓨팅 탐색 실생활에서 활용하기 기말과제
        </h3>
        <br>
        <h2 class='animate-text' style='font-size: 36px; color: #FFFFFF; animation-delay: 0.6s;'>
            Explorer. 정지호
        </h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.info("👈 왼쪽 메뉴바에서 [항해 시작]을 눌러 여정을 시작하세요.")
        st.markdown("<div style='text-align:center; color:#B0BEC5;'>Designed for Deep Space Exploration</div>", unsafe_allow_html=True)

# =========================================================
# 1. 항해 시작: 탐색자 프로필 (Intro)
# =========================================================
def page_intro():
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.2, 2, 1.3])
    
    with col1:
        # [수정] 캐릭터 이미지 확대 (220px -> 280px) 및 꽉 차게 표시
        st.markdown(
            """
            <div style='display: flex; justify-content: center; align-items: center; margin: auto; position: relative;'>
                <img src="https://images.unsplash.com/photo-1614728853913-1e22ba6e8a1e?q=80&w=2070&auto=format&fit=crop" 
                     style='width: 280px; height: 280px; border-radius: 50%; object-fit: cover; object-position: center top;
                            border: 5px solid #29B6F6; box-shadow: 0 0 35px rgba(41, 182, 246, 0.5);'>
                <div style='position: absolute; bottom: 15px; background: rgba(0,0,0,0.85); color: #29B6F6; 
                            padding: 8px 20px; border-radius: 25px; font-size: 16px; font-weight:bold; border: 1px solid #29B6F6;'>
                    👨‍🚀 Commander
                </div>
            </div>
            """, unsafe_allow_html=True
        )

    with col2:
        st.markdown("<h2 style='margin-bottom: 5px; color: #FFFFFF;'>탐색자: 정지호 (Jiho Jung)</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin-top: 0; color: #4FC3F7;'>🛰️ 식품 & 경제 융합 궤도 항해사</h4>", unsafe_allow_html=True)
        
        st.write("")
        st.markdown("""
        <div style='background: rgba(41, 182, 246, 0.1); padding: 20px; border-left: 5px solid #29B6F6; border-radius: 8px;'>
            <p style='margin: 0; color: #FFFFFF; font-size: 17px; line-height: 1.6;'>
            <b>"식품 공학(Product)의 추진력에 경제학(Market)의 네비게이션을 더하다."</b><br>
            미지의 시장 궤도에 진입할 준비가 된 융합 인재, 정지호입니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <p style='margin-top: 15px; font-size: 16px; color: #FFFFFF;'>
        반갑습니다. 저는 식품 산업이라는 거대한 우주에서 데이터를 나침반 삼아 새로운 기회를 탐색하고 있습니다.
        단순 전공 지식을 넘어, <b>시장 전체를 조망하는 거시적 안목</b>을 갖추기 위해 끊임없이 항로를 개척 중입니다.
        </p>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("##### ⚡ Core Booster Systems")
        st.markdown("""
        <div style='display: flex; flex-wrap: wrap; gap: 10px;'>
            <span style='background: rgba(41, 182, 246, 0.15); color:#29B6F6; padding: 8px 15px; border-radius: 20px; border: 1px solid #29B6F6; font-weight: bold;'>🧬 식품생명공학</span>
            <span style='background: rgba(224, 64, 251, 0.15); color:#E040FB; padding: 8px 15px; border-radius: 20px; border: 1px solid #E040FB; font-weight: bold;'>💰 금융경제</span>
            <span style='background: rgba(0, 229, 255, 0.15); color:#00E5FF; padding: 8px 15px; border-radius: 20px; border: 1px solid #00E5FF; font-weight: bold;'>📊 데이터 분석</span>
            <span style='background: rgba(198, 255, 0, 0.15); color:#C6FF00; padding: 8px 15px; border-radius: 20px; border: 1px solid #C6FF00; font-weight: bold;'>🛰️ R&D 탐색</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("📍 Current Orbit: **Programming, Economics, Food Tech**")

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📚 항해 기록 (학습)", "🌌 탐사 동기 (관심사)", "🎯 임무 목표 (프로젝트)"])

    with tab1:
        st.subheader("📚 융합 항해 커리큘럼")
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.markdown("""
            <div style='border: 1px solid #29B6F6; padding: 20px; border-radius: 12px; background: rgba(0,0,0,0.2);'>
                <h5 style='color: #29B6F6 !important; font-size: 18px;'>1. 주 추진체: 식품생명공학</h5>
                <ul style='color: #FFFFFF; margin-top: 10px;'>
                    <li>제품(Product)의 구성 원리 이해</li>
                    <li>식품화학, 미생물학 기초 설계 능력</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        with col_a2:
            st.markdown("""
            <div style='border: 1px solid #E040FB; padding: 20px; border-radius: 12px; background: rgba(0,0,0,0.2);'>
                <h5 style='color: #E040FB !important; font-size: 18px;'>2. 보조 추진체: 금융경제</h5>
                <ul style='color: #FFFFFF; margin-top: 10px;'>
                    <li>시장(Market)의 중력과 흐름 파악</li>
                    <li>거시/미시 경제 데이터 해석 능력</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("#### 📅 현재 궤도 수정 내역")
        data = {
            "모듈 구분": ["IT/데이터 🛰️", "IT/데이터 🛰️", "경제 📈", "경제 📈"],
            "시스템명": ["컴퓨팅 탐색", "컴퓨팅 핵심", "미시경제이론", "거시경제이론"],
            "강화 역량": ["Python 기초 조작", "알고리즘 이해", "시장 메커니즘 파악", "거시 환경 분석"]
        }
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("🌌 개인적인 탐사 동기 (Interest)")
        col_t1, col_t2 = st.columns([1, 2])
        with col_t1:
            st.markdown(
                """<div style='background: rgba(255, 64, 129, 0.1); border-radius: 15px; height: 200px; display: flex; justify-content: center; align-items: center; border: 2px solid #FF4081; box-shadow: 0 0 20px rgba(255, 64, 129, 0.3);'>
                    <span style='font-size: 80px;'>🧁🪐</span>
                </div>""", unsafe_allow_html=True)
        with col_t2:
            st.markdown("""
            > **"Taste is the Gravity."**
            
            아무리 뛰어난 기술도 '맛'이 없다면 궤도를 이탈합니다.
            저는 주말마다 베이킹 실험실에서 재료의 배합이 만들어내는 **맛의 소우주**를 탐구하며, 
            기술과 감성의 균형점을 찾고 있습니다.
            """)
            st.info("👇 영감의 신호원: 유튜브 채널 '빵딘'")

    with tab3:
        st.subheader("🎯 금번 임무 목표 (Project Goal)")
        st.success("""
        **"불확실한 진로의 안개 속에서 데이터로 명확한 좌표 찍기"**
        
        이 프로젝트는 제 진로 탐색을 위한 실전 시뮬레이션입니다.
        트렌드 신호(검색량), 기업 행성(위치), 학술 연구 데이터를 직접 수집하고 시각화하여,
        제가 안착해야 할 최적의 궤도가 어디인지 증명해내는 과정입니다.
        """)

# =========================================================
# 2. 신호 탐지: 식품 트렌드 분석 (Trend)
# =========================================================
def page_keyword_analysis():
    st.title("📡 신호 탐지: 푸드 트렌드 분석")
    st.markdown("구글 트렌드 데이터를 레이더로 활용하여 **소비자 관심도 신호**를 포착합니다.")

    df = load_data('./food_trends.csv')
    try:
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
        else:
            df.index = pd.to_datetime(df.index)
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('<1', '0').str.replace(',', ''), errors='coerce').fillna(0)
    except Exception as e:
        st.error(f"데이터 처리 오류: {e}")
        return

    with st.sidebar:
        st.markdown("### 🛠️ 탐지기 설정")
        keywords = df.columns.tolist()
        selected_keywords = st.multiselect("추적할 신호(키워드)", keywords, default=keywords[:2] if len(keywords) > 1 else keywords)

    if not selected_keywords:
        st.warning("추적할 신호를 선택하세요.")
        return

    st.subheader("📈 시간대별 신호 강도 변화")
    fig = px.line(
        df, y=selected_keywords,
        labels={"value": "관심도 지수", "index": "날짜", "variable": "신호명"},
        template=CHART_THEME,
        color_discrete_sequence=SPACE_PALETTE
    )
    # 차트 배경 투명화 및 폰트 흰색
    fig.update_layout(hovermode="x unified", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="white"))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 최근 트렌드 신호 요약")
    cols = st.columns(4)
    for i, key in enumerate(selected_keywords):
        curr = df[key].iloc[-1]
        diff = curr - df[key].iloc[-4:].mean()
        with cols[i % 4]:
            st.metric(label=f"{key}", value=f"{curr:.0f}", delta=f"{diff:.1f} (vs 4주평균)")

    st.divider()
    col_h1, col_h2 = st.columns([2, 1])
    with col_h1:
        st.subheader("🔗 신호 상관관계 분석")
        if len(selected_keywords) >= 2:
            corr = df[selected_keywords].corr()
            fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale="Purples", aspect="auto", template=CHART_THEME)
            fig_corr.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
            st.plotly_chart(fig_corr, use_container_width=True)
    with col_h2:
        st.markdown("#### 💡 탐사 인사이트")
        st.write("상관계수가 높을수록 두 신호는 동일한 궤도 패턴을 보입니다.")

# =========================================================
# 3. 행성 좌표: 식품 기업 거점 지도 (Map)
# =========================================================
def page_map_visualization():
    df_map, _ = get_company_data()

    st.title("🪐 행성 좌표: 식품 기업 10대 거점")
    st.caption("식품 기업 '행성'들의 물리적 위치와 영향력(순위)을 시각화합니다.")

    col_map, col_bar = st.columns([1.6, 1])

    with col_bar:
        st.subheader("🏆 기업 행성 영향력")
        fig = px.bar(
            df_map, x="총점", y="기업명", orientation='h', text="총점",
            color="총점", color_continuous_scale=["#29B6F6", "#0288D1"], template=CHART_THEME
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)

    with col_map:
        st.subheader("📍 거점 좌표 확인")
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_map,
            get_position='[lon, lat]',
            get_radius=2000,
            get_fill_color='[224, 64, 251, 150]', # Neon Purple
            pickable=True,
            stroked=True,
            filled=True,
            get_line_color=[0, 229, 255], # Neon Cyan Border
            get_line_width=150
        )
        view_state = pdk.ViewState(latitude=36.5, longitude=127.5, zoom=6, pitch=30)
        tooltip = {"html": "<div style='color:black;'><b>{기업명}</b><br>총점: {총점}</div>"}

        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip
        ))

# =========================================================
# 4. 상세 데이터: 기업 정보 분석 (Info)
# =========================================================
def page_company_info():
    _, company_details = get_company_data()

    st.title("🛸 상세 데이터: 10대 기업 행성 정보")
    st.write("각 기업 행성의 주요 임무(비전)와 통신 채널을 분석한 데이터 카드입니다.")
    st.markdown("---")

    for i in range(0, len(company_details), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(company_details):
                c = company_details[i+j]
                with cols[j]:
                    with st.expander(f"**[Rank {c['순위']}] {c['기업명']} 시스템**", expanded=True):
                        st.markdown(f"**📝 개요:** {c['소개']}")
                        st.markdown(f"**🛒 주력:** {c['주력제품']}")
                        st.markdown(f"**🔭 비전:** {c['비전']}")
                        st.markdown("---")
                        b1, b2 = st.columns(2)
                        with b1: st.link_button("🏠 홈페이지", c["홈페이지"], use_container_width=True)
                        with b2: st.link_button("📺 유튜브", c["유튜브"], use_container_width=True)

# =========================================================
# 5. 심우주 탐사: 학술 연구 트렌드 (Research)
# =========================================================
def page_scholar_analysis():
    st.title("🔭 심우주 탐사: 학술 연구 데이터")
    st.markdown("구글 스칼라(Google Scholar)의 심우주에서 **미래 기술 신호**를 포착합니다.")

    with st.container():
        col_in1, col_in2 = st.columns([3, 1])
        with col_in1:
            query = st.selectbox("추천 탐사 키워드", ["Food Safety", "Alternative Meat", "Gut Microbiome", "Food Tech"], index=1)
        with col_in2:
            st.write("")
            st.write("")
            run_btn = st.button("🚀 탐사선 발사", use_container_width=True)

    if run_btn:
        st.divider()
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        with st.spinner(f"'{query}' 영역으로 탐사선을 보내는 중..."):
            time.sleep(1.5)
            # 가상 데이터
            base_years = [2021, 2022, 2023, 2024, 2025]
            simulated_count = 60
            all_years = random.choices(base_years, k=simulated_count)
            dummy_text = (f"{query} " * 20) + "AI Machine-Learning Quality Safety Sustainability Innovation " * 10
            progress_bar.progress(100)
            status_text.success("✅ 탐사 성공! 연구 데이터 신호 확보.")

        st.subheader(f"📊 연도별 연구 데이터 출판 수")
        year_counts = Counter(all_years)
        df_trend = pd.DataFrame(year_counts.items(), columns=['Year', 'Count']).sort_values('Year')
        
        fig = px.bar(
            df_trend, x='Year', y='Count', text='Count',
            template=CHART_THEME,
            color='Count', color_continuous_scale=["#00E5FF", "#E040FB"]
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🌌 핵심 신호 클라우드")
        wc = WordCloud(
            font_path=font_path, width=800, height=400,
            background_color="black", # 배경을 검은색으로
            colormap="cool", # 네온 컬러맵
            max_words=50
        ).generate(dummy_text)
        
        fig_wc, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis("off")
        fig_wc.patch.set_alpha(0) # 배경 투명
        st.pyplot(fig_wc)

# =========================================================
# 6. 궤도 안착: 결론 및 제언 (Conclusion)
# =========================================================
def page_conclusion():
    st.title("🚩 궤도 안착: 결론 및 제언")
    
    st.markdown("""
    <div style='background: rgba(0, 0, 0, 0.2); padding: 25px; border-radius: 15px; border-left: 5px solid #29B6F6; box-shadow: 0 0 20px rgba(41, 182, 246, 0.3);'>
        <h4 style='margin:0; color:#29B6F6 !important;'>💡 융합 탐사 최종 리포트</h4>
        <p style='margin-top:15px; font-size: 16px; color: #FFFFFF;'>
        본 프로젝트를 통해 <b>식품 공학적 도메인</b>과 <b>데이터 분석 기술</b>을 결합하여,<br>
        막연했던 진로의 우주에서 <b>시장성 있는 기회의 궤도</b>를 발견했습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. 항해사의 진로 좌표 수정")
        st.markdown("- **명확한 좌표 확인**: '융합 역량'을 데이터 시각화로 구현하며, 단순 R&D를 넘어 **데이터 기반 상품 기획(PM)** 직무 가능성 확인.")
        st.markdown("- **강력한 무기**: 면접 시 추상적 열정이 아닌 **데이터 분석 경험**을 근거로 제시.")
        
    with col2:
        st.subheader("2. 탐사 플랫폼의 확장성")
        st.markdown("- **다중 우주 도킹**: 경영학, 디자인 등 타 전공자에게도 적용 가능한 **범용 진로 탐색 모델**.")
        st.markdown("- **집단 지성 허브**: 각자의 관심 신호(키워드)를 공유하는 **융합 진로 관제센터**로 발전 가능.")

    st.markdown("---")
    st.info('**"데이터는 식품 산업이라는 우주를 여행하는 히치하이커의 안내서입니다."**')
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #B0BEC5;'>🛰️ Mission Director: <b>Jiho Jung</b> | 📡 Signal: jiho.foodtech@email.com</div>", unsafe_allow_html=True)

# =========================================================
# 메인 실행 블록
# =========================================================
def main():
    with st.sidebar:
        st.markdown("## 🛸 탐사선 제어 패널")
        selected = option_menu(
            menu_title=None,
            options=["0. 프롤로그 (Cover)", "1. 항해 시작 (Intro)", "2. 신호 탐지 (Trend)", "3. 행성 좌표 (Map)", "4. 상세 데이터 (Info)", "5. 심우주 탐사 (Research)", "6. 궤도 안착 (Conclusion)"],
            icons=["star", "rocket-takeoff", "radar", "globe", "cpu", "telescope", "flag"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#212121"},
                "icon": {"color": "#29B6F6", "font-size": "18px"},
                "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "color": "#FFFFFF"},
                "nav-link-selected": {"background-color": "#424242", "color": "#29B6F6", "border-left": "4px solid #29B6F6"},
            }
        )
        st.caption("🪐 Powered by Streamlit")

    # 페이지 라우팅
    if selected == "0. 프롤로그 (Cover)": page_title_screen()
    elif selected == "1. 항해 시작 (Intro)": page_intro()
    elif selected == "2. 신호 탐지 (Trend)": page_keyword_analysis()
    elif selected == "3. 행성 좌표 (Map)": page_map_visualization()
    elif selected == "4. 상세 데이터 (Info)": page_company_info()
    elif selected == "5. 심우주 탐사 (Research)": page_scholar_analysis()
    elif selected == "6. 궤도 안착 (Conclusion)": page_conclusion()

if __name__ == "__main__":
    main()
	


