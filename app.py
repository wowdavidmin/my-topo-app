import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="TOPO 시스템 관리자", layout="wide", page_icon="🏢")

# 2. 스타일 설정 (CSS)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ TOPO 시스템 통합 관리 도구")
st.info("엑셀 파일을 업로드하여 공정 및 업무 내역을 관리하세요.")

# 3. 사이드바 - 파일 업로드
with st.sidebar:
    st.header("📂 데이터 로드")
    uploaded_file = st.file_uploader("엑셀 파일(.xlsx) 선택", type=["xlsx"])
    
    if uploaded_file:
        st.success("파일 업로드 완료!")
        # 모든 시트 이름 가져오기
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        selected_sheet = st.selectbox("조회할 시트(공정/날짜) 선택", sheet_names)

# 4. 메인 화면 로직
if uploaded_file and selected_sheet:
    # 데이터 불러오기 (헤더 위치가 다를 수 있어 자동 감지 시도)
    df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
    
    # 상단 요약 카드
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 데이터 행 수", f"{len(df)}건")
    with col2:
        st.metric("현재 시트", selected_sheet)
    with col3:
        st.metric("데이터 열(Columns)", f"{len(df.columns)}개")

    st.divider()

    # 5. 검색 및 필터링
    st.subheader("🔍 실시간 데이터 조회")
    search_query = st.text_input("필터링하고 싶은 키워드를 입력하세요 (예: 공정, 담당자, 품목)")
    
    if search_query:
        # 모든 컬럼을 문자열로 변환 후 검색어 포함 여부 확인
        mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        display_df = df[mask]
    else:
        display_df = df

    # 6. 결과 표 시각화
    st.dataframe(display_df, use_container_width=True, height=500)

    # 7. 추가 기능 (데이터 분석)
    if not display_df.empty:
        st.subheader("📊 시각화 분석")
        numeric_cols = display_df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols:
            target_col = st.selectbox("수치 분석 항목 선택", numeric_cols)
            st.bar_chart(display_df[target_col])
        else:
            st.warning("이 시트에는 차트로 나타낼 수 있는 숫자 데이터가 없습니다.")

else:
    # 초기 화면 안내
    st.write("---")
    st.markdown("### 👈 왼쪽 사이드바에서 엑셀 파일을 먼저 업로드해 주세요!")
    st.write("이 앱을 통해 다음과 같은 작업을 수행할 수 있습니다:")
    st.markdown("""
    * **공정별 데이터 통합 관리**
    * **날짜별 작업 내역 실시간 검색**
    * **수치 데이터 기반의 자동 차트 생성**
    * **필터링된 데이터 재추출**
    """)
