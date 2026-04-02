import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="TOPO 생산 관리 시스템", layout="wide", page_icon="🏭")

# 2. 사이드바: 분류 및 날짜 선택
with st.sidebar:
    st.header("📍 조회 조건 설정")
    
    # 가. 작성 날짜 선택 (달력 위젯)
    selected_date = st.date_input("작성 날짜 선택", datetime.now())
    
    # 나. 대분류 선택
    main_category = st.selectbox("대분류 선택", ["생산부", "관리부", "생산지원"])
    
    # 다. 부서 선택 (대분류에 따른 동적 필터링은 아니지만, 요청하신 목록 구성)
    # 완성을 세부적으로 나누기 위해 딕셔너리 구조 활용 가능
    dept_list = ["재단", "봉제", "완성", "기타"]
    selected_dept = st.selectbox("부서 선택", dept_list)
    
    # 라. 완성 부서인 경우 추가 세부 구분 표시
    sub_dept = None
    if selected_dept == "완성":
        sub_dept = st.radio(
            "완성 세부 구분",
            ["Iron", "Folding", "Packing", "완성창고", "WET PROCESS"]
        )

    st.divider()
    uploaded_file = st.file_uploader("엑셀 파일(.xlsx) 업로드", type=["xlsx"])

# 3. 메인 화면 구성
st.title(f"📊 {main_category} - {selected_dept} {f'({sub_dept})' if sub_dept else ''} 관리 현황")
st.info(f"선택된 날짜: **{selected_date}**")

if uploaded_file:
    try:
        # 엑셀의 모든 시트 읽기
        df_dict = pd.read_excel(uploaded_file, sheet_name=None)
        sheet_names = list(df_dict.keys())
        
        selected_sheet = st.selectbox("조회할 엑셀 시트 선택", sheet_names)
        df = df_dict[selected_sheet]

        # 4. 데이터 필터링 로직 (데이터 내에 날짜나 부서 컬럼이 있다고 가정할 경우)
        # 만약 엑셀 내에 '날짜'나 '부서' 컬럼이 있다면 아래처럼 자동 필터링 기능을 넣을 수 있습니다.
        # 예: df = df[df['부서'] == selected_dept] 

        # 5. 요약 지표
        col1, col2, col3 = st.columns(3)
        col1.metric("선택 부서", selected_dept)
        col2.metric("세부 구분", sub_dept if sub_dept else "해당 없음")
        col3.metric("데이터 행 수", f"{len(df)}건")

        st.divider()

        # 6. 데이터 출력
        st.subheader("📋 상세 내역")
        st.dataframe(df, use_container_width=True)

        # 7. 엑셀 다운로드 (필터링된 설정값 포함 가공용)
        st.download_button(
            label="현재 화면 데이터 추출 (CSV)",
            data=df.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"{selected_date}_{selected_dept}_report.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"파일 처리 중 오류 발생: {e}")
else:
    st.warning("왼쪽 사이드바에서 엑셀 파일을 업로드해 주세요.")
    # 초기 안내 가이드
    st.markdown("""
    ### 사용 방법
    1. 왼쪽 사이드바에서 **날짜**를 선택합니다.
    2. **대분류**와 **부서**를 지정합니다.
    3. 관리 중인 **TOPO 시스템 엑셀 템플릿**을 업로드합니다.
    4. 하단에 나타나는 표와 차트를 확인합니다.
    """)
