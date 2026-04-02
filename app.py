import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="법인별 TO & PO 현황", layout="wide", page_icon="📊")
st.title("📊 법인별 TO & PO 현황")

# 2. 상단 조회 조건 (콤보박스)
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

# 3. 데이터 구조 설계 (관리부 세부 부서 세분화 및 '간접' 일괄 적용)
# 에러 방지를 위해 새로운 캐시 이름(df_v6)을 사용합니다.
if "df_v6" not in st.session_state:
    departments = [
        # 생산부
        ("생산부", "재단(Cutting)"), ("생산부", "봉제(Sewing)"), 
        ("생산부", "완성(Iron)"), ("생산부", "완성(Folding)"), 
        ("생산부", "완성(Packing)"), ("생산부", "완성창고"), 
        ("생산부", "WET PROCESS"), 
        # 관리부 (세분화)
        ("관리부", "인사(HRD)"), ("관리부", "총무(GA)"), ("관리부", "시설(Utility)"),
        ("관리부", "IT"), ("관리부", "회계(ACC)"), ("관리부", "무역(EXIM)"),
        ("관리부", "IT INVENTORY"), ("관리부", "BP"), ("관리부", "CSR"),
        ("관리부", "기타(Cleaner/Nurse)"),
        # 지원부
        ("지원부", "지원공통")
    ]
    
    initial_data = []
    for main, sub in departments:
        if main == "생산부":
            # 생산부는 직접/간접/합계 모두 표시
            initial_data.append({"대분류": main, "부서명": sub, "구분": "직접", "TO_인원": 0, "PO_인원": 0, "비고": ""})
            initial_data.append({"대분류": main, "부서명": sub, "구분": "간접", "TO_인원": 0, "PO_인원": 0, "비고": ""})
            initial_data.append({"대분류": main, "부서명": sub, "구분": "▶ 합계", "TO_인원": 0, "PO_인원": 0, "비고": ""}) 
        elif main == "관리부":
            # 관리부는 요청하신 대로 '간접'으로만 단일 표시
            initial_data.append({"대분류": main, "부서명": sub, "구분": "간접", "TO_인원": 0, "PO_인원": 0, "비고": ""})
        else:
            # 지원부 등
            initial_data.append({"대분류": main, "부서명": sub, "구분": "해당없음", "TO_인원": 0, "PO_인원": 0, "비고": ""})
            
    st.session_state.df_v6 = pd.DataFrame(initial_data)

df = st.session_state.df_v6.copy()

# 4. 자동 계산 로직 (부서별 합계 및 전체 합계)
for dept in df['부서명'].unique():
    mask = df['부서명'] == dept
    if '▶ 합계' in df.loc[mask, '구분'].values:
        sub_to = df.loc[mask & df['구분'].isin(['직접', '간접']), 'TO_인원'].sum()
        sub_po = df.loc[mask & df['구분'].isin(['직접', '간접']), 'PO_인원'].sum()
        df.loc[mask & (df['구분'] == '▶ 합계'), 'TO_인원'] = sub_to
        df.loc[mask & (df['구분'] == '▶ 합계'), 'PO_인원'] = sub_po

# 전체 총합 (합계 줄은 중복계산되므로 빼고 직접/간접/해당없음만 더합니다)
calc_mask = df['구분'].isin(['직접', '간접', '해당없음'])
total_to = df.loc[calc_mask, 'TO_인원'].sum()
total_po = df.loc[calc_mask, 'PO_인원'].sum()

# 비율 및 차이 계산
df["TO_비중(%)"] = (df["TO_인원"] / total_to * 100).fillna(0) if total_to > 0 else 0.0
df["PO_비중(%)"] = (df["PO_인원"] / total_po * 100).fillna(0) if total_po > 0 else 0.0
df["차이(TO-PO)"] = df["TO_인원"] - df["PO_인원"]

# 5. 엑셀 셀 병합 시각적 효과 구현
df["대분류_표시"] = df["대분류"]
df["부서명_표시"] = df["부서명"]

for i in range(1, len(df)):
    if df.loc[i, "대분류"] == df.loc[i-1, "대분류"]:
        df.loc[i, "대분류_표시"] = "" 
    if df.loc[i, "부서명"] == df.loc[i-1, "부서명"]:
        df.loc[i, "부서명_표시"] = "" 

# 화면에 보여줄 컬럼 순서 지정
display_cols = ["대분류_표시", "부서명_표시", "구분", "TO_인원", "TO_비중(%)", "PO_인원", "PO_비중(%)", "차이(TO-PO)", "비고"]
editor_df = df[display_cols]

st.subheader(f"📝 {selected_factory} 상세 현황 입력")
st.caption("💡 **'직접'**, **'간접'**, **'해당없음'** 줄에만 인원을 입력하세요. **'▶ 합계'** 줄은 자동으로 계산됩니다.")

# 6. 데이터 에디터 출력
edited_df = st.data_editor(
    editor_df,
    use_container_width=True,
    num_rows="fixed",
    column_config={
        "대분류_표시": st.column_config.TextColumn("대분류", disabled=True),
        "부서명_표시": st.column_config.TextColumn("부서명", disabled=True),
        "구분": st.column_config.TextColumn("구분", disabled=True),
        "TO_인원": st.column_config.NumberColumn("TO (인원)", min_value=0, format="%d"),
        "TO_비중(%)": st.column_config.NumberColumn("TO (전체대비)", format="%.1f%%", disabled=True),
        "PO_인원": st.column_config.NumberColumn("PO (인원)", min_value=0, format="%d"),
        "PO_비중(%)": st.column_config.NumberColumn("PO (전체대비)", format="%.1f%%", disabled=True),
        "차이(TO-PO)": st.column_config.NumberColumn("차이 (TO-PO)", disabled=True),
        "비고": st.column_config.TextColumn("비고"),
    },
    hide_index=True,
)

# 7. 사용자가 입력한 값 세션에 저장 (다음 새로고침 시 자동 계산을 위해)
st.session_state.df_v6["TO_인원"] = edited_df["TO_인원"]
st.session_state.df_v6["PO_인원"] = edited_df["PO_인원"]
st.session_state.df_v6["비고"] = edited_df["비고"]

# 8. 하단 합계 요약 대시보드
st.divider()
k1, k2, k3, k4 = st.columns(4)
k1.metric("전체 정원 (TO 합계)", f"{total_to:,} 명")
k2.metric("전체 현원 (PO 합계)", f"{total_po:,} 명")
k3.metric("과/부족 (TO-PO)", f"{(total_to - total_po):,} 명")
k4.metric("평균 충원율", f"{(total_po / total_to * 100):.1f}%" if total_to > 0 else "0.0%")

# 9. 데이터 내보내기
st.write("")
csv = edited_df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="💾 현재 결과 엑셀용으로 다운로드 (CSV)",
    data=csv,
    file_name=f"TOPO_{selected_factory}_{selected_date}.csv",
    mime="text/csv",
)
