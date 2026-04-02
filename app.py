import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="법인별 TO & PO 현황", layout="wide", page_icon="📊")

# 타이틀
st.title("📊 법인별 TO & PO 현황")

# 2. 상단 조회 조건 (엑셀 양식 느낌으로 가로 배치)
factory_data = {
    "약진": ["VK(비나코리아)", "YV(약진베트남)", "MH(미시간하이징)", "YC(약진캄보디아)", "YTC", "JAYA1(약진자야1)", "JAYA2(약진자야2)", "약진과테말라"],
    "JS": ["JSJ", "JSB", "JSV 핸드백", "JSV 의류창", "JSP"]
}

# 4등분 하여 엑셀 상단처럼 깔끔하게 배치
col1, col2, col3, col4 = st.columns([1, 1, 1, 1.5])
with col1:
    selected_corp = st.selectbox("🏢 법인명", list(factory_data.keys()), index=0)
with col2:
    selected_factory = st.selectbox("🏭 공장명", factory_data[selected_corp])
with col3:
    selected_date = st.date_input("📅 기준 일자", datetime.now())

st.divider()

# 3. 데이터 초기화 및 상태 유지 (과/부족 자동 계산을 위함)
# 앱이 새로고침 되어도 입력한 데이터를 기억하도록 Session State를 사용합니다.
if "df_base" not in st.session_state:
    initial_data = [
        {"대분류": "생산", "부서명": "재단", "정원(TO)": 0, "현원(PO)": 0},
        {"대분류": "생산", "부서명": "봉제", "정원(TO)": 0, "현원(PO)": 0},
        {"대분류": "생산", "부서명": "완성(Iron)", "정원(TO)": 0, "현원(PO)": 0},
        {"대분류": "생산", "부서명": "완성(Folding)", "정원(TO)": 0, "현원(PO)": 0},
        {"대분류": "생산", "부서명": "완성(Packing)", "정원(TO)": 0, "현원(PO)": 0},
        {"대분류": "생산", "부서명": "완성창고", "정원(TO)": 0, "현원(PO)": 0},
        {"대분류": "생산", "부서명": "WET PROCESS", "정원(TO)": 0, "현원(PO)": 0},
        {"대분류": "관리", "부서명": "관리공통", "정원(TO)": 0, "현원(PO)": 0},
        {"대분류": "지원", "부서명": "지원공통", "정원(TO)": 0, "현원(PO)": 0},
    ]
    st.session_state.df_base = pd.DataFrame(initial_data)

# 4. 과/부족 자동 계산
# 현원(PO)에서 정원(TO)을 뺀 값을 실시간으로 계산하여 열을 추가합니다.
df = st.session_state.df_base.copy()
df["과/부족"] = df["현원(PO)"] - df["정원(TO)"]

st.subheader(f"📝 {selected_factory} 상세 내역 입력")

# 5. 엑셀형 데이터 에디터 (오른쪽 화면 레이아웃 반영)
edited_df = st.data_editor(
    df,
    use_container_width=True,
    num_rows="fixed", # 부서명 고정
    column_config={
        "대분류": st.column_config.TextColumn("대분류", disabled=True),
        "부서명": st.column_config.TextColumn("부서명", disabled=True),
        "정원(TO)": st.column_config.NumberColumn("정원(TO)", min_value=0, format="%d"),
        "현원(PO)": st.column_config.NumberColumn("현원(PO)", min_value=0, format="%d"),
        "과/부족": st.column_config.NumberColumn("과/부족", disabled=True), # 자동 계산되므로 입력 불가 처리
    },
    hide_index=True,
)

# 사용자가 입력한 TO, PO 값을 세션에 다시 저장하여 자동 계산 루프 완성
st.session_state.df_base["정원(TO)"] = edited_df["정원(TO)"]
st.session_state.df_base["현원(PO)"] = edited_df["현원(PO)"]

# 6. 하단 합계 요약 (엑셀의 마지막 줄 느낌)
st.divider()
total_to = edited_df["정원(TO)"].sum()
total_po = edited_df["현원(PO)"].sum()
total_diff = total_po - total_to
fill_rate = (total_po / total_to * 100) if total_to > 0 else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("총 정원(TO)", f"{total_to:,} 명")
k2.metric("총 현원(PO)", f"{total_po:,} 명")
k3.metric("과/부족 합계", f"{total_diff:,} 명", delta=int(total_diff))
k4.metric("충원율", f"{fill_rate:.1f}%")

# 7. 파일 저장
st.write("")
csv = edited_df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="💾 현재 결과 다운로드 (CSV)",
    data=csv,
    file_name=f"TOPO_{selected_factory}_{selected_date}.csv",
    mime="text/csv",
)
