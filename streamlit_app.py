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
import chromedriver_autoinstaller

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import chromedriver_autoinstaller

@st.cache_resource
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # [중요] Streamlit Cloud 환경(리눅스) 경로 강제 지정
    # packages.txt로 설치된 chromium은 보통 이 경로에 있습니다.
    if os.path.exists("/usr/bin/chromium") and os.path.exists("/usr/bin/chromedriver"):
        options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
        return driver
        
    # [로컬 환경] 내 컴퓨터(윈도우/맥)에서는 자동 설치 사용
    try:
        chromedriver_autoinstaller.install()
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        st.error(f"드라이버 실행 오류: {e}")
        return None


# ==========================================
# [설정] 페이지 및 폰트 설정
# ==========================================
st.set_page_config(
    page_title="융합 인재 포트폴리오",
    page_icon="🎓",
    layout="wide"
)

# 한글 폰트 설정 (OS별 자동 대응)
system_name = platform.system()
font_path = None

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
    font_path = '/System/Library/Fonts/Supplemental/AppleGothic.ttf'
else:
    # 리눅스/클라우드 환경 (한글 폰트가 없을 경우 기본값 사용)
    pass

plt.rcParams['axes.unicode_minus'] = False

# =========================================================
# 0. 공통 데이터 관리 함수 (Data Loader)
# =========================================================

