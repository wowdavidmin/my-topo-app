import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="법인별 TO&OP 현황", layout="wide", page_icon="📊")

# 제목
st.title("📊 법인별 TO&OP 현황")

# 2. 법인 및 공장 데이터 구조 정의
factory_data = {
    "JS": ["JSJ", "JSB", "JSV 핸드백", "JSV 의류창", "JSP"],
    "약진": ["VK(비나코리아)", "YV(약진베트남)", "MH(미시간하이징)", "YC(약진캄보디아)", "YTC", "JAYA1(약진자야1)", "JAYA2(약진자야2)", "약진과테말라"]
}

# 3. 상단 조회 조건 (콤보박스 및 날짜)
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    selected_corp = st.selectbox("🏢 법인 선택", list(factory_data.keys()))

with col2:
    selected_factory = st.selectbox("🏭 공장 선택", factory_data[selected_corp])

with col3:
    selected_date = st.date_input("📅 기준 날짜 선택", datetime.now())

st.divider()

# 4. 입력 양식 초기 데이터 (업로드하신 이미지 기반 구성)
# 대분류와 부서를 미리 세팅하여 사용자가 숫자만 입력하게 합니다.
initial_rows = [
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

# 5. 데이터 입력 섹션
st.subheader(f"📝 {selected_factory} 상세 내역 입력")
st.caption("표의 'TO'와 'OP' 열을 클릭하여 숫자를 입력하세요. 행을 추가하려면 표 하단의 + 버튼을 누르세요.")

# 엑셀 파일 업로드 기능 (데이터를 불러와서 편집하고 싶을 때 사용)
uploaded_file = st.file_uploader("📂 기존 엑셀 파일 불러오기 (선택사항)", type=["xlsx"])

if uploaded_file:
    try:
        df_input = pd.read_excel(uploaded_file)
    except:
        df_input = pd.DataFrame(initial_rows)
else:
    df_input = pd.DataFrame(initial_rows)

# 데이터 에디터 구현
edited_df = st.data_editor(
    df_input,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "대분류": st.column_config.SelectboxColumn(
            "대분류", 
            options=["생산부", "관리부", "생산지원", "기타"],
            required=True
        ),
        "부서": st.column_config.TextColumn("부서명", required=True),
        "TO": st.column_config.NumberColumn("정원 (TO)", min_value=0, format="%d", help="정원을 입력하세요"),
        "OP": st.column_config.NumberColumn("현원 (OP)", min_value=0, format="%d", help="현원을 입력하세요"),
    },
    hide_index=True,
)

# 6. 하단 실시간 요약 (KPI)
st.divider()
total_to = edited_df["TO"].sum()
total_op = edited_df["OP"].sum()
shortage = total_to - total_op
fill_rate = (total_op / total_to * 100) if total_to > 0 else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("총 TO", f"{total_to:,} 명")
kpi2.metric("총 OP", f"{total_op:,} 명")
kpi3.metric("과부족", f"{shortage:,} 명", delta=-shortage, delta_color="inverse")
kpi4.metric("충원율", f"{fill_rate:.1f}%")

# 7. 데이터 저장 및 출력
st.write("")
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    # 파일명에 법인과 공장명 포함
    file_name = f"TOOP_{selected_corp}_{selected_factory}_{selected_date}.csv"
    csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="💾 입력 내용 저장 (CSV)",
        data=csv,
        file_name=file_name,
        mime="text/csv",
    )

with col_btn2:
    if st.button("🔄 입력 값 초기화"):
        st.rerun()
