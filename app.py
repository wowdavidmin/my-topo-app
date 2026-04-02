import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="법인별 TO & PO 현황", layout="wide", page_icon="📊")
st.title("📊 법인별 TO & PO 현황")

# 2. 상단 조회 조건
factory_data = {
    "약진": ["VK(비나코리아)", "YV(약진베트남)", "MH(미시간하이징)", "YC(약진캄보디아)", "YTC", "JAYA1(약진자야1)", "JAYA2(약진자야2)", "약진과테말라"],
    "JS": ["JSJ", "JSB", "JSV 핸드백", "JSV 의류창", "JSP"]
}

col1, col2, col3, col4 = st.columns([1, 1, 1, 1.5])
with col1:
    selected_corp = st.selectbox("🏢 법인명", list(factory_data.keys()), index=0)
with col2:
    selected_factory = st.selectbox("🏭 공장명", factory_data[selected_corp])
with col3:
    selected_date = st.date_input("📅 기준 일자", datetime.now())

st.divider()

# 3. 데이터 구조 설계 (직접/간접 세분화 및 필요 컬럼 추가)
if "df_base" not in st.session_state:
    # 엑셀의 직접/간접을 '구분' 열로 나누어 데이터화합니다.
    departments = [
        ("생산", "재단(Cutting)"), ("생산", "봉제(Sewing)"), 
        ("생산", "완성(Iron)"), ("생산", "완성(Folding)"), 
        ("생산", "완성(Packing)"), ("생산", "완성창고"), 
        ("생산", "WET PROCESS"), ("관리", "관리공통"), ("지원", "지원공통")
    ]
    
    initial_data = []
    for main, sub in departments:
        # 생산부서의 경우 직접/간접을 나눕니다.
        if main == "생산":
            initial_data.append({"대분류": main, "부서명": sub, "구분": "직접", "TO_인원": 0, "PO_인원": 0, "비고": ""})
            initial_data.append({"대분류": main, "부서명": sub, "구분": "간접", "TO_인원": 0, "PO_인원": 0, "비고": ""})
        else:
            initial_data.append({"대분류": main, "부서명": sub, "구분": "해당없음", "TO_인원": 0, "PO_인원": 0, "비고": ""})
            
    st.session_state.df_base = pd.DataFrame(initial_data)

# 4. 자동 계산 로직 (비중 및 차이)
df = st.session_state.df_base.copy()

# 전체 합계를 구해서 '전체대비 비율(%)'을 계산합니다.
total_to = df["TO_인원"].sum()
total_po = df["PO_인원"].sum()

# 비율 계산 (분모가 0일 경우 에러 방지)
df["TO_비중(%)"] = (df["TO_인원"] / total_to * 100).fillna(0) if total_to > 0 else 0.0
df["PO_비중(%)"] = (df["PO_인원"] / total_po * 100).fillna(0) if total_po > 0 else 0.0

# 차이 계산 (요청하신 TO - PO)
df["차이(TO-PO)"] = df["TO_인원"] - df["PO_인원"]

# 보기 좋게 열 순서 재배치
df = df[["대분류", "부서명", "구분", "TO_인원", "TO_비중(%)", "PO_인원", "PO_비중(%)", "차이(TO-PO)", "비고"]]

st.subheader(f"📝 {selected_factory} 상세 현황 입력")
st.caption("💡 '인원'과 '비고' 칸만 입력하세요. 비중(%)과 차이는 자동으로 계산됩니다.")

# 5. 데이터 에디터 (표 UI 설정)
edited_df = st.data_editor(
    df,
    use_container_width=True,
    num_rows="fixed",
    column_config={
        "대분류": st.column_config.TextColumn("대분류", disabled=True),
        "부서명": st.column_config.TextColumn("부서명", disabled=True),
        "구분": st.column_config.TextColumn("구분", disabled=True),
        
        "TO_인원": st.column_config.NumberColumn("TO (인원)", min_value=0, format="%d"),
        "TO_비중(%)": st.column_config.NumberColumn("TO (전체대비)", format="%.1f%%", disabled=True),
        
        "PO_인원": st.column_config.NumberColumn("PO (인원)", min_value=0, format="%d"),
        "PO_비중(%)": st.column_config.NumberColumn("PO (전체대비)", format="%.1f%%", disabled=True),
        
        "차이(TO-PO)": st.column_config.NumberColumn("차이 (TO-PO)", disabled=True),
        "비고": st.column_config.TextColumn("비고 (Text 입력)"),
    },
    hide_index=True,
)

# 6. 사용자가 수정한 값을 세션에 다시 저장 (그래야 실시간 계산이 됨)
st.session_state.df_base["TO_인원"] = edited_df["TO_인원"]
st.session_state.df_base["PO_인원"] = edited_df["PO_인원"]
st.session_state.df_base["비고"] = edited_df["비고"]

# 7. 하단 합계 요약
st.divider()
k1, k2, k3, k4 = st.columns(4)
k1.metric("총 정원 (TO 합계)", f"{total_to:,} 명")
k2.metric("총 현원 (PO 합계)", f"{total_po:,} 명")
k3.metric("과/부족 (TO-PO)", f"{(total_to - total_po):,} 명")
k4.metric("평균 충원율", f"{(total_po / total_to * 100):.1f}%" if total_to > 0 else "0.0%")

# 8. 데이터 내보내기
st.write("")
csv = edited_df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="💾 현재 결과 엑셀용으로 다운로드 (CSV)",
    data=csv,
    file_name=f"TOPO_{selected_factory}_{selected_date}.csv",
    mime="text/csv",
)