# [수정] 데이터 로딩 함수 (캐싱 적용)
@st.cache_data
def load_data(file_path):
    """
    CSV 파일을 로드하는 함수입니다.
    Streamlit의 캐시 기능을 사용하여 속도를 최적화합니다.
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        # utf-8로 먼저 시도하고 실패하면 euc-kr로 시도
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='euc-kr')
        
    return df

@st.cache_data
def get_company_data():
    """기업 순위, 위치, 상세 정보를 반환하는 함수"""
    # 1. 지도 및 차트용 데이터
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

    # 2. 기업 상세 정보 리스트
    company_details = [
        {
            "순위": 1, "기업명": "농심", 
            "소개": "1968년 설립, 라면·스낵·음료의 국내 1위 제조기업.",
            "주력제품": "신라면, 안성탕면, 짜파게티, 너구리, 새우깡",
            "비전": "글로벌 라면 시장 확대, 스마트팜 기술 도입",
            "홈페이지": "https://www.nongshim.com", "유튜브": "https://www.youtube.com/@nongshim"
        },
        {
            "순위": 2, "기업명": "오리온", 
            "소개": "1974년 초코파이 출시. 국내 제과업계의 대표기업.",
            "주력제품": "초코파이, 포카칩, 오징어땅콩, 닥터유",
            "비전": "글로벌 시장 심화, 건강기능식품 확대",
            "홈페이지": "https://www.orionworld.com", "유튜브": "https://www.youtube.com/@ORIONworld"
        },
        {
            "순위": 3, "기업명": "CJ제일제당", 
            "소개": "국내 최대 식품회사. 식품·제약·물류·바이오 등 사업 다각화.",
            "주력제품": "백설, 다시다, 햇반, 비비고",
            "비전": "글로벌 식품기업 도약, K-푸드 세계화",
            "홈페이지": "https://www.cj.net", "유튜브": "https://www.youtube.com/@CJCheilJedangOfficial"
        },
        {
            "순위": 4, "기업명": "삼양식품", 
            "소개": "불닭볶음면의 글로벌 성공으로 급성장한 라면 및 식품 기업.",
            "주력제품": "삼양라면, 불닭볶음면",
            "비전": "글로벌 종합식품 기업 도약",
            "홈페이지": "https://www.samyangfoods.com", "유튜브": "https://www.youtube.com/@samyangfoods"
        },
        {
            "순위": 5, "기업명": "풀무원", 
            "소개": "바른 먹거리 원칙을 지키는 로하스(LOHAS) 선도 기업.",
            "주력제품": "두부, 콩나물, 얄피만두, 지구식단",
            "비전": "식물성 지향 식품 확대, 지속가능경영",
            "홈페이지": "https://www.pulmuone.co.kr", "유튜브": "https://www.youtube.com/@pulmuone.official"
        },
        {
            "순위": 6, "기업명": "빙그레", 
            "소개": "바나나맛우유, 요플레 등 유가공 및 아이스크림 전문 기업.",
            "주력제품": "바나나맛우유, 요플레, 투게더, 메로나",
            "비전": "글로벌 비즈니스 확대, 프리미엄 제품 강화",
            "홈페이지": "https://www.bing.co.kr", "유튜브": "https://www.youtube.com/@official.binggrae"
        },
        {
            "순위": 7, "기업명": "매일유업", 
            "소개": "우유, 분유, 치즈 등 유제품 전문 기업. 성인 영양식 셀렉스 보유.",
            "주력제품": "매일우유, 상하목장, 앱솔루트, 셀렉스",
            "비전": "생애주기별 맞춤형 영양 설계, 건강기능식품 강화",
            "홈페이지": "https://www.maeil.com", "유튜브": "https://www.youtube.com/@maeili2mo"
        },
        {
            "순위": 8, "기업명": "하이트진로", 
            "소개": "대한민국 대표 주류 기업. 소주와 맥주 시장의 강자.",
            "주력제품": "참이슬, 진로, 테라, 켈리",
            "비전": "글로벌 주류 기업 도약, ESG 경영 강화",
            "홈페이지": "https://www.hitejinro.com", "유튜브": "https://www.youtube.com/watch?v=CjYD_J_2tt0"
        },
        {
            "순위": 9, "기업명": "롯데칠성음료", 
            "소개": "음료 및 주류 전문 기업. 칠성사이다와 처음처럼 보유.",
            "주력제품": "칠성사이다, 펩시, 처음처럼, 새로",
            "비전": "Z세대 타겟 마케팅 강화, 헬스케어 포트폴리오 확대",
            "홈페이지": "https://company.lottechilsung.co.kr", "유튜브": "https://www.youtube.com/@Lotte7star"
        },
        {
            "순위": 10, "기업명": "대상", 
            "소개": "청정원, 종가집 브랜드를 보유한 종합 식품 기업.",
            "주력제품": "청정원, 미원, 종가집 김치",
            "비전": "글로벌 한식 대표 브랜드 육성",
            "홈페이지": "https://www.daesang.com", "유튜브": "https://www.youtube.com/@DAESANG"
        }
    ]

    return df_map, company_details

# =========================================================
# 1. 포트폴리오 소개 (Intro)
# =========================================================

def page_intro():
    st.title("🙋‍♂️ 융합 인재 포트폴리오")
    st.caption("식품생명공학 x 경제 x 데이터 사이언스")

    tab1, tab2, tab3 = st.tabs(["🙋‍♂️ 프로필 & 관심사", "📚 수강 및 학습 현황", "🎯 프로젝트 목표"])

    with tab1:
        st.header("Who am I?")
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("<h1 style='text-align: center;'>👨‍🔬</h1>", unsafe_allow_html=True)
        with col2:
            st.markdown("""
            - **이름:** 정지호 (02년생)
            - **전공:** 식품생명공학 (21학번, 4학년)
            - **관심 분야:** 식품 R&D, 데이터 분석, 경제 동향
            """)

        st.divider()
        st.subheader("📢 자기소개")
        st.write("""
        안녕하세요! 저는 **식품생명공학**을 전공하고 있는 4학년 정지호입니다.
        본 학기에는 전공 지식을 넓히기 위해 **경제** 관련 연계 전공 수업과 **'컴퓨팅 탐색'** 등 IT 수업을 함께 수강하고 있습니다.
        
        현재 가장 큰 고민은 **졸업 후 진로**입니다. 단순히 식품을 연구하는 것을 넘어, 
        데이터와 경제적 관점을 결합하여 시장이 원하는 인재가 되기 위해 치열하게 고민하고 있습니다.
        """)

        st.subheader("💖 좋아하는 것")
        with st.expander("🍰 저의 달콤한 취미 보러가기 (Click!)"):
            st.write("""
            제가 가장 좋아하는 것은 **디저트**입니다. 잘 만들어진 케이크와 음료 한 잔은 큰 행복을 줍니다.
            본가에서는 마들렌, 휘낭시에 같은 구움과자를 직접 만들어 먹으며 스트레스를 해소하곤 합니다.
            """)
            st.info("👇 대리만족을 위해 자주 보는 채널")
            st.link_button("유튜버 '빵딘' 보러가기", "https://www.youtube.com/@빵딘")

    with tab2:
        st.header("Academic Roadmap")
        col1, col2, col3 = st.columns(3)
        col1.metric("현재 학년", "4학년")
        col2.metric("이번 학기 수강", "4과목", "융합 학습")
        col3.metric("총 학점", "12학점", "-6 (집중 학기)", delta_color="inverse")

        st.divider()
        st.subheader("📅 이번 학기 시간표")
        data = {
            "교시": ["1교시", "2교시"],
            "월": ["컴퓨팅 핵심", ""],
            "화": ["거시경제이론", ""],
            "수": ["컴퓨팅 핵심", "미시경제이론"],
            "목": ["", ""],
            "금": ["컴퓨팅 탐색", ""]
        }
        st.table(pd.DataFrame(data))

        st.subheader("🔍 수업 상세 정보")
        st.caption("JSON 트리 구조를 통해 데이터 구조화 능력을 보여줍니다.")
        json_data = {
            "컴퓨팅 탐색": {"교수": "변해선", "강의실": "26동 104호", "유형": "교양"},
            "컴퓨팅 핵심": {"교수": "김현주", "강의실": "26동 104호", "유형": "교양"},
            "미시경제이론": {"교수": "Gueron Yves", "강의실": "16동 110호", "유형": "연계전공"},
            "거시경제이론": {"교수": "최재원", "강의실": "223동 107호", "유형": "연계전공"}
        }
        st.json(json_data)

    with tab3:
        st.header("Why this Project?")
        st.success("이 프로젝트는 막연한 취업 시장을 데이터를 통해 명확하게 분석하기 위해 시작되었습니다.")
        
        st.write("""
        **앞으로의 목표:**
        대학 생활 동안 다양한 경험을 쌓고 새로운 지식을 습득하여, 졸업 후 제가 진정으로 원하는 길을 찾고 싶습니다.
        이번 프로젝트를 통해 **식품 산업의 트렌드**와 **연구 동향**을 직접 수집하고 분석하여 그 해답을 찾아보려 합니다.
        """)
        
        st.subheader("🔧 사용된 기술 스택")
        st.code("""
