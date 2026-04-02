# 3. 데이터 구조 설계 (합계 Row 기호 강조)
if "df_v3" not in st.session_state:
    departments = [
        ("생산", "재단(Cutting)"), ("생산", "봉제(Sewing)"), 
        ("생산", "완성(Iron)"), ("생산", "완성(Folding)"), 
        ("생산", "완성(Packing)"), ("생산", "완성창고"), 
        ("생산", "WET PROCESS"), ("관리", "관리공통"), ("지원", "지원공통")
    ]
    
    initial_data = []
    for main, sub in departments:
        if main == "생산":
            initial_data.append({"대분류": main, "부서명": sub, "구분": "직접", "TO_인원": 0, "PO_인원": 0, "비고": ""})
            initial_data.append({"대분류": main, "부서명": sub, "구분": "간접", "TO_인원": 0, "PO_인원": 0, "비고": ""})
            # 합계 대신 눈에 띄는 기호 추가
            initial_data.append({"대분류": main, "부서명": sub, "구분": "▶ 합계", "TO_인원": 0, "PO_인원": 0, "비고": ""}) 
        else:
            initial_data.append({"대분류": main, "부서명": sub, "구분": "해당없음", "TO_인원": 0, "PO_인원": 0, "비고": ""})
            
    st.session_state.df_v3 = pd.DataFrame(initial_data)

df = st.session_state.df_v3.copy()

# 4. 자동 계산 로직 (부서별 합계 계산 조건 수정)
for dept in df['부서명'].unique():
    mask = df['부서명'] == dept
    if '▶ 합계' in df.loc[mask, '구분'].values:
        sub_to = df.loc[mask & df['구분'].isin(['직접', '간접']), 'TO_인원'].sum()
        sub_po = df.loc[mask & df['구분'].isin(['직접', '간접']), 'PO_인원'].sum()
        df.loc[mask & (df['구분'] == '▶ 합계'), 'TO_인원'] = sub_to
        df.loc[mask & (df['구분'] == '▶ 합계'), 'PO_인원'] = sub_po
