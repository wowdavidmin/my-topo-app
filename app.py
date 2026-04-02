import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="법인별 TO&PO 현황", layout="wide", page_icon="📊")

# 제목 수정 (요청사항: TO&PO로 변경)
st.title("📊 법인별 TO&PO 현황")

# 2. 법인 및 공장 데이터 구조
factory_data = {
    "JS": ["JSJ", "JSB", "JSV 핸드백", "JSV 의류창", "JSP"],
    "약진": ["VK(비나코리아)", "YV(약진베트남)", "MH(미시간하이징)", "YC(약진캄보디아)", "YTC", "JAYA1(약진자야1)", "JAYA2(약진자야2)", "약진과테말라"]
}

# 3. 상단 조회 조건
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    selected_corp = st.selectbox("🏢 법인 선택", list(factory_data.keys()))
with col2:
    selected_factory = st.selectbox("🏭 공장 선택", factory_data[selected_corp])
with col3:
    selected_date = st.date_input("📅 기준 날짜 선택", datetime.now())

st.divider()

# 4. 엑셀 양식을 반영한 고정 부서 데이터 세팅
# 엑셀 화면과 동일한 순서로 구성했습니다.
initial_data = [
    {"대분류": "생산부", "부서": "재단", "TO": 0, "PO": 0},
    {"대분류": "생산부", "부서": "봉제", "TO": 0, "PO": 0},
    {"대분류": "생산부", "부서": "완성(Iron)", "TO": 0, "PO": 0},
    {"대분류": "생산부", "부서": "완성(Folding)", "TO": 0, "PO": 0},
    {"대분류": "생산부", "부서": "완성(Packing)", "TO": 0, "PO": 0},
    {"대분류": "생산부", "부서": "완성창고", "TO": 0, "PO": 0},
    {"대분류": "생산부", "부서": "WET PROCESS", "TO": 0, "PO": 0},
    {"대분류": "관리부", "부서": "관리공통", "TO": 0, "PO": 0},
    {"대분류": "생산지원", "부서": "지원공통", "TO": 0, "PO": 0},
]

# 5. 입력 섹션 제목 수정 (요청사항 반영)
st.subheader(f"📝 {selected_factory} 상세 TO&PO")

# 데이터 에디터 (엑셀처럼 입력 가능한 표)
# 사용자가 실수로 대분류나 부서명을 지우지 않도록 해당 컬럼은 수정을 제한할 수 있습니다.
df_input = pd.DataFrame(initial_data)

edited_df = st.data_editor(
    df_input,
    use_container_width=True,
    num_rows="fixed",  # 부서 목록 고정 (엑셀 양식 유지)
    column_config={
        "대분류": st.column_config.TextColumn("대분류", disabled=True), # 수정 불가
        "부서": st.column_config.TextColumn("부서", disabled=True),     # 수정 불가
        "TO": st.column_config.NumberColumn(
            "정원 (TO)", 
            min_value=0, 
            format="%d", 
            help="정원을 입력하세요"
        ),
        "PO": st.column_config.NumberColumn(
            "현원 (PO)", 
            min_value=0, 
            format="%d", 
            help="현원을 입력하세요"
        ),
    },
    hide_index=True,
)

# 6. 하단 실시간 요약 (KPI)
st.divider()
total_to = edited_df["TO"].sum()
total_po = edited_df["PO"].sum()
diff = total_po - total_to # 과부족
rate = (total_po / total_to * 100) if total_to > 0 else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("전체 TO 합계", f"{total_to:,}명")
k2.metric("전체 PO 합계", f"{total_po:,}명")
k3.metric("과부족 (PO-TO)", f"{diff:,}명", delta=int(diff))
k4.metric("충원율", f"{rate:.1f}%")

# 7. 하단 버튼
col_save, col_clear = st.columns([1, 5])
with col_save:
    # 파일명에도 TO&PO 반영
    csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="💾 현재 결과 저장 (CSV)",
        data=csv,
        file_name=f"TOPO_{selected_factory}_{selected_date}.csv",
        mime="text/csv",
    )
with col_clear:
    if st.button("🔄 입력 값 초기화"):
        st.rerun()

st.caption(f"최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
