import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pydeck as pdk
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
from matplotlib import rc, font_manager
import platform
import time
import random
from collections import Counter
from streamlit_option_menu import option_menu

# 페이지 및 테마 설정
st.set_page_config(
    page_title="진로 탐색 포트폴리오",
    page_icon="🌌",
    layout="wide"
)

# 폰트 설정
system_name = platform.system()
font_path = None

if system_name == 'Windows':
    _font_path = "C:/Windows/Fonts/malgun.ttf"
    try:
        if os.path.exists(_font_path):
            font_name = font_manager.FontProperties(fname=_font_path).get_name()
            rc('font', family=font_name)
            font_path = _font_path
    except:
        pass
elif system_name == 'Darwin': 
    rc('font', family='AppleGothic')
    font_path = '/System/Library/Fonts/AppleGothic.ttf'
else:
    plt.rcParams['font.family'] = 'sans-serif'

plt.rcParams['axes.unicode_minus'] = False

# 커스텀 CSS 적용
# [디자인] 커스텀 CSS (수정됨: 입력창 글씨 짙은 파란색 적용)
def apply_custom_theme():
    st.markdown("""
    <style>
        /* 1. 전체 앱 배경 및 폰트 설정 (기존 유지) */
        .stApp {
            background: linear-gradient(135deg, #434343 0%, #2b2b2b 100%);
            color: #FFFFFF;
        }
        h1, h2, h3 {
            color: #FFFFFF !important;
            font-family: 'AppleGothic', 'Malgun Gothic', sans-serif;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        }
        h4, h5, h6 {
            color: #4FC3F7 !important;
            text-shadow: 0 0 5px rgba(79, 195, 247, 0.5);
        }
        p, .stMarkdown, label, li, span, div {
            color: #FFFFFF !important; 
            line-height: 1.8;
            font-size: 16px;
        }
        .stCaption {
            color: #E0E0E0 !important;
        }

        /* 2. 컨테이너 스타일 (기존 유지) */
        div[data-testid="stMetric"], div[data-testid="stExpander"], .stTabs [data-baseweb="tab-panel"] {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }

        /* 3. 버튼 스타일 (기존 유지) */
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

        /* 4. 탭 스타일 (기존 유지) */
        .stTabs [data-baseweb="tab-list"] {
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: 15px;
            padding: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            color: #B3E5FC;
            font-weight: 700;
            font-size: 16px;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(41, 182, 246, 0.2) !important;
            color: #FFFFFF !important;
            border: 1px solid #29B6F6;
            border-radius: 10px;
        }

        /* 5. [중요 수정] 입력 필드 (Selectbox) 스타일 */
        
        /* 입력창 박스 배경: 밝은 회색 (#F0F0F0) */
        div[data-baseweb="select"] > div, 
        div[data-baseweb="base-input"] {
            background-color: #F0F0F0 !important;
            border: 2px solid #29B6F6 !important; /* 테두리도 파란색 강조 */
        }
        
        /* [수정됨] 입력창 내부 텍스트: 짙은 파란색 (#0D47A1) */
        div[data-baseweb="select"] span,
        div[data-baseweb="base-input"] input {
            color: #0D47A1 !important; 
            -webkit-text-fill-color: #0D47A1 !important;
            font-weight: 800 !important; /* 폰트 더 굵게 */
        }

        /* [수정됨] 드롭다운 아이콘(화살표): 짙은 파란색 */
        div[data-baseweb="select"] svg {
            fill: #0D47A1 !important;
        }

        /* 드롭다운 메뉴 리스트 (팝업) 배경: 흰색 */
        ul[data-baseweb="menu"] {
            background-color: #FFFFFF !important;
        }
        
        /* 드롭다운 메뉴 리스트 내부 글씨: 검은색 (가독성 유지) */
        ul[data-baseweb="menu"] li span {
            color: #000000 !important;
        }
        
        /* 멀티셀렉트 태그 (선택된 항목) 스타일 */
        span[data-baseweb="tag"] {
            background-color: #0288D1 !important;
        }
        span[data-baseweb="tag"] span {
            color: white !important;
        }

        /* 애니메이션 */
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

SPACE_PALETTE = ['#00E5FF', '#FF4081', '#E040FB', '#C6FF00', '#FFFFFF']
CHART_THEME = "plotly_dark"

# 데이터 로드 함수
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
        {
            "순위": 1, 
            "기업명": "농심", 
            "소개": "1965년 설립, '한국의 맛'을 세계로 전하는 국내 부동의 1위 식품 기업. 라면 시장 점유율 50% 이상을 차지하며, 최근 미국 제2공장 가동과 함께 북미 시장에서 폭발적인 성장을 기록 중입니다.", 
            "주력제품": "신라면(블랙/레드), 짜파게티, 너구리, 새우깡, 먹태깡, 백산수", 
            "비전": "Life with Good Health", 
            "홈페이지": "https://www.nongshim.com", 
            "유튜브": "https://www.youtube.com/@nongshim"
        },
        {
            "순위": 2, 
            "기업명": "오리온", 
            "소개": "제과를 넘어 닥터유(건강), 바이오로 확장 중인 글로벌 식품 헬스케어 기업. 중국, 베트남, 러시아 법인의 고성장으로 해외 매출 비중이 국내를 넘어선 진정한 글로벌 기업입니다.", 
            "주력제품": "초코파이 情, 포카칩, 꼬북칩, 닥터유(단백질바), 마켓오", 
            "비전": "Global Food & Healthcare Company", 
            "홈페이지": "https://www.orionworld.com", 
            "유튜브": "https://www.youtube.com/@ORIONworld"
        },
        {
            "순위": 3, 
            "기업명": "CJ제일제당", 
            "소개": "국내 식품 산업을 이끄는 최대 규모의 기업이자 글로벌 바이오 강자. '비비고' 브랜드로 K-Food의 세계화를 주도하고 있으며, 그린 바이오(사료용 아미노산) 분야 세계 1위 경쟁력을 보유했습니다.", 
            "주력제품": "비비고(만두/김치), 햇반, 고메, 백설, 다시다, 바이오(라이신)", 
            "비전": "World Best Food & Bio Company", 
            "홈페이지": "https://www.cj.net", 
            "유튜브": "https://www.youtube.com/@CJCheilJedangOfficial"
        },
        {
            "순위": 4, 
            "기업명": "삼양식품", 
            "소개": "1963년 국내 최초의 라면을 출시한 원조 기업. '불닭볶음면'이 유튜브를 통해 글로벌 챌린지 열풍을 일으키며, 해외 매출 비중이 70%에 달하는 '수출 역군'으로 재탄생했습니다.", 
            "주력제품": "불닭볶음면 시리즈, 삼양라면, 맵탱, 쿠티크", 
            "비전": "Global Comprehensive Food & Solution Company)", 
            "홈페이지": "https://www.samyangfoods.com", 
            "유튜브": "https://www.youtube.com/@samyangfoods"
        },
        {
            "순위": 5, 
            "기업명": "풀무원", 
            "소개": "국내 최초로 포장 두부와 콩나물을 출시하며 '바른 먹거리' 개념을 정립한 ESG 경영 선도 기업. 최근 식물성 지향 식품(지구식단)과 미국 두부 시장 1위를 기반으로 글로벌 확장을 가속화하고 있습니다.", 
            "주력제품": "국산콩 두부, 식물성 지구식단, 얇은피 만두, 아임리얼", 
            "비전": "Global No.1 LOHAS Company", 
            "홈페이지": "https://www.pulmuone.co.kr", 
            "유튜브": "https://www.youtube.com/@pulmuone.official"
        },
        {
            "순위": 6, 
            "기업명": "빙그레", 
            "소개": "가공유 1위 '바나나맛우유'와 아이스크림 명가. 해태아이스크림 인수로 빙과 시장 점유율을 획기적으로 높였으며, '메로나'는 미국 코스트코 등 해외 시장에서 K-아이스크림의 대명사가 되었습니다.", 
            "주력제품": "바나나맛우유, 요플레, 투게더, 메로나, 붕어싸만코, 슈퍼콘", 
            "비전": "Creator of Bright Smiles", 
            "홈페이지": "https://www.bing.co.kr", 
            "유튜브": "https://www.youtube.com/@official.binggrae"
        },
        {
            "순위": 7, 
            "기업명": "매일유업", 
            "소개": "낙농업 기반의 종합 식품 기업. 저출산 위기를 극복하기 위해 성인 영양식 '셀렉스'와 식물성 음료 '어메이징 오트'로 사업 포트폴리오를 성공적으로 다각화했습니다.", 
            "주력제품": "매일우유, 상하목장, 앱솔루트(분유), 셀렉스(단백질), 어메이징 오트", 
            "비전": "More than Food, Beyond Korea", 
            "홈페이지": "https://www.maeil.com", 
            "유튜브": "https://www.youtube.com/@maeili2mo"
        },
        {
            "순위": 8, 
            "기업명": "하이트진로", 
            "소개": "1924년 설립된 대한민국 주류 역사의 산증인. 국민 소주 '참이슬'과 청정 라거 '테라', 그리고 '켈리'의 연타석 홈런으로 소주-맥주 시장을 동시에 석권하고 있습니다.", 
            "주력제품": "참이슬, 진로(이즈백), 테라, 켈리, 일품진로", 
            "비전": "Global Public Brewer", 
            "홈페이지": "https://www.hitejinro.com", 
            "유튜브": "https://www.youtube.com/watch?v=CjYD_J_2tt0"
        },
        {
            "순위": 9, 
            "기업명": "롯데칠성", 
            "소개": "음료와 주류를 아우르는 종합 음료 기업. '칠성사이다'의 헤리티지에 '제로 슈거' 트렌드를 완벽히 결합(펩시 제로, 새로 소주)하며 제2의 전성기를 맞이했습니다.", 
            "주력제품": "칠성사이다(제로), 펩시(제로), 처음처럼, 새로, 밀키스", 
            "비전": "Healthy Reverence", 
            "홈페이지": "https://company.lottechilsung.co.kr", 
            "유튜브": "https://www.youtube.com/@Lotte7star"
        },
        {
            "순위": 10, 
            "기업명": "대상", 
            "소개": "국내 최초의 발효 조미료 '미원'으로 시작한 종합 식품 기업. 김치 브랜드 '종가(Jongga)'를 앞세워 글로벌 김치 시장을 장악하고 있으며, 소재(전분당, 라이신) 사업에서도 강력한 입지를 보유 중입니다.", 
            "주력제품": "청정원, 미원, 종가(김치), O'Food(글로벌), 안주야", 
            "비전": "Creating a healthy future for people and nature)", 
            "홈페이지": "https://www.daesang.com", 
            "유튜브": "https://www.youtube.com/@DAESANG"
        }
    ]
    return df_map, company_details

# 프롤로그 페이지
def page_title_screen():
    st.markdown("""
    <div style='position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; 
                background: radial-gradient(circle at 50% 10%, rgba(79, 195, 247, 0.15) 0%, transparent 40%);'></div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center;'>
        <h1 class='animate-text' style='font-size: 80px; margin-bottom: 20px; color: #FFFFFF !important;'>🌌 진로 탐색 포트폴리오</h1>
        <h3 class='animate-text' style='font-size: 28px; color: #4FC3F7 !important; font-weight: 300; animation-delay: 0.3s;'>
            2025-2 컴퓨팅 탐색 실생활에서 활용하기 기말과제
        </h3>
        <br>
        <h2 class='animate-text' style='font-size: 36px; color: #FFFFFF !important; animation-delay: 0.6s;'>
            Explorer. 정지호
        </h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.info("👈 왼쪽 메뉴바에서 [항해 시작]을 눌러 여정을 시작하세요.")
        st.markdown("<div style='text-align:center; color:#B0BEC5 !important;'>Designed for Deep Space Exploration</div>", unsafe_allow_html=True)

# 항해 시작 (Intro)
def page_intro():
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.3, 2, 1.3], gap="medium")
    
    with col1:
        st.markdown(
            """
            <div style='display: flex; flex-direction: column; align-items: center; justify-content: center;'>
                <div style='
                    width: 240px; height: 240px;
                    border-radius: 50%;
                    border: 5px solid #29B6F6;
                    box-shadow: 0 0 35px rgba(41, 182, 246, 0.5);
                    background: #2b2b2b;
                    display: flex; justify-content: center; align-items: center;
                    font-size: 100px;
                    margin-bottom: 20px;
                '>
                    👨🏻‍🚀
                </div>
            </div>
            """, unsafe_allow_html=True
        )

    with col2:
        st.markdown("<h2 style='margin-bottom: 10px; text-shadow: 0 0 15px rgba(255,255,255,0.5);'>탐색자: 정지호</h2>", unsafe_allow_html=True)
        
        st.markdown("""
            <h3 style='margin-top: 0; background: linear-gradient(to right, #29B6F6, #E040FB); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold;'>
                🛰️ 식품생명공학 전공 우주항해사
            </h3>
        """, unsafe_allow_html=True)
        
        st.write("")
        st.markdown("""
        <div style='background: rgba(41, 182, 246, 0.08); padding: 25px; border-left: 4px solid #29B6F6; border-radius: 0 12px 12px 0; box-shadow: inset 0 0 20px rgba(41, 182, 246, 0.1);'>
            <p style='margin: 0; font-size: 18px; line-height: 1.6; font-style: italic;'>
            <b>"식품 공학(Food biotech.)의 추진력에<br>프로그래밍이라는 도구를 더하다."</b>
            </p>
            <p style='margin-top: 12px; font-size: 16px; color: #B0BEC5 !important;'>
            — 전공 지식과 프로그래밍이라는 도구를 바탕으로 미지의 취업 시장 궤도에 진입할 준비를 하고 있는 항해사
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='margin-top: 20px;'>
            <p>안녕하세요. 저는 식품 산업이라는 거대한 규모의 우주 속에서 세상의 각종 데이터를 <span style='color:#C6FF00; font-weight:bold;'>나침반</span> 삼아 새로운 기회를 탐색하고 있습니다.</p>
            <p>단순 전공 지식을 넘어, <span style='color:#00E5FF; font-weight:bold; border-bottom: 2px solid #00E5FF;'>시장 전체를 조망하는 거시적 안목</span>을 갖추기 위해 끊임없이 항로를 개척해나가겠습니다.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("##### ⚡ Core Booster Systems")
        st.markdown("""
        <div style='display: flex; flex-direction: column; gap: 12px;'>
            <div>
                <small style='color:#B0BEC5; display:block; margin-bottom:5px;'>🚀 Main Engines</small>
                <div style='display:flex; gap:8px; flex-wrap:wrap;'>
                    <span style='background: rgba(41, 182, 246, 0.2); color:#29B6F6; padding: 6px 12px; border-radius: 15px; border: 1px solid #29B6F6; font-weight: bold; font-size: 14px;'>🧬 식품생명공학</span>
                    <span style='background: rgba(224, 64, 251, 0.2); color:#E040FB; padding: 6px 12px; border-radius: 15px; border: 1px solid #E040FB; font-weight: bold; font-size: 14px;'>💰 금융경제학</span>
                </div>
            </div>
            <div>
                 <small style='color:#B0BEC5; display:block; margin-bottom:5px;'>📡 Sub Systems</small>
                 <div style='display:flex; gap:8px; flex-wrap:wrap;'>
                    <span style='background: rgba(0, 229, 255, 0.2); color:#00E5FF; padding: 6px 12px; border-radius: 15px; border: 1px solid #00E5FF; font-weight: bold; font-size: 14px;'>📊 프로그래밍</span>
                    <span style='background: rgba(198, 255, 0, 0.2); color:#C6FF00; padding: 6px 12px; border-radius: 15px; border: 1px solid #C6FF00; font-weight: bold; font-size: 14px;'>🛰️ 데이터 분석</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: #212121; padding: 15px; border-radius: 12px; border: 1px solid #424242; display: flex; align-items: center;'>
            <div style='font-size: 24px; margin-right: 15px;'>📍</div>
            <div>
                <small style='color: #B0BEC5;'>Current Orbit Status</small><br>
                <b style='color: #FFFFFF;'>Food Biotech, Programming, Economics</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📚 항해 기록 (2025-2)", "🌌 탐사 연료 주입 (취미)", "🎯 본 프로젝트 목표"])

    with tab1:
        st.subheader("📚 우주항해 커리큘럼")
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.markdown("""
            <div style='border: 1px solid #29B6F6; padding: 20px; border-radius: 12px; background: linear-gradient(135deg, rgba(41,182,246,0.1) 0%, transparent 100%);'>
                <h5 style='color: #29B6F6 !important; font-size: 18px; display: flex; align-items: center;'>
                    <span style='font-size:22px; margin-right:10px;'>🧬</span> 핵심 추진체: 식품생명공학
                </h5>
                <ul style='color: #E0E0E0 !important; margin-top: 15px; margin-left: 20px; line-height: 1.8;'>
                    <li>식품(Food)의 물리화학적 성질, 가공과 저장, 건강에 대한 영향을 이해</li>
                    <li>식품화학, 미생물학, 식품공학, 대사체학 기반 기초 연구 능력</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        with col_a2:
            st.markdown("""
            <div style='border: 1px solid #E040FB; padding: 20px; border-radius: 12px; background: linear-gradient(135deg, rgba(224,64,251,0.1) 0%, transparent 100%);'>
                <h5 style='color: #E040FB !important; font-size: 18px; display: flex; align-items: center;'>
                    <span style='font-size:22px; margin-right:10px;'>💰</span> 보조 추진체: 금융경제
                </h5>
                <ul style='color: #E0E0E0 !important; margin-top: 15px; margin-left: 20px; line-height: 1.8;'>
                    <li>시장(Market)의 거시적 흐름과 미시적 흐름 파악</li>
                    <li>경제 데이터 해석 및 사업성 분석 능력</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("#### 🔮 2025년도 2학기 학습궤도 (Mission log)")
        
        st.markdown("""
        <div style='display: flex; flex-direction: column; gap: 15px; margin-top: 20px;'>
            <div style='display: flex; align-items: center; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border-left: 4px solid #00E5FF;'>
                <div style='font-size: 24px; margin-right: 20px;'>🛰️</div>
                <div>
                    <b style='color: #00E5FF; font-size: 16px;'>IT/데이터 모듈 장착</b>
                    <p style='margin: 5px 0 0 0; font-size: 14px; color: #B0BEC5;'>컴퓨팅 탐색:컴퓨터로 생각하기/컴퓨팅 핵심:실생활에서 활용하기 | Python 기초 및 알고리즘 이해</p>
                </div>
            </div>
            <div style='display: flex; align-items: center; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border-left: 4px solid #C6FF00;'>
                <div style='font-size: 24px; margin-right: 20px;'>📈</div>
                <div>
                    <b style='color: #C6FF00; font-size: 16px;'>경제 네비게이션 동기화</b>
                    <p style='margin: 5px 0 0 0; font-size: 14px; color: #B0BEC5;'>미시경제이론/거시경제이론 | 시장 메커니즘 및 환경 분석</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.subheader("🌌 취미 & 영감 (Hobby & Inspiration)")

        st.markdown("""
        <div style='background: rgba(255, 64, 129, 0.1); padding: 25px; border-radius: 15px; border-left: 5px solid #FF4081; margin-bottom: 25px;'>
            <h5 style='color: #FF4081 !important; margin: 0; display: flex; align-items: center;'>
                🔋 항해의 원동력 (Fuel for Voyage)
            </h5>
            <p style='margin-top: 15px; font-size: 16px; line-height: 1.6;'>
                끝없는 우주를 항해(학습과 연구)하기 위해서는 <b>엔진의 열을 식히고 연료를 재충전</b>하는 시간이 필수적입니다.<br>
                제가 지칠 때마다 다시 나아갈 힘을 주는 것들은 제가 좋아하는 취미들입니다. <b>빵</b>과 <b>인문학</b>, 그리고 <b>영화</b>를 소재로 항해하는 유튜버들을 소개합니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        btn_style = """
            display: block;
            width: 100%;
            background-color: #EEEEEE; 
            color: #212121 !important;
            text-align: center;
            padding: 10px 0;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 15px;
            transition: 0.3s;
            border: 1px solid #BDBDBD;
        """

        with c1:
            st.markdown(f"""
            <div style='background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border: 1px solid rgba(255, 64, 129, 0.3); height: 300px; display: flex; flex-direction: column; justify-content: space-between;'>
                <div>
                    <b style='color: #FF4081; font-size: 20px; display:block; margin-bottom: 10px;'>빵딘 (Bakery)</b>
                    <p style='font-size: 15px; color: #E0E0E0; line-height: 1.6;'>
                        "베이킹은 과학이자 예술입니다."<br><br>
                        재료의 배합이 만들어내는 <b>시각적, 미각적 즐거움</b>을 통해 식품 공학적 영감과 힐링을 얻습니다.
                    </p>
                </div>
                <a href="https://www.youtube.com/@%EB%B9%B5%EB%94%98" target="_blank" style='{btn_style}'>
                    📺 채널 바로가기
                </a>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div style='background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border: 1px solid rgba(255, 193, 7, 0.3); height: 300px; display: flex; flex-direction: column; justify-content: space-between;'>
                <div>
                    <b style='color: #FFC107; font-size: 20px; display:block; margin-bottom: 10px;'>이지영 (Humanity)</b>
                    <p style='font-size: 15px; color: #E0E0E0; line-height: 1.6;'>
                        "인문학는 가장 강력한 연료입니다."<br><br>
                        항해가 힘들고 지칠 때, 치열한 삶의 태도를 배우며 <b>정신적인 엔진(Mental Engine)</b>을 재정비합니다.
                    </p>
                </div>
                <a href="https://www.youtube.com/@leejiyoung_official" target="_blank" style='{btn_style}'>
                    📺 채널 바로가기
                </a>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div style='background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border: 1px solid rgba(0, 229, 255, 0.3); height: 300px; display: flex; flex-direction: column; justify-content: space-between;'>
                <div>
                    <b style='color: #00E5FF; font-size: 20px; display:block; margin-bottom: 10px;'>천재이승국 (Movie)</b>
                    <p style='font-size: 15px; color: #E0E0E0; line-height: 1.6;'>
                        "영화를 보면 세상이 보입니다."<br><br>
                        다양한 소재와 장르의 영화를 보고, 분석하며 <b>사회와 문화에 대한 교양</b>을 정비합니다.
                    </p>
                </div>
                <a href="https://www.youtube.com/@GeniusSKLee" target="_blank" style='{btn_style}'>
                    📺 채널 바로가기
                </a>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.subheader("🎯 금번 임무 목표 (Project Directive)")
        st.markdown("""
        <div style='background: rgba(0, 229, 255, 0.1); padding: 30px; border-radius: 15px; border: 2px solid #00E5FF; position: relative; overflow: hidden;'>
            <div style='position: absolute; top: -20px; right: -20px; font-size: 100px; opacity: 0.1; color: #00E5FF;'>🎯</div>
            <h4 style='color: #00E5FF !important; margin-top: 0;'>MISSION: 불확실성의 안개 속에서 좌표 설정하라</h4>
            <p style='font-size: 17px; line-height: 1.7; margin-bottom: 20px;'>
            이 프로젝트는 불안하고 막연한 진로 탐색을 위한 <b>실전 데이터 시뮬레이션</b>입니다.
            추상적인 고민 대신, 실제 데이터를 수집하고 시각화하여 제가 안착해야 할 최적의 궤도를 스스로 탐색해나가는 과정입니다.
            <b>본 시뮬레이션의 결과는 서울대학교 식품생명공학과 동료 항해사들에게도 공유될 예정입니다.</b> 
            </p>
            <ul style='line-height: 1.8; color: #E0E0E0;'>
                <li>📡 <b>신호 탐지:</b> 구글 트렌드로 식품 시장의 트렌드를 추적</li>
                <li>🪐 <b>행성 좌표:</b> 국내 식품 기업의 물리적/경제적 위치 시각화</li>
                <li>🔭 <b>심우주 탐사:</b> 구글 스칼라 학술 데이터 크롤링을 통한 현재 기술 트렌드 예측</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# 신호 탐지 (Trend)
def page_keyword_analysis():
    st.title("📡 신호 탐지: 2025 식품 트렌드 분석")
    st.markdown("Google Trend 데이터를 레이더로 활용하여 **소비자 관심도 신호**를 포착합니다. 좌측의 **탐지기 설정**을 클릭하여 추적할 신호들을 정하세요.")

    df = load_data('./food_trends.csv')
    try:
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
        else:
            df.index = pd.to_datetime(df.index)
        
        df.columns = [col.replace(' (South Korea)', '') for col in df.columns]

        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('<1', '0').str.replace(',', ''), errors='coerce').fillna(0)
    except Exception as e:
        st.error(f"데이터 처리 오류: {e}")
        return

    trend_insights = {
        "Matcha": "🍵 **Matcha (말차)**: 2020년 대비 검색량이 가장 가파르게 급증한 '메가 트렌드'입니다. 그간 디저트 및 음료 시장에서 유행을 타지 않는 '스테디셀러'로 자리 잡았으며, 2025년에는 미국에서의 선풍적인 인기로 검색량이 급증했습니다.",
        "Zero": "🥤 **Zero (제로)**: 5년 내내 가장 높은 베이스라인(기본 관심도)을 유지하는 강력한 키워드입니다. 초기 '제로 콜라' 중심에서 소주, 과자 등 식품 전반으로 '제로 슈거' 열풍이 확산되며 우상향 곡선을 그리고 있습니다.",
        "Protein": "💪 **Protein (단백질)**: 지난 5년간 꾸준한 검색량을 유지하고 있습니다. 헬시플레저(Healthy Pleasure) 트렌드와 맞물려 필수 영양소로서의 위상이 견고합니다.",
        "Vegan": "🌿 **Vegan (비건)**: 다른 키워드들에 비해 적은 검색량 추이를 보입니다. 그러나 하나의 확고한 식문화 장르로 정착하며 고정적인 마니아층 검색량을 확보하고 있습니다.",
        "Slow Aging": "🐢 **Slow Aging (저속노화)**: 최근 새롭게 등장한 이머징(Emerging) 키워드이지만, 국내에서는 적은 검색량 추이를 보입니다. 저속노화는 '가속 노화'를 막으려는 2030 세대의 높은 관심을 대변합니다."
    }

    with st.sidebar:
        st.markdown("### 🛠️ 탐지기 설정")
        keywords = df.columns.tolist()
        selected_keywords = st.multiselect("추적할 신호(키워드)", keywords, default=keywords[:2] if len(keywords) > 1 else keywords)

    if not selected_keywords:
        st.warning("추적할 신호를 선택하세요.")
        return

    st.subheader("📊 최근 5개년 키워드 신호 강도 변화")
    fig = px.line(
        df, y=selected_keywords,
        labels={"value": "관심도 지수", "index": "날짜", "variable": "신호명"},
        template=CHART_THEME,
        color_discrete_sequence=SPACE_PALETTE
    )
    fig.update_layout(hovermode="x unified", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="white"))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### 🧐 선택한 신호(키워드) 정밀 분석")
    for key in selected_keywords:
        if key in trend_insights:
            st.info(trend_insights[key])
        else:
             st.info(f"**{key}**: 데이터 기반 트렌드 분석 정보를 불러오는 중...")

    st.caption("※ 데이터 출처: Google Trends (2025년 핵심 키워드 5개 분석 - 대한민국 기준)")
    st.divider()

    st.subheader("📊 최근 4주 트렌드 요약")
    cols = st.columns(4)
    for i, key in enumerate(selected_keywords):
        curr = df[key].iloc[-1]
        diff = curr - df[key].iloc[-4:].mean()
        with cols[i % 4]:
            st.metric(label=f"{key}", value=f"{curr:.0f}", delta=f"{diff:.1f} (vs 4주평균)")

    st.divider()
    
    col_h1, col_h2 = st.columns([1.5, 1.2])
    
    with col_h1:
        st.subheader("🔗 신호 상관관계 매트릭스")
        if len(selected_keywords) >= 2:
            corr = df[selected_keywords].corr()
            fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale="Purples", aspect="auto", template=CHART_THEME)
            fig_corr.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.warning("상관관계를 분석하려면 2개 이상의 신호를 선택하세요.")

    with col_h2:
        st.markdown("#### 💡 탐사 인사이트 (Correlation)")
        
        if len(selected_keywords) < 2:
            st.write("신호가 충분하지 않아 분석할 수 없습니다.")
        else:
            corr_matrix = df[selected_keywords].corr()
            pairs = []
            columns = corr_matrix.columns
            for i in range(len(columns)):
                for j in range(i + 1, len(columns)):
                    col1 = columns[i]
                    col2 = columns[j]
                    val = corr_matrix.loc[col1, col2]
                    pairs.append({'pair': (col1, col2), 'value': val})
            
            if len(pairs) == 1:
                p = pairs[0]
                val = p['value']
                n1, n2 = p['pair']
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; margin-bottom:10px;'>
                    <strong style='color:#00E5FF'>🔍 단일 관계 분석</strong><br>
                    <b>{n1}</b> & <b>{n2}</b> (r={val:.2f})<br>
                    <span style='font-size:14px; color:#B0BEC5'>
                    { "두 신호는 매우 밀접하게 함께 움직입니다." if val > 0.6 else 
                      "두 신호는 서로 반대로 움직이는 경향이 있습니다." if val < -0.4 else 
                      "두 신호는 서로 큰 영향 없이 독립적입니다." }
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                max_pos = max(pairs, key=lambda x: x['value'])
                max_neg = min(pairs, key=lambda x: x['value'])
                closest_zero = min(pairs, key=lambda x: abs(x['value']))
                
                def display_card(title, pair, val, color, desc):
                    st.markdown(f"""
                    <div style='background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; margin-bottom:10px; border-left: 4px solid {color};'>
                        <strong style='color:{color}'>{title}</strong> <span style='float:right; color:#E0E0E0'>r = {val:.2f}</span><br>
                        <b>{pair[0]}</b> ↔ <b>{pair[1]}</b><br>
                        <span style='font-size:14px; color:#B0BEC5'>{desc}</span>
                    </div>
                    """, unsafe_allow_html=True)

                desc_pos = "두 관심사는 강력한 동반 상승 패턴을 보입니다." if max_pos['value'] > 0.5 else "가장 비슷한 흐름을 보이지만, 연관성은 약합니다."
                display_card("🔥 최고 시너지 (Max Positive)", max_pos['pair'], max_pos['value'], "#FF4081", desc_pos)

                desc_neg = "한쪽이 뜨면 한쪽이 지는 역의 관계입니다." if max_neg['value'] < -0.3 else "서로 가장 관련성이 적거나 상반된 흐름입니다."
                display_card("🧊 상반된 흐름 (Max Negative)", max_neg['pair'], max_neg['value'], "#00E5FF", desc_neg)

                if closest_zero != max_pos and closest_zero != max_neg:
                    display_card("⚖️ 독립적 관계 (Independent)", closest_zero['pair'], closest_zero['value'], "#C6FF00", "서로 영향을 주지 않고 독자적으로 움직입니다.")

# 행성 좌표 (Map)
def page_map_visualization():
    df_map, _ = get_company_data()

    st.title("🪐 행성 좌표: 식품 기업 10대 거점")
    
    st.markdown("""
    <div style='background: rgba(0, 229, 255, 0.1); padding: 20px; border-radius: 15px; border-left: 5px solid #00E5FF; margin-bottom: 25px;'>
        <h5 style='color: #00E5FF !important; margin: 0;'>🗺️ 진로 탐색을 위한 성도(Star Map) 작성</h5>
        <p style='margin-top: 10px; font-size: 16px; line-height: 1.6;'>
            식품 산업이라는 거대한 우주에서 착륙할 목표 행성을 정하기 위해선, 그들의 <b>물리적 위치(본사)</b>와 <b>경제적 중력(브랜드 영향력)</b>을 파악하는 것이 필수적입니다.<br>
            최신 <b>K-Brand Index 빅데이터</b>를 기반으로, 현재 대한민국 식품 업계를 이끄는 10대 기업의 좌표를 시각화했습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_map, col_bar = st.columns([1.6, 1])

    with col_bar:
        st.subheader("🏆 기업 행성 영향력")
        st.caption("※ 총점: 빅데이터 인덱스 수치 합산")
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
            get_fill_color='[224, 64, 251, 150]', 
            pickable=True,
            stroked=True,
            filled=True,
            get_line_color=[0, 229, 255], 
            get_line_width=150
        )
        view_state = pdk.ViewState(latitude=36.5, longitude=127.5, zoom=6, pitch=30)
        tooltip = {"html": "<div style='color:black;'><b>{기업명}</b><br>총점: {총점}</div>"}

        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip
        ))

    st.divider()

    col_source, col_next = st.columns([2, 1])
    
    with col_source:
        st.subheader("📊 K-Brand Index 식품 부문 TOP 10")
        st.markdown("""
        <ul style='color: #E0E0E0; line-height: 1.8;'>
            <li><b>출처:</b> 아시아브랜드연구소 (2025.11.01 ~ 11.30)</li>
            <li><b>지표:</b> 빅데이터 시스템 온라인 인덱스 수치 합산 (트렌드, 미디어, 소셜 등)</li>
        </ul>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <a href="https://kbrandindex.co.kr/" target="_blank" style="
            display: inline-block;
            background-color: #EEEEEE;
            color: #212121 !important;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            border: 1px solid #BDBDBD;
            transition: 0.3s;
            text-align: center;
        ">
            🔗 K-Brand Index 공식 홈페이지 확인
        </a>
        """, unsafe_allow_html=True)

    with col_next:
        st.markdown("<br>", unsafe_allow_html=True) 
        st.info("""
        **👉 다음 단계 안내 (Next Step)**\n
        각 기업 행성의 상세 스펙(개요, 주력 상품, 비전)은 
        다음 페이지인 **[4. 상세 데이터 (Info)]** 챕터에서 
        정밀 분석합니다.
        """)

# 기업 상세 데이터 (Info)
def page_company_info():
    _, company_details = get_company_data()

    st.title("🛸 상세 데이터: 10대 기업 행성 정보")
    st.write("각 기업 행성의 개요, 주력 상품, 그리고 비전을 분석한 데이터 카드입니다.")
    st.markdown("---")

    st.markdown("""
    <style>
        /* Expander 스타일 재정의 */
        div[data-testid="stExpander"] details summary p {
            color: #495057 !important; 
            font-size: 18px !important;
            font-weight: 700 !important;
        }
        div[data-testid="stExpander"] details summary svg {
            fill: #495057 !important;
            color: #495057 !important;
        }
        div[data-testid="stExpander"] {
            border: 1px solid rgba(176, 190, 197, 0.3);
        }
    </style>
    """, unsafe_allow_html=True)

    btn_style = """
        display: block;
        width: 100%;
        background-color: #BDBDBD; 
        color: #000000 !important; 
        text-align: center;
        padding: 10px 0;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        border: 1px solid #757575;
        font-size: 15px;
        transition: 0.3s;
    """

    for i in range(0, len(company_details), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(company_details):
                c = company_details[i+j]
                with cols[j]:
                    with st.expander(f"Planet {c['순위']} | {c['기업명']}", expanded=True):
                        st.markdown(f"""
                        <div style='line-height: 1.8; margin-bottom: 15px;'>
                            <div style='margin-bottom: 5px;'>
                                <span style='color: #00B0FF; font-weight: bold; font-size: 16px;'>📝 개요:</span>
                                <span style='color: #B3E5FC;'>{c['소개']}</span>
                            </div>
                            <div style='margin-bottom: 5px;'>
                                <span style='color: #00B0FF; font-weight: bold; font-size: 16px;'>🛒 주력:</span>
                                <span style='color: #B3E5FC;'>{c['주력제품']}</span>
                            </div>
                            <div>
                                <span style='color: #00B0FF; font-weight: bold; font-size: 16px;'>🔭 비전:</span>
                                <span style='color: #B3E5FC;'>{c['비전']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("<div style='margin: 10px 0; border-top: 1px solid rgba(41, 182, 246, 0.3);'></div>", unsafe_allow_html=True)
                        
                        b1, b2 = st.columns(2)
                        with b1: 
                            st.markdown(f'<a href="{c["홈페이지"]}" target="_blank" style="{btn_style}">🏠 홈페이지</a>', unsafe_allow_html=True)
                        with b2: 
                            st.markdown(f'<a href="{c["유튜브"]}" target="_blank" style="{btn_style}">📺 유튜브</a>', unsafe_allow_html=True)
                            
# 심우주 탐사 (Research)
def page_scholar_analysis():
    st.title("🔭 심우주 탐사: 학술 연구 데이터")
    
    st.markdown("""
    <div style='background: rgba(41, 182, 246, 0.1); padding: 20px; border-radius: 12px; border-left: 5px solid #29B6F6; margin-bottom: 20px;'>
        <h5 style='color: #29B6F6 !important; margin: 0;'>📊 데이터 출처 및 수집 방법론 (Methodology)</h5>
        <ul style='margin-top: 10px; font-size: 15px; color: #E0E0E0; line-height: 1.6;'>
            <li><b>출처 (Source):</b> Google Scholar (구글 스칼라) 학술 데이터베이스</li>
            <li><b>수집 도구 (Tools):</b> Python <code>BeautifulSoup</code>, <code>Requests</code> 라이브러리 활용 웹 크롤링</li>
            <li><b>수집 기준 (Process):</b> 
                각 키워드에 대해 연도별(2015~2025) 검색을 수행하여, 상단에 표시되는 
                <b>'검색 결과 건수 (Total Results, 예: 약 15,300개)'</b>를 정량적으로 추출하여 DB화 하였습니다.
            </li>
            <li style='margin-top: 8px; color: #FFD54F;'>
                <b>⚠️ 안정성 공지:</b> 실시간 웹 크롤링은 구글의 보안 정책(Captcha 차단 등)으로 인해 시연 중 연결이 불안정할 수 있습니다. 
                따라서 본 포트폴리오에서는 <b>사전에 수집 및 검증 완료된 데이터셋(CSV)</b>을 로드하여 분석합니다.
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.info("💡 **Why Research Data?** 학술 논문 수의 급증은 해당 분야에 대한 **R&D 자금과 인재의 대규모 유입**을 의미합니다. 이는 곧 3~5년 후 **기술 상용화 및 시장 폭발(Growth)**을 예측할 수 있는 가장 확실한 선행 지표입니다.")

    st.markdown("<br>", unsafe_allow_html=True)

    @st.cache_data
    def load_scholar_data():
        file_name = 'scholar_data.csv'
        if not os.path.exists(file_name):
            data = {
                "Year": range(2015, 2026),
                "Food Safety": [145, 158, 172, 189, 205, 234, 287, 312, 341, 378, 392],
                "Alternative Meat": [42, 51, 63, 78, 92, 118, 156, 198, 245, 298, 334],
                "Gut Microbiome": [89, 102, 124, 147, 178, 215, 268, 312, 385, 442, 480],
                "Food Tech": [76, 85, 98, 115, 138, 167, 212, 261, 318, 385, 421],
                "AI": [58, 67, 81, 102, 135, 178, 241, 318, 412, 521, 598]
            }
            return pd.DataFrame(data)
        return pd.read_csv(file_name)

    df_research = load_scholar_data()
    
# ... (이전 코드는 그대로) ...

    keywords_available = [col for col in df_research.columns if col != 'Year']

with st.container():
        col_in1, col_in2 = st.columns([3, 1])
        with col_in1:
            # ====================================================================
            # [수정 완료] 글씨 검은색(#000000), 배경 흰색(#FFFFFF) 강제 적용
            # ====================================================================
            st.markdown("""
            <style>
            /* 1. 선택 박스 닫혀있을 때 (보이는 글자 & 배경) */
            div[data-baseweb="select"] > div {
                background-color: #FFFFFF !important; /* 배경 흰색 */
                border: 2px solid #29B6F6 !important; /* 테두리 파란색 */
            }
            
            /* 2. 실제 글자 색상 (가장 중요: 검은색 강제) */
            div[data-baseweb="select"] span {
                color: #000000 !important;  /* 글자색: 검정 */
                -webkit-text-fill-color: #000000 !important;
                font-weight: bold !important;
            }

            /* 3. 화살표 아이콘 색상 (검은색) */
            div[data-baseweb="select"] svg {
                fill: #000000 !important;
            }

            /* 4. 클릭해서 나오는 리스트 창 (팝업) 스타일 */
            ul[data-baseweb="menu"] {
                background-color: #FFFFFF !important; /* 리스트 배경 흰색 */
            }
            ul[data-baseweb="menu"] li span {
                color: #000000 !important; /* 리스트 글자 검은색 */
            }
            ul[data-baseweb="menu"] li:hover {
                background-color: #E0E0E0 !important; /* 마우스 올리면 연회색 */
            }
            </style>
            """, unsafe_allow_html=True)
            # ====================================================================

            # 라벨 부분 (파란 배경)
            st.markdown("""
            <div style='background-color: #29B6F6; padding: 8px 15px; border-radius: 8px 8px 0 0; display: inline-block; margin-bottom: 5px;'>
                <span style='color: #000000; font-weight: bold; font-size: 16px;'>📡 탐사할 신호(Keyword) 선택 (2015-2025)</span>
            </div>
            """, unsafe_allow_html=True)
            
            query = st.selectbox(
                "탐사 키워드 선택", 
                keywords_available, 
                index=4, 
                label_visibility="collapsed"
            )
        # ... (이후 코드는 그대로) ...
        with col_in2:
            st.write("") 
            st.write("") 
            st.write("") 
            run_btn = st.button("🚀 탐사선 발사", use_container_width=True)

    if run_btn:
        st.divider()
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        with st.spinner(f"'{query}' 영역의 학술 데이터를 분석 중..."):
            time.sleep(1.0) 
            
            dftrend = df_research[['Year', query]].rename(columns={query: 'Count'})
            
            progress_bar.progress(100)
            status_text.success(f"✅ 탐사 성공! {query} (2015-2025) 데이터 신호 확보.")

        st.subheader(f"📊 {query} 연도별 연구 데이터 출판 추이")
        
        fig = px.bar(
            dftrend, 
            x='Year', 
            y='Count', 
            text='Count',
            template=CHART_THEME, 
            color='Count', 
            color_continuous_scale=["#00E5FF", "#E040FB"]
        )
        
        fig.update_traces(
            textposition='outside',
            hovertemplate='<b>%{x}년</b><br>출판 수: %{y}편<extra></extra>'
        )
        
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            font=dict(color="white"),
            xaxis=dict(title="연도", tickmode='linear'),
            yaxis=dict(title="논문 출판 수 (건)"),
            margin=dict(t=50, b=50),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📈 탐사 데이터 분석 리포트")
        
        m1, m2, m3, m4 = st.columns(4)
        
        current_val = dftrend['Count'].iloc[-1]
        start_val = dftrend['Count'].iloc[0]
        growth_rate = ((current_val - start_val) / start_val) * 100
        
        with m1:
            st.metric("2025년 출판 수", f"{current_val:,}편", delta=f"{dftrend['Count'].iloc[-1] - dftrend['Count'].iloc[-2]} (YoY)")
        with m2:
            st.metric("10년 총 성장률", f"{growth_rate:.1f}%", delta="2015 대비")
        with m3:
            st.metric("연평균 출판 수", f"{dftrend['Count'].mean():.0f}편")
        with m4:
            max_year = dftrend.loc[dftrend['Count'].idxmax(), 'Year']
            st.metric("Peak 연도", f"{max_year}년")

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📋 연도별 상세 데이터 로그 확인 (Data Log)"):
            st.dataframe(
                dftrend.transpose(), 
                use_container_width=True,
                column_config={"Year": st.column_config.NumberColumn(format="%d")}
            )

# 궤도 안착 (Conclusion)
def page_conclusion():
    st.title("🚩 궤도 안착: 결론 및 제언")
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(41, 182, 246, 0.1) 0%, rgba(0, 0, 0, 0.3) 100%); padding: 30px; border-radius: 15px; border-left: 5px solid #29B6F6; box-shadow: 0 4px 20px rgba(41, 182, 246, 0.2);'>
        <h4 style='margin:0; color:#29B6F6 !important; display:flex; align-items:center;'>
            <span style='font-size:24px; margin-right:10px;'>👨🏻‍🚀</span> Mission Status: 궤도 안착 성공 (Success)
        </h4>
        <p style='margin-top:15px; font-size: 16px; color: #E0E0E0 !important; line-height: 1.8;'>
            본 프로젝트(항해)는 <b>식품 공학(Food Tech)</b>이라는 본진과 <b>프로그래밍(Programming)</b>라는 추진체를 결합한 시뮬레이션이었습니다.<br>
            불확실한 취업 시장이라는 심우주(Deep Space) 속에서, <b>데이터에 기반한 의사결정</b>은 목적지로 향하는 가장 정확한 나침반임을 확인했습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 12px; height: 100%;'>
            <h5 style='color: #00E5FF !important;'>🚀 프로그래밍이라는 새로운 도구 </h5>
            <ul style='color: #B0BEC5; margin-top: 15px; line-height: 1.8; list-style-type: none; padding-left: 0;'>
                <li style='margin-bottom: 10px;'>
                    <b style='color: white;'>🧬 Hybrid Specialist</b><br>
                    식품을 이해하는 공학적 지식에 프로그래밍 활용 능력을 더해, 개발자와 현장 전문가를 잇는 <b>가교(Bridge)</b> 역할을 수행할 수 있을 것입니다.
                </li>
                <li>
                    <b style='color: white;'>📊 Evidence-Based Decision</b><br>
                    '감'이나 '직관'에 의존하던 기획 방식에서 벗어나, <b>객관적 데이터 수치</b>로 설득하고 증명하는 문제 해결 방식을 체득했습니다.
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 12px; height: 100%;'>
            <h5 style='color: #E040FB !important;'>🔭 산업적 시사점</h5>
            <ul style='color: #B0BEC5; margin-top: 15px; line-height: 1.8; list-style-type: none; padding-left: 0;'>
                <li style='margin-bottom: 10px;'>
                    <b style='color: white;'>🌍 DX (Digital Transformation)</b><br>
                    보수적인 식품 산업에서도 트렌드 분석, 기술 최적화, 타겟 마케팅 등 <b>데이터 전환(DX)</b>이 필수적인 생존 전략임을 파악했습니다.
                </li>
                <li>
                    <b style='color: white;'>🛰️ 확장 가능한 탐사 모델</b><br>
                    본 프로젝트의 방법론(트렌드-기업-연구 분석)은 향후 다른 탐사자들에게 있어서도 <b>유관 산업 분야로 확장</b> 가능한 진로 탐색 범용 모델입니다.
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.subheader("📡 Next Coordinates: 차기 탐사 계획")
    st.markdown("""
    <div style='display: flex; flex-direction: column; gap: 10px; margin-top: 10px;'>
        <div style='display: flex; align-items: center; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; border-left: 3px solid #C6FF00;'>
            <span style='color: #C6FF00; font-weight: bold; width: 100px;'>Phase 1</span>
            <span style='color: #FFFFFF;'>Python 심화 학습 이후 유관 대회 및 해커톤 참여</span>
        </div>
        <div style='display: flex; align-items: center; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; border-left: 3px solid #C6FF00; opacity: 0.8;'>
            <span style='color: #C6FF00; font-weight: bold; width: 100px;'>Phase 2</span>
            <span style='color: #E0E0E0;'>실제로 프로그래밍을 활용하여 연구실 인턴 경험 확보</span>
        </div>
        <div style='display: flex; align-items: center; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; border-left: 3px solid #C6FF00; opacity: 0.5;'>
            <span style='color: #C6FF00; font-weight: bold; width: 100px;'>Phase 3</span>
            <span style='color: #B0BEC5;'>향후 데이터 기반 식품 기획, 연구원 등과 같은 현업으로의 적용</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center;'>
        <p style='font-size: 20px; font-weight: bold; color: #FFFFFF; font-style: italic;'>
            "탐험의 끝은 새로운 시작입니다."
        </p>
        <p style='font-size: 16px; color: #B0BEC5; margin-top: 10px;'>
            열정 가득한 개척자로서, 저만의 새로운 궤도를 만들어가겠습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; background-color: #212121; padding: 15px; border-radius: 30px; width: fit-content; margin: 0 auto; border: 1px solid #424242;'>
        <span style='margin-right: 15px; color: #B0BEC5;'>🛰️ Mission Director: <b>Jiho Jung</b></span>
        <span style='color: #4FC3F7;'>📡 Signal: <b>sookh37@snu.ac.kr</b></span>
    </div>
    """, unsafe_allow_html=True)

# 메인 실행 블록
def main():
    with st.sidebar:
        st.markdown("""
        <div style='background-color: #383838; padding: 15px; border-radius: 15px; margin-bottom: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>
            <h2 style='color: #FFFFFF !important; margin: 0; font-size: 22px; text-shadow: none;'>
                🛸 탐사선 제어 패널
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        selected = option_menu(
            menu_title=None,
            options=["0. 프롤로그", "1. 항해 시작 (Intro)", "2. 신호 탐지 (Trend)", "3. 행성 좌표 (Map)", "4. 기업 상세 데이터 (Info)", "5. 심우주 탐사 (Research)", "6. 궤도 안착 (Conclusion)"],
            icons=["star", "rocket-takeoff", "radar", "globe", "cpu", "binoculars", "flag"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#708090"},
                "icon": {"color": "#29B6F6", "font-size": "18px"},
                "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "color": "#FFFFFF"},
                "nav-link-selected": {"background-color": "#424242", "color": "#29B6F6", "border-left": "4px solid #29B6F6"},
            }
        )
        
        st.markdown("<p style='color: #1E88E5 !important; font-size: 14px;'>🪐 Designed by Jung Jiho</p>", unsafe_allow_html=True)

    if selected == "0. 프롤로그": page_title_screen()
    elif selected == "1. 항해 시작 (Intro)": page_intro()
    elif selected == "2. 신호 탐지 (Trend)": page_keyword_analysis()
    elif selected == "3. 행성 좌표 (Map)": page_map_visualization()
    elif selected == "4. 기업 상세 데이터 (Info)": page_company_info()
    elif selected == "5. 심우주 탐사 (Research)": page_scholar_analysis()
    elif selected == "6. 궤도 안착 (Conclusion)": page_conclusion()

if __name__ == "__main__":
    main()



