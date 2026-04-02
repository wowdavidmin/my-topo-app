import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="법인별 TO&OP 현황", layout="wide", page_icon="📊")

# 제목 변경
st.title("📊 법인별 TO&OP 현황")

# 2. 날짜 선택 및 파일 업로드 (상단 배치)
col_date, col_file = st.columns([1, 2])
with col_date:
    selected_date = st.date_input("📅 기준 날짜 선택", datetime.now())
with col_file:
    uploaded_file = st.file_uploader("📂 엑셀 템플릿 업로드", type=["xlsx"])

st.divider()

# 3. 데이터 구조 정의 (기본 틀)
# 엑셀 파일이 없을 때나 초기화를 위한 기본 데이터프레임 구조
default_data = [
    {"대분류": "생산부", "부서": "재단", "TO": 0, "OP": 0},
    {"대분류": "생산부", "부서": "봉제", "TO": 0, "OP": 0},
    {"대분류": "생산부", "부서": "완성(Iron)", "TO": 0, "OP": 0},
    {"대분류": "생산부", "부서": "완성(Folding)", "TO": 0, "OP": 0},
    {"대분류": "생산부", "부서": "완성(Packing)", "TO": 0, "OP": 0},
    {"대분류": "생산부", "부서": "완성창고", "TO": 0, "OP": 0},
    {"대분류": "생산부", "부서": "WET PROCESS", "TO": 0, "OP": 0},
    {"대분류": "관리부", "부서": "관리공통", "TO": 0, "OP": 0},
    {"대분류": "생산지원", "부서": "지원공통", "TO": 0, "OP": 0},
]

# 4. 메인 로직
if uploaded_file:
    # 엑셀에서 데이터를 읽어오되, 화면에서 수정 가능하도록 세팅
    try:
        # 첫 번째 시트를 기본으로 읽음
        df_excel = pd.read_excel(uploaded_file)
        # 엑셀에 필요한 컬럼이 없다면 기본 구조 사용
        if not all(col in df_excel.columns for col in ["대분류", "부서", "TO", "OP"]):
            df_to_edit = pd.DataFrame(default_data)
        else:
            df_to_edit = df_excel
    except:
        df_to_edit = pd.DataFrame(default_data)
else:
    # 파일이 없을 때는 기본 틀 표시
    df_to_edit = pd.DataFrame(default_data)

st.subheader(f"📝 상세 내역 입력 ({selected_date})")
st.info("💡 아래 표의 숫자를 클릭하여 직접 인원을 입력하거나 수정할 수 있습니다.")

# 5. 데이터 에디터 (화면에서 직접 입력 가능)
edited_df = st.data_editor(
    df_to_edit,
    use_container_width=True,
    num_rows="dynamic", # 행 추가/삭제 가능
    column_config={
        "TO": st.column_config.NumberColumn("정원 (TO)", min_value=0, format="%d명"),
        "OP": st.column_config.NumberColumn("현원 (OP)", min_value=0, format="%d명"),
        "대분류": st.column_config.SelectboxColumn("대분류", options=["생산부", "관리부", "생산지원"]),
    },
    hide_index=True,
)

# 6. 하단 요약 정보 계산
st.divider()
total_to = edited_df["TO"].sum()
total_op = edited_df["OP"].sum()

c1, c2, c3 = st.columns(3)
c1.metric("전체 TO 합계", f"{total_to} 명")
c2.metric("전체 OP 합계", f"{total_op} 명")
c3.metric("충원율", f"{(total_op/total_to*100):.1f}%" if total_to > 0 else "0%")

# 7. 저장 및 다운로드
st.write("")
col_btn1, col_btn2 = st.columns([1, 5])
with col_btn1:
    # 수정된 데이터를 CSV로 다운로드
    csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="💾 현재 내역 저장 (CSV)",
        data=csv,
        file_name=f"TOOP_현황_{selected_date}.csv",
        mime="text/csv",
    )