import streamlit as st        # 웹 대시보드 구현
import pandas as pd           # 데이터 정제 및 분석
from bs4 import BeautifulSoup # 웹 데이터 수집 (크롤링)
import pydeck as pdk          # 지도 시각화
        """, language="python")

        st.subheader("📈 분석 방법론 (예시)")
        st.write("데이터 간의 상관관계를 분석하기 위해 다음과 같은 통계적 접근을 시도할 예정입니다.")
        st.latex(r"Correlation(X, Y) = \frac{\sum(x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum(x_i - \bar{x})^2 \sum(y_i - \bar{y})^2}}")

# =========================================================
# 2. 국내 식품 트렌드 분석 (Trend)
# =========================================================
def page_keyword_analysis():
    st.title("📈 푸드 트렌드 & 키워드 분석")
    st.markdown("구글 트렌드 데이터를 활용하여 **실제 소비자 관심도** 변화를 분석합니다.")

    # [수정] 파일 경로 설정 (GitHub 배포 시 경로 문제 해결을 위해 상대 경로 사용 권장)
    csv_file = './food_trends.csv'
    
    # 캐싱된 함수를 통해 데이터 로드
    df = load_data(csv_file)

    if df is None:
        st.error(f"⚠️ '{csv_file}' 파일을 찾을 수 없습니다.")
        st.warning(f"현재 폴더 위치: {os.getcwd()}")
        st.info("Tip: GitHub에 올릴 때 'food_trends.csv' 파일이 app.py와 같은 폴더에 있는지 확인하세요.")
        return

    try:
        # 1. 날짜 컬럼 변환
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
        else:
            df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)

        # 2. 데이터 전처리
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace('<1', '0')
                df[col] = df[col].astype(str).str.replace(',', '')
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = df[col].fillna(0)
        
    except Exception as e:
        st.error(f"데이터 전처리 중 오류 발생: {e}")
        return

    # 사이드바 설정
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 키워드 선택")
    
    keywords = df.columns.tolist()
    default_selection = keywords[:3] if len(keywords) > 0 else []
    
    selected_keywords = st.sidebar.multiselect(
        "분석할 키워드를 선택하세요",
        keywords,
        default=default_selection
    )

    if not selected_keywords:
        st.warning("분석할 키워드를 1개 이상 선택해주세요.")
        return

    # [시각화 1] 시계열 그래프
    st.subheader("🗓️ 주간 관심도 변화 (Time Series)")
    if not df.empty:
        st.caption(f"분석 기간: {df.index.min().date()} ~ {df.index.max().date()}")
    
    fig = px.line(
        df,
        y=selected_keywords,
        labels={"value": "검색 지수", "Date": "날짜", "variable": "키워드"},
        template="plotly_white"
    )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # [시각화 2] 데이터 요약 (Metric)
    st.divider()
    st.subheader("📊 최근 트렌드 요약 (Last 4 Weeks)")
    
    cols = st.columns(len(selected_keywords))
    for i, key in enumerate(selected_keywords):
        if len(df) > 8:
            recent = df[key].iloc[-4:].mean()
            past = df[key].iloc[-8:-4].mean()
            diff = recent - past
        else:
            recent = df[key].mean()
            diff = 0
        
        with cols[i % 4]:
            st.metric(
                label=key,
                value=f"{recent:.1f}",
                delta=f"{diff:.1f}",
                help="최근 4주 평균 검색량입니다."
            )

    # [시각화 3] 상관관계 히트맵
    st.divider()
    st.subheader("🔗 키워드 간 상관관계 (Correlation)")
    if len(selected_keywords) >= 2:
        corr = df[selected_keywords].corr()
        fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r")
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("상관관계 분석을 위해 2개 이상의 키워드를 선택하세요.")

# =========================================================
# 3. 식품 기업 거점 지도 (Map)
# =========================================================

def page_map_visualization():
    """ 3. 기업 순위 및 위치 시각화 페이지 """
    df_map, _ = get_company_data()

    st.title("🗺️ 식품 기업 10대 거점 지도")
    st.info("K-Brand Index 상위 10개 기업의 위치와 브랜드 평판 순위를 시각화했습니다.")

    # --- 1. 기업 순위 시각화 ---
    st.subheader("📊 K-Brand Index 식품 부문 TOP 10")
    st.markdown("""
    - **출처:** 아시아브랜드연구소 (2025.11.01 ~ 11.30)
    - **지표:** 빅데이터 시스템 온라인 인덱스 수치 합산
    """)

    fig = px.bar(
        df_map, 
        x="총점", 
        y="기업명", 
        orientation='h', 
        text="총점", 
        color="총점", 
        color_continuous_scale="Bluered", 
        title="기업별 브랜드 평판 총점 비교"
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'}) 
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- 2. 지도 시각화 (PyDeck) ---
    st.subheader("📍 본사 위치 시각화")
    st.caption("지도의 점을 클릭하거나 마우스를 올리면 기업명과 주소가 표시됩니다.")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_map,
        get_position='[lon, lat]',
        get_radius=2000,
        get_fill_color='[255, 0, 0, 180]',
        pickable=True,
        stroked=True,
        filled=True
    )

    view_state = pdk.ViewState(
        latitude=36.5,
        longitude=127.5, 
        zoom=6,
        pitch=0
    )

    tooltip = {
        "html": "<b>{순위}위 {기업명}</b><br>총점: {총점}점<br>주소: {주소}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip
    ))

# =========================================================
# 4. 식품 기업 상세 정보 (Info)
# =========================================================

def page_company_info():
    """ 4. 기업별 상세 정보 페이지 """
    _, company_details = get_company_data()

    st.title("🏢 10대 식품 기업 상세 정보")
    st.info("각 기업의 주요 비전, 주력 제품 및 공식 채널 링크를 정리했습니다.")
    
    st.markdown("---")

    for i in range(0, len(company_details), 2):
        cols = st.columns(2)
        with cols[0]:
            c1 = company_details[i]
            with st.expander(f"**{c1['순위']}위. {c1['기업명']}**", expanded=True):
                st.markdown(f"**💡 소개:** {c1['소개']}")
                st.markdown(f"**🛒 제품:** {c1['주력제품']}")
                st.markdown(f"**🚀 비전:** {c1['비전']}")
                st.markdown("---")
                if c1.get("홈페이지"):
                    st.link_button("🏠 홈페이지", c1["홈페이지"], use_container_width=True)
                if c1.get("유튜브"):
                    st.link_button("📺 유튜브 채널", c1["유튜브"], use_container_width=True)
        
        if i + 1 < len(company_details):
            with cols[1]:
                c2 = company_details[i+1]
                with st.expander(f"**{c2['순위']}위. {c2['기업명']}**", expanded=True):
                    st.markdown(f"**💡 소개:** {c2['소개']}")
                    st.markdown(f"**🛒 제품:** {c2['주력제품']}")
                    st.markdown(f"**🚀 비전:** {c2['비전']}")
                    st.markdown("---")
                    if c2.get("홈페이지"):
                        st.link_button("🏠 홈페이지", c2["홈페이지"], use_container_width=True)
                    if c2.get("유튜브"):
                        st.link_button("📺 유튜브 채널", c2["유튜브"], use_container_width=True)

# =========================================================
# 5. 연구 트렌드 분석 (Research)
# =========================================================

def page_scholar_analysis():
    """ 5. 연구 트렌드 분석 페이지 (Google Scholar Crawling - Year Extraction Fix) """
    st.title("🎓 연구 트렌드 심층 분석")
    st.markdown("""
    구글 스칼라(Google Scholar)에서 **다중 페이지 크롤링**을 통해 더 풍부한 데이터를 수집합니다.
    (수집된 데이터를 바탕으로 연도별 트렌드와 핵심 키워드를 시각화합니다.)
    """)

    # 1. 키워드 입력
    st.subheader("🔍 Search Keywords")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("**Recommended Keywords**")
        keywords = [
            "Food Chemistry", "Food Microbiology", "Food Engineering", 
            "Functional Food", "Fermentation Technology", "Food Safety", 
            "Food Nutrition", "Biotechnology", "Microbiome", "Alternative Meat"
        ]
        selected_keyword = st.selectbox("Select a keyword", keywords)
    
    with col2:
        query = st.text_input("Or type your own keyword", value=selected_keyword)

    pages_to_crawl = st.slider("크롤링할 페이지 수 (페이지당 10개)", 1, 5, 3)

    run_search = st.button("🚀 Start Analysis (Data Collection)")

    if run_search and query:
        st.divider()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 데이터 저장소
        all_titles = []
        all_years = []

        try:
            chromedriver_autoinstaller.install()
            
            options = Options()
            # 봇 탐지 회피 옵션
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
            options.add_argument("--headless") 
            options.add_argument("--disable-gpu")
            
            driver = webdriver.Chrome(options=options)
            
            # 페이지 반복 크롤링
            for i in range(pages_to_crawl):
                start_index = i * 10
                status_text.info(f"⏳ '{query}' 관련 데이터를 수집 중입니다... ({i+1}/{pages_to_crawl} 페이지)")
                
                url = f"https://scholar.google.co.kr/scholar?start={start_index}&q={query}&hl=en&as_sdt=0,5"
                driver.get(url)
                
                time.sleep(2 + random.random()) # random delay
                driver.implicitly_wait(5)

                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                
                results = soup.find_all("div", class_="gs_r gs_or gs_scl")
                
                for row in results:
                    title_tag = row.find("h3", class_="gs_rt")
                    
                    # 제목이 있는 경우에만 연도 찾기를 시도 (데이터 짝 맞추기 위함)
                    if title_tag:
                        # 1. 제목 추출
                        clean_title = title_tag.text.replace("[PDF]", "").replace("[HTML]", "").replace("[BOOK]", "").replace("[B]", "").strip()
                        all_titles.append(clean_title)
                        
                        # 2. 연도 추출 (제목에 대응하는 연도를 찾거나, 없으면 None 저장)
                        meta_tag = row.find("div", class_="gs_a")
                        year_val = None # 기본값
                        
                        if meta_tag:
                            # 19xx 또는 20xx 형태의 4자리 숫자를 모두 찾음
                            years_found = re.findall(r'(19\d{2}|20\d{2})', meta_tag.get_text())
                            if years_found:
                                # 여러 숫자가 나올 경우 보통 맨 뒤에 나오는 것이 출판 연도일 확률이 높음
                                try:
                                    year_val = int(years_found[-1])
                                except:
                                    year_val = None
                        
                        # 연도를 찾았든 못 찾았든 리스트에 추가 (제목과 길이 맞추기)
                        all_years.append(year_val)
                
                progress_bar.progress((i + 1) / pages_to_crawl)
            
            driver.quit()

            if all_titles:
                # None이 아닌 실제 연도 데이터만 필터링하여 카운트
                valid_years = [y for y in all_years if y is not None]
                
                status_text.success(f"✅ 분석 완료! 총 {len(all_titles)}건 중 {len(valid_years)}건의 연도 정보를 확보했습니다.")
                
                # 1. 연도별 트렌드 차트
                st.subheader(f"📊 Research Trends by Year ({query})")
                
                if valid_years:
                    year_counts = Counter(valid_years)
                    df_trend = pd.DataFrame(list(year_counts.items()), columns=['Year', 'Count'])
                    df_trend = df_trend.sort_values('Year')
                    
                    # 최근 데이터 위주로 보여주기 위해 정렬
                    fig = px.bar(
                        df_trend, 
                        x='Year', 
                        y='Count',
                        text='Count',
                        title=f"Annual Publication Count for '{query}'",
                        labels={'Count': 'Number of Papers', 'Year': 'Year'},
                        template='plotly_white',
                        color='Count',
                        color_continuous_scale='Blues'
                    )
                    fig.update_traces(textposition='outside')
                    fig.update_layout(xaxis=dict(type='category')) # X축을 카테고리로 설정하여 정수만 표시
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ 연도 정보를 추출하지 못했습니다. (구글 스칼라 페이지 구조가 변경되었거나 정보가 없습니다.)")

                # 2. 워드 클라우드
                st.subheader(f"☁️ Key Topics Word Cloud")
                
                all_text = " ".join(all_titles)
                stopwords = {"of", "and", "the", "in", "a", "for", "on", "with", "to", "at", "by", "an", "analysis", "study", "review", "using", "based", "effect", "effects", "application", "applications"}
                
                wc = WordCloud(
                    font_path=font_path,
                    width=800,
                    height=400,
                    background_color="white",
                    colormap="viridis",
                    stopwords=stopwords
                ).generate(all_text)
                
                fig_wc, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig_wc)
                
                # 3. 논문 목록 (데이터프레임 생성 시 길이 불일치 오류 방지)
                with st.expander("📜 View Collected Papers List"):
                    df_papers = pd.DataFrame({
                        "Title": all_titles,
                        "Year": all_years 
                    })
                    # 연도가 없는(None) 행은 맨 아래로 보내거나 표시
                    st.dataframe(df_papers.sort_values(by="Year", ascending=False, na_position='last'))
            
            else:
                status_text.error("데이터를 수집하지 못했습니다. (Google Scholar 봇 탐지 가능성)")
                st.info("잠시 후 다시 시도하거나, 크롤링 페이지 수를 줄여보세요.")

        except Exception as e:
            st.error(f"Error occurred: {e}")
            

# =========================================================
# 6. 결론 및 제언 (Conclusion)
# =========================================================

def page_conclusion():
    st.title("📝 결론 및 제언 (Conclusion & Suggestion)")
    st.markdown("""
    본 포트폴리오 프로젝트를 통해 식품 산업의 현재 트렌드를 데이터를 통해 정량적으로 분석하고, 
    미래 식품 산업에서의 데이터 기반 의사결정 가능성을 구체적으로 탐색했습니다.
    """)

    st.subheader("1. 분석 요약 (Summary of Analysis)")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**📈 트렌드(Trend) 분석 결론**")
        st.markdown("""
        - **건강 지향성 심화**: '저속노화', '제로슈거', '단백질' 키워드의 검색량이 꾸준히 상위권을 유지하며, 소비자들이 단순한 맛을 넘어 **'기능성'과 '건강'**을 식품 선택의 최우선 가치로 두고 있음을 확인했습니다.
        - **SNS 바이럴의 영향력**: '두바이초콜릿', '요아정'과 같은 키워드의 급등락 패턴은 현대 식품 시장에서 **SNS 숏폼 콘텐츠와 시각적 요소**가 트렌드 형성에 결정적인 역할을 함을 시사합니다.
        """)
    with col2:
        st.success("**🎓 연구(Research) 동향 결론**")
        st.markdown("""
        - **융합 기술의 부상**: 학술 검색 결과, **Microbiome(마이크로바이옴)**과 **Alternative Meat(대체육)** 분야의 연구 논문 수가 최근 3년간 꾸준히 증가 추세입니다.
        - **미래 방향성**: 이는 식품 공학이 단순 가공 기술을 넘어 **바이오/생명공학 기술**과 융합되고 있으며, 개인 맞춤형 영양(Personalized Nutrition) 시대로 나아가고 있음을 보여줍니다.
        """)

    st.divider()

    st.subheader("2. 기대 효과 및 활용 방안 (Expected Effects & Utilization)")
    
    with st.expander("💡 융합적 관점에서의 기대 효과 (Click)", expanded=True):
        st.markdown("""
        **1) 식품공학 x 경제학의 시너지: '데이터 기반 제품 기획'**
        * 기존의 직관에 의존한 기획에서 벗어나, 검색량 데이터와 경제 지표(물가 상승률 등)를 결합하여 **'성공 확률이 높은' 제품군**을 선별할 수 있습니다.
        * 예: 불황기에는 '가성비' 키워드와 연관된 '대용량/PB상품' 기획, 호황기에는 '가심비' 중심의 '프리미엄 디저트' 기획 등 유연한 전략 수립이 가능합니다.

        **2) R&D 파이프라인 최적화**
        * 구글 스칼라의 연구 트렌드 분석을 통해 **학계에서 주목받는 기술**을 조기에 포착하고, 이를 기업의 선행 연구 주제로 빠르게 도입할 수 있습니다.
        * 이는 경쟁사보다 한발 앞선 기술 선점과 특허 확보로 이어질 수 있습니다.
        """)

    with st.expander("🚀 실무 및 학업 활용 전략 (Strategy)"):
        st.markdown("""
        - **마케팅 전략 수립**: 시즈널 키워드(예: 여름철 '요아정', 겨울철 '호빵') 분석을 통한 프로모션 시기 및 타겟 최적화.
        - **글로벌 진출 전략**: K-Food 관심도가 높은 국가의 키워드 데이터를 분석하여 현지화 제품 개발(예: 미국 시장 내 '비건 만두' 수요 분석).
        - **위기 관리 시스템**: 식품 안전 관련 키워드(HACCP, 식중독, 이물질)의 검색량 급증을 실시간 모니터링하여 선제적인 품질 관리 시스템 구축.
        """)

    st.divider()

    st.subheader("3. 과제 후기 및 자기 성찰 (Self-Reflection)")
    st.write("이 프로젝트를 진행하며 느낀 점, 기술적 어려움 극복 과정, 그리고 앞으로의 다짐을 자유롭게 작성합니다.")
    
    review = st.text_area(
        "👇 여기에 과제 후기를 작성하세요 (작성 후 Ctrl+Enter를 누르면 저장됩니다)",
        height=150,
        placeholder="예시: 처음에는 파이썬 코드가 낯설었지만, 직접 데이터를 크롤링하고 시각화해보니 데이터의 힘을 실감할 수 있었습니다. 특히 경제학 수업에서 배운 수요 예측 이론을 실제 검색량 데이터에 적용해보고 싶은 욕심이 생겼습니다. Selenium 크롤링 과정에서 봇 탐지 문제를 해결하며 문제 해결 능력도 기를 수 있었습니다."
    )
    
    if review:
        st.success("✅ 후기가 성공적으로 저장되었습니다! (이 내용은 발표 시 활용 가능합니다)")
        st.write(f"**작성된 내용:** {review}")

# =========================================================
# 메인 실행 블록
# =========================================================

def main():
    st.sidebar.title("🗂️ Portfolio Menu")
    
    menu = st.sidebar.radio(
        "이동할 페이지를 선택하세요",
        [
            "1. Intro: 융합 인재 포트폴리오", 
            "2. Trend: 키워드 검색 수 분석", 
            "3. Map: 식품 기업 순위 및 지도", 
            "4. Info: 10대 기업 상세 정보", 
            "5. Research: 연구 트렌드 분석", 
            "6. Conclusion: 결론 및 제언" 
        ]
    )

    if menu.startswith("1."):
        page_intro()
    elif menu.startswith("2."):
        page_keyword_analysis()
    elif menu.startswith("3."):
        page_map_visualization()
    elif menu.startswith("4."):
        page_company_info()
    elif menu.startswith("5."):
        page_scholar_analysis()
    elif menu.startswith("6."):
        page_conclusion()

if __name__ == "__main__":
    main()




